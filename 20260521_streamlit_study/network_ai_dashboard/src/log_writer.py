from datetime import datetime
from pathlib import Path

import pandas as pd


LOG_DIR = Path("data/logs")
SYSTEM_LOG_PATH = LOG_DIR / "system_log.csv"


def ensure_log_dir():
    """
    로그 저장 폴더가 없으면 생성한다.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def build_log_row(system_status, network_speed, risk_result):
    """
    현재 시스템 상태, 네트워크 속도, 위험 분석 결과를
    CSV에 저장할 한 줄 데이터로 변환한다.
    """
    cpu = system_status["cpu"]
    memory = system_status["memory"]
    disk = system_status["disk"]
    network = system_status["network"]
    summary = risk_result["summary"]

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": cpu["cpu_percent"],
        "cpu_count": cpu["cpu_count"],
        "memory_percent": memory["memory_percent"],
        "memory_total_gb": memory["memory_total_gb"],
        "memory_used_gb": memory["memory_used_gb"],
        "disk_percent": disk["disk_percent"],
        "disk_total_gb": disk["disk_total_gb"],
        "disk_used_gb": disk["disk_used_gb"],
        "send_speed_mbps": network_speed["send_speed_mbps"],
        "recv_speed_mbps": network_speed["recv_speed_mbps"],
        "bytes_sent_mb": network["bytes_sent_mb"],
        "bytes_recv_mb": network["bytes_recv_mb"],
        "packets_sent": network["packets_sent"],
        "packets_recv": network["packets_recv"],
        "risk_level": risk_result["level"],
        "risk_score": risk_result["score"],
        "total_connections": summary["total_connections"],
        "established_count": summary["established_count"],
        "listen_count": summary["listen_count"],
        "risk_reasons": " | ".join(risk_result["reasons"]),
    }


def append_system_log(system_status, network_speed, risk_result):
    """
    현재 상태를 system_log.csv에 추가 저장한다.
    """
    ensure_log_dir()

    row = build_log_row(
        system_status=system_status,
        network_speed=network_speed,
        risk_result=risk_result,
    )

    row_df = pd.DataFrame([row])

    if SYSTEM_LOG_PATH.exists():
        row_df.to_csv(
            SYSTEM_LOG_PATH,
            mode="a",
            header=False,
            index=False,
            encoding="utf-8-sig",
        )
    else:
        row_df.to_csv(
            SYSTEM_LOG_PATH,
            mode="w",
            header=True,
            index=False,
            encoding="utf-8-sig",
        )

    return SYSTEM_LOG_PATH


def load_system_log(limit=100):
    """
    저장된 로그를 읽어온다.
    최근 limit개만 반환한다.
    """
    if not SYSTEM_LOG_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(SYSTEM_LOG_PATH, encoding="utf-8-sig")

    if df.empty:
        return df

    return df.tail(limit).sort_values("timestamp", ascending=False)