import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_titanic():
    url = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
    return pd.read_csv(url)

df = load_titanic().copy()
df['Age'] = df['Age'].fillna(df['Age'].median())

st.title("타이타닉 대시보드")

with st.sidebar:
    st.header("필터")
    pclass_options = st.multiselect("객실 등급", [1, 2, 3], default=[1, 2, 3])
    gender = st.selectbox("성별", ["전체", "male", "female"])
    age_range = st.slider("나이 범위", 0, 80, (0, 80))
    survived_only = st.checkbox("생존자만")

filtered = df[df['Pclass'].isin(pclass_options)]
filtered = filtered[(filtered['Age'] >= age_range[0]) & (filtered['Age'] <= age_range[1])]
if gender != "전체": filtered = filtered[filtered['Sex'] == gender]
if survived_only:    filtered = filtered[filtered['Survived'] == 1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 승객 수", len(filtered))

with col2:
    survival_rate = filtered['Survived'].mean() * 100 if len(filtered) > 0 else 0
    st.metric("생존율", f"{survival_rate:.1f}%")

with col3:
    avg_age = filtered['Age'].mean() if len(filtered) > 0 else 0
    st.metric("평균 나이", f"{avg_age:.1f}세")

tab1, tab2 = st.tabs(["📊 차트", "📋 데이터"])

with tab1:
    fig = px.histogram(filtered, x='Age', nbins=20,
                       title='나이 분포', template='simple_white')
    st.plotly_chart(fig, width='stretch')
with tab2:
    st.dataframe(filtered[['Name','Survived','Pclass','Sex','Age','Fare']],
                 hide_index=True)