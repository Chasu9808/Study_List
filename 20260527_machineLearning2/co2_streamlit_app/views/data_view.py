import pandas as pd
import streamlit as st

from config import IMPORTANT_COLUMNS
from utils.ui import render_hero, render_section_title


def render_data_overview(df):
    render_hero(
        title="데이터 탐색",
        description="CO₂ 데이터셋의 기본 구조, 주요 컬럼, 결측치 현황을 확인합니다.",
        badge_text="Data Overview"
    )

    render_section_title(
        "데이터 기본 정보",
        "전체 데이터의 규모와 국가 수, 연도 범위를 확인합니다."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("전체 행 수", f"{len(df):,}")
    col2.metric("전체 컬럼 수", f"{len(df.columns):,}")
    col3.metric("국가/지역 수", f"{df['country'].nunique():,}")
    col4.metric("연도 범위", f"{int(df['year'].min())} ~ {int(df['year'].max())}")

    render_section_title(
        "데이터 미리보기",
        "원본 데이터의 상위 일부 행을 확인합니다."
    )

    st.dataframe(df.head(30), use_container_width=True)

    render_section_title(
        "주요 컬럼 결측치 현황",
        "모델링과 분석에 사용할 주요 컬럼의 결측치 개수와 비율을 확인합니다."
    )

    existing_columns = [col for col in IMPORTANT_COLUMNS if col in df.columns]

    summary_df = pd.DataFrame({
        "주요 컬럼": existing_columns,
        "결측치 개수": [df[col].isna().sum() for col in existing_columns],
        "결측치 비율(%)": [
            round(df[col].isna().mean() * 100, 2) for col in existing_columns
        ]
    })

    st.dataframe(summary_df, use_container_width=True)