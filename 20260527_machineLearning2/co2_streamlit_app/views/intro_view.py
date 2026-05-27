import streamlit as st

from utils.ui import render_hero, render_section_title


def render_project_intro():
    render_hero(
        title="국가별 CO₂ 배출량 분석 및 예측 대시보드",
        description=(
            "공개 기후 데이터를 기반으로 국가별 탄소배출량 추세를 분석하고, "
            "경제·에너지 지표를 활용해 CO₂ 배출량을 예측하는 머신러닝 대시보드입니다."
        ),
        badge_text="Climate Data · Regression Model · Streamlit"
    )

    render_section_title(
        "프로젝트 개요",
        "이 프로젝트는 데이터 분석, 머신러닝 모델링, 웹 대시보드 구현 흐름을 하나의 서비스 형태로 구성하는 것을 목표로 합니다."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Data Source", "OWID CO₂")
        st.markdown(
            """
            국가·연도별 CO₂ 배출량, 인구, GDP, 에너지 소비량 데이터를 활용합니다.
            """
        )

    with col2:
        st.metric("Model Type", "Regression")
        st.markdown(
            """
            sklearn 기반 회귀 모델을 비교하고 MAE 기준으로 Best Model을 선정합니다.
            """
        )

    with col3:
        st.metric("Interface", "Streamlit")
        st.markdown(
            """
            분석 결과, 모델 성능, 사용자 입력 예측 기능을 웹 화면에서 제공합니다.
            """
        )

    render_section_title("핵심 기능")

    st.markdown(
        """
        - 국가별 CO₂ 배출량 추세 분석
        - 연도별 배출량 상위 국가 시각화
        - GDP, 인구, 에너지 소비량과 CO₂ 배출량의 관계 분석
        - sklearn 회귀 모델 학습 및 성능 비교
        - Best Model 저장 및 재사용
        - 사용자 입력 기반 CO₂ 배출량 예측
        """
    )

    render_section_title("프로젝트 목적")

    st.info(
        """
        단순히 CO₂ 배출량을 예측하는 것이 아니라, 공개 데이터를 기반으로  
        어떤 경제·에너지 지표가 탄소배출량과 관련이 있는지 분석하고  
        이를 사용자가 확인할 수 있는 대시보드 형태로 구현하는 데 목적이 있습니다.
        """
    )