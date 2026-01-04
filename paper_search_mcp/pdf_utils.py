"""PDF text extraction utilities with pdftotext (poppler) support."""

import subprocess
import shutil
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file.

    Uses pdftotext (poppler) for best quality extraction of academic papers,
    with fallback to PyPDF2 if pdftotext is not available.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text content
    """
    # Try pdftotext first (better quality for academic papers)
    text = _extract_with_pdftotext(pdf_path)
    if text is not None:
        return text

    # Fallback to PyPDF2
    return _extract_with_pypdf(pdf_path)


def _extract_with_pdftotext(pdf_path: str) -> Optional[str]:
    """Extract text using pdftotext (poppler).

    Returns None if pdftotext is not available.
    """
    if not shutil.which('pdftotext'):
        return None

    try:
        # -layout preserves the original physical layout
        # -enc UTF-8 ensures proper encoding
        result = subprocess.run(
            ['pdftotext', '-layout', '-enc', 'UTF-8', pdf_path, '-'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return None


def _extract_with_pypdf(pdf_path: str) -> str:
    """Extract text using PyPDF2 as fallback."""
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader

    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {e}"
