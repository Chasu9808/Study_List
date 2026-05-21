from datetime import datetime
from pathlib import Path

import pandas as pd

from src.ping_monitor import load_ping_log


INCIDENT_LOG_DIR = Path("data/logs")
INCIDENT_LOG_PATH = INCIDENT_LOG_DIR / "incident_log.csv"


def ensure_incident_log_dir():
    """
    장애 이력 저장 폴더가 없으면 생성한다.
    """
    INCIDENT_LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_incident_log(limit=100):
    """
    저장된 장애 이력을 최근 limit개만 읽어온다.
    """
    if not INCIDENT_LOG_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(INCIDENT_LOG_PATH, encoding="utf-8-sig")

    if df.empty:
        return df

    return df.tail(limit).sort_values("event_time", ascending=False)


def append_incident_log(incident_df):
    """
    장애 이력 DataFrame을 incident_log.csv에 추가 저장한다.
    """
    if incident_df.empty:
        return None

    ensure_incident_log_dir()

    if INCIDENT_LOG_PATH.exists():
        incident_df.to_csv(
            INCIDENT_LOG_PATH,
            mode="a",
            header=False,
            index=False,
            encoding="utf-8-sig",
        )
    else:
        incident_df.to_csv(
            INCIDENT_LOG_PATH,
            mode="w",
            header=True,
            index=False,
            encoding="utf-8-sig",
        )

    return INCIDENT_LOG_PATH


def get_previous_device_status_map():
    """
    ping_log.csv에서 장비별 가장 최근 상태를 가져온다.

    반환 예:
    {
        "device_id_1": "UP",
        "device_id_2": "DOWN"
    }
    """
    ping_log_df = load_ping_log(limit=10000)

    if ping_log_df.empty:
        return {}

    if "checked_at" not in ping_log_df.columns or "device_id" not in ping_log_df.columns:
        return {}

    ping_log_df = ping_log_df.copy()

    ping_log_df["checked_at"] = pd.to_datetime(
        ping_log_df["checked_at"],
        errors="coerce",
    )

    ping_log_df = ping_log_df.dropna(subset=["checked_at"])
    ping_log_df = ping_log_df.sort_values("checked_at")

    latest_df = ping_log_df.groupby("device_id").tail(1)

    status_map = {}

    for _, row in latest_df.iterrows():
        device_id = str(row.get("device_id", "")).strip()
        status = str(row.get("status", "")).strip()

        if device_id:
            status_map[device_id] = status

    return status_map


def detect_incidents(current_ping_df):
    """
    현재 Ping 결과와 이전 Ping 상태를 비교해서 장애 이벤트를 생성한다.

    이벤트 유형:
    - DOWN: 이전 UP → 현재 DOWN
    - RECOVERED: 이전 DOWN → 현재 UP
    """
    if current_ping_df.empty:
        return pd.DataFrame(
            columns=[
                "event_time",
                "device_id",
                "name",
                "ip",
                "role",
                "location",
                "previous_status",
                "current_status",
                "event_type",
                "message",
            ]
        )

    previous_status_map = get_previous_device_status_map()

    if not previous_status_map:
        return pd.DataFrame(
            columns=[
                "event_time",
                "device_id",
                "name",
                "ip",
                "role",
                "location",
                "previous_status",
                "current_status",
                "event_type",
                "message",
            ]
        )

    rows = []
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, row in current_ping_df.iterrows():
        device_id = str(row.get("device_id", "")).strip()
        current_status = str(row.get("status", "")).strip()

        if not device_id:
            continue

        previous_status = previous_status_map.get(device_id)

        if previous_status is None:
            continue

        event_type = None
        message = None

        if previous_status == "UP" and current_status == "DOWN":
            event_type = "DOWN"
            message = f"{row.get('name', '')}({row.get('ip', '')}) 장비가 DOWN 상태로 변경되었습니다."

        elif previous_status == "DOWN" and current_status == "UP":
            event_type = "RECOVERED"
            message = f"{row.get('name', '')}({row.get('ip', '')}) 장비가 복구되었습니다."

        if event_type:
            rows.append(
                {
                    "event_time": event_time,
                    "device_id": device_id,
                    "name": row.get("name", ""),
                    "ip": row.get("ip", ""),
                    "role": row.get("role", ""),
                    "location": row.get("location", ""),
                    "previous_status": previous_status,
                    "current_status": current_status,
                    "event_type": event_type,
                    "message": message,
                }
            )

    return pd.DataFrame(rows)