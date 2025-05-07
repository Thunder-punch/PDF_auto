import os
from pdf.pdf_generator import generate_pdf_with_template_check
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# 폰트 경로 (NanumGothic)
FONT_PATH = r"C:\Users\texcl\HaelfriendsApp\resources\fonts\NanumGothic.ttf"

# 폰트 등록
pdfmetrics.registerFont(TTFont('NanumGothic', FONT_PATH))

# PDF 저장 경로
OUTPUT_DIR = r"C:\Users\texcl\HaelfriendsApp\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 공통 날짜 값
today = {
    "date_pdf_year": "2025",
    "date_pdf_month": "04",
    "date_pdf_day": "16"
}

# 각 문서 유형별 데이터 예시
pdf_data_map = {
    "CMS": {
        "ceo_business": "하엘프랜즈",
        "payer_business": "고객사"
    },
    "건강": {
        **today,
        "business_id_pdf_part1": "123",
        "business_id_pdf_part2": "45",
        "business_id_pdf_part3": "67890",
        "ceo_name": "김대표",
        "company_name": "하엘프랜즈",
        "company_name_pdf": "하엘프랜즈",
        "ceo_id_pdf_part1": "900101",
        "ceo_id_pdf_part2": "1234567",
        "company_address": "서울시 강남구",
        "manage_id_pdf": "MNG001",
    },
    "계약서": {
        "ceo_name": "김대표",
        "company_name": "하엘프랜즈",
        "contract_date": "2025-04-16"
    },
    "고용": {
        **today,
        "ceo_name": "김대표",
        "company_name": "하엘프랜즈",
        "company_address_pdf": "서울시 강남구",
        "ceo_business": "하엘프랜즈",
        "business_type": "AI 솔루션 개발",
        "num_employees": "10",
        "phone_pdf_part1": "010",
        "phone_pdf_part2": "1234",
        "phone_pdf_part3": "5678",
        "manage_id": "MNG001",
    },
    "국민": {
        **today,
        "ceo_name": "김대표",
        "company_name_pdf": "하엘프랜즈",
        "company_address_pdf": "서울시 강남구",
        "business_id_pdf_part1": "123",
        "business_id_pdf_part2": "45",
        "business_id_pdf_part3": "67890",
        "corporate_id_pdf": "CORP001",
        "manage_id_pdf": "MNG002",
    },
    "대리인별지1": {
        **today,
        "company_name_pdf": "하엘프랜즈",
        "company_address_pdf": "서울시 강남구",
        "ceo_id_pdf_part1": "900101",
        "ceo_id_pdf_part2": "1234567",
        "start_date": "2025-04-16",
        "ceo_business": "하엘프랜즈",
        "phone_pdf_part1": "02",
        "phone_pdf_part2": "123",
        "phone_pdf_part3": "4567",
    },
    "대리인별지2": {
        **today,
        "company_name_pdf": "하엘프랜즈",
        "company_address_pdf": "서울시 강남구",
        "ceo_id_pdf_part1": "900101",
        "ceo_id_pdf_part2": "1234567",
        "ceo_business": "하엘프랜즈",
        "manage_id_pdf": "MNG003",
    },
}

# 일괄 생성
for doc_type, data_dict in pdf_data_map.items():
    output_path = os.path.join(OUTPUT_DIR, f"{doc_type}_출력본.pdf")
    print(f"▶ {doc_type} 생성 중...")
    generate_pdf_with_template_check(doc_type, output_path, data_dict)
