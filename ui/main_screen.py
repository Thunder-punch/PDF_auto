# File: ui/main_screen.py

import os
import logging
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.config import RESOURCE_IMAGES, VERSION

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("사무자동화")
        self.root.minsize(1025, 500)
        self.root.geometry("830x1350")
        self.root.configure(bg="white")

        self.setup_style()
        self.load_resources()
        self.setup_layout()
        self.create_header_frame()
        self.create_main_frame()

    def setup_style(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        # 전체 배경 흰색
        self.style.configure(".", background="white")
        self.style.configure("TFrame", background="white")
        self.style.configure("TLabel", font=("NanumGothic", 14), background="white")
        self.style.configure("Header.TLabel", font=("NanumGothicBold", 24), background="white")
        # 버튼 스타일 원복: 기본 테두리 및 배경 유지
        self.style.configure("TButton", font=("NanumGothic", 14), background="white")

    def load_resources(self):
        logo_path = os.path.join(RESOURCE_IMAGES, "logo.png")
        self.logo_image = None
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                w, h = img.size
                resized = img.resize((int(w * 0.363), int(h * 0.363)), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(resized, master=self.root)
            except Exception as e:
                logging.error("로고 이미지 로드 실패: %s", e)
        else:
            logging.warning("로고 이미지 파일이 존재하지 않습니다: %s", logo_path)
        self.root.logo_image = self.logo_image

    def setup_layout(self):
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def create_header_frame(self):
        self.header_frame = ttk.Frame(self.root, style="TFrame")
        self.header_frame.grid(row=0, column=0, sticky="EW", padx=10, pady=10)
        self.header_frame.columnconfigure(0, weight=1)

        if self.logo_image:
            logo_label = tk.Label(self.header_frame, image=self.logo_image, bg="white")
            logo_label.grid(row=0, column=0, sticky="E")
        else:
            logo_label = tk.Label(self.header_frame, text="로고 없음", bg="white", fg="red")
            logo_label.grid(row=0, column=0, sticky="E")

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.grid(row=1, column=0, sticky="NSEW", padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)

        # 제목
        label_title = ttk.Label(
            self.main_frame,
            text="사무자동화",
            style="Header.TLabel",    # ← 여기에 헤더 스타일 적용
            anchor="center",
            justify="center"
        )
        label_title.grid(row=0, column=0, columnspan=2, pady=(20, 10))


        # 안내문
        label_announce = ttk.Label(
            self.main_frame,
            text=(
                "본 프로그램은 고객사의 동일한 정보를\n" 
                "여러 PDF에 입력하는 단순 작업을 줄이기 위해\n"
                "제작한 프로그램입니다."
            ),
            style="TLabel",
            anchor="center",
            justify="center"
        )
        label_announce.grid(row=1, column=0, sticky="EW", padx=20, pady=(0, 20))

        # 업체별 버튼 영역
        button_frame = ttk.Frame(self.main_frame, style="TFrame")
        button_frame.grid(row=2, column=0, sticky="EW", pady=(10, 20))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        for idx, company in enumerate(["업체1", "업체2"]):
            # 연한 회색 배경 + 회색 테두리
            comp_frame = tk.Frame(
                button_frame,
                bg="#F7F7F7",
                highlightbackground="#CCCCCC",
                highlightthickness=1,
                bd=0
            )
            # 프레임 균등 확장, 좌우 간격 확보
            comp_frame.grid(row=0, column=idx, sticky="EW", padx=20, pady=10)
            comp_frame.columnconfigure(0, weight=1)

            # 업체명 (컬럼 0~1 합침)
            lbl = ttk.Label(
                comp_frame,
                text=company,
                font=("NanumGothicBold", 18),
                background="#F7F7F7"
            )
            lbl.grid(row=0, column=0, columnspan=2, sticky="W", padx=10, pady=10)

            # 정보 수정 버튼 (레이블 아래, 너비 통일)
            btn_edit = ttk.Button(
                comp_frame,
                text="정보 수정",
                command=lambda c=company: self.show_edit_info_screen(c),
                width=15
            )
            btn_edit.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="EW")

            # PDF 생성 버튼 (레이블 아래, 너비 통일)
            btn_pdf = ttk.Button(
                comp_frame,
                text="PDF 생성",
                command=lambda c=company: self.on_click_pdf_generation(c),
                width=15
            )
            btn_pdf.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="EW")

        # 피드백 안내
        label_error = ttk.Label(
            self.main_frame,
            text=(
                "프로그램 사용 중 문제가 발생했다면 아래 로그 파일을 첨부하여 문의해 주세요.\n\n"
                "▶ logs 폴더 내 로그 파일\n"
                "   - pdf사무자동화_v1.2.1_날짜.txt\n\n"
                "▶ 문의 연락처\n"
                "   - 이메일: jtw1508@naver.com\n"
                "   - 전화번호: 070-8027-1477\n\n"
            ),
            style="TLabel",
            anchor="w",
            justify="left"
        )
        label_error.grid(row=4, column=0, columnspan=2, sticky="W", padx=20, pady=(10, 20))

        # 2. 회사 정보 영역 (가운데 정렬)
        label_footer = ttk.Label(
            self.main_frame,
            text=(
                "하엘프랜즈 | 사람 곁의 AI\n"
                "Copyright ⓒ HaelFriends. All rights reserved."
            ),
            style="TLabel",
            anchor="center",
            justify="center"
        )
        label_footer.grid(row=5, column=0, columnspan=2, sticky="EW", padx=20, pady=(0, 20))

        # 버전 표시
        label_version = ttk.Label(
            self.main_frame,
            text=f"버전 {VERSION}",
            style="TLabel",
            anchor="e",
            justify="right"
        )
        label_version.grid(row=5, column=0, sticky="E", padx=20, pady=(0, 10))

    def on_click_pdf_generation(self, company):
        logging.debug("on_click_pdf_generation() called. company=%s", company)
        self.main_frame.destroy()
        from ui.pdf_generation_screen import PDFGenerationScreen
        PDFGenerationScreen(self.root, company)


    def show_edit_info_screen(self, company):
        logging.debug("show_edit_info_screen() called. company=%s", company)
        self.main_frame.destroy()
        from ui.edit_info_screen import EditInfoScreen
        EditInfoScreen(self.root, company)

    def run(self):
        self.root.mainloop()

def show_main_screen(root):
    app = App.__new__(App)
    app.root = root
    app.setup_style()
    app.load_resources()
    app.setup_layout()
    app.create_header_frame()
    app.create_main_frame()
