# 파일경로: pdf/pdf_generator.py

import os
import io
import logging
from utils.config import RESOURCE_FONTS, RESOURCE_PDF_TEMPLATES
from tkinter import messagebox
from typing import Dict, List

from pdfrw import PdfReader, PdfWriter, PageMerge, PdfName
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ───────────────────────── 1. 폰트 등록 ─────────────────────────
FONT_PATH = os.path.join(RESOURCE_FONTS, 'NanumGothic.ttf')
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("NanumGothic", FONT_PATH))
    logging.debug(f"NanumGothic 폰트 등록 완료: {FONT_PATH}")
else:
    logging.warning(f"NanumGothic 폰트를 찾을 수 없습니다: {FONT_PATH}")
FONT_PATH_GHB = os.path.join(RESOURCE_FONTS, "GapyeongHanseokbongB.ttf")
if os.path.exists(FONT_PATH_GHB):
    pdfmetrics.registerFont(TTFont("GHB", FONT_PATH_GHB))   # 등록 이름: GHB

from reportlab.lib import colors
STAMP_COLOR = colors.HexColor("#db4b57")

def _draw_vector_stamp(can, rect, text):
    can.saveState()

    llx, lly, urx, ury = rect
    W, H = urx - llx, ury - lly

    scale = min(W / 120, H / 280)
    drawW, drawH = 120 * scale, 280 * scale
    ox = llx
    oy = lly + (H - drawH) / 2
    bw = 8 * scale

    # 1) 테두리 (PNG와 같은 색·굵기)
    can.setLineWidth(bw)
    can.setStrokeColor(STAMP_COLOR)
    can.ellipse(ox + bw / 2, oy + bw / 2,
                ox + drawW - bw / 2, oy + drawH - bw / 2)

    # 2) 글씨
    if text:
        base = (drawH - 2 * bw) / len(text)
        fsize = max(base - 4, 4)                  # 1 pt 더 줄임
        can.setFont("GHB", fsize)
        can.setFillColor(STAMP_COLOR)

        total_h = len(text) * fsize
        y = oy + (drawH - 2 * bw - total_h) / 2 + total_h - fsize + 20*scale
        cx = ox + drawW / 2
        for ch in text:
            tw = pdfmetrics.stringWidth(ch, "GHB", fsize)
            can.drawString(cx - tw / 2, y, ch)
            y -= fsize

    can.restoreState()


# ───────────────────────── 2. 로깅 설정 ─────────────────────────
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ───────────────────────── 3. 템플릿 경로 매핑 ─────────────────────────
TEMPLATE_DIR = RESOURCE_PDF_TEMPLATES
TEMPLATES = {
    "계약서":        os.path.join(TEMPLATE_DIR, "계약서_양식.pdf"),
    "고용 EDI":      os.path.join(TEMPLATE_DIR, "고용_양식.pdf"),
    "건강 EDI":      os.path.join(TEMPLATE_DIR, "건강_양식.pdf"),
    "국민 EDI":      os.path.join(TEMPLATE_DIR, "국민_양식.pdf"),
    "CMS":           os.path.join(TEMPLATE_DIR, "CMS_양식.pdf"),
    "대리인 별지 1": os.path.join(TEMPLATE_DIR, "대리인별지1_양식.pdf"),
    "대리인 별지 2": os.path.join(TEMPLATE_DIR, "대리인별지2_양식.pdf"),
}

# ───────────────────────── 4. 전각→ASCII 키 매핑 ─────────────────────────
def _alt_key(field_name: str) -> str | None:
    if field_name.startswith("ｃｅｏ＿"):
        return "ceo_business"
    if field_name.startswith("ｐａｙｅｒ＿"):
        return "payer_business"
    return None

# ───────────────────────── 5. 페이지별 필드 좌표 추출 ─────────────────────────
def extract_field_rectangles(template_path: str) -> Dict[int, Dict[str, List[List[float]]]]:
    """
    { page_index: { field_name: [ [llx,lly,urx,ury], ... ], ... }, ... }
    """
    reader = PdfReader(template_path)
    page_map: Dict[int, Dict[str, List[List[float]]]] = {}
    for pidx, page in enumerate(reader.pages):
        annots = page.get(PdfName.Annots) or []
        fld_map: Dict[str, List[List[float]]] = {}
        for annot in annots:
            name = annot.get('/T')
            box  = annot.get('/Rect')
            if not name or not box:
                continue
            key = name.strip().strip('()')
            coords = [float(v) for v in box]
            fld_map.setdefault(key, []).append(coords)
            logging.debug(f"[extract] page{pidx} {key} {coords}")
        page_map[pidx] = fld_map
    return page_map

# ───────────────────────── 6. 멀티페이지 오버레이 생성 ─────────────────────────
def generate_overlay(template_path: str, data: dict) -> io.BytesIO:
    rects_by_page = extract_field_rectangles(template_path)
    reader = PdfReader(template_path)
    num_pages = len(reader.pages)

    buf = io.BytesIO()
    can = canvas.Canvas(buf, pagesize=A4)

    for pidx in range(num_pages):
        rects_map = rects_by_page.get(pidx, {})

        # ── (A) 회사 고정 PNG 인감  ───────────────────────────
        if data.get("use_edit_stamp", True):        # ← 키 없으면 True
            for key, rect_list in rects_map.items():
                if key.startswith("edit_stamp"):
                    for rect in rect_list:
                        llx, lly, urx, ury = (rect[0] if len(rect)==1 else rect)
                        w, h = urx - llx, ury - lly
                        img_path = data.get(key) or data.get("edit_stamp")
                        if img_path and os.path.exists(img_path):
                            can.drawImage(img_path, llx, lly, width=w, height=h,
                                        preserveAspectRatio=True, mask='auto')

        # ── (B) 대표자 도장 PNG(단일 stamp 필드) ────────────────
        if data.get("use_stamp"):
            for rect in rects_map.get("stamp", []):
                llx, lly, urx, ury = (rect[0] if len(rect)==1 else rect)
                w, h = urx - llx, ury - lly
                img_path = data.get("stamp")
                if img_path and os.path.exists(img_path):
                    can.drawImage(img_path, llx, lly, width=w, height=h,
                                preserveAspectRatio=True, mask='auto')


        # 2) 대표자 벡터 도장(stamp_1~stamp_30) ─ use_stamp 플래그
        if data.get("use_stamp"):
            for i in range(1, 31):
                key = f"stamp_{i}"
                text = data.get("ceo_business", "")        # 대표자명
                for rect in rects_map.get(key, []):
                    if len(rect) == 1 and isinstance(rect[0], list):
                        rect = rect[0]
                    if len(rect) == 4 and text:
                        _draw_vector_stamp(can, rect, text)

        # 3) 텍스트 필드
        split_keys = {
            "phone_pdf_part1","phone_pdf_part2","phone_pdf_part3",
            "ceo_id_pdf_part1",
            "business_id_pdf_part1","business_id_pdf_part2","business_id_pdf_part3",
        }

        for key, rect_list in rects_map.items():
            # 텍스트 필드 처리 시 'stamp', 'stamp_*', 'edit_stamp*' 건너뜀
            if key == "stamp" or key.startswith("stamp_") or key.startswith("edit_stamp"):
                continue
            val = str(data.get(key,"")).strip()
            if not val:
                alt = _alt_key(key)
                if alt:
                    val = str(data.get(alt,"")).strip()
            if not val:
                continue
            if key == "ceo_id_pdf_part2_1":
                val = val[:1]

            for rect in rect_list:
                if len(rect)==1 and isinstance(rect[0], list):
                    rect = rect[0]
                if len(rect)!=4:
                    continue
                llx,lly,urx,ury = rect
                fw,fh = urx-llx, ury-lly

                pt = max(int(fh*0.8),4)
                while pt>4 and pdfmetrics.stringWidth(val,"NanumGothic",pt) > fw*0.95:
                    pt -= 1
                can.setFont("NanumGothic", pt)

                if key in split_keys:
                    n = len(val)
                    if n>1:
                        widths = [pdfmetrics.stringWidth(ch,"NanumGothic",pt) for ch in val]
                        extra = fw - sum(widths)
                        gap = extra/(n-1)
                        y = lly + (fh-pt)/2 + pt*0.25
                        x = llx
                        for w_, ch in zip(widths, val):
                            can.drawString(x, y, ch)
                            x += w_ + gap
                    else:
                        tw = pdfmetrics.stringWidth(val,"NanumGothic",pt)
                        x = llx + (fw-tw)/2
                        y = lly + (fh-pt)/2 + pt*0.25
                        can.drawString(x, y, val)
                else:
                    tw = pdfmetrics.stringWidth(val,"NanumGothic",pt)
                    x = llx + (fw-tw)/2
                    y = lly + (fh-pt)/2 + pt*0.25
                    can.drawString(x, y, val)

        # 다음 페이지로 이동
        if pidx < num_pages - 1:
            can.showPage()

    can.save()
    buf.seek(0)
    return buf

# ───────────────────────── 7. 필드 제거(평면화) ─────────────────────────
def _strip_fields(page):
    if PdfName.Annots in page:
        keep = {'ksycp','USER'}
        page[PdfName.Annots] = [
            a for a in page[PdfName.Annots]
            if not a.get('/T') or a.get('/T').strip().strip('()') in keep
        ]
    return page

# ───────────────────────── 8. 템플릿+오버레이 병합 저장 ─────────────────────────
def fill_pdf_overlay(doc_type: str, data: dict, out_path: str):
    norm = doc_type.replace('\u00A0',' ').strip()
    tpl  = TEMPLATES.get(norm)
    if not tpl or not os.path.exists(tpl):
        logging.error(f"템플릿 없음: {doc_type}")
        return

    template_pdf = PdfReader(tpl)
    overlay_pdf  = PdfReader(generate_overlay(tpl, data))

    # 모든 페이지에 대해 병합
    for pidx, pg in enumerate(template_pdf.pages):
        if pidx < len(overlay_pdf.pages):
            PageMerge(pg).add(overlay_pdf.pages[pidx], prepend=False).render()

    writer = PdfWriter()
    for pg in template_pdf.pages:
        writer.addpage(_strip_fields(pg))

    with open(out_path, 'wb') as f:
        writer.write(f)
    logging.info(f"PDF 저장 완료: {out_path}")

# ───────────────────────── 9. 호출용 ─────────────────────────
def generate_pdf_with_template_check(doc_type: str, out_path: str, data: dict):
    logging.debug(f"PDF 생성 요청 {doc_type} → {out_path}")
    if os.path.exists(out_path):
        if not messagebox.askyesno("확인", f"'{os.path.basename(out_path)}'을(를) 덮어쓸까요?"):
            return
    fill_pdf_overlay(doc_type, data, out_path)
