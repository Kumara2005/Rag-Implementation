"""
Handles saving uploaded PDF files to the data/ folder.
"""

from pathlib import Path
from config import DATA_DIR


def save_uploaded_pdf(uploaded_file) -> Path:
    """
    Save an uploaded PDF to data/ and return its path.

    Args:
        uploaded_file: A file-like object from Streamlit
                       (has .name and .getbuffer() / .read()).

    Returns:
        Path to the saved PDF file.
    """
    # Always save as uploaded_pdf.pdf for this simple demo
    save_path = DATA_DIR / "uploaded_pdf.pdf"

    # Write bytes to disk
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return save_path


def get_uploaded_pdf_path() -> Path | None:
    """Return the path of the saved PDF if it exists, else None."""
    path = DATA_DIR / "uploaded_pdf.pdf"
    return path if path.exists() else None
