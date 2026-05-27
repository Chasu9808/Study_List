import os
import streamlit as st

from config import STYLE_PATH


def load_css():
    """
    외부 CSS 파일을 Streamlit 앱에 적용하는 함수
    """
    if not os.path.exists(STYLE_PATH):
        st.warning(f"CSS 파일을 찾을 수 없습니다: {STYLE_PATH}")
        return

    with open(STYLE_PATH, "r", encoding="utf-8") as file:
        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


def render_hero(title, description, badge_text=None):
    """
    페이지 상단의 기업형 히어로 영역 렌더링
    """
    badge_html = ""

    if badge_text:
        badge_html = f'<div class="status-badge">{badge_text}</div>'

    st.markdown(
        f"""
        <div class="hero-card">
            {badge_html}
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_title(title, description=None):
    """
    공통 섹션 제목 렌더링
    """
    description_html = ""

    if description:
        description_html = f'<div class="section-description">{description}</div>'

    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        {description_html}
        """,
        unsafe_allow_html=True
    )


def render_card(content):
    """
    일반 HTML 카드 렌더링
    """
    st.markdown(
        f"""
        <div class="dashboard-card">
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_badge(text):
    """
    중립 배지 렌더링
    """
    st.markdown(
        f"""
        <span class="neutral-badge">{text}</span>
        """,
        unsafe_allow_html=True
    )


def render_page_gap():
    """
    페이지 섹션 사이 간격용 함수
    """
    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)


def render_small_caption(text):
    """
    작은 보조 설명 텍스트
    """
    st.markdown(
        f"""
        <div style="
            color:#64748b;
            font-size:0.92rem;
            line-height:1.6;
            margin-top:-0.2rem;
            margin-bottom:0.8rem;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )