# Study List

생성형 AI 기반 기업솔루션 개발 실무 프로젝트 과정에서 진행 중인 학습 내용을 날짜별로 정리한 저장소입니다.

Python 데이터 분석, 데이터 시각화, Streamlit 대시보드, 머신러닝 실습 내용을 수업 진행 순서에 따라 기록하고 있습니다.

---

## 학습 목적

이 저장소는 수업 중 진행한 실습 코드와 학습 내용을 정리하기 위한 공간입니다.

단순히 결과 파일만 저장하는 것이 아니라, 각 날짜별로 어떤 개념을 학습했고 어떤 실습을 진행했는지 기록하여 이후 복습과 포트폴리오 정리에 활용하는 것을 목표로 합니다.

---

## 현재 학습 흐름

| 날짜 | 폴더 | 학습 내용 | 상태 |
|---|---|---|---|
| 2026-05-19 | `20260519_pandas` | uv 환경 구성, numpy, pandas 기초, 타이타닉 데이터 탐색 | 완료 |
| 2026-05-20 | `20260520_eda` | EDA 심화, matplotlib, plotly 데이터 시각화 | 완료 |
| 2026-05-21 | `20260521_streamlit_study` | Streamlit 입문, 위젯, 대시보드 구성 | 완료 |
| 2026-05-22 | `20260522_streamlit_study2` | session_state, 멀티페이지, 배포 | 완료 |
| 2026-05-26 | `20260526_machineLearning` | 머신러닝 개요, 지도학습, k-NN 분류 | 완료 |
| 2026-05-27 | `20260527_machineLearning2` | 회귀 알고리즘, StandardScaler, Ridge/Lasso | 진행 중 |

---

## 주요 학습 키워드

- Python 데이터 분석 환경 구성
- uv 기반 프로젝트 관리
- pandas 데이터 탐색 및 전처리
- matplotlib / plotly 데이터 시각화
- Streamlit 대시보드 제작
- session_state 기반 상태 관리
- 머신러닝 지도학습 파이프라인
- k-NN 분류 및 회귀
- 선형 회귀
- StandardScaler 표준화
- Ridge / Lasso 규제

---

## 프로젝트 구조

```text
Study_List-main/
├── 20260519_pandas/
├── 20260520_eda/
├── 20260521_streamlit_study/
├── 20260522_streamlit_study2/
├── 20260526_machineLearning/
├── 20260527_machineLearning2/
├── pyproject.toml
└── README.md

실행 방법

이 저장소는 uv 기반으로 Python 환경을 관리합니다.

uv sync

각 날짜별 실습 폴더로 이동하여 필요한 파일을 실행합니다.

cd 20260527_machineLearning2
uv run python 파일명.py

Streamlit 앱은 아래와 같이 실행합니다.

uv run streamlit run app.py
학습 정리

현재 이 저장소는 수업 진행에 맞춰 계속 업데이트 중입니다.

초반에는 pandas를 활용한 데이터 탐색과 전처리를 학습했고, 이후 matplotlib, plotly를 활용하여 데이터를 시각화했습니다.

그다음 Streamlit을 사용해 분석 결과를 웹 대시보드 형태로 구성하는 방법을 실습했습니다.

현재는 머신러닝 파트로 넘어와 지도학습의 기본 흐름을 학습하고 있으며, k-NN 분류, 회귀, 선형 회귀, 표준화, Ridge/Lasso 규제를 실습하고 있습니다.

앞으로의 학습 예정
분류 알고리즘 심화
Logistic Regression
Precision / Recall 평가 지표
Cross-Entropy 손실 함수
SGD 기반 학습
머신러닝 결과를 활용한 Streamlit 예측 앱 구성
