# main.py

import os
import sys
import subprocess
import winreg
import datetime
import logging
from logging import Formatter
import tkinter as tk
from tkinter import messagebox
from utils.config import VERSION, RESOURCE_FONTS
from ui.main_screen import App
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tkinter.font as tkfont
import reportlab
import reportlab.pdfgen
import reportlab.lib

def get_hardware_id():
    """
    윈도우 설치 고유값인 MachineGuid를 레지스트리에서 읽어 반환합니다.
    실패 시 None을 반환합니다.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        logging.debug(f"64비트 레지스트리에서 MachineGuid 읽기 성공: {guid}")
        return guid
    except Exception as e:
        logging.debug(f"64비트 레지스트리에서 MachineGuid 읽기 실패: {e}")
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Wow6432Node\Microsoft\Cryptography",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_32KEY
            )
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            logging.debug(f"32비트 레지스트리에서 MachineGuid 읽기 성공: {guid}")
            return guid
        except Exception as e:
            logging.error(f"32비트 레지스트리에서 MachineGuid 읽기 실패: {e}")
            return None

def write_hwid_to_registry(hwid):
    """
    레지스트리에 HWID를 기록합니다.
    설치 프로그램 단계에서 실행하도록 설계되었습니다.
    """
    hive64 = r"SOFTWARE\HaelFriends\PDF사무자동화"
    hive32 = r"SOFTWARE\Wow6432Node\HaelFriends\PDF사무자동화"

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            hive64,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
        )
    except FileNotFoundError:
        key = winreg.CreateKeyEx(
            winreg.HKEY_LOCAL_MACHINE,
            hive32,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_32KEY
        )
    try:
        winreg.SetValueEx(key, 'HWID', 0, winreg.REG_SZ, hwid)
    finally:
        winreg.CloseKey(key)

def check_installation():
    try:
        # 64비트 레지스트리 먼저 시도
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\HaelFriends\PDF사무자동화",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            )
            logging.debug("64비트 레지스트리 키 열기 성공")
        except FileNotFoundError:
            # 32비트 레지스트리 시도
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Wow6432Node\HaelFriends\PDF사무자동화",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_32KEY
            )
            logging.debug("32비트 레지스트리 키 열기 성공")

        try:
            installed, _ = winreg.QueryValueEx(key, 'Installed')
            logging.debug(f"Installed 값: {installed}")
            
            if installed != 'True':
                messagebox.showerror(
                    "설치 오류",
                    "이 소프트웨어는 올바르게 설치되지 않았습니다.\n재설치해주세요."
                )
                sys.exit()

            stored_hwid, _ = winreg.QueryValueEx(key, 'HWID')
            logging.debug(f"저장된 HWID: {stored_hwid}")
            
            current_hwid = get_hardware_id()
            logging.debug(f"현재 HWID: {current_hwid}")
            
            if not current_hwid:
                messagebox.showerror(
                    "라이선스 오류",
                    "HWID를 가져올 수 없습니다."
                )
                sys.exit()
                
            if stored_hwid != current_hwid:
                logging.error(f"HWID 불일치: 저장된 값={stored_hwid}, 현재 값={current_hwid}")
                messagebox.showerror(
                    "라이선스 오류",
                    "라이선스가 등록된 PC가 아닙니다."
                )
                sys.exit()

        except FileNotFoundError as e:
            logging.error(f"레지스트리 값 없음: {e}")
            messagebox.showerror(
                "설치 오류",
                "이 소프트웨어는 올바르게 설치되지 않았습니다.\n재설치해주세요."
            )
            sys.exit()
        except OSError as e:
            logging.error(f"레지스트리 접근 오류: {e}")
            messagebox.showerror(
                "라이선스 오류",
                "라이선스 정보(HWID)가 등록되지 않았습니다.\n"
                "정상 설치 프로그램을 통해 다시 설치해주세요."
            )
            sys.exit()
        finally:
            winreg.CloseKey(key)

    except PermissionError:
        logging.error("관리자 권한 없음")
        messagebox.showerror(
            "권한 오류",
            "관리자 권한이 필요합니다. 관리자 권한으로 실행해주세요."
        )
        sys.exit()
    except Exception as e:
        logging.error(f"예상치 못한 오류: {e}")
        messagebox.showerror(
            "오류",
            f"알 수 없는 오류가 발생했습니다: {e}"
        )
        sys.exit()

# ─────────── 로그 디렉토리 및 파일 준비 ───────────
LOG_DIR = os.path.join(
    os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__),
    'logs'
)
os.makedirs(LOG_DIR, exist_ok=True)

today = datetime.date.today().strftime('%Y%m%d')
log_filename = os.path.join(
    LOG_DIR,
    f"pdf사무자동화_v{VERSION}_{today}.txt"
)

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

log_file = None
try:
    log_file = open(log_filename, "a", encoding="utf-8")
except Exception as e:
    print(f"[경고] 로그 파일을 열 수 없습니다: {e}")

def cleanup_resources():
    """프로그램 종료 시 리소스를 정리합니다."""
    if log_file:
        try:
            log_file.close()
        except Exception as e:
            print(f"로그 파일 닫기 실패: {e}")

# 프로그램 종료 시 리소스 정리
import atexit
atexit.register(cleanup_resources)

class TeeStream:
    def __init__(self, *streams):
        self.streams = [s for s in streams if s]

    def write(self, data):
        for s in self.streams:
            try:
                s.write(data)
                s.flush()
            except Exception:
                pass

    def flush(self):
        for s in self.streams:
            try:
                s.flush()
            except Exception:
                pass

def handle_unhandled(exc_type, exc_value, exc_traceback):
    logging.error(
        "처리되지 않은 예외 발생",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    if log_file:
        log_file.write("------------------\n")
        log_file.write(f"{datetime.datetime.now()}\n")
        import traceback
        traceback.print_exception(
            exc_type, exc_value, exc_traceback, file=log_file
        )
    from tkinter import messagebox
    messagebox.showerror(
        "오류",
        "예기치 않은 오류가 발생했습니다.\n로그를 확인 후 개발자에게 문의하세요."
    )

sys.stdout = TeeStream(sys.stdout, log_file)
sys.stderr = TeeStream(sys.stderr, log_file)
sys.excepthook = handle_unhandled

def resource_path(relative_path):
    # PyInstaller 환경 대응
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# Pretendard 폰트 등록 (tkinter)
pretendard_path = resource_path('resources/fonts/PretendardVariable.ttf')
try:
    tkfont.nametofont("TkDefaultFont").configure(family="Pretendard")
except Exception:
    try:
        tkfont.Font(root=None, name="Pretendard", family=pretendard_path)
    except Exception:
        pass

# ─────────── 폰트 등록 ───────────
logging.debug(f"프로그램 시작 (버전 {VERSION}): 폰트 등록을 시작합니다.")
try:
    pdfmetrics.registerFont(
        TTFont('Pretendard', pretendard_path)
    )
    pdfmetrics.registerFont(
        TTFont('PretendardBold', pretendard_path)
    )
    pdfmetrics.registerFont(
        TTFont('NanumGothic', os.path.join(RESOURCE_FONTS, 'NanumGothic.ttf'))
    )
    pdfmetrics.registerFont(
        TTFont('NanumGothicBold', os.path.join(RESOURCE_FONTS, 'NanumGothicBold.ttf'))
    )
except Exception as e:
    logging.error(f"폰트 등록 실패: {e}")

# ─────────── 앱 실행 ───────────
if __name__ == '__main__':
    # 배포용 exe에서만 설치 및 라이선스 검사
    if getattr(sys, 'frozen', False):
        check_installation()

    logging.debug("App 인스턴스 생성 시작")
    app = App()
    logging.debug("App 인스턴스 생성 완료. 앱 실행 중...")
    app.run()
    logging.debug("App 종료")
