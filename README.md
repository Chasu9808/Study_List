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
| 2026-05-22 | `20260522_streamlit_study2` | session_state, 멀티페이지, form, file_uploader, 배포 | 완료 |
| 2026-05-26 | `20260526_machineLearning` | 머신러닝 개요, 지도학습, k-NN 분류 | 완료 |
| 2026-05-27 | `20260527_machineLearning2` | 회귀 알고리즘, StandardScaler, 선형 회귀, Ridge/Lasso 규제 | 진행 중 |

---

## 주요 학습 키워드

- Python 데이터 분석 환경 구성
- uv 기반 프로젝트 관리
- numpy 기초
- pandas 데이터 탐색 및 전처리
- matplotlib 데이터 시각화
- plotly 인터랙티브 시각화
- Streamlit 대시보드 제작
- session_state 기반 상태 관리
- Streamlit 멀티페이지 구성
- 머신러닝 지도학습 파이프라인
- k-NN 분류
- k-NN 회귀
- 선형 회귀
- StandardScaler 표준화
- PolynomialFeatures 특성 공학
- Ridge / Lasso 규제
- train/test 성능 비교

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
```

---

## 날짜별 학습 내용

## 2026-05-19: uv · numpy · pandas 기초

Python 데이터 분석을 위한 기본 환경을 구성하고, pandas를 활용한 데이터 탐색과 전처리 기초를 학습했습니다.

### 주요 학습 내용

- uv 기반 Python 프로젝트 생성
- Jupyter Notebook 실행 환경 구성
- numpy와 pandas의 기본 역할 이해
- DataFrame 기본 탐색
- 결측치 확인 및 처리
- 조건 필터링
- groupby 기반 집계 분석

### 주요 실습

- 타이타닉 데이터 기초 탐색
- 성별 생존율 분석
- 결측치 확인 및 age 컬럼 처리
- 쇼핑몰 주문 데이터 생성
- 매출 컬럼 생성
- 카테고리별 집계 분석

---

## 2026-05-20: EDA 심화 + matplotlib · plotly 데이터 시각화

데이터 분석 과정에서 시각화가 가지는 역할을 이해하고, 분석 목적에 맞는 차트를 선택하는 방법을 학습했습니다.

### 주요 학습 내용

- EDA의 개념과 필요성
- 질문 유형별 차트 선택
- matplotlib의 fig/ax 구조
- plotly express 기반 인터랙티브 시각화
- 시각화 결과 PNG 및 HTML 저장

### 주요 실습

- 타이타닉 데이터 matplotlib 시각화
- 히스토그램, 막대그래프, 산점도, 박스플롯, 파이차트 작성
- 서울 아파트 실거래 데이터 시계열 시각화
- IMDB 장르별 평균 평점 분석
- plotly 차트 HTML 저장

---

## 2026-05-21: Streamlit 입문

Python 코드만으로 데이터 대시보드를 구성할 수 있는 Streamlit의 기본 사용법을 학습했습니다.

### 주요 학습 내용

- Streamlit의 개념
- Flask, Dash, Gradio와 Streamlit의 차이
- top-to-bottom rerun 실행 구조
- @st.cache_data의 역할
- 사이드바 위젯 구성
- metric, columns, tabs 기반 대시보드 레이아웃

### 주요 실습

- 타이타닉 필터 대시보드 구현
- selectbox, slider, text_input, multiselect 사용
- 사이드바 필터 적용
- st.metric으로 주요 지표 출력
- st.plotly_chart로 차트 표시
- st.tabs로 화면 분리

---

## 2026-05-22: Streamlit 심화

Streamlit 앱에서 상태를 유지하는 방법과 멀티페이지 앱 구성, 파일 업로드, 배포 과정을 학습했습니다.

### 주요 학습 내용

- st.session_state의 필요성
- rerun 구조와 상태 관리
- 명시적 session_state 읽기/쓰기 패턴
- key 기반 위젯 자동 연결
- st.Page와 st.navigation 기반 멀티페이지 구성
- st.form을 활용한 입력 묶음 처리
- st.file_uploader를 활용한 CSV 업로드
- Streamlit Community Cloud 배포 흐름

### 주요 실습

- 마케팅 또는 이커머스 대시보드 구현
- session_state 기반 필터 초기화 버튼 구현
- overview/detail 멀티페이지 구조 구성
- 페이지 간 필터 상태 공유
- 사용자 CSV 업로드 기능 추가
- requirements.txt 작성
- Streamlit Community Cloud 배포

---

## 2026-05-26: 머신러닝 Day 1

머신러닝의 기본 개념과 지도학습 파이프라인을 학습하고, k-NN 분류 모델을 처음으로 구현했습니다.

### 주요 학습 내용

- AI, ML, DL의 관계
- 지도학습, 비지도학습, 강화학습 구분
- Feature와 Label의 차이
- 지도학습 파이프라인
- train_test_split의 필요성
- 일반화 개념
- k-NN 분류 모델의 작동 방식

### 주요 실습

- 도미/빙어 생선 데이터 구성
- fish_data, fish_target 생성
- KNeighborsClassifier 모델 학습
- fit, predict, score 패턴 실습
- train_test_split으로 훈련/테스트 데이터 분리
- 타이타닉 데이터 문제 정의 워크숍
- 예측 대상, ML 유형, 특성 가설 정리

---

## 2026-05-27: 머신러닝 Day 2

회귀 알고리즘을 학습하고, StandardScaler, 선형 회귀, 다항 회귀, Ridge/Lasso 규제를 실습했습니다.

### 주요 학습 내용

- 회귀와 분류의 차이
- R² 결정 계수
- MSE 손실 함수
- 경사 하강법의 직관
- StandardScaler 표준화
- Data Leakage 방지
- k-NN 회귀
- 선형 회귀
- 다항 특성 생성
- 과적합과 규제
- Ridge와 Lasso의 차이
- 파라미터와 하이퍼파라미터의 차이

### 주요 실습

- 농어 길이 기반 무게 예측
- KNeighborsRegressor 모델 학습
- LinearRegression 모델 학습
- coef_, intercept_ 해석
- PolynomialFeatures로 다항 특성 생성
- degree 증가에 따른 과적합 확인
- StandardScaler 적용
- Ridge(alpha=0.1) 적용
- Lasso(alpha=10) 적용
- Ridge alpha 탐색 그래프 작성
- 캘리포니아 집값 데이터 다중 회귀 실습

---

## 회귀 학습 정리

회귀는 머신러닝에서 연속적인 숫자 값을 예측하는 문제입니다.

분류가 `도미/빙어`, `생존/사망`처럼 정해진 범주를 예측하는 것이라면, 회귀는 `무게`, `집값`, `점수`, `매출`처럼 숫자로 이어지는 값을 예측합니다.

예를 들어 농어의 길이를 보고 무게를 예측하거나, 아파트의 위치와 면적을 보고 집값을 예측하는 문제가 회귀에 해당합니다.

---

## StandardScaler 정리

머신러닝에서는 여러 특성을 함께 사용할 때 각 데이터의 단위와 크기가 다를 수 있습니다.

예를 들어 생선 데이터에서 길이는 cm 단위이고, 무게는 g 단위입니다.

이처럼 서로 다른 단위의 데이터를 그대로 모델에 넣으면 값의 크기가 큰 특성이 모델 판단에 더 큰 영향을 줄 수 있습니다.

`StandardScaler`는 이러한 데이터를 평균 0, 표준편차 1 기준으로 변환하여 모델이 특성을 비슷한 기준에서 비교할 수 있도록 도와줍니다.

```python
ss.fit_transform(train_input)
ss.transform(test_input)
```

훈련 데이터에는 `fit_transform()`을 사용하고, 테스트 데이터에는 `transform()`만 사용해야 합니다.

테스트 데이터에 `fit()`을 적용하면 모델이 평가 데이터의 정보를 미리 알게 되는 Data Leakage 문제가 발생할 수 있습니다.

---

## k-NN 회귀 정리

k-NN 회귀는 새로운 데이터가 들어왔을 때 가까운 이웃들의 정답값을 평균 내어 예측하는 알고리즘입니다.

예를 들어 새 아파트의 가격을 예측할 때, 주변의 비슷한 아파트 3채의 가격이 각각 5억, 5억 5천만, 4억 5천만 원이라면 평균인 약 5억 원을 예측값으로 사용할 수 있습니다.

다만 k-NN 회귀는 기존 훈련 데이터 범위를 벗어난 값을 예측하는 데 약합니다.

훈련 데이터에 45cm 농어까지만 있다면, 100cm 농어가 들어와도 100cm 근처의 이웃을 찾을 수 없기 때문에 45cm 근처 농어들의 평균 무게로 예측하게 됩니다.

이처럼 k-NN 회귀는 외삽에 약하다는 한계가 있습니다.

---

## 선형 회귀 정리

선형 회귀는 데이터의 흐름을 가장 잘 설명하는 하나의 직선을 찾아 값을 예측하는 알고리즘입니다.

```text
y = ax + b
```

| 기호 | 의미 |
|---|---|
| x | 입력값 |
| y | 예측값 |
| a | 기울기, coef_ |
| b | 절편, intercept_ |

선형 회귀는 실제값과 예측값 사이의 오차가 가장 작아지는 기울기와 절편을 찾습니다.

이때 오차를 측정하는 대표적인 방법이 MSE입니다.

선형 회귀는 직선 공식을 학습하기 때문에 기존 데이터 범위를 넘어선 값도 직선을 연장하여 예측할 수 있습니다.

---

## 모델 비교

| 모델 | 예측 방식 | 장점 | 한계 |
|---|---|---|---|
| k-NN 회귀 | 가까운 이웃들의 평균으로 예측 | 직관적이고 이해하기 쉬움 | 훈련 데이터 범위 밖 예측에 약함 |
| 선형 회귀 | 데이터를 설명하는 직선을 학습 | 외삽 가능, 공식 해석 가능 | 데이터가 직선 관계가 아니면 성능이 낮을 수 있음 |
| 다항 회귀 | 다항 특성으로 곡선 관계 학습 | 복잡한 패턴 표현 가능 | 과적합 위험 증가 |
| Ridge | L2 규제로 계수 크기 제한 | 과적합 완화 | alpha 설정 필요 |
| Lasso | L1 규제로 일부 계수 제거 가능 | 특성 선택 효과 | alpha가 크면 과소적합 가능 |

---

## 실행 방법

이 저장소는 `uv` 기반으로 Python 환경을 관리합니다.

```bash
uv sync
```

각 날짜별 실습 폴더로 이동하여 필요한 파일을 실행합니다.

```bash
cd 20260527_machineLearning2
uv run python 파일명.py
```

Jupyter Notebook을 사용하는 경우 VSCode에서 해당 `.ipynb` 파일을 열고 커널을 선택한 뒤 실행합니다.

Streamlit 앱은 아래와 같이 실행합니다.

```bash
uv run streamlit run app.py
```

---

## 현재 진행 상태

현재 이 저장소는 수업 진행에 맞춰 계속 업데이트 중입니다.

초반에는 pandas를 활용한 데이터 탐색과 전처리를 학습했고, 이후 matplotlib과 plotly를 활용하여 데이터를 시각화했습니다.

그다음 Streamlit을 사용해 분석 결과를 웹 대시보드 형태로 구성하는 방법을 실습했습니다.

현재는 머신러닝 파트로 넘어와 지도학습의 기본 흐름을 학습하고 있으며, k-NN 분류, k-NN 회귀, 선형 회귀, 표준화, Ridge/Lasso 규제를 실습하고 있습니다.

---

## 앞으로의 학습 예정

- 분류 알고리즘 심화
- Logistic Regression
- Precision / Recall 평가 지표
- Cross-Entropy 손실 함수
- SGD 기반 학습
- Bias / Variance 진단
- 머신러닝 결과를 활용한 Streamlit 예측 앱 구성

---

## 학습 회고

이 저장소를 통해 데이터 분석부터 웹 대시보드, 머신러닝 예측 모델까지 이어지는 흐름을 단계적으로 학습하고 있습니다.

데이터를 불러오고 확인하는 과정에서 시작하여, 결측치 처리와 집계 분석을 수행했고, 시각화를 통해 데이터의 패턴을 확인했습니다.

이후 Streamlit을 사용해 분석 결과를 사용자가 조작할 수 있는 웹 대시보드로 구성했습니다.

머신러닝 파트에서는 데이터를 Feature와 Label로 나누고, 훈련 데이터와 테스트 데이터를 분리한 뒤, 모델을 학습하고 평가하는 기본 흐름을 익히고 있습니다.

앞으로도 수업 진행에 맞춰 실습 코드와 개념 정리를 계속 업데이트할 예정입니다.
