# 파일경로: utils/resource_manager.py

import os
import sys
from utils.config import BASE_PATH

def resource_path(relative_path: str) -> str:
    """
    1) 설치 폴더 옆 외부 resources 폴더 확인 → 있으면 사용
    2) PyInstaller 내장 리소스 임시 폴더(_MEIPASS) 확인 → 있으면 사용
    3) 개발 모드(BASE_PATH/resources) 최종 fallback
    """
    # 1) 설치 폴더 옆 resources
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        abs_path = os.path.join(exe_dir, relative_path)
        if os.path.exists(abs_path):
            return abs_path

    # 2) 내장 리소스
    if getattr(sys, '_MEIPASS', False):
        abs_path = os.path.join(sys._MEIPASS, relative_path)
        if os.path.exists(abs_path):
            return abs_path

    # 3) 개발 모드
    return os.path.join(BASE_PATH, relative_path)
