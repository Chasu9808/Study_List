def analyze_system_risk(system_status, network_speed, connections_df):
    """
    시스템 상태와 네트워크 연결 정보를 기반으로 기본 위험도를 판단한다.

    반환값:
    {
        "level": "NORMAL" | "WARNING" | "DANGER",
        "score": int,
        "reasons": list[str]
    }
    """
    score = 0
    reasons = []

    cpu_percent = system_status["cpu"]["cpu_percent"]
    memory_percent = system_status["memory"]["memory_percent"]
    disk_percent = system_status["disk"]["disk_percent"]

    send_speed = network_speed["send_speed_mbps"]
    recv_speed = network_speed["recv_speed_mbps"]

    total_connections = len(connections_df)

    if not connections_df.empty and "status" in connections_df.columns:
        established_count = len(connections_df[connections_df["status"] == "ESTABLISHED"])
        listen_count = len(connections_df[connections_df["status"] == "LISTEN"])
    else:
        established_count = 0
        listen_count = 0

    # CPU 위험 판단
    if cpu_percent >= 90:
        score += 3
        reasons.append(f"CPU 사용률이 매우 높습니다. 현재 {cpu_percent}%")
    elif cpu_percent >= 75:
        score += 1
        reasons.append(f"CPU 사용률이 다소 높습니다. 현재 {cpu_percent}%")

    # RAM 위험 판단
    if memory_percent >= 90:
        score += 3
        reasons.append(f"RAM 사용률이 매우 높습니다. 현재 {memory_percent}%")
    elif memory_percent >= 75:
        score += 1
        reasons.append(f"RAM 사용률이 다소 높습니다. 현재 {memory_percent}%")

    # 디스크 위험 판단
    if disk_percent >= 95:
        score += 3
        reasons.append(f"디스크 사용률이 매우 높습니다. 현재 {disk_percent}%")
    elif disk_percent >= 85:
        score += 1
        reasons.append(f"디스크 사용률이 다소 높습니다. 현재 {disk_percent}%")

    # 네트워크 속도 위험 판단
    if recv_speed >= 50:
        score += 3
        reasons.append(f"초당 수신량이 매우 높습니다. 현재 {recv_speed}MB/s")
    elif recv_speed >= 10:
        score += 1
        reasons.append(f"초당 수신량이 다소 높습니다. 현재 {recv_speed}MB/s")

    if send_speed >= 50:
        score += 3
        reasons.append(f"초당 송신량이 매우 높습니다. 현재 {send_speed}MB/s")
    elif send_speed >= 10:
        score += 1
        reasons.append(f"초당 송신량이 다소 높습니다. 현재 {send_speed}MB/s")

    # 연결 수 위험 판단
    if total_connections >= 300:
        score += 3
        reasons.append(f"전체 네트워크 연결 수가 매우 많습니다. 현재 {total_connections}개")
    elif total_connections >= 150:
        score += 1
        reasons.append(f"전체 네트워크 연결 수가 다소 많습니다. 현재 {total_connections}개")

    # ESTABLISHED 연결 수 판단
    if established_count >= 150:
        score += 3
        reasons.append(f"활성 연결 수가 매우 많습니다. 현재 {established_count}개")
    elif established_count >= 80:
        score += 1
        reasons.append(f"활성 연결 수가 다소 많습니다. 현재 {established_count}개")

    # LISTEN 포트 수 판단
    if listen_count >= 50:
        score += 2
        reasons.append(f"대기 중인 LISTEN 포트가 많습니다. 현재 {listen_count}개")

    if score >= 7:
        level = "DANGER"
    elif score >= 3:
        level = "WARNING"
    else:
        level = "NORMAL"

    if not reasons:
        reasons.append("현재 기준에서는 특별한 이상 징후가 감지되지 않았습니다.")

    return {
        "level": level,
        "score": score,
        "reasons": reasons,
        "summary": {
            "total_connections": total_connections,
            "established_count": established_count,
            "listen_count": listen_count,
        },
    }


def get_risk_label(level):
    """
    위험도 코드를 한글 라벨로 변환한다.
    """
    labels = {
        "NORMAL": "정상",
        "WARNING": "주의",
        "DANGER": "위험",
    }

    return labels.get(level, "알 수 없음")