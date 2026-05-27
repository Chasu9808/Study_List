import pandas as pd
import streamlit as st

from services.data_service import create_model_dataset
from services.model_service import load_saved_model, saved_model_exists
from utils.ui import render_hero, render_section_title, render_page_gap


def find_similar_countries(model_df, target, prediction, top_n=5):
    """
    예측된 CO₂ 배출량과 실제 데이터상 유사한 국가를 찾는 함수

    기준:
    - 최신 연도 데이터 우선 사용
    - 예측값과 실제 co2 값의 절대 차이가 작은 순서
    """

    latest_year = int(model_df["year"].max())

    latest_df = model_df[
        (model_df["year"] == latest_year) &
        (model_df[target].notna())
    ].copy()

    if latest_df.empty:
        latest_df = model_df[model_df[target].notna()].copy()

    latest_df["difference_from_prediction"] = (
        latest_df[target] - prediction
    ).abs()

    similar_df = latest_df.sort_values(
        "difference_from_prediction",
        ascending=True
    ).head(top_n)

    return similar_df


def render_prediction(df):
    render_hero(
        title="사용자 입력 기반 CO₂ 배출량 예측",
        description=(
            "저장된 Best Model 또는 현재 학습된 모델을 사용하여 "
            "사용자가 입력한 경제·에너지 지표 기반 CO₂ 배출량을 예측합니다."
        ),
        badge_text="Prediction"
    )

    if "best_model" not in st.session_state:
        render_section_title(
            "모델 상태",
            "예측을 실행하려면 먼저 학습된 모델이 필요합니다."
        )

        if saved_model_exists():
            st.info("현재 세션에는 모델이 없지만 저장된 모델 파일이 존재합니다.")

            if st.button("저장된 모델 불러오기"):
                saved_model, metadata = load_saved_model()

                if saved_model is None or metadata is None:
                    st.error("저장된 모델을 불러오지 못했습니다.")
                    return

                st.session_state["best_model"] = saved_model
                st.session_state["best_model_name"] = metadata["best_model_name"]
                st.session_state["features"] = metadata["features"]
                st.session_state["target"] = metadata["target"]
                st.session_state["result_df"] = metadata["result_df"]

                if metadata.get("evaluation_df") is not None:
                    st.session_state["evaluation_df"] = metadata["evaluation_df"]

                st.success("저장된 모델을 불러왔습니다. 예측 화면을 다시 구성합니다.")
                st.rerun()
        else:
            st.warning("아직 학습된 모델이 없습니다.")
            st.info("먼저 왼쪽 메뉴의 `모델 학습` 페이지에서 모델 학습을 실행해주세요.")

        return

    best_model = st.session_state["best_model"]
    best_model_name = st.session_state["best_model_name"]
    features = st.session_state["features"]

    render_section_title(
        "현재 사용 중인 모델",
        "예측에 사용되는 모델명과 입력 변수를 확인합니다."
    )

    col1, col2 = st.columns(2)

    col1.metric("Best Model", best_model_name)
    col2.metric("입력 변수 수", len(features))

    st.write("모델 입력 변수")
    st.code(", ".join(features), language="text")

    render_page_gap()

    render_section_title(
        "예측 값 입력",
        "국가 단위의 경제·에너지 지표를 입력하면 CO₂ 배출량을 예측합니다."
    )

    st.info(
        """
        아래 입력값은 원본 데이터셋 기준의 숫자 범위를 참고해서 입력하는 것이 좋습니다.  
        실제 정책 판단용 값이 아니라, 학습된 회귀 모델이 계산한 추정값입니다.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        input_year = st.number_input(
            "연도",
            min_value=1900,
            max_value=2100,
            value=2023,
            step=1
        )

        input_population = st.number_input(
            "인구",
            min_value=0.0,
            value=51_000_000.0,
            step=1_000_000.0,
            format="%.2f"
        )

        input_gdp = st.number_input(
            "GDP",
            min_value=0.0,
            value=1_700_000_000_000.0,
            step=10_000_000_000.0,
            format="%.2f"
        )

    with col2:
        input_primary_energy = st.number_input(
            "1차 에너지 소비량",
            min_value=0.0,
            value=3000.0,
            step=100.0,
            format="%.2f"
        )

        input_energy_per_capita = st.number_input(
            "1인당 에너지 소비량",
            min_value=0.0,
            value=60000.0,
            step=1000.0,
            format="%.2f"
        )

    input_data = pd.DataFrame([{
        "year": input_year,
        "population": input_population,
        "gdp": input_gdp,
        "primary_energy_consumption": input_primary_energy,
        "energy_per_capita": input_energy_per_capita
    }])

    input_data = input_data[features]

    render_section_title(
        "입력 데이터 확인",
        "모델에 전달될 최종 입력 데이터를 확인합니다."
    )

    st.dataframe(input_data, use_container_width=True)

    if st.button("CO₂ 배출량 예측 실행"):
        prediction = best_model.predict(input_data)[0]

        render_section_title(
            "예측 결과",
            "입력한 경제·에너지 지표를 기준으로 계산된 CO₂ 배출량 예측값입니다."
        )

        st.metric(
            "예상 CO₂ 배출량",
            f"{prediction:,.2f}"
        )

        st.success(
            f"""
            입력한 경제·에너지 지표를 기준으로 예측한 CO₂ 배출량은  
            **{prediction:,.2f}** 입니다.
            """
        )

        st.warning(
            """
            이 예측값은 실제 정책 판단용 예측이 아니라,  
            공개 기후 데이터를 기반으로 학습한 회귀 모델의 추정 결과입니다.
            """
        )

        model_df, _, target = create_model_dataset(df)

        similar_df = find_similar_countries(
            model_df=model_df,
            target=target,
            prediction=prediction,
            top_n=5
        )

        render_section_title(
            "예측값과 유사한 국가",
            "예측된 CO₂ 배출량과 실제 최신 연도 데이터가 비슷한 국가를 보여줍니다."
        )

        display_similar_df = similar_df[
            [
                "country",
                "year",
                target,
                "difference_from_prediction"
            ]
        ].copy()

        display_similar_df = display_similar_df.rename(columns={
            target: "actual_co2"
        })

        display_similar_df["actual_co2"] = display_similar_df["actual_co2"].round(4)
        display_similar_df["difference_from_prediction"] = (
            display_similar_df["difference_from_prediction"].round(4)
        )

        st.dataframe(
            display_similar_df,
            use_container_width=True
        )

        if not display_similar_df.empty:
            nearest_country = display_similar_df.iloc[0]["country"]
            nearest_year = int(display_similar_df.iloc[0]["year"])

            st.info(
                f"""
                입력값으로 예측된 CO₂ 배출량은 최신 데이터 기준  
                **{nearest_country}({nearest_year})** 의 실제 CO₂ 배출량과 가장 유사합니다.
                """
            )

    render_page_gap()

    render_section_title(
        "입력값 참고용 데이터",
        "입력값을 정할 때 참고할 수 있도록 실제 데이터 일부를 CO₂ 배출량 높은 순서로 보여줍니다."
    )

    model_df, features, target = create_model_dataset(df)

    reference_df = model_df[["country"] + features + [target]].copy()

    st.dataframe(
        reference_df.sort_values(target, ascending=False).head(20),
        use_container_width=True
    )