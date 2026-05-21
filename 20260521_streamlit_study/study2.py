import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_imdb():
    df = pd.read_csv('imdb_top_1000.csv')
    df['Released_Year'] = pd.to_numeric(
        df['Released_Year'], errors='coerce')
    return df

imdb = load_imdb().copy()


st.title("IMDB 영화 대시보드")

with st.sidebar:
    min_rating = st.slider("최소 평점", 7.0, 9.5, 7.6, step=0.1)
    year_range = st.slider("개봉 연도", 1920, 2020, (2000, 2020))

filtered = imdb[
    (imdb['IMDB_Rating'] >= min_rating) &
    (imdb['Released_Year'] >= year_range[0]) &
    (imdb['Released_Year'] <= year_range[1])
]

col1, col2 = st.columns(2)

with col1:
    st.metric("영화 수", len(filtered))

with col2:
    avg_rating = filtered['IMDB_Rating'].mean() if len(filtered) > 0 else 0
    st.metric("평균 평점", f"{avg_rating:.2f}")

tab1, tab2 = st.tabs(["평점 히스토그램", "평점 산점도"])

with tab1:
    st.subheader("IMDB 평점 분포")

    fig = px.histogram(
        filtered,
        x="IMDB_Rating",
        nbins=20,
        title="IMDB 평점 히스토그램"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("개봉 연도별 IMDB 평점")

    fig = px.scatter(
        filtered,
        x="Released_Year",
        y="IMDB_Rating",
        hover_name="Series_Title",
        title="개봉 연도별 IMDB 평점 분포"
    )

    st.plotly_chart(fig, use_container_width=True)

st.subheader("필터링된 데이터")
st.dataframe(filtered)