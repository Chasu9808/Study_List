# config/settings.py

APP_TITLE = "로컬 AI 기반 네트워크 모니터링 대시보드"

DEFAULT_REFRESH_SECONDS = 3

REFRESH_OPTIONS = [1, 3, 5, 10]

RISK_LEVELS = {
    "normal": "정상",
    "warning": "주의",
    "danger": "위험",
}