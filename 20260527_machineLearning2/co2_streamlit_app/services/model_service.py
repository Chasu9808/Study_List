import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from config import MODEL_PATH, MODEL_METADATA_PATH


def get_models():
    models = {
        "LinearRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LinearRegression())
        ]),
        "Ridge": Pipeline([
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=1.0))
        ]),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        ),
        "GradientBoostingRegressor": GradientBoostingRegressor(
            random_state=42
        )
    }

    return models


def train_and_evaluate_models(model_df, features, target):
    """
    여러 회귀 모델을 학습하고 평가하는 함수

    추가 반환:
    - evaluation_df: Best Model 기준 실제값/예측값/오차 비교 데이터
    """

    X = model_df[features]
    y = model_df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    models = get_models()

    results = []
    trained_models = {}

    for model_name, model in models.items():
        model.fit(X_train, y_train)

        pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, pred)
        rmse = np.sqrt(mean_squared_error(y_test, pred))
        r2 = r2_score(y_test, pred)

        results.append({
            "model_name": model_name,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2
        })

        trained_models[model_name] = model

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values("MAE", ascending=True).reset_index(drop=True)

    best_model_name = result_df.iloc[0]["model_name"]
    best_model = trained_models[best_model_name]

    best_pred = best_model.predict(X_test)

    evaluation_df = model_df.loc[X_test.index, ["country", "year", target]].copy()
    evaluation_df = evaluation_df.rename(columns={target: "actual_co2"})
    evaluation_df["predicted_co2"] = best_pred
    evaluation_df["absolute_error"] = (
        evaluation_df["actual_co2"] - evaluation_df["predicted_co2"]
    ).abs()

    evaluation_df = evaluation_df.sort_values(
        "absolute_error",
        ascending=False
    ).reset_index(drop=True)

    return (
        result_df,
        trained_models,
        best_model_name,
        best_model,
        X_train,
        X_test,
        y_train,
        y_test,
        evaluation_df
    )


def get_feature_importance(best_model, best_model_name, features):
    if best_model_name in ["RandomForestRegressor", "GradientBoostingRegressor"]:
        importance_df = pd.DataFrame({
            "feature": features,
            "importance": best_model.feature_importances_
        }).sort_values("importance", ascending=False)

        return importance_df

    return None


def save_best_model(best_model, best_model_name, features, target, result_df, evaluation_df=None):
    """
    Best Model과 메타데이터를 파일로 저장하는 함수

    저장 파일:
    - models/best_model.pkl
    - models/model_metadata.pkl
    """

    os.makedirs("models", exist_ok=True)

    best_row = result_df.iloc[0].to_dict()

    metadata = {
        "best_model_name": best_model_name,
        "features": features,
        "target": target,
        "best_metrics": {
            "MAE": best_row["MAE"],
            "RMSE": best_row["RMSE"],
            "R2": best_row["R2"]
        },
        "result_df": result_df,
        "evaluation_df": evaluation_df
    }

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(metadata, MODEL_METADATA_PATH)

    return MODEL_PATH, MODEL_METADATA_PATH


def load_saved_model():
    """
    저장된 Best Model과 메타데이터를 불러오는 함수
    """

    if not os.path.exists(MODEL_PATH):
        return None, None

    if not os.path.exists(MODEL_METADATA_PATH):
        return None, None

    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(MODEL_METADATA_PATH)

    return model, metadata


def saved_model_exists():
    """
    저장된 모델 파일 존재 여부 확인 함수
    """

    return os.path.exists(MODEL_PATH) and os.path.exists(MODEL_METADATA_PATH)