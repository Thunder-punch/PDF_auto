# File: ui/pdf_generation_screen.py

import os
import datetime
import logging
import tempfile
import tkinter.font as tkfont

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

from PIL import Image, ImageDraw, ImageFont, ImageTk

from utils.config_manager import load_last_folder, load_company_info, save_company_info
from utils.folder_manager import make_folders
from utils.config import RESOURCE_FONTS, RESOURCE_IMAGES, RESOURCE_PDF_TEMPLATES
from pdf.pdf_generator import TEMPLATES, generate_pdf_with_template_check

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def make_stamp_image(text: str, font_path: str) -> str:
    """
    PDF 벡터 도장(_draw_vector_stamp)과 100% 동일한 비율로
    테두리·글씨를 PIL 이미지로 렌더링합니다.
    """
    from PIL import Image, ImageDraw, ImageFont
    W, H = 120, 280

    # ── PDF 쪽과 같은 방식의 축척 계산 ─────────────────
    scale = min(W / 120, H / 280)
    drawW, drawH = 120 * scale, 280 * scale
    ox, oy = (W - drawW) / 2, (H - drawH) / 2
    bw = 8 * scale

    # ── 캔버스 생성 및 테두리 그리기 ────────────────────
    img = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    border_color = "#db4b57"
    # ellipse box: PDF _draw_vector_stamp 과 동일하게
    left   = ox + bw/2
    top    = oy + bw/2
    right  = ox + drawW - bw/2
    bottom = oy + drawH - bw/2
    draw.ellipse((left, top, right, bottom),
                 outline=border_color, width=int(bw))

    # ── 글씨 그리기 ───────────────────────────────────
    if text:
        base  = (drawH - 2*bw) / len(text)
        fsize = max(int(base - 15), 4)
        font  = ImageFont.truetype(font_path, fsize)

        total_h = len(text) * fsize
        # PDF 쪽 y 계산과 똑같이 중앙 정렬
        y = oy + (drawH - total_h) / 2 - 10
        x_center = ox + drawW / 2

        for ch in text:
            w = font.getbbox(ch)[2] - font.getbbox(ch)[0]
            draw.text((x_center - w/2, y),
                      ch, font=font, fill=border_color)
            y += fsize

    # ── 임시파일 저장 후 경로 반환 ────────────────────
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    return tmp.name


class PDFGenerationScreen:
    STAMP_FONT = os.path.join(RESOURCE_FONTS, "GapyeongHanseokbongB.ttf")

    def __init__(self, parent, company: str):
        # —————————————————————————————————————
        # 라벨과 입력필드 글씨 크기 통일
        style = ttk.Style()
        # 라벨 폰트 (예: NanumGothic 12pt)  
        style.configure('TLabel', font=('NanumGothic', 12))
        # 입력필드 폰트 (예: NanumGothic 12pt)  
        style.configure('TEntry', font=('NanumGothic', 12))
        # —————————————————————————————————————

        try:
            for fn in (
                "TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont",
                "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"
            ):
                f = tkfont.nametofont(fn)
                f.configure(size=f['size'] - 1 )
        except Exception:
            pass

        self.parent  = parent
        self.company = company

        self.company_info = load_company_info(company)   # ← 먼저 로드
        self.use_stamp_var = tk.BooleanVar(
            value=self.company_info.get("use_stamp", True)
        )

        # 3) 메인 프레임 생성
        self.frame = ttk.Frame(parent, style="TFrame")
        self.frame.grid(row=0, column=0, sticky="NSEW")
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=0)

        # 4) 마지막 저장 폴더
        init_path = load_last_folder(company) or "(경로가 없으므로 비어있음)"
        self.folder_var = tk.StringVar(value=init_path)

        # 5) 기타 컨트롤용 딕셔너리
        self.entries: dict[str, tk.Widget] = {}
        self.doc_vars: dict[str, tk.IntVar] = {}

        # 6) UI 빌드
        self._build_ui()
        self._build_stamp_preview()

        # 7) 대표자명 입력 시 도장 미리보기 갱신
        ceo_entry = self.entries.get("ceo_business")
        if ceo_entry:
            ceo_entry.bind("<KeyRelease>",
                           lambda e: self._update_stamp_preview())

    def _build_ui(self):
        # 창 크기 조정
        if isinstance(self.parent, tk.Tk):
            self.parent.geometry("830x1350")

        self._header()
        self._doc_checkboxes()
        self.right_col = ttk.Frame(self.frame)
        self.right_col.grid(row=2, column=1, sticky="N", padx=20)
        self._form_inputs()
        self._folder_path_info()
        self._bottom_buttons()

    def _header(self):
        ttk.Label(
            self.frame,
            text=f"{self.company} PDF 생성",
            style="Header.TLabel",
            anchor="center"
        ).grid(row=0, column=0, columnspan=2, pady=10, sticky="EW")

    def _doc_checkboxes(self):
        lf = ttk.LabelFrame(self.frame, text="생성할 PDF 항목 선택", labelanchor="nw")
        lf.grid(row=1, column=0, padx=20, pady=(0,10), sticky="EW")
        inner = ttk.Frame(lf)
        inner.pack()

        self.doc_order = [
            "계약서", "고용 EDI", "건강 EDI", "국민 EDI",
            "CMS", "대리인 별지 1", "대리인 별지 2"
        ]
        for col, doc in enumerate(self.doc_order):
            var = tk.IntVar(value=self.company_info.get(f"doc_{doc}", 0))
            tk.Checkbutton(
                inner, text=doc, variable=var,
                font=("NanumGothic", 14),
                indicatoron=False, padx=5, pady=5
            ).grid(row=0, column=col, padx=5)
            self.doc_vars[doc] = var

    def _form_inputs(self):
        f = ttk.Frame(self.frame)
        f.grid(row=2, column=0, padx=20, pady=10, sticky="NSEW")
        row = 0

        # 기본 입력
        for label, key in [
            ("관리번호", "manage_id_pdf"),
            ("사업장명(필수)", "company_name_pdf"),
            ("사업장 소재지", "company_address_pdf"),
            ("사업의 종류", "business_type"),
            ("상시사용근로자수", "num_employees"),
        ]:
            row = self._entry(f, row, label, key)

        # 법인등록번호
        row = self._entry(f, row, "법인등록번호", "corporate_id_pdf")

        # 사업자등록번호 3분할
        ttk.Label(f, text="사업자등록번호").grid(row=row, column=0, sticky="W", padx=10, pady=5)
        sub1 = ttk.Frame(f)
        sub1.grid(row=row, column=1, sticky="EW", padx=10, pady=5)
        for i, width in enumerate((5,5,8), start=1):
            e = ttk.Entry(sub1, width=width)
            val = self.company_info.get(f"business_id_pdf_part{i}", "")
            if val:
                e.insert(0, val)
            e.pack(side="left", padx=5)
            self.entries[f"business_id_pdf_part{i}"] = e
        row += 1

        # 대표자 주민등록번호 2분할
        ttk.Label(f, text="대표자 주민등록번호").grid(row=row, column=0, sticky="W", padx=10, pady=5)
        sub2 = ttk.Frame(f)
        sub2.grid(row=row, column=1, sticky="EW", padx=10, pady=5)
        for i, width in enumerate((8,9), start=1):
            e = ttk.Entry(sub2, width=width)
            val = self.company_info.get(f"ceo_id_pdf_part{i}", "")
            if val:
                e.insert(0, val)
            e.pack(side="left", padx=5)
            self.entries[f"ceo_id_pdf_part{i}"] = e
        row += 1

        # 전화번호 3분할
        ttk.Label(f, text="전화번호").grid(row=row, column=0, sticky="W", padx=10, pady=5)
        sub3 = ttk.Frame(f)
        sub3.grid(row=row, column=1, sticky="EW", padx=10, pady=5)
        for i, width in enumerate((5,6,6), start=1):
            e = ttk.Entry(sub3, width=width)
            val = self.company_info.get(f"phone_pdf_part{i}", "")
            if val:
                e.insert(0, val)
            e.pack(side="left", padx=5)
            self.entries[f"phone_pdf_part{i}"] = e
        row += 1

        # 계약서 담당자 전화번호
        row = self._entry(f, row, "계약서 담당자 전화번호", "phone_pdf_emp")

        # 기타 입력
        for label, key in [
            ("팩스번호", "company_fax"),
            ("전자우편주소", "company_email"),
            ("대표자명", "ceo_business"),
            ("결제사명", "pay_company"),
            ("결제자명", "payer_business"),
            ("납부자 전화번호", "payer_phone"),
            ("납부 금액", "amount"),
            ("결제번호", "payment_number"),
        ]:
            row = self._entry(f, row, label, key)
        # ───────────────────── 여기부터 추가 ─────────────────────
        # 납부일(DateEntry)  ← 변수명: payment_date
        row = self._entry(f, row, "납부일(1 ~ 31일)", "payment_date")

        # 수납목적(텍스트)    ← 변수명: edit_purpose
        row = self._entry(f, row, "수납목적", "edit_purpose")
        # ───────────────────── 여기까지 추가 ─────────────────────

        # 사무처리 시작일
        row = self._date_entry(f, row, "사무처리 시작일", "start_date")
        # 결제방법 (콤보박스만)
        row = self._payment_method(f, row)
        # 유효기간(월/년)
        row = self._validity_row(f, row)
        # 작성일자
        row = self._date_entry(f, row, "작성일자", "date_pdf")

    def _entry(self, parent, row, label, key):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="W", padx=10, pady=5)
        e = ttk.Entry(parent)

        # ← 이 부분만 교체
        val = self.company_info.get(key, "")
        if val:
            e.insert(0, val)

        e.grid(row=row, column=1, sticky="EW", padx=10, pady=5)
        self.entries[key] = e
        return row + 1


    def _date_entry(self, parent, row, label, key):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="W", padx=10, pady=5)
        de = DateEntry(parent, date_pattern="yyyy-MM-dd", width=18)
        
        if key == "start_date" and all(k in self.company_info for k in ("start_date_year","start_date_month","start_date_day")):
            y = int(self.company_info["start_date_year"])
            m = int(self.company_info["start_date_month"])
            d = int(self.company_info["start_date_day"])
            de.set_date(datetime.date(y, m, d))
        elif key == "date_pdf" and all(k in self.company_info for k in ("date_pdf_year","date_pdf_month","date_pdf_day")):
            y = int(self.company_info["date_pdf_year"])
            m = int(self.company_info["date_pdf_month"])
            d = int(self.company_info["date_pdf_day"])
            de.set_date(datetime.date(y, m, d))
        else:
            de.set_date(datetime.date.today())
        de.grid(row=row, column=1, sticky="W", padx=10, pady=5)
        self.entries[key] = de
        return row + 1

    def _payment_method(self, parent, row):
        ttk.Label(parent, text="결제방법").grid(row=row, column=0, sticky="W", padx=10, pady=5)
        var = tk.StringVar(value=self.company_info.get("payment_method", "은행계좌(CMS)"))
        cmb = ttk.Combobox(parent, textvariable=var, width=34,
                           values=["은행계좌(CMS)", "신용카드", "휴대전화", "유선전화"])
        cmb.grid(row=row, column=1, sticky="W", padx=10, pady=5)
        self.entries["payment_method"] = var
        return row + 1

    def _validity_row(self, parent, row):
        ttk.Label(parent, text="유효기간(월/년)").grid(row=row, column=0, sticky="W", padx=10, pady=5)
        box = ttk.Frame(parent)
        box.grid(row=row, column=1, sticky="W", padx=10, pady=5)
        m = ttk.Entry(box, width=5)
        val_m = self.company_info.get("validity_month", "")
        if val_m:
            m.insert(0, val_m)
        m.pack(side="left", padx=5)
        self.entries["validity_month"] = m
        y = ttk.Entry(box, width=5)
        val_y = self.company_info.get("validity_year", "")
        if val_y:
            y.insert(0, val_y)
        y.pack(side="left", padx=5)
        self.entries["validity_year"] = y
        return row + 1

    def _folder_path_info(self):
        fr = ttk.Frame(self.frame)
        fr.grid(row=3, column=0, padx=20, pady=(0,10), sticky="EW")
        ttk.Label(fr, text="업체폴더 생성경로:").pack(anchor="w")
        ttk.Label(fr, textvariable=self.folder_var).pack(anchor="w")

    def _bottom_buttons(self):
        fr = ttk.Frame(self.right_col)            # ← 부모를 right_col 로
        fr.pack(anchor="n")                       # 맨 위에 붙이기

        ttk.Button(fr, text="메인 화면", command=self.go_back)\
            .pack(fill="x", pady=(0, 8), ipadx=10, ipady=5)
        ttk.Button(fr, text="초기화", command=self.reset_form)\
            .pack(fill="x", pady=(0, 8), ipadx=10, ipady=5)
        ttk.Button(fr, text="입력완료", command=self.save_pdf_data)\
            .pack(fill="x",               ipadx=10, ipady=5)
        
        ttk.Frame(self.right_col, height=30).pack(fill="x")

    def reset_form(self):
        # 입력 필드 초기화
        for widget in self.entries.values():
            if isinstance(widget, DateEntry):
                widget.set_date(datetime.date.today())
            else:
                widget. delete(0, tk.END)
        # 체크박스, 문서 선택 초기화
        self.use_stamp_var.set(True)
        for var in self.doc_vars.values():
            var.set(0)
        self._update_stamp_preview()

    def _build_stamp_preview(self):
        pf = ttk.LabelFrame(self.right_col, text="인감", style="TFrame")
        pf.pack(anchor="n")              # 버튼 바로 아래로
        self._preview_img_label = ttk.Label(pf)
        self._preview_img_label.pack(padx=10, pady=(10,5))
        ttk.Label(pf, text="대표자명 입력시 도장생성", font=("NanumGothic", 10)).pack(pady=(0,10))
        # 인감 날인 토글 버튼
        tk.Checkbutton(
            pf,
            text="인감 날인",
            variable=self.use_stamp_var,
            font=("NanumGothic", 14),
            indicatoron=False,
            padx=5, pady=5
        ).pack(pady=(0,10))
        self._update_stamp_preview()

    def _update_stamp_preview(self, event=None):
        """대표자명 입력 시, PDF에 들어갈 것과 동일한 도장 이미지를 미리보기로 표시"""
        ceo = self.entries.get("ceo_business", tk.Entry()).get().strip()

        # ① 빈 입력이면 미리보기 비우고 종료
        if not ceo:
            self._preview_img_label.config(image="")
            self._preview_img_label.image = None
            return

        # ② make_stamp_image()로 PNG 생성 (PDF와 동일 로직)
        path = make_stamp_image(ceo, self.STAMP_FONT)

        # ③ Tk 이미지로 변환 후 레이블에 표시
        img = Image.open(path)
        tk_img = ImageTk.PhotoImage(img)
        self._preview_img_label.config(image=tk_img)
        self._preview_img_label.image = tk_img


    def save_pdf_data(self):
        data: dict[str,str] = {}
        for k, w in self.entries.items():
            if isinstance(w, DateEntry):
                d = w.get_date()
                data[f"{k}_year"] = str(d.year)
                data[f"{k}_month"] = f"{d.month:02d}"
                data[f"{k}_day"] = f"{d.day:02d}"
            else:
                data[k] = w.get().strip()
        # 인감 날인 여부 추가
        data["use_stamp"] = self.use_stamp_var.get()

        # 1) config.json에서 저장된 값을 로드
        merged = load_company_info(self.company)
        # 2) 화면 입력값(data)으로 덮어쓰기
        merged.update(data)

        if merged.get("use_stamp") and merged.get("ceo_business"):
            img_path = make_stamp_image(
                merged["ceo_business"],
                self.STAMP_FONT
            )
            merged["stamp"] = img_path
            for i in range(1, 31):
                merged[f"stamp_{i}"] = img_path     

        # 3) 예외적으로 ceo_id_pdf_part2_1만 생성
        merged["ceo_id_pdf_part2_1"] = merged.get("ceo_id_pdf_part2", "")
        pm = merged.get("payment_method", "")
        m  = {"은행계좌(CMS)":"payment_method_cms",
            "신용카드":"payment_method_card",
            "휴대전화":"payment_method_phone",
            "유선전화":"payment_method_landline"}
        if pm in m:
            merged.update({f"{m[pm]}_{i}":"√" for i in range(1,31)})


        # 3-A) 대표자 주민번호 앞 6자리 → 생년월일
        front6 = merged.get("ceo_id_pdf_part1", "")
        if len(front6) == 6 and front6.isdigit():
            yy, mm, dd = front6[:2], front6[2:4], front6[4:6]

            this_yy = datetime.date.today().year % 100
            yyyy = 2000 + int(yy) if int(yy) <= this_yy else 1900 + int(yy)

            merged["ceo_birth_date"] = f"{yyyy}년{mm}월{dd}일"
        # 3-1) 모든 문자열 필드를 _1~_30까지 복제
        for key, val in list(merged.items()):
            # 이미 번호가 붙은 키나 불리언·딕트 등은 건너뜀
            if any(key.endswith(f"_{i}") for i in range(1, 31)):
                continue
            if not isinstance(val, str) or not val:
                continue
            for i in range(1, 31):
                merged[f"{key}_{i}"] = val
        # config.json에 저장
        save_company_info(self.company, merged)
        # PDF 생성 준비
        root = make_folders(self.folder_var.get(), merged.get("company_name_pdf", ""))
        base = os.path.join(root, "0. 기초자료")
        outsource = os.path.join(base, "사무위탁")

        # ── (A) 업체별 계약서 템플릿 경로 덮어쓰기 ─────────────
        #   self.company == "업체1" 또는 "업체2"
        contract_tpl = os.path.join(
            RESOURCE_PDF_TEMPLATES,
            f"{self.company}_계약서_양식.pdf"
        )
        if os.path.exists(contract_tpl):
            from pdf.pdf_generator import TEMPLATES   # ★ 기존 dict
            TEMPLATES["계약서"] = contract_tpl        #   항목만 교체
        # -------------------------------------------------------------

        created, skipped = [], []
        for doc in self.doc_order:
            if not self.doc_vars[doc].get():
                continue
            tpl = TEMPLATES.get(doc)
            if not tpl or not os.path.exists(tpl):
                skipped.append(doc)
                continue
            filename = f"{merged.get('company_name_pdf', '')}_{doc.replace(' ', '')}.pdf"
            folder = base if doc == "CMS" else outsource
            out_path = os.path.join(folder, filename)
            logging.debug("PDF 생성 %s → %s", doc, out_path)
            generate_pdf_with_template_check(doc, out_path, merged)
            created.append(doc)
        if created:
            msg = f"{merged.get('company_name_pdf', '')} PDF 저장 완료 ({', '.join(created)})"
            if skipped:
                msg += f"\n※ 템플릿 누락: {', '.join(skipped)}"
            messagebox.showinfo("완료", msg)
        else:
            messagebox.showerror("실패", "선택한 문서에 사용할 템플릿이 없습니다.")

    def go_back(self):
        from ui.main_screen import show_main_screen
        root = self.parent.winfo_toplevel()  # ← 먼저 가져와야 함
        self.frame.destroy()
        show_main_screen(root)


