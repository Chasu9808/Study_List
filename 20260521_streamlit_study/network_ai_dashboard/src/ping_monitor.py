import platform
import re
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd


PING_LOG_DIR = Path("data/logs")
PING_LOG_PATH = PING_LOG_DIR / "ping_log.csv"


def ensure_ping_log_dir():
    """
    Ping 로그 저장 폴더가 없으면 생성한다.
    """
    PING_LOG_DIR.mkdir(parents=True, exist_ok=True)


def build_ping_command(ip, timeout_ms=1000):
    """
    운영체제에 맞는 ping 명령어를 생성한다.

    Windows:
        ping -n 1 -w 1000 192.168.0.1

    Linux / macOS:
        ping -c 1 -W 1 192.168.0.1
    """
    system_name = platform.system().lower()

    if "windows" in system_name:
        return ["ping", "-n", "1", "-w", str(timeout_ms), ip]

    timeout_sec = max(1, int(timeout_ms / 1000))
    return ["ping", "-c", "1", "-W", str(timeout_sec), ip]


def parse_latency_ms(output_text):
    """
    ping 결과 문자열에서 응답 시간(ms)을 추출한다.

    Windows 영문 예:
        time=3ms
        time<1ms

    Windows 한글 예:
        시간=3ms
        시간<1ms

    Linux 예:
        time=0.123 ms
    """
    patterns = [
        r"time[=<]\s*([\d\.]+)\s*ms",
        r"시간[=<]\s*([\d\.]+)\s*ms",
    ]

    for pattern in patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None

    if "time<1ms" in output_text or "시간<1ms" in output_text:
        return 1.0

    return None


def ping_ip(ip, timeout_ms=1000):
    """
    단일 IP에 Ping을 보내고 UP/DOWN 상태를 반환한다.
    """
    ip = str(ip).strip()

    if not ip:
        return {
            "status": "UNKNOWN",
            "latency_ms": None,
            "error": "IP 주소가 비어 있습니다.",
        }

    command = build_ping_command(ip, timeout_ms=timeout_ms)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=max(2, int(timeout_ms / 1000) + 1),
            encoding="cp949" if platform.system().lower() == "windows" else "utf-8",
            errors="ignore",
        )

        output_text = f"{result.stdout}\n{result.stderr}"

        if result.returncode == 0:
            latency_ms = parse_latency_ms(output_text)

            return {
                "status": "UP",
                "latency_ms": latency_ms,
                "error": "",
            }

        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Ping 응답 없음",
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Ping 시간 초과",
        }

    except Exception as error:
        return {
            "status": "UNKNOWN",
            "latency_ms": None,
            "error": str(error),
        }


def check_devices_status(devices_df, timeout_ms=1000):
    """
    등록된 장비 목록에 대해 Ping 상태를 확인한다.
    """
    if devices_df.empty:
        return pd.DataFrame(
            columns=[
                "checked_at",
                "device_id",
                "name",
                "ip",
                "role",
                "location",
                "status",
                "latency_ms",
                "error",
            ]
        )

    rows = []
    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, device in devices_df.iterrows():
        ip = str(device.get("ip", "")).strip()

        ping_result = ping_ip(ip, timeout_ms=timeout_ms)

        rows.append(
            {
                "checked_at": checked_at,
                "device_id": device.get("device_id", ""),
                "name": device.get("name", ""),
                "ip": ip,
                "role": device.get("role", ""),
                "location": device.get("location", ""),
                "status": ping_result["status"],
                "latency_ms": ping_result["latency_ms"],
                "error": ping_result["error"],
            }
        )

    return pd.DataFrame(rows)


def append_ping_log(ping_df):
    """
    Ping 체크 결과를 ping_log.csv에 저장한다.
    """
    if ping_df.empty:
        return None

    ensure_ping_log_dir()

    if PING_LOG_PATH.exists():
        ping_df.to_csv(
            PING_LOG_PATH,
            mode="a",
            header=False,
            index=False,
            encoding="utf-8-sig",
        )
    else:
        ping_df.to_csv(
            PING_LOG_PATH,
            mode="w",
            header=True,
            index=False,
            encoding="utf-8-sig",
        )

    return PING_LOG_PATH


def load_ping_log(limit=100):
    """
    저장된 Ping 로그를 최근 limit개만 읽어온다.
    """
    if not PING_LOG_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(PING_LOG_PATH, encoding="utf-8-sig")

    if df.empty:
        return df

    return df.tail(limit).sort_values("checked_at", ascending=False)