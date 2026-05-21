def analyze_without_llm(system_status, network_speed, risk_result):
    """
    LLM/Ollama/API 없이 룰 기반 분석 결과를 자연어 요약으로 변환한다.
    """
    level = risk_result["level"]
    score = risk_result["score"]
    reasons = risk_result["reasons"]
    summary = risk_result["summary"]

    cpu_percent = system_status["cpu"]["cpu_percent"]
    memory_percent = system_status["memory"]["memory_percent"]
    disk_percent = system_status["disk"]["disk_percent"]

    send_speed = network_speed["send_speed_mbps"]
    recv_speed = network_speed["recv_speed_mbps"]

    status_text = _get_status_text(level)

    summary_text = _build_summary_text(
        level=level,
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        disk_percent=disk_percent,
        send_speed=send_speed,
        recv_speed=recv_speed,
        total_connections=summary["total_connections"],
        established_count=summary["established_count"],
        listen_count=summary["listen_count"],
    )

    action_items = _build_action_items(
        level=level,
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        disk_percent=disk_percent,
        send_speed=send_speed,
        recv_speed=recv_speed,
        total_connections=summary["total_connections"],
        established_count=summary["established_count"],
        listen_count=summary["listen_count"],
    )

    return {
        "status": status_text,
        "level": level,
        "score": score,
        "summary": summary_text,
        "reasons": reasons,
        "actions": action_items,
    }


def _get_status_text(level):
    if level == "NORMAL":
        return "정상"
    if level == "WARNING":
        return "주의"
    if level == "DANGER":
        return "위험"

    return "알 수 없음"


def _build_summary_text(
    level,
    cpu_percent,
    memory_percent,
    disk_percent,
    send_speed,
    recv_speed,
    total_connections,
    established_count,
    listen_count,
):
    if level == "NORMAL":
        return (
            "현재 PC의 시스템 사용률과 네트워크 연결 상태는 전반적으로 안정적인 범위에 있습니다. "
            f"CPU {cpu_percent}%, RAM {memory_percent}%, 디스크 {disk_percent}% 수준이며, "
            f"활성 연결 수는 {established_count}개로 현재 기준에서는 특별한 이상 징후가 크지 않습니다."
        )

    if level == "WARNING":
        return (
            "현재 일부 시스템 또는 네트워크 지표가 주의 기준에 도달했습니다. "
            f"CPU {cpu_percent}%, RAM {memory_percent}%, 디스크 {disk_percent}%이며, "
            f"전체 연결 수 {total_connections}개, 활성 연결 수 {established_count}개를 기준으로 상태 확인이 필요합니다."
        )

    if level == "DANGER":
        return (
            "현재 시스템 또는 네트워크 상태에서 위험 수준의 지표가 감지되었습니다. "
            f"CPU {cpu_percent}%, RAM {memory_percent}%, 디스크 {disk_percent}%이며, "
            f"송신 {send_speed}MB/s, 수신 {recv_speed}MB/s, 활성 연결 수 {established_count}개 상태를 우선 확인해야 합니다."
        )

    return "현재 상태를 해석할 수 없습니다."


def _build_action_items(
    level,
    cpu_percent,
    memory_percent,
    disk_percent,
    send_speed,
    recv_speed,
    total_connections,
    established_count,
    listen_count,
):
    actions = []

    if cpu_percent >= 75:
        actions.append("CPU 사용률이 높은 프로세스를 작업 관리자에서 확인하세요.")

    if memory_percent >= 75:
        actions.append("메모리를 많이 사용하는 프로그램을 확인하고 불필요한 프로그램을 종료하세요.")

    if disk_percent >= 85:
        actions.append("디스크 여유 공간을 확보하고 로그 또는 임시 파일을 정리하세요.")

    if send_speed >= 10 or recv_speed >= 10:
        actions.append("네트워크 송수신량이 높은 프로세스와 외부 연결 대상을 확인하세요.")

    if total_connections >= 150:
        actions.append("전체 네트워크 연결 수가 많으므로 비정상적으로 연결을 많이 생성하는 프로그램이 있는지 확인하세요.")

    if established_count >= 80:
        actions.append("활성 연결 수가 많으므로 브라우저, 메신저, 백그라운드 프로그램의 연결 상태를 확인하세요.")

    if listen_count >= 50:
        actions.append("LISTEN 포트가 많으므로 불필요하게 열려 있는 서비스가 있는지 확인하세요.")

    if not actions:
        actions.append("현재는 별도 조치 없이 주기적으로 상태를 모니터링하면 됩니다.")

    if level == "DANGER":
        actions.append("위험 상태가 지속되면 네트워크를 일시적으로 차단하고 원인 프로세스를 먼저 확인하세요.")

    return actions