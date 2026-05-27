import streamlit as st
import plotly.express as px

from services.data_service import create_model_dataset
from services.model_service import (
    train_and_evaluate_models,
    get_feature_importance,
    save_best_model,
    saved_model_exists,
    load_saved_model
)
from utils.ui import render_hero, render_section_title, render_page_gap


def render_model_training(df):
    render_hero(
        title="CO₂ 배출량 예측 모델 학습",
        description=(
            "국가별 경제·에너지 지표를 기반으로 sklearn 회귀 모델을 학습하고, "
            "MAE, RMSE, R² 기준으로 성능을 비교합니다."
        ),
        badge_text="Model Training"
    )

    model_df, features, target = create_model_dataset(df)

    render_section_title(
        "모델 학습 데이터 정보",
        "학습에 사용할 데이터 수, 입력 변수, 예측 대상을 확인합니다."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("학습 가능 데이터 수", f"{len(model_df):,}")
    col2.metric("입력 변수 수", f"{len(features):,}")
    col3.metric("예측 대상", target)

    st.write("사용 입력 변수")
    st.code(", ".join(features), language="text")

    st.warning(
        """
        현재 모델은 CO₂의 직접 구성 요소인 `coal_co2`, `oil_co2`, `gas_co2`, `cement_co2`를 제외하고 학습합니다.  
        이유는 해당 변수들이 전체 CO₂ 배출량의 하위 구성 요소이기 때문에, 포함할 경우 예측 성능은 높아지지만 모델 해석이 단순해질 수 있기 때문입니다.
        """
    )

    render_section_title(
        "학습 데이터 미리보기",
        "모델 학습에 사용되는 일부 데이터를 확인합니다."
    )

    display_columns = ["country"] + features + [target]
    existing_display_columns = [
        col for col in display_columns if col in model_df.columns
    ]

    st.dataframe(
        model_df[existing_display_columns].head(30),
        use_container_width=True
    )

    render_page_gap()

    render_section_title(
        "저장된 모델 상태",
        "이미 학습되어 저장된 모델 파일이 있는지 확인하고 불러올 수 있습니다."
    )

    if saved_model_exists():
        st.success("저장된 모델 파일이 존재합니다.")

        if st.button("저장된 모델 불러오기"):
            saved_model, metadata = load_saved_model()

            if saved_model is None or metadata is None:
                st.error("저장된 모델을 불러오지 못했습니다.")
            else:
                st.session_state["best_model"] = saved_model
                st.session_state["best_model_name"] = metadata["best_model_name"]
                st.session_state["features"] = metadata["features"]
                st.session_state["target"] = metadata["target"]
                st.session_state["result_df"] = metadata["result_df"]

                if metadata.get("evaluation_df") is not None:
                    st.session_state["evaluation_df"] = metadata["evaluation_df"]

                st.success("저장된 모델을 현재 세션으로 불러왔습니다.")
    else:
        st.info("아직 저장된 모델 파일이 없습니다.")

    render_section_title(
        "모델 학습 실행",
        "여러 회귀 모델을 학습하고 성능을 비교한 뒤 Best Model을 저장합니다."
    )

    if st.button("모델 학습 실행"):
        with st.spinner("모델을 학습하고 성능을 평가하는 중입니다..."):
            (
                result_df,
                trained_models,
                best_model_name,
                best_model,
                X_train,
                X_test,
                y_train,
                y_test,
                evaluation_df
            ) = train_and_evaluate_models(model_df, features, target)

            st.session_state["result_df"] = result_df
            st.session_state["trained_models"] = trained_models
            st.session_state["best_model_name"] = best_model_name
            st.session_state["best_model"] = best_model
            st.session_state["features"] = features
            st.session_state["target"] = target
            st.session_state["evaluation_df"] = evaluation_df

            model_path, metadata_path = save_best_model(
                best_model=best_model,
                best_model_name=best_model_name,
                features=features,
                target=target,
                result_df=result_df,
                evaluation_df=evaluation_df
            )

        st.success("모델 학습 및 저장이 완료되었습니다.")
        st.info(f"모델 저장 경로: `{model_path}`")
        st.info(f"메타데이터 저장 경로: `{metadata_path}`")

    if "result_df" not in st.session_state:
        st.info("모델 학습 실행 버튼을 눌러 성능 비교를 진행하세요.")
        return

    result_df = st.session_state["result_df"]
    best_model_name = st.session_state["best_model_name"]
    best_model = st.session_state["best_model"]
    features = st.session_state["features"]

    render_page_gap()

    render_section_title(
        "모델별 성능 비교",
        "MAE는 낮을수록 좋고, R²는 1에 가까울수록 설명력이 높다고 볼 수 있습니다."
    )

    formatted_result_df = result_df.copy()
    formatted_result_df["MAE"] = formatted_result_df["MAE"].round(4)
    formatted_result_df["RMSE"] = formatted_result_df["RMSE"].round(4)
    formatted_result_df["R2"] = formatted_result_df["R2"].round(4)

    st.dataframe(formatted_result_df, use_container_width=True)

    render_section_title(
        "모델별 MAE 비교",
        "MAE 기준으로 모델의 평균 예측 오차를 비교합니다."
    )

    fig_mae = px.bar(
        result_df.sort_values("MAE", ascending=False),
        x="MAE",
        y="model_name",
        orientation="h",
        title="모델별 MAE 비교",
        labels={
            "MAE": "MAE",
            "model_name": "모델명"
        },
        text="MAE"
    )

    fig_mae.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_mae.update_layout(
        height=450,
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_mae, use_container_width=True)

    render_section_title(
        "Best Model",
        "현재 기준에서는 MAE가 가장 낮은 모델을 Best Model로 선정합니다."
    )

    best_row = result_df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Best Model", best_model_name)
    col2.metric("MAE", f"{best_row['MAE']:,.4f}")
    col3.metric("RMSE", f"{best_row['RMSE']:,.4f}")
    col4.metric("R²", f"{best_row['R2']:,.4f}")

    st.info(
        f"""
        선택된 Best Model은 `{best_model_name}` 입니다.  
        해당 모델은 현재 비교 대상 모델 중 MAE가 가장 낮게 나온 모델입니다.
        """
    )

    importance_df = get_feature_importance(best_model, best_model_name, features)

    render_section_title(
        "변수 중요도",
        "트리 기반 모델이 Best Model로 선택된 경우, 예측에 영향을 준 변수 중요도를 확인합니다."
    )

    if importance_df is not None:
        fig_importance = px.bar(
            importance_df.sort_values("importance", ascending=True),
            x="importance",
            y="feature",
            orientation="h",
            title=f"{best_model_name} 변수 중요도",
            labels={
                "importance": "중요도",
                "feature": "변수"
            },
            text="importance"
        )

        fig_importance.update_traces(
            texttemplate="%{text:.4f}",
            textposition="outside"
        )

        fig_importance.update_layout(
            height=450,
            template="plotly_white",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig_importance, use_container_width=True)

        st.dataframe(importance_df, use_container_width=True)

    else:
        st.info(
            """
            현재 Best Model은 선형 계열 모델입니다.  
            이번 단계에서는 트리 기반 모델의 `feature_importances_`만 시각화합니다.
            """
        )

    if "evaluation_df" not in st.session_state:
        st.info("실제값과 예측값 비교 데이터가 없습니다. 모델을 다시 학습하면 생성됩니다.")
        return

    evaluation_df = st.session_state["evaluation_df"].copy()

    render_page_gap()

    render_section_title(
        "실제값 vs 예측값 비교",
        "Best Model이 테스트 데이터에서 실제 CO₂ 배출량을 얼마나 비슷하게 예측했는지 확인합니다."
    )

    fig_actual_pred = px.scatter(
        evaluation_df,
        x="actual_co2",
        y="predicted_co2",
        hover_name="country",
        hover_data=["year", "absolute_error"],
        title="실제 CO₂ 배출량 vs 예측 CO₂ 배출량",
        labels={
            "actual_co2": "실제 CO₂ 배출량",
            "predicted_co2": "예측 CO₂ 배출량"
        }
    )

    min_value = min(
        evaluation_df["actual_co2"].min(),
        evaluation_df["predicted_co2"].min()
    )

    max_value = max(
        evaluation_df["actual_co2"].max(),
        evaluation_df["predicted_co2"].max()
    )

    fig_actual_pred.add_shape(
        type="line",
        x0=min_value,
        y0=min_value,
        x1=max_value,
        y1=max_value,
        line=dict(
            dash="dash",
            width=2,
            color="#2563eb"
        )
    )

    fig_actual_pred.update_layout(
        height=600,
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_actual_pred, use_container_width=True)

    render_section_title(
        "오차가 큰 국가 TOP 10",
        "테스트 데이터 중 실제값과 예측값의 차이가 큰 국가를 확인합니다."
    )

    error_top10 = evaluation_df.sort_values(
        "absolute_error",
        ascending=False
    ).head(10)

    display_error_df = error_top10.copy()
    display_error_df["actual_co2"] = display_error_df["actual_co2"].round(4)
    display_error_df["predicted_co2"] = display_error_df["predicted_co2"].round(4)
    display_error_df["absolute_error"] = display_error_df["absolute_error"].round(4)

    st.dataframe(
        display_error_df[
            [
                "country",
                "year",
                "actual_co2",
                "predicted_co2",
                "absolute_error"
            ]
        ],
        use_container_width=True
    )

    fig_error = px.bar(
        error_top10.sort_values("absolute_error", ascending=True),
        x="absolute_error",
        y="country",
        orientation="h",
        title="오차가 큰 국가 TOP 10",
        labels={
            "absolute_error": "절대 오차",
            "country": "국가"
        },
        text="absolute_error"
    )

    fig_error.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_error.update_layout(
        height=500,
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_error, use_container_width=True)