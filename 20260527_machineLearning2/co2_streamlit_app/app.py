import streamlit as st

from config import PAGE_TITLE, PAGE_ICON
from services.data_service import load_data
from utils.ui import load_css

from views.intro_view import render_project_intro
from views.data_view import render_data_overview
from views.trend_view import render_country_trend
from views.top_emitters_view import render_top_emitters
from views.relationship_view import render_variable_relationship
from views.training_view import render_model_training
from views.prediction_view import render_prediction


st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)


def main():
    load_css()

    try:
        df = load_data()

        st.sidebar.title("CO₂ Dashboard")

        st.sidebar.markdown(
            """
            <div class="sidebar-caption">
                Climate Data Analysis<br>
                Regression Model Dashboard
            </div>
            """,
            unsafe_allow_html=True
        )

        menu = st.sidebar.radio(
            "Navigation",
            [
                "프로젝트 소개",
                "데이터 탐색",
                "국가별 추세",
                "배출량 상위 국가",
                "변수 관계 분석",
                "모델 학습",
                "직접 예측"
            ]
        )

        if menu == "프로젝트 소개":
            render_project_intro()

        elif menu == "데이터 탐색":
            render_data_overview(df)

        elif menu == "국가별 추세":
            render_country_trend(df)

        elif menu == "배출량 상위 국가":
            render_top_emitters(df)

        elif menu == "변수 관계 분석":
            render_variable_relationship(df)

        elif menu == "모델 학습":
            render_model_training(df)

        elif menu == "직접 예측":
            render_prediction(df)

    except FileNotFoundError:
        st.error("data/owid-co2-data.csv 파일을 찾을 수 없습니다.")
        st.info("CSV 파일을 data 폴더 안에 넣었는지 확인해주세요.")

    except Exception as e:
        st.error("앱 실행 중 오류가 발생했습니다.")
        st.exception(e)


if __name__ == "__main__":
    main()