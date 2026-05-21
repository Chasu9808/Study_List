from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd


DEVICE_DIR = Path("data/devices")
DEVICE_PATH = DEVICE_DIR / "devices.csv"


DEVICE_COLUMNS = [
    "device_id",
    "name",
    "ip",
    "role",
    "location",
    "vendor",
    "snmp_enabled",
    "snmp_version",
    "snmp_community",
    "description",
    "created_at",
]


def ensure_device_dir():
    """
    장비 목록 저장 폴더가 없으면 생성한다.
    """
    DEVICE_DIR.mkdir(parents=True, exist_ok=True)


def create_empty_device_df():
    """
    장비 목록 기본 DataFrame을 생성한다.
    """
    return pd.DataFrame(columns=DEVICE_COLUMNS)


def load_devices():
    """
    devices.csv 파일에서 장비 목록을 읽어온다.
    파일이 없으면 빈 DataFrame을 반환한다.
    """
    ensure_device_dir()

    if not DEVICE_PATH.exists():
        return create_empty_device_df()

    df = pd.read_csv(
        DEVICE_PATH,
        encoding="utf-8-sig",
        dtype=str,
    )

    for column in DEVICE_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    return df[DEVICE_COLUMNS]


def save_devices(devices_df):
    """
    장비 목록 DataFrame을 devices.csv에 저장한다.
    """
    ensure_device_dir()

    devices_df = devices_df.copy()

    for column in DEVICE_COLUMNS:
        if column not in devices_df.columns:
            devices_df[column] = ""

    devices_df = devices_df[DEVICE_COLUMNS]

    devices_df.to_csv(
        DEVICE_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    return DEVICE_PATH


def is_duplicate_ip(devices_df, ip):
    """
    같은 IP가 이미 등록되어 있는지 확인한다.
    """
    if devices_df.empty:
        return False

    return ip in devices_df["ip"].astype(str).tolist()


def add_device(
    name,
    ip,
    role,
    location,
    vendor,
    snmp_enabled,
    snmp_version,
    snmp_community,
    description,
):
    """
    장비 1개를 추가한다.
    """
    devices_df = load_devices()

    name = str(name).strip()
    ip = str(ip).strip()
    role = str(role).strip()
    location = str(location).strip()
    vendor = str(vendor).strip()
    snmp_version = str(snmp_version).strip()
    snmp_community = str(snmp_community).strip()
    description = str(description).strip()

    if not name:
        return False, "장비명을 입력해야 합니다."

    if not ip:
        return False, "IP 주소를 입력해야 합니다."

    if is_duplicate_ip(devices_df, ip):
        return False, f"이미 등록된 IP입니다: {ip}"

    new_row = {
        "device_id": str(uuid4()),
        "name": name,
        "ip": ip,
        "role": role,
        "location": location,
        "vendor": vendor,
        "snmp_enabled": "true" if snmp_enabled else "false",
        "snmp_version": snmp_version,
        "snmp_community": snmp_community,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    new_df = pd.DataFrame([new_row])
    devices_df = pd.concat([devices_df, new_df], ignore_index=True)

    save_devices(devices_df)

    return True, f"장비가 등록되었습니다: {name} ({ip})"


def delete_device(device_id):
    """
    device_id 기준으로 장비를 삭제한다.
    """
    devices_df = load_devices()

    if devices_df.empty:
        return False, "삭제할 장비가 없습니다."

    before_count = len(devices_df)

    devices_df = devices_df[devices_df["device_id"] != device_id]

    after_count = len(devices_df)

    if before_count == after_count:
        return False, "선택한 장비를 찾을 수 없습니다."

    save_devices(devices_df)

    return True, "선택한 장비가 삭제되었습니다."