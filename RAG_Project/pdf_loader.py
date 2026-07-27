"""
Extracts text from a PDF file using pypdf.
"""

from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Read every page of a PDF and return all text as one string.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Full text extracted from the PDF.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages_text = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages_text.append(text)

    full_text = "\n\n".join(pages_text)

    if not full_text.strip():
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It may be a scanned/image-only PDF."
        )

    return full_text
