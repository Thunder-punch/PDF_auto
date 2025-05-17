# 파일경로: ui/edit_info_screen.py
import os, pathlib, datetime, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk                    # ← Pillow 백업 로드
from utils.resource_manager import resource_path
from utils.config_manager import (
    load_last_folder, save_last_folder,
    load_company_info, save_company_info,
)

class EditInfoScreen:
    """업체 정보 수정 화면 (PDF 생성 화면과 동일한 크기)"""

    def __init__(self, parent, company: str):
        self.parent   = parent
        self.company  = company          # "업체1" 또는 "업체2"
        if isinstance(self.parent, tk.Tk):
            self.parent.geometry("830x890")


        # ── 상태값 ───────────────────────────────────────
        self.company_info = load_company_info(company)
        self.entries: dict[str, tk.Widget] = {}
        self.use_edit_stamp_var = tk.BooleanVar(
            value=self.company_info.get("use_edit_stamp", True)
        )
        init_path = load_last_folder(company) or "(경로가 없으므로 비어있음)"
        self.folder_var = tk.StringVar(value=init_path)

        # ── 레이아웃 ─────────────────────────────────────
        self.frame = ttk.Frame(parent, style="TFrame")
        self.frame.grid(row=0, column=0, sticky="NSEW")

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=0)

        self.setup_style()
        self._build_ui()
        self._load_stamp_image()

    # ────────────────────────────────────────────────────────
    # UI 빌더
    # ────────────────────────────────────────────────────────
    def _build_ui(self):
        ttk.Label(self.frame, text=f"{self.company} 정보 수정",
                  style="Header.TLabel", anchor="center")\
           .grid(row=0, column=0, columnspan=2, pady=10, sticky="EW")

        form = ttk.Frame(self.frame)
        form.grid(row=1, column=0, padx=20, pady=20, sticky="NSEW")
        self._build_form(form)
        self._build_folder_path(form)
        self._build_buttons(form)

    def _build_form(self, parent):
        row = 0
        for label, key in [
            ("관리번호", "manage_id"), ("사업장명", "company_name"),
            ("사업장 소재지", "company_address"), ("사업자 등록번호", "business_id"),
            ("법인등록번호", "edit_corporate_id"), ("대표자명", "ceo_name"),
            ("대표자 주민등록번호", "edit_ceo_id"), ("전화번호", "edit_phone"),
            ("자택주소", "edit_home"), ("휴대폰번호", "edit_cell"),
            ("직위 또는 직책", "edit_po"),
        ]:
            ttk.Label(parent, text=label, style="TLabel")\
               .grid(row=row, column=0, padx=10, pady=2, sticky="W")
            if key == "edit_ceo_id":
                e = ttk.Entry(parent, font=("Pretendard", 11))
                if key in self.company_info:
                    e.insert(0, self.company_info[key])
                def on_rrn_entry(event, entry=e):
                    value = entry.get().replace("-", "")
                    if len(value) > 6:
                        value = value[:6] + "-" + value[6:]
                    entry.delete(0, tk.END)
                    entry.insert(0, value)
                e.bind("<KeyRelease>", on_rrn_entry)
            else:
                e = ttk.Entry(parent, font=("Pretendard", 11))
                if key in self.company_info:
                    e.insert(0, self.company_info[key])
            e.grid(row=row, column=1, padx=10, pady=2, sticky="EW", ipady=0)
            self.entries[key] = e
            row += 1

        # 작성일자
        ttk.Label(parent, text="작성일자", style="TLabel")\
           .grid(row=row, column=0, padx=10, pady=2, sticky="W")
        d = DateEntry(parent, width=32, date_pattern="yyyy-MM-dd",
                      font=("Pretendard", 11))
        try:
            d.set_date(self.company_info.get("edit_date",
                                             datetime.date.today()))
        except Exception:
            pass
        d.grid(row=row, column=1, padx=10, pady=2, sticky="W", ipady=0)
        self.entries["edit_date"] = d

    def _build_folder_path(self, parent):
        ttk.Label(parent, text="업체폴더 생성경로:", style="TLabel")\
           .grid(row=999, column=0, padx=10, pady=(10, 4), sticky="W")
        ttk.Label(parent, textvariable=self.folder_var, style="TLabel")\
           .grid(row=1000, column=0, columnspan=2, padx=10, sticky="W")
        ttk.Button(parent, text="경로 선택", command=self._pick_folder)\
           .grid(row=1001, column=0, padx=10, pady=(4, 10), sticky="W")

    def _build_buttons(self, parent):
        btn = ttk.Frame(parent)
        btn.grid(row=1002, column=0, columnspan=2, pady=8)
        ttk.Button(btn, text="메인 화면", command=self.go_back)\
           .pack(side="left", padx=6, ipadx=8, ipady=3)
        ttk.Button(btn, text="입력완료", command=self.save_info)\
           .pack(side="left", padx=6, ipadx=8, ipady=3)

    # ────────────────────────────────────────────────────────
    # 보조 메서드
    # ────────────────────────────────────────────────────────
    def _pick_folder(self):
        sel = filedialog.askdirectory(title="자문사 폴더 경로 선택")
        if sel:
            self.folder_var.set(sel)
            save_last_folder(self.company, sel)

    def _load_stamp_image(self):
        idx = ''.join(filter(str.isdigit, self.company)) or "1"
        # 설치 폴더 옆 resources 우선, 없으면 내장 리소스, 없으면 개발 모드
        rel = os.path.join("resources", "images", f"업체{idx}인감.png")
        path = pathlib.Path(resource_path(rel))
        self.stamp_img = None
        try:
            self.stamp_img = tk.PhotoImage(file=str(path))
        except Exception:
            try:
                self.stamp_img = ImageTk.PhotoImage(Image.open(path))
            except Exception:
                pass

        frame = ttk.Frame(self.frame)
        frame.grid(row=1, column=1, padx=20, pady=8, sticky="N")
        ttk.Label(frame, text=f"{self.company} 인감", style="TLabel")\
           .pack(pady=(0, 2))
        if self.stamp_img:
            ttk.Label(frame, image=self.stamp_img).pack()
        tk.Checkbutton(frame, text="인감 날인",
                       variable=self.use_edit_stamp_var,
                       font=("Pretendard", 11), indicatoron=False,
                       padx=5, pady=2).pack(pady=(2, 0))

    # ────────────────────────────────────────────────────────
    # 저장 / 이동
    # ────────────────────────────────────────────────────────
    def save_info(self):
        new: dict[str, str] = {}

        for k, w in self.entries.items():
            new[k] = (w.get_date().strftime("%Y-%m-%d")
                      if isinstance(w, DateEntry) else w.get().strip())

        new["use_edit_stamp"] = self.use_edit_stamp_var.get()

        # 주민번호 → 생년월일
        rrn = new.get("edit_ceo_id", "").replace("-", "")
        if len(rrn) >= 6 and rrn[:6].isdigit():
            yy, mm, dd = rrn[:2], rrn[2:4], rrn[4:6]
            yyyy = (2000 if int(yy) <= datetime.date.today().year % 100
                    else 1900) + int(yy)
            new["edit_ceo_id_birth"] = f"{yyyy}년{mm}월{dd}일"

        idx = ''.join(filter(str.isdigit, self.company)) or "1"
        rel = os.path.join("resources", "images", f"업체{idx}인감.png")
        new["edit_stamp"] = resource_path(rel)

        # 기존 설정과 병합 저장
        merged = load_company_info(self.company)
        merged.update(new)
        save_company_info(self.company, merged)

        messagebox.showinfo("완료", "수정이 완료되었습니다.")
        self.go_back()

    def go_back(self):
        from ui.main_screen import show_main_screen
        root = self.parent.winfo_toplevel()  # ← 먼저 가져와야 함
        self.frame.destroy()
        show_main_screen(root)

    def setup_style(self):
        self.style = ttk.Style(self.parent)
        self.style.theme_use("clam")
        self.style.configure(".", background="#FFFFFF")
        self.style.configure("TFrame", background="#FFFFFF")
        self.style.configure("TLabel", font=("Pretendard", 13), background="#FFFFFF", foreground="#222")
        self.style.configure("Header.TLabel", font=("Pretendard", 28, "bold"), background="#FFFFFF", foreground="#5B8DEF")
        self.style.configure("TButton",
            font=("Pretendard", 16, "bold"),
            background="#E9F0FB", foreground="#5B8DEF",
            borderwidth=2, focusthickness=0, focuscolor="#5B8DEF", padding=12,
            relief="solid", bordercolor="#888"
        )
        self.style.map("TButton",
            background=[
                ("active", "#5B8DEF"),
                ("pressed", "#5B8DEF"),
                ("hover", "#D6E6FB"),
                ("!active", "#E9F0FB")
            ],
            foreground=[
                ("active", "#fff"),
                ("pressed", "#fff"),
                ("hover", "#5B8DEF"),
                ("!active", "#5B8DEF")
            ],
            bordercolor=[
                ("active", "#888"),
                ("pressed", "#888"),
                ("hover", "#888"),
                ("!active", "#888")
            ]
        )
        self.style.configure("TEntry", font=("Pretendard", 11), fieldbackground="#F7FAFF", bordercolor="#D6E6FB", relief="flat", padding=0)

