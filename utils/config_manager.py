# File: utils/config_manager.py

import json
import os
import sys

# 1) exe 로 묶였을 때: 실행 파일(.exe) 위치 기준
# 2) 개발 모드: 프로젝트 루트 기준
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(APP_DIR, "config.json")

def load_last_folder(company):
    """해당 업체(company)의 마지막 저장 경로를 반환"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get(f"last_folder_{company}", "")
        except Exception as e:
            print("구성 파일 로드 오류:", e)
    return ""


def save_last_folder(company, folder_path):
    """해당 업체(company)의 마지막 저장 경로를 파일에 저장"""
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print("구성 파일 로드 오류:", e)
    config[f"last_folder_{company}"] = folder_path
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("구성 파일 저장 오류:", e)


def load_company_info(company):
    """해당 업체(company)의 저장된 정보를 반환합니다."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 저장된 회사 정보 전체 반환 (PDF 전용 키 포함)
                return config.get(f"company_info_{company}", {})
        except Exception as e:
            print("구성 파일 로드 오류:", e)
    return {}


def save_company_info(company, info_dict):
    """해당 업체(company)의 정보를 config.json에 저장합니다."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print("구성 파일 로드 오류:", e)
    config[f"company_info_{company}"] = info_dict
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("구성 파일 저장 오류:", e)
