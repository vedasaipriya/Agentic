"""
PDF text extraction module.
Uses pymupdf4llm to extract text while preserving document structure
(headings, bullet points, tables) as Markdown.
"""

import pymupdf4llm
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract text from a PDF file, preserving structure as Markdown.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Markdown-formatted text extracted from the PDF

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the file is not a PDF or extraction fails
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {pdf_path}")

    logger.info(f"Extracting text from: {pdf_path.name}")

    try:
        # pymupdf4llm preserves headings, bullets, and tables as Markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))

        if not md_text or not md_text.strip():
            raise ValueError(f"No text could be extracted from: {pdf_path.name}")

        page_count = md_text.count("-----") + 1  # Rough page estimate
        logger.info(
            f"Extraction complete: {len(md_text)} characters, ~{page_count} pages"
        )

        return md_text

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Failed to extract text from PDF: {e}") from e
