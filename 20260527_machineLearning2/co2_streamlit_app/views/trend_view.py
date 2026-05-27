import streamlit as st
import plotly.express as px

from services.data_service import get_country_list
from utils.ui import render_hero, render_section_title, render_page_gap


def render_country_trend(df):
    render_hero(
        title="국가별 CO₂ 배출량 추세",
        description="선택한 국가의 연도별 CO₂ 배출량 변화를 시계열 그래프로 확인합니다.",
        badge_text="Country Trend"
    )

    country_list = get_country_list(df)

    render_section_title(
        "국가 선택",
        "분석할 국가를 선택하면 해당 국가의 CO₂ 배출량 추세가 표시됩니다."
    )

    selected_country = st.selectbox(
        "국가를 선택하세요.",
        country_list,
        index=country_list.index("South Korea") if "South Korea" in country_list else 0
    )

    country_df = df[
        (df["country"] == selected_country) &
        (df["co2"].notna())
    ].copy()

    if country_df.empty:
        st.warning("선택한 국가의 CO₂ 데이터가 없습니다.")
        return

    country_df = country_df.sort_values("year")

    latest_row = country_df.iloc[-1]
    first_row = country_df.iloc[0]

    render_section_title(
        "요약 지표",
        f"{selected_country}의 데이터 시작 연도, 최신 연도, 최신 CO₂ 배출량을 요약합니다."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("데이터 시작 연도", int(first_row["year"]))
    col2.metric("최신 연도", int(latest_row["year"]))
    col3.metric("최신 CO₂ 배출량", f"{latest_row['co2']:,.2f}")

    render_page_gap()

    render_section_title(
        "연도별 CO₂ 배출량 추세",
        "시계열 그래프를 통해 장기적인 배출량 증가 또는 감소 흐름을 확인합니다."
    )

    fig = px.line(
        country_df,
        x="year",
        y="co2",
        markers=True,
        title=f"{selected_country} CO₂ 배출량 추세",
        labels={
            "year": "연도",
            "co2": "CO₂ 배출량"
        }
    )

    fig.update_layout(
        xaxis_title="연도",
        yaxis_title="CO₂ 배출량",
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    render_section_title(
        "최근 데이터",
        "선택 국가의 최근 연도 데이터를 표로 확인합니다."
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
        col for col in display_columns if col in country_df.columns
    ]

    st.dataframe(
        country_df[existing_display_columns].tail(20),
        use_container_width=True
    )