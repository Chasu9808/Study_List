from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config.settings import (
    APP_TITLE,
    DEFAULT_REFRESH_SECONDS,
    REFRESH_OPTIONS,
)

from src.incident_manager import (
    append_incident_log,
    detect_incidents,
    load_incident_log,
)

from src.ai_analyzer import analyze_without_llm
from src.log_writer import append_system_log, load_system_log
from src.network_connections import get_network_connections
from src.rule_analyzer import analyze_system_risk, get_risk_label
from src.session_summary import build_session_summary
from src.system_monitor import bytes_to_mb, get_system_status
from src.device_store import add_device, delete_device, load_devices
from src.ping_monitor import append_ping_log, check_devices_status, load_ping_log


def render_sidebar():
    st.sidebar.header("설정")

    auto_refresh = st.sidebar.checkbox(
        "자동 새로고침 사용",
        value=True,
    )

    refresh_seconds = st.sidebar.selectbox(
        "새로고침 주기",
        REFRESH_OPTIONS,
        index=REFRESH_OPTIONS.index(DEFAULT_REFRESH_SECONDS),
    )

    use_ai = st.sidebar.checkbox(
        "로컬 요약 분석 사용",
        value=True,
    )

    enable_logging = st.sidebar.checkbox(
        "상태 로그 저장",
        value=False,
    )

    show_charts = st.sidebar.checkbox(
        "로그 그래프 표시",
        value=True,
    )

    show_risk_events = st.sidebar.checkbox(
        "위험 이벤트 표시",
        value=True,
    )

    show_listen = st.sidebar.checkbox(
        "LISTEN 연결 포함",
        value=True,
    )

    max_rows = st.sidebar.slider(
        "표시할 연결 수",
        min_value=10,
        max_value=200,
        value=50,
        step=10,
    )

    log_limit = st.sidebar.slider(
        "로그 조회 개수",
        min_value=20,
        max_value=1000,
        value=100,
        step=20,
    )

    st.sidebar.divider()

    st.sidebar.caption(
        "현재 버전은 Ollama 없이 룰 기반 결과를 자연어로 요약합니다."
    )

    return (
        auto_refresh,
        refresh_seconds,
        use_ai,
        enable_logging,
        show_charts,
        show_risk_events,
        show_listen,
        max_rows,
        log_limit,
    )


def apply_auto_refresh(auto_refresh, refresh_seconds):
    if auto_refresh:
        st_autorefresh(
            interval=refresh_seconds * 1000,
            key="network_dashboard_auto_refresh",
        )


def calculate_network_speed(current_network, refresh_seconds):
    previous_network = st.session_state.get("previous_network")

    if previous_network is None:
        st.session_state["previous_network"] = current_network

        return {
            "send_speed_mbps": 0.0,
            "recv_speed_mbps": 0.0,
        }

    sent_diff = current_network["bytes_sent"] - previous_network["bytes_sent"]
    recv_diff = current_network["bytes_recv"] - previous_network["bytes_recv"]

    send_speed_mbps = bytes_to_mb(sent_diff) / refresh_seconds
    recv_speed_mbps = bytes_to_mb(recv_diff) / refresh_seconds

    st.session_state["previous_network"] = current_network

    return {
        "send_speed_mbps": round(send_speed_mbps, 2),
        "recv_speed_mbps": round(recv_speed_mbps, 2),
    }


def render_header(auto_refresh, refresh_seconds):
    st.title(APP_TITLE)

    st.caption(
        "PC 상태, 네트워크 세션, 세션 요약, 로그 그래프, 위험 이벤트, 로컬 요약 분석 결과를 한 화면에서 확인하는 대시보드입니다."
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if auto_refresh:
        st.success(f"자동 새로고침 활성화: {refresh_seconds}초 주기 / 마지막 갱신: {now}")
    else:
        st.warning(f"자동 새로고침 비활성화 / 마지막 갱신: {now}")


def render_system_metrics(system_status, network_speed):
    cpu = system_status["cpu"]
    memory = system_status["memory"]
    disk = system_status["disk"]
    network = system_status["network"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "CPU 사용률",
            f"{cpu['cpu_percent']}%",
            help=f"논리 CPU 코어 수: {cpu['cpu_count']}",
        )

    with col2:
        st.metric(
            "RAM 사용률",
            f"{memory['memory_percent']}%",
            help=(
                f"전체: {memory['memory_total_gb']}GB / "
                f"사용 중: {memory['memory_used_gb']}GB / "
                f"여유: {memory['memory_available_gb']}GB"
            ),
        )

    with col3:
        st.metric(
            "디스크 사용률",
            f"{disk['disk_percent']}%",
            help=(
                f"전체: {disk['disk_total_gb']}GB / "
                f"사용 중: {disk['disk_used_gb']}GB / "
                f"여유: {disk['disk_free_gb']}GB"
            ),
        )

    with col4:
        st.metric(
            "수신 속도",
            f"{network_speed['recv_speed_mbps']} MB/s",
            delta=f"송신 {network_speed['send_speed_mbps']} MB/s",
            help=(
                f"누적 송신: {network['bytes_sent_mb']}MB / "
                f"누적 수신: {network['bytes_recv_mb']}MB"
            ),
        )


def render_risk_panel(risk_result):
    st.subheader("룰 기반 이상 탐지 결과")

    level = risk_result["level"]
    label = get_risk_label(level)
    score = risk_result["score"]

    if level == "NORMAL":
        st.success(f"상태: {label} / 위험 점수: {score}")
    elif level == "WARNING":
        st.warning(f"상태: {label} / 위험 점수: {score}")
    else:
        st.error(f"상태: {label} / 위험 점수: {score}")

    summary = risk_result["summary"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("전체 연결 수", summary["total_connections"])

    with col2:
        st.metric("활성 연결 수", summary["established_count"])

    with col3:
        st.metric("LISTEN 포트 수", summary["listen_count"])

    st.write("판단 근거")

    for reason in risk_result["reasons"]:
        st.write(f"- {reason}")


def render_session_summary(session_summary):
    st.subheader("네트워크 세션 요약")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "외부 IP TOP",
            "외부 포트 TOP",
            "프로세스 TOP",
            "주의 포트",
        ]
    )

    with tab1:
        st.write("외부 IP별 연결 수 상위 목록입니다.")
        st.dataframe(
            session_summary["remote_ip_summary"],
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.write("외부 포트별 연결 수 상위 목록입니다.")
        st.dataframe(
            session_summary["remote_port_summary"],
            use_container_width=True,
            hide_index=True,
        )

    with tab3:
        st.write("프로세스별 네트워크 연결 수 상위 목록입니다.")
        st.dataframe(
            session_summary["process_summary"],
            use_container_width=True,
            hide_index=True,
        )

    with tab4:
        watch_ports = session_summary["watch_ports"]

        if watch_ports.empty:
            st.success("현재 기준에서 주의 포트 연결은 감지되지 않았습니다.")
        else:
            st.warning("주의해서 볼 포트 연결이 감지되었습니다.")
            st.dataframe(
                watch_ports,
                use_container_width=True,
                hide_index=True,
            )


def render_system_detail(system_status, network_speed):
    st.subheader("PC 상태 상세 정보")

    cpu = system_status["cpu"]
    memory = system_status["memory"]
    disk = system_status["disk"]
    network = system_status["network"]

    detail_data = pd.DataFrame(
        [
            {"구분": "CPU", "항목": "사용률", "값": f"{cpu['cpu_percent']}%"},
            {"구분": "CPU", "항목": "논리 코어 수", "값": cpu["cpu_count"]},
            {"구분": "RAM", "항목": "전체 메모리", "값": f"{memory['memory_total_gb']}GB"},
            {"구분": "RAM", "항목": "사용 중 메모리", "값": f"{memory['memory_used_gb']}GB"},
            {"구분": "RAM", "항목": "사용률", "값": f"{memory['memory_percent']}%"},
            {"구분": "DISK", "항목": "전체 디스크", "값": f"{disk['disk_total_gb']}GB"},
            {"구분": "DISK", "항목": "사용 중 디스크", "값": f"{disk['disk_used_gb']}GB"},
            {"구분": "DISK", "항목": "사용률", "값": f"{disk['disk_percent']}%"},
            {"구분": "NETWORK", "항목": "초당 송신 속도", "값": f"{network_speed['send_speed_mbps']}MB/s"},
            {"구분": "NETWORK", "항목": "초당 수신 속도", "값": f"{network_speed['recv_speed_mbps']}MB/s"},
            {"구분": "NETWORK", "항목": "누적 송신량", "값": f"{network['bytes_sent_mb']}MB"},
            {"구분": "NETWORK", "항목": "누적 수신량", "값": f"{network['bytes_recv_mb']}MB"},
            {"구분": "NETWORK", "항목": "송신 패킷 수", "값": network["packets_sent"]},
            {"구분": "NETWORK", "항목": "수신 패킷 수", "값": network["packets_recv"]},
        ]
    )

    st.dataframe(
        detail_data,
        use_container_width=True,
        hide_index=True,
    )

def render_device_management_panel():
    st.subheader("장비 목록 관리")

    devices_df = load_devices()

    with st.expander("장비 추가", expanded=False):
        with st.form("device_add_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "장비명",
                    placeholder="예: Core-Switch-01",
                )

                ip = st.text_input(
                    "IP 주소",
                    placeholder="예: 192.168.0.1",
                )

                role = st.selectbox(
                    "장비 역할",
                    [
                        "Router",
                        "Switch",
                        "Firewall",
                        "Server",
                        "AP",
                        "NAS",
                        "Printer",
                        "PC",
                        "Other",
                    ],
                )

                location = st.text_input(
                    "위치",
                    placeholder="예: 서버실 / 사무실 / 지점A",
                )

            with col2:
                vendor = st.text_input(
                    "벤더",
                    placeholder="예: Cisco / Fortinet / HP / Dell",
                )

                snmp_enabled = st.checkbox(
                    "SNMP 사용",
                    value=False,
                )

                snmp_version = st.selectbox(
                    "SNMP 버전",
                    ["2c", "3"],
                )

                snmp_community = st.text_input(
                    "SNMP Community",
                    value="public",
                    type="password",
                )

            description = st.text_area(
                "설명",
                placeholder="장비 설명 또는 비고를 입력하세요.",
            )

            submitted = st.form_submit_button("장비 등록")

            if submitted:
                success, message = add_device(
                    name=name,
                    ip=ip,
                    role=role,
                    location=location,
                    vendor=vendor,
                    snmp_enabled=snmp_enabled,
                    snmp_version=snmp_version,
                    snmp_community=snmp_community,
                    description=description,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.write("등록된 장비 목록")

    if devices_df.empty:
        st.info("아직 등록된 장비가 없습니다.")
        return

    display_df = devices_df.copy()

    hidden_columns = ["device_id", "snmp_community"]

    show_columns = [
        column for column in display_df.columns if column not in hidden_columns
    ]

    st.dataframe(
        display_df[show_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.write("장비 삭제")

    device_options = {
        f"{row['name']} / {row['ip']} / {row['role']}": row["device_id"]
        for _, row in devices_df.iterrows()
    }

    selected_label = st.selectbox(
        "삭제할 장비 선택",
        list(device_options.keys()),
    )

    if st.button("선택한 장비 삭제"):
        selected_device_id = device_options[selected_label]

        success, message = delete_device(selected_device_id)

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

def render_device_ping_panel():
    st.subheader("장비 Ping 상태 체크")

    devices_df = load_devices()

    if devices_df.empty:
        st.info("등록된 장비가 없습니다. 먼저 장비 목록 관리에서 장비를 등록하세요.")
        return

    col1, col2 = st.columns([1, 3])

    with col1:
        timeout_ms = st.number_input(
            "Ping 타임아웃(ms)",
            min_value=500,
            max_value=5000,
            value=1000,
            step=500,
        )

    with col2:
        st.caption(
            "등록된 장비 IP에 Ping을 보내 UP/DOWN 상태를 확인합니다. "
            "현재 Ping 결과와 이전 Ping 로그를 비교해 장애 발생/복구 이력을 기록합니다."
        )

    if st.button("등록 장비 Ping 체크 실행"):
        ping_df = check_devices_status(
            devices_df=devices_df,
            timeout_ms=int(timeout_ms),
        )

        incident_df = detect_incidents(ping_df)

        if not incident_df.empty:
            append_incident_log(incident_df)
            st.session_state["last_incident_result"] = incident_df

        append_ping_log(ping_df)

        st.session_state["last_ping_result"] = ping_df

        st.success("Ping 체크가 완료되었습니다.")

        if not incident_df.empty:
            st.warning(f"상태 변경 이벤트가 {len(incident_df)}건 감지되었습니다.")

    ping_result_df = st.session_state.get("last_ping_result")

    if ping_result_df is None or ping_result_df.empty:
        st.info("아직 이번 세션에서 실행한 Ping 체크 결과가 없습니다.")
    else:
        up_count = len(ping_result_df[ping_result_df["status"] == "UP"])
        down_count = len(ping_result_df[ping_result_df["status"] == "DOWN"])
        unknown_count = len(ping_result_df[ping_result_df["status"] == "UNKNOWN"])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("전체 장비", len(ping_result_df))

        with col2:
            st.metric("UP", up_count)

        with col3:
            st.metric("DOWN", down_count)

        with col4:
            st.metric("UNKNOWN", unknown_count)

        if down_count > 0:
            st.error(f"DOWN 상태 장비가 {down_count}개 있습니다.")
        else:
            st.success("현재 Ping 기준 DOWN 장비가 없습니다.")

        st.dataframe(
            ping_result_df,
            use_container_width=True,
            hide_index=True,
        )

    last_incident_df = st.session_state.get("last_incident_result")

    if last_incident_df is not None and not last_incident_df.empty:
        st.write("이번 Ping 체크에서 감지된 상태 변경")
        st.dataframe(
            last_incident_df,
            use_container_width=True,
            hide_index=True,
        )

    st.write("최근 Ping 로그")

    ping_log_df = load_ping_log(limit=100)

    if ping_log_df.empty:
        st.warning("저장된 Ping 로그가 없습니다.")
        return

    st.dataframe(
        ping_log_df,
        use_container_width=True,
        hide_index=True,
    )

def get_current_down_devices_from_ping_log(limit=1000):
    """
    최근 Ping 로그를 기준으로 장비별 최신 상태를 확인하고,
    현재 devices.csv에 등록된 장비 중 DOWN 상태인 장비만 반환한다.
    """
    ping_log_df = load_ping_log(limit=limit)

    if ping_log_df.empty:
        return pd.DataFrame()

    ping_log_df = filter_registered_devices_only(
        ping_log_df,
        device_id_column="device_id",
    )

    if ping_log_df.empty:
        return pd.DataFrame()

    required_columns = ["checked_at", "device_id", "name", "ip", "role", "location", "status"]

    for column in required_columns:
        if column not in ping_log_df.columns:
            return pd.DataFrame()

    df = ping_log_df.copy()

    df["checked_at"] = pd.to_datetime(
        df["checked_at"],
        errors="coerce",
    )

    df = df.dropna(subset=["checked_at"])
    df = df.sort_values("checked_at")

    latest_df = df.groupby("device_id").tail(1)

    down_df = latest_df[latest_df["status"] == "DOWN"].copy()

    if down_df.empty:
        return pd.DataFrame()

    return down_df.sort_values("checked_at", ascending=False)

def filter_registered_devices_only(df, device_id_column="device_id"):
    """
    현재 devices.csv에 등록된 장비만 남긴다.
    삭제된 장비의 과거 로그는 화면에 표시하지 않는다.
    """
    if df.empty:
        return df

    if device_id_column not in df.columns:
        return df

    devices_df = load_devices()

    if devices_df.empty or "device_id" not in devices_df.columns:
        return pd.DataFrame(columns=df.columns)

    registered_device_ids = set(
        devices_df["device_id"].astype(str).str.strip().tolist()
    )

    filtered_df = df.copy()
    filtered_df[device_id_column] = filtered_df[device_id_column].astype(str).str.strip()

    filtered_df = filtered_df[
        filtered_df[device_id_column].isin(registered_device_ids)
    ]

    return filtered_df

def render_global_alert_panel():
    """
    대시보드 상단에서 현재 장애 상태를 요약 경고로 표시한다.
    """
    down_devices_df = get_current_down_devices_from_ping_log(limit=1000)

    if down_devices_df.empty:
        st.success("현재 Ping 기준 DOWN 상태 장비가 없습니다.")
        return

    down_count = len(down_devices_df)

    st.error(f"현재 DOWN 상태 장비가 {down_count}개 있습니다. 장애 이력과 Ping 상태를 확인하세요.")

    with st.expander("현재 DOWN 장비 목록 보기", expanded=True):
        st.dataframe(
            down_devices_df[
                [
                    "checked_at",
                    "name",
                    "ip",
                    "role",
                    "location",
                    "status",
                    "error",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

def render_incident_panel():
    st.subheader("장애 이력 관리")

    incident_df = load_incident_log(limit=200)

    incident_df = filter_registered_devices_only(
    incident_df,
    device_id_column="device_id",
)
    current_down_df = get_current_down_devices_from_ping_log(limit=1000)
    
    current_down_count = len(current_down_df) if not current_down_df.empty else 0

    if incident_df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("현재 DOWN 장비", current_down_count)

        with col2:
            st.metric("장애 발생 이력", 0)

        with col3:
            st.metric("복구 이력", 0)

        if current_down_count > 0:
            st.error(f"현재 DOWN 상태 장비가 {current_down_count}개 있습니다.")
            st.dataframe(
                current_down_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("아직 저장된 장애 이력이 없습니다.")

        return

    down_count = len(incident_df[incident_df["event_type"] == "DOWN"])
    recovered_count = len(incident_df[incident_df["event_type"] == "RECOVERED"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("현재 DOWN 장비", current_down_count)

    with col2:
        st.metric("전체 이벤트", len(incident_df))

    with col3:
        st.metric("장애 발생", down_count)

    with col4:
        st.metric("복구", recovered_count)

    if current_down_count > 0:
        st.error(f"현재 장애 상태 장비가 {current_down_count}개 있습니다.")
        with st.expander("현재 DOWN 장비 상세", expanded=True):
            st.dataframe(
                current_down_df,
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.success("현재 Ping 기준 DOWN 상태 장비가 없습니다.")

    event_filter = st.multiselect(
        "이벤트 유형 필터",
        ["DOWN", "RECOVERED"],
        default=["DOWN", "RECOVERED"],
    )

    filtered_df = incident_df[incident_df["event_type"].isin(event_filter)].copy()

    if filtered_df.empty:
        st.warning("선택한 조건에 해당하는 장애 이력이 없습니다.")
        return

    filtered_df["event_time"] = pd.to_datetime(
        filtered_df["event_time"],
        errors="coerce",
    )

    filtered_df = filtered_df.sort_values(
        "event_time",
        ascending=False,
    )

    down_events_df = filtered_df[filtered_df["event_type"] == "DOWN"]
    recovered_events_df = filtered_df[filtered_df["event_type"] == "RECOVERED"]

    tab1, tab2, tab3 = st.tabs(
        [
            "전체 이벤트",
            "장애 발생",
            "복구",
        ]
    )

    with tab1:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        if down_events_df.empty:
            st.success("선택한 조건에서 장애 발생 이벤트가 없습니다.")
        else:
            st.error(f"장애 발생 이벤트 {len(down_events_df)}건")
            st.dataframe(
                down_events_df,
                use_container_width=True,
                hide_index=True,
            )

    with tab3:
        if recovered_events_df.empty:
            st.info("선택한 조건에서 복구 이벤트가 없습니다.")
        else:
            st.success(f"복구 이벤트 {len(recovered_events_df)}건")
            st.dataframe(
                recovered_events_df,
                use_container_width=True,
                hide_index=True,
            )

    csv_data = filtered_df.to_csv(
        index=False,
        encoding="utf-8-sig",
    )

    st.download_button(
        label="장애 이력 CSV 다운로드",
        data=csv_data,
        file_name="incident_log.csv",
        mime="text/csv",
    )

def render_network_connections(connections_df, show_listen, max_rows):
    st.subheader("현재 네트워크 연결 세션")

    display_df = connections_df.copy()

    if not show_listen and "status" in display_df.columns:
        display_df = display_df[display_df["status"] != "LISTEN"]

    total_connections = len(display_df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("표시 중인 연결 수", total_connections)

    with col2:
        tcp_count = (
            len(display_df[display_df["protocol"] == "TCP"])
            if not display_df.empty
            else 0
        )
        st.metric("TCP 연결 수", tcp_count)

    with col3:
        udp_count = (
            len(display_df[display_df["protocol"] == "UDP"])
            if not display_df.empty
            else 0
        )
        st.metric("UDP 연결 수", udp_count)

    st.dataframe(
        display_df.head(max_rows),
        use_container_width=True,
        hide_index=True,
    )


def render_log_panel(enable_logging, system_status, network_speed, risk_result, log_limit):
    st.subheader("상태 로그")

    if enable_logging:
        log_path = append_system_log(
            system_status=system_status,
            network_speed=network_speed,
            risk_result=risk_result,
        )

        st.success(f"현재 상태가 로그에 저장되었습니다: {log_path}")
    else:
        st.info("상태 로그 저장이 비활성화되어 있습니다.")

    log_df = load_system_log(limit=log_limit)

    if log_df.empty:
        st.warning("아직 저장된 로그가 없습니다.")
        return pd.DataFrame()

    st.write("최근 저장 로그")
    st.dataframe(
        log_df,
        use_container_width=True,
        hide_index=True,
    )

    return log_df


def prepare_log_chart_data(log_df):
    chart_df = log_df.copy()

    chart_df["timestamp"] = pd.to_datetime(
        chart_df["timestamp"],
        errors="coerce",
    )

    chart_df = chart_df.dropna(subset=["timestamp"])
    chart_df = chart_df.sort_values("timestamp")

    numeric_columns = [
        "cpu_percent",
        "memory_percent",
        "disk_percent",
        "send_speed_mbps",
        "recv_speed_mbps",
        "risk_score",
        "total_connections",
        "established_count",
        "listen_count",
    ]

    for column in numeric_columns:
        if column in chart_df.columns:
            chart_df[column] = pd.to_numeric(
                chart_df[column],
                errors="coerce",
            )

    return chart_df


def render_log_charts(show_charts, log_df):
    st.subheader("로그 기반 그래프")

    if not show_charts:
        st.info("로그 그래프 표시가 비활성화되어 있습니다.")
        return

    if log_df.empty:
        st.warning("그래프를 그릴 로그 데이터가 없습니다.")
        return

    chart_df = prepare_log_chart_data(log_df)

    if chart_df.empty:
        st.warning("timestamp 변환 후 사용할 수 있는 로그 데이터가 없습니다.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "시스템 사용률",
            "네트워크 속도",
            "위험 점수",
            "연결 수",
        ]
    )

    with tab1:
        metric_df = chart_df.melt(
            id_vars="timestamp",
            value_vars=["cpu_percent", "memory_percent", "disk_percent"],
            var_name="metric",
            value_name="value",
        )

        fig = px.line(
            metric_df,
            x="timestamp",
            y="value",
            color="metric",
            markers=True,
            title="CPU / RAM / 디스크 사용률 변화",
        )

        fig.update_layout(
            xaxis_title="시간",
            yaxis_title="사용률 (%)",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with tab2:
        network_df = chart_df.melt(
            id_vars="timestamp",
            value_vars=["send_speed_mbps", "recv_speed_mbps"],
            var_name="metric",
            value_name="value",
        )

        fig = px.line(
            network_df,
            x="timestamp",
            y="value",
            color="metric",
            markers=True,
            title="네트워크 송신/수신 속도 변화",
        )

        fig.update_layout(
            xaxis_title="시간",
            yaxis_title="속도 (MB/s)",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with tab3:
        fig = px.line(
            chart_df,
            x="timestamp",
            y="risk_score",
            markers=True,
            title="위험 점수 변화",
        )

        fig.update_layout(
            xaxis_title="시간",
            yaxis_title="위험 점수",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with tab4:
        connection_df = chart_df.melt(
            id_vars="timestamp",
            value_vars=["total_connections", "established_count", "listen_count"],
            var_name="metric",
            value_name="value",
        )

        fig = px.line(
            connection_df,
            x="timestamp",
            y="value",
            color="metric",
            markers=True,
            title="네트워크 연결 수 변화",
        )

        fig.update_layout(
            xaxis_title="시간",
            yaxis_title="연결 수",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


def prepare_risk_event_data(log_df):
    if log_df.empty:
        return pd.DataFrame()

    event_df = log_df.copy()

    event_df["timestamp"] = pd.to_datetime(
        event_df["timestamp"],
        errors="coerce",
    )

    event_df = event_df.dropna(subset=["timestamp"])

    if "risk_score" in event_df.columns:
        event_df["risk_score"] = pd.to_numeric(
            event_df["risk_score"],
            errors="coerce",
        ).fillna(0)

    event_df = event_df[event_df["risk_level"].isin(["WARNING", "DANGER"])]

    if event_df.empty:
        return event_df

    event_df = event_df.sort_values(
        by=["risk_score", "timestamp"],
        ascending=[False, False],
    )

    display_columns = [
        "timestamp",
        "risk_level",
        "risk_score",
        "cpu_percent",
        "memory_percent",
        "disk_percent",
        "send_speed_mbps",
        "recv_speed_mbps",
        "total_connections",
        "established_count",
        "listen_count",
        "risk_reasons",
    ]

    existing_columns = [
        column for column in display_columns if column in event_df.columns
    ]

    return event_df[existing_columns]


def render_risk_event_panel(show_risk_events, log_df):
    st.subheader("로그 기반 위험 이벤트")

    if not show_risk_events:
        st.info("위험 이벤트 표시가 비활성화되어 있습니다.")
        return

    if log_df.empty:
        st.warning("분석할 로그 데이터가 없습니다.")
        return

    event_df = prepare_risk_event_data(log_df)

    if event_df.empty:
        st.success("현재 저장된 로그 기준으로 WARNING 또는 DANGER 이벤트가 없습니다.")
        return

    warning_count = len(event_df[event_df["risk_level"] == "WARNING"])
    danger_count = len(event_df[event_df["risk_level"] == "DANGER"])
    max_score = event_df["risk_score"].max() if "risk_score" in event_df.columns else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("WARNING 이벤트", warning_count)

    with col2:
        st.metric("DANGER 이벤트", danger_count)

    with col3:
        st.metric("최고 위험 점수", int(max_score))

    risk_filter = st.multiselect(
        "표시할 위험 등급",
        ["WARNING", "DANGER"],
        default=["WARNING", "DANGER"],
    )

    filtered_event_df = event_df[event_df["risk_level"].isin(risk_filter)]

    if filtered_event_df.empty:
        st.warning("선택한 위험 등급에 해당하는 로그가 없습니다.")
        return

    st.dataframe(
        filtered_event_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered_event_df.to_csv(
        index=False,
        encoding="utf-8-sig",
    )

    st.download_button(
        label="위험 이벤트 CSV 다운로드",
        data=csv_data,
        file_name="risk_events.csv",
        mime="text/csv",
    )


def render_ai_analysis(use_ai, system_status, network_speed, risk_result):
    st.subheader("로컬 요약 분석 결과")

    if not use_ai:
        st.warning("현재 로컬 요약 분석은 비활성화되어 있습니다.")
        return

    analysis_result = analyze_without_llm(
        system_status=system_status,
        network_speed=network_speed,
        risk_result=risk_result,
    )

    level = analysis_result["level"]
    status = analysis_result["status"]
    score = analysis_result["score"]

    if level == "NORMAL":
        st.success(f"상태: {status} / 위험 점수: {score}")
    elif level == "WARNING":
        st.warning(f"상태: {status} / 위험 점수: {score}")
    else:
        st.error(f"상태: {status} / 위험 점수: {score}")

    st.write("요약")
    st.write(analysis_result["summary"])

    st.write("판단 근거")
    for reason in analysis_result["reasons"]:
        st.write(f"- {reason}")

    st.write("권장 조치")
    for action in analysis_result["actions"]:
        st.write(f"- {action}")


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🖥️",
        layout="wide",
    )

    (
        auto_refresh,
        refresh_seconds,
        use_ai,
        enable_logging,
        show_charts,
        show_risk_events,
        show_listen,
        max_rows,
        log_limit,
    ) = render_sidebar()

    apply_auto_refresh(auto_refresh, refresh_seconds)

    render_global_alert_panel()

    st.divider()

    render_header(auto_refresh, refresh_seconds)

    system_status = get_system_status()

    network_speed = calculate_network_speed(
        current_network=system_status["network"],
        refresh_seconds=refresh_seconds,
    )

    connections_df = get_network_connections()

    risk_result = analyze_system_risk(
        system_status=system_status,
        network_speed=network_speed,
        connections_df=connections_df,
    )

    session_summary = build_session_summary(connections_df)

    render_system_metrics(system_status, network_speed)

    st.divider()

    render_risk_panel(risk_result)

    st.divider()

    render_session_summary(session_summary)

    st.divider()

    render_device_management_panel()

    st.divider()

    render_device_ping_panel()

    st.divider()

    render_incident_panel()

    st.divider()

    render_system_detail(system_status, network_speed)

    st.divider()

    render_network_connections(connections_df, show_listen, max_rows)

    st.divider()

    log_df = render_log_panel(
        enable_logging=enable_logging,
        system_status=system_status,
        network_speed=network_speed,
        risk_result=risk_result,
        log_limit=log_limit,
    )

    st.divider()

    render_log_charts(
        show_charts=show_charts,
        log_df=log_df,
    )

    st.divider()

    render_risk_event_panel(
        show_risk_events=show_risk_events,
        log_df=log_df,
    )

    st.divider()

    render_ai_analysis(
        use_ai=use_ai,
        system_status=system_status,
        network_speed=network_speed,
        risk_result=risk_result,
    )


if __name__ == "__main__":
    main()