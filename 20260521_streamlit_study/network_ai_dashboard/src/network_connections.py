import psutil
import pandas as pd


def _safe_address(address):
    """
    psutil의 주소 객체에서 IP와 포트를 안전하게 추출한다.
    주소가 없으면 '-'로 반환한다.
    """
    if not address:
        return "-", "-"

    ip = getattr(address, "ip", "-")
    port = getattr(address, "port", "-")

    return ip, port


def _get_process_name(pid):
    """
    PID를 기준으로 프로세스 이름을 가져온다.
    권한 문제나 이미 종료된 프로세스는 '-'로 처리한다.
    """
    if pid is None:
        return "-"

    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "-"


def get_network_connections():
    """
    현재 PC의 네트워크 연결 정보를 조회한다.

    반환 컬럼:
    - protocol
    - local_ip
    - local_port
    - remote_ip
    - remote_port
    - status
    - pid
    - process_name
    """
    rows = []

    try:
        connections = psutil.net_connections(kind="inet")
    except psutil.AccessDenied:
        return pd.DataFrame(
            [
                {
                    "protocol": "ERROR",
                    "local_ip": "권한 부족",
                    "local_port": "-",
                    "remote_ip": "관리자 권한으로 실행 필요",
                    "remote_port": "-",
                    "status": "ACCESS_DENIED",
                    "pid": "-",
                    "process_name": "-",
                }
            ]
        )

    for conn in connections:
        local_ip, local_port = _safe_address(conn.laddr)
        remote_ip, remote_port = _safe_address(conn.raddr)

        protocol = "TCP" if conn.type.name == "SOCK_STREAM" else "UDP"

        rows.append(
            {
                "protocol": protocol,
                "local_ip": local_ip,
                "local_port": local_port,
                "remote_ip": remote_ip,
                "remote_port": remote_port,
                "status": conn.status,
                "pid": conn.pid if conn.pid is not None else "-",
                "process_name": _get_process_name(conn.pid),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "protocol",
                "local_ip",
                "local_port",
                "remote_ip",
                "remote_port",
                "status",
                "pid",
                "process_name",
            ]
        )

    return df