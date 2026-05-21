import psutil


def bytes_to_mb(value):
    """
    byte 단위 값을 MB 단위 숫자로 변환한다.
    """
    return round(value / 1024 / 1024, 2)


def bytes_to_gb(value):
    """
    byte 단위 값을 GB 단위 숫자로 변환한다.
    """
    return round(value / 1024 / 1024 / 1024, 2)


def get_cpu_info():
    """
    CPU 사용률 정보를 가져온다.
    """
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count(logical=True)

    return {
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
    }


def get_memory_info():
    """
    RAM 사용 정보를 가져온다.
    """
    memory = psutil.virtual_memory()

    return {
        "memory_total_gb": bytes_to_gb(memory.total),
        "memory_used_gb": bytes_to_gb(memory.used),
        "memory_available_gb": bytes_to_gb(memory.available),
        "memory_percent": memory.percent,
    }


def get_disk_info():
    """
    디스크 사용 정보를 가져온다.
    """
    disk = psutil.disk_usage("/")

    return {
        "disk_total_gb": bytes_to_gb(disk.total),
        "disk_used_gb": bytes_to_gb(disk.used),
        "disk_free_gb": bytes_to_gb(disk.free),
        "disk_percent": disk.percent,
    }


def get_network_info():
    """
    네트워크 송신/수신 누적 정보를 가져온다.

    bytes_sent, bytes_recv는 초당 속도 계산을 위해 원본 byte 값도 함께 반환한다.
    """
    net = psutil.net_io_counters()

    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
        "bytes_sent_mb": bytes_to_mb(net.bytes_sent),
        "bytes_recv_mb": bytes_to_mb(net.bytes_recv),
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
    }


def get_system_status():
    """
    대시보드에서 사용할 전체 시스템 상태 정보를 한 번에 가져온다.
    """
    cpu = get_cpu_info()
    memory = get_memory_info()
    disk = get_disk_info()
    network = get_network_info()

    return {
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "network": network,
    }