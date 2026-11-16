
from pathlib import Path

import pymupdf


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract text from a PDF and preserve page numbers.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    pages = []

    with pymupdf.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append(
                    f"[PAGE {page_number}]\n{text}"
                )

    extracted_text = "\n\n".join(pages)

    if not extracted_text.strip():
        raise ValueError(
            "No readable text found. The PDF may be scanned."
        )

    return extracted_text
