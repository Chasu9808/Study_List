import streamlit as st

age_range = st.slider("나이 범위", 0, 80, (0,80), key='age_range')

# 읽기
st.write("현재 선택 값 :", st.session_state['age_range'])