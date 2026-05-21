import streamlit as st

st.title("스트림릿에 대해 배우자!")
st.header("위젯")
st.text("위젯이란? 사용자 입력을 받는 UI요소들 ...python 변수로 돌아옴")

# 텍스트 입력
name = st.text_input("이름 : ", placeholder="홍갈동")
st.write(f"{name}님 반가워요")

# 드롭다운 선택
gender = st.selectbox("성별", ["선택", "mail", "femail"])
st.write("성별 : ", gender)