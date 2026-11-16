
from app.tools.pdf_reader import extract_pdf_text

PDF_PATH = r"D:\PaperPilot-AI\data\uploads\ReAct.pdf"

text = extract_pdf_text(PDF_PATH)

print("\n========== PDF EXTRACTION TEST ==========\n")
print(text[:3000])
print("\n========== EXTRACTION SUCCESSFUL ==========")
