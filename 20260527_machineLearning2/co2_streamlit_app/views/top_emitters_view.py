import streamlit as st
import plotly.express as px

from utils.ui import render_hero, render_section_title, render_page_gap


def render_top_emitters(df):
    render_hero(
        title="연도별 CO₂ 배출량 상위 국가",
        description="선택한 연도를 기준으로 CO₂ 배출량이 높은 국가를 비교합니다.",
        badge_text="Top Emitters"
    )

    valid_df = df[
        (df["iso_code"].notna()) &
        (df["co2"].notna())
    ].copy()

    latest_year = int(valid_df["year"].max())

    render_section_title(
        "조회 조건",
        "분석할 연도와 상위 국가 개수를 선택합니다."
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_year = st.slider(
            "조회할 연도 선택",
            min_value=int(valid_df["year"].min()),
            max_value=latest_year,
            value=latest_year
        )

    with col2:
        top_n = st.slider(
            "상위 국가 개수",
            min_value=5,
            max_value=30,
            value=10
        )

    year_df = valid_df[valid_df["year"] == selected_year].copy()

    if year_df.empty:
        st.warning("선택한 연도의 데이터가 없습니다.")
        return

    top_emitters = year_df.sort_values("co2", ascending=False).head(top_n)

    render_section_title(
        "배출량 상위 국가 시각화",
        f"{selected_year}년 기준 CO₂ 배출량 상위 {top_n}개 국가를 비교합니다."
    )

    fig = px.bar(
        top_emitters.sort_values("co2", ascending=True),
        x="co2",
        y="country",
        orientation="h",
        title=f"{selected_year}년 CO₂ 배출량 상위 국가",
        labels={
            "co2": "CO₂ 배출량",
            "country": "국가"
        },
        text="co2"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="CO₂ 배출량",
        yaxis_title="국가",
        height=600,
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    render_page_gap()

    render_section_title(
        "상위 국가 데이터",
        "그래프에 사용된 국가별 상세 데이터를 확인합니다."
    )

    display_columns = [
        "country",
        "year",
        "population",
        "gdp",
        "co2",
        "co2_per_capita",
        "primary_energy_consumption",
        "energy_per_capita"
    ]

    existing_display_columns = [
        col for col in display_columns if col in top_emitters.columns
    ]

    st.dataframe(
        top_emitters[existing_display_columns],
        use_container_width=True
    )