import pandas as pd


COMMON_PORTS = {
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH",
    23: "TELNET",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3389: "RDP",
    5432: "PostgreSQL",
    3306: "MySQL",
    6379: "Redis",
    27017: "MongoDB",
}

WATCH_PORTS = {
    21: "FTP 연결 감지",
    22: "SSH 연결 감지",
    23: "Telnet 연결 감지",
    445: "SMB 연결 감지",
    3389: "원격 데스크톱 RDP 연결 감지",
    6379: "Redis 포트 연결 감지",
    27017: "MongoDB 포트 연결 감지",
}


def get_port_name(port):
    """
    포트 번호를 서비스 이름으로 변환한다.
    """
    try:
        port = int(port)
    except (TypeError, ValueError):
        return "-"

    return COMMON_PORTS.get(port, "UNKNOWN")


def summarize_remote_ips(connections_df, top_n=10):
    """
    외부 IP 기준 연결 수를 집계한다.
    """
    if connections_df.empty or "remote_ip" not in connections_df.columns:
        return pd.DataFrame(columns=["remote_ip", "connection_count"])

    df = connections_df.copy()
    df = df[df["remote_ip"] != "-"]

    if df.empty:
        return pd.DataFrame(columns=["remote_ip", "connection_count"])

    result = (
        df.groupby("remote_ip")
        .size()
        .reset_index(name="connection_count")
        .sort_values("connection_count", ascending=False)
        .head(top_n)
    )

    return result


def summarize_remote_ports(connections_df, top_n=10):
    """
    외부 포트 기준 연결 수를 집계한다.
    """
    if connections_df.empty or "remote_port" not in connections_df.columns:
        return pd.DataFrame(columns=["remote_port", "service", "connection_count"])

    df = connections_df.copy()
    df = df[df["remote_port"] != "-"]

    if df.empty:
        return pd.DataFrame(columns=["remote_port", "service", "connection_count"])

    df["remote_port"] = pd.to_numeric(df["remote_port"], errors="coerce")
    df = df.dropna(subset=["remote_port"])
    df["remote_port"] = df["remote_port"].astype(int)

    result = (
        df.groupby("remote_port")
        .size()
        .reset_index(name="connection_count")
        .sort_values("connection_count", ascending=False)
        .head(top_n)
    )

    result["service"] = result["remote_port"].apply(get_port_name)

    return result[["remote_port", "service", "connection_count"]]


def summarize_processes(connections_df, top_n=10):
    """
    프로세스 이름 기준 연결 수를 집계한다.
    """
    if connections_df.empty or "process_name" not in connections_df.columns:
        return pd.DataFrame(columns=["process_name", "connection_count"])

    df = connections_df.copy()
    df = df[df["process_name"] != "-"]

    if df.empty:
        return pd.DataFrame(columns=["process_name", "connection_count"])

    result = (
        df.groupby("process_name")
        .size()
        .reset_index(name="connection_count")
        .sort_values("connection_count", ascending=False)
        .head(top_n)
    )

    return result


def detect_watch_ports(connections_df):
    """
    주의해서 볼 포트 연결을 탐지한다.
    """
    if connections_df.empty or "remote_port" not in connections_df.columns:
        return pd.DataFrame(columns=["remote_ip", "remote_port", "description", "process_name", "status"])

    df = connections_df.copy()
    df = df[df["remote_port"] != "-"]

    if df.empty:
        return pd.DataFrame(columns=["remote_ip", "remote_port", "description", "process_name", "status"])

    df["remote_port"] = pd.to_numeric(df["remote_port"], errors="coerce")
    df = df.dropna(subset=["remote_port"])
    df["remote_port"] = df["remote_port"].astype(int)

    watch_df = df[df["remote_port"].isin(WATCH_PORTS.keys())].copy()

    if watch_df.empty:
        return pd.DataFrame(columns=["remote_ip", "remote_port", "description", "process_name", "status"])

    watch_df["description"] = watch_df["remote_port"].map(WATCH_PORTS)

    columns = ["remote_ip", "remote_port", "description", "process_name", "status"]

    return watch_df[columns].drop_duplicates().reset_index(drop=True)


def build_session_summary(connections_df):
    """
    네트워크 연결 정보를 요약 분석한다.
    """
    remote_ip_summary = summarize_remote_ips(connections_df)
    remote_port_summary = summarize_remote_ports(connections_df)
    process_summary = summarize_processes(connections_df)
    watch_ports = detect_watch_ports(connections_df)

    return {
        "remote_ip_summary": remote_ip_summary,
        "remote_port_summary": remote_port_summary,
        "process_summary": process_summary,
        "watch_ports": watch_ports,
    }