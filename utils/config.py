# utils/config.py

import os, sys

# ─── 실행환경별 BASE_PATH 결정 ───
if getattr(sys, 'frozen', False):
    # PyInstaller --onefile 로 묶였을 때
    BASE_PATH = sys._MEIPASS      # exe 내부로 풀린 임시 폴더
else:
    # 개발 모드: 이 파일의 상위 폴더를 프로젝트 루트로
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESOURCE_FONTS         = os.path.join(BASE_PATH, "resources", "fonts")
RESOURCE_IMAGES        = os.path.join(BASE_PATH, "resources", "images")
RESOURCE_PDF_TEMPLATES = os.path.join(BASE_PATH, "resources", "pdf_templates")

VERSION = "1.2.1"