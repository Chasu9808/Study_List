import os
import sys
import traceback
from pathlib import Path

from streamlit.web import cli as stcli


def get_base_dir():
    """
    exe로 실행될 때는 exe가 있는 폴더를 기준으로 사용한다.
    일반 Python 실행 시에는 현재 파일 위치를 기준으로 사용한다.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def get_app_path(base_dir):
    """
    app.py 위치를 찾는다.
    PyInstaller onedir 배포에서는 app.py를 exe 폴더에 같이 복사해두는 구조를 사용한다.
    """
    app_path = base_dir / "app.py"

    if app_path.exists():
        return app_path

    internal_app_path = base_dir / "_internal" / "app.py"

    if internal_app_path.exists():
        return internal_app_path

    return app_path


def main():
    try:
        base_dir = get_base_dir()
        app_path = get_app_path(base_dir)

        os.chdir(base_dir)

        print("================================")
        print("Network AI Dashboard 실행")
        print("기준 폴더:", base_dir)
        print("app.py 경로:", app_path)
        print("접속 주소: http://localhost:8501")
        print("================================")

        if not app_path.exists():
            print(f"app.py 파일을 찾을 수 없습니다: {app_path}")
            input("엔터를 누르면 종료합니다...")
            return

        sys.argv = [
            "streamlit",
            "run",
            str(app_path),

            "--global.developmentMode=false",

            "--server.headless=false",
            "--server.fileWatcherType=none",
            "--browser.gatherUsageStats=false",
            "--server.port=8501",
            "--server.address=localhost",
        ]

        stcli.main()

    except Exception:
        print("실행 중 오류가 발생했습니다.")
        traceback.print_exc()
        input("엔터를 누르면 종료합니다...")


if __name__ == "__main__":
    main()