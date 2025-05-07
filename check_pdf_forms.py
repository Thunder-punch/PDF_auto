import os
from PyPDF2 import PdfReader
from PyPDF2.generic import IndirectObject

pdf_folder = r"C:\Users\texcl\HaelfriendsApp\resources\pdf_templates"
results = []

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(pdf_folder, filename)
        try:
            reader = PdfReader(file_path)
            root = reader.trailer.get("/Root", {})

            if isinstance(root, IndirectObject):
                root = root.get_object()

            acroform = root.get("/AcroForm", None)

            if isinstance(acroform, IndirectObject):
                acroform = acroform.get_object()

            if acroform:
                if "/XFA" in acroform:
                    result = f"❌ {filename}: XFA 폼 기반"
                else:
                    result = f"✅ {filename}: AcroForm 기반"
            else:
                result = f"⚠️ {filename}: AcroForm 정보 없음"

        except Exception as e:
            result = f"⚠️ {filename}: 읽기 오류 발생 ({str(e)})"

        results.append(result)

print("\n📝 PDF 폼 형식 검사 결과:")
for r in results:
    print(r)
