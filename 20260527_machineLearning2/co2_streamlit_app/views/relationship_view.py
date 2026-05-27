import streamlit as st
import plotly.express as px

from utils.ui import render_hero, render_section_title, render_page_gap


def render_variable_relationship(df):
    render_hero(
        title="변수 관계 분석",
        description=(
            "GDP, 인구, 에너지 소비량 등 주요 경제·에너지 지표와 "
            "CO₂ 배출량의 관계를 산점도와 상관계수로 분석합니다."
        ),
        badge_text="Feature Analysis"
    )

    valid_df = df[
        (df["iso_code"].notna()) &
        (df["co2"].notna())
    ].copy()

    candidate_features = [
        "population",
        "gdp",
        "primary_energy_consumption",
        "energy_per_capita",
        "co2_per_capita"
    ]

    available_features = [
        col for col in candidate_features if col in valid_df.columns
    ]

    if not available_features:
        st.warning("분석 가능한 숫자형 변수가 없습니다.")
        return

    render_section_title(
        "분석 조건 선택",
        "CO₂ 배출량과 비교할 변수와 분석 연도를 선택합니다."
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_feature = st.selectbox(
            "CO₂ 배출량과 비교할 변수",
            available_features,
            index=available_features.index("primary_energy_consumption")
            if "primary_energy_consumption" in available_features
            else 0
        )

    with col2:
        min_year = int(valid_df["year"].min())
        max_year = int(valid_df["year"].max())

        selected_year = st.slider(
            "분석할 연도",
            min_value=min_year,
            max_value=max_year,
            value=max_year
        )

    year_df = valid_df[
        (valid_df["year"] == selected_year) &
        (valid_df[selected_feature].notna())
    ].copy()

    if year_df.empty:
        st.warning("선택한 연도와 변수에 해당하는 데이터가 없습니다.")
        return

    render_section_title(
        "요약 지표",
        f"{selected_year}년 기준 분석 대상 국가 수와 평균값을 확인합니다."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("분석 대상 국가 수", f"{year_df['country'].nunique():,}")
    col2.metric("평균 CO₂ 배출량", f"{year_df['co2'].mean():,.2f}")
    col3.metric(f"평균 {selected_feature}", f"{year_df[selected_feature].mean():,.2f}")

    corr_value = year_df[[selected_feature, "co2"]].corr().iloc[0, 1]

    st.info(
        f"""
        선택한 연도 기준 `{selected_feature}`와 `co2`의 상관계수는 **{corr_value:.4f}** 입니다.

        상관계수는 -1에서 1 사이의 값을 가지며,  
        1에 가까울수록 양의 관계, -1에 가까울수록 음의 관계,  
        0에 가까울수록 선형 관계가 약하다고 볼 수 있습니다.
        """
    )

    render_page_gap()

    render_section_title(
        "선택 변수와 CO₂ 배출량 관계",
        "산점도를 통해 국가별 지표와 CO₂ 배출량 사이의 분포를 확인합니다."
    )

    fig = px.scatter(
        year_df,
        x=selected_feature,
        y="co2",
        hover_name="country",
        size="population" if "population" in year_df.columns else None,
        color="country",
        title=f"{selected_year}년 {selected_feature}와 CO₂ 배출량 산점도",
        labels={
            selected_feature: selected_feature,
            "co2": "CO₂ 배출량"
        }
    )

    fig.update_layout(
        xaxis_title=selected_feature,
        yaxis_title="CO₂ 배출량",
        showlegend=False,
        height=650,
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    render_section_title(
        "상관계수 비교",
        "주요 변수들이 CO₂ 배출량과 어느 정도 선형 관계를 가지는지 비교합니다."
    )

    corr_columns = [
        "co2",
        "population",
        "gdp",
        "primary_energy_consumption",
        "energy_per_capita",
        "co2_per_capita"
    ]

    corr_columns = [col for col in corr_columns if col in year_df.columns]

    corr_df = year_df[corr_columns].corr(numeric_only=True)

    st.dataframe(corr_df, use_container_width=True)

    if "co2" in corr_df.columns:
        co2_corr = (
            corr_df["co2"]
            .drop("co2")
            .dropna()
            .sort_values(ascending=False)
            .reset_index()
        )

        co2_corr.columns = ["feature", "correlation_with_co2"]

        render_section_title(
            "CO₂ 배출량과 변수별 상관관계",
            "CO₂ 배출량과 각 변수의 상관계수를 막대그래프로 확인합니다."
        )

        fig_corr = px.bar(
            co2_corr,
            x="feature",
            y="correlation_with_co2",
            title="CO₂ 배출량과 주요 변수의 상관계수",
            labels={
                "feature": "변수",
                "correlation_with_co2": "CO₂와의 상관계수"
            },
            text="correlation_with_co2"
        )

        fig_corr.update_traces(
            texttemplate="%{text:.3f}",
            textposition="outside"
        )

        fig_corr.update_layout(
            yaxis_range=[-1, 1],
            height=500,
            template="plotly_white",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig_corr, use_container_width=True)

    render_section_title(
        "분석 데이터",
        "현재 선택한 연도와 변수 기준으로 분석에 사용된 데이터를 확인합니다."
    )

    display_columns = [
        "country",
        "year",
        selected_feature,
        "population",
        "gdp",
        "primary_energy_consumption",
        "energy_per_capita",
        "co2",
        "co2_per_capita"
    ]

    display_columns = list(dict.fromkeys(display_columns))

    existing_display_columns = [
        col for col in display_columns if col in year_df.columns
    ]

    st.dataframe(
        year_df[existing_display_columns]
        .sort_values("co2", ascending=False)
        .head(30),
        use_container_width=True
    )