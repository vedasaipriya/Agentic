"""
Text cleaning module.
Removes Confluence-specific noise and normalizes extracted text
for optimal LLM processing.
"""

import re

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Patterns commonly found in Confluence-exported PDFs
NOISE_PATTERNS = [
    # Confluence footer
    r"(?i)powered\s+by\s+(atlassian\s+)?confluence",
    r"(?i)created\s+with\s+confluence",
    # Page numbers
    r"(?m)^\s*page\s+\d+\s*(of\s+\d+)?\s*$",
    r"(?m)^\s*\d+\s*$",  # Standalone page numbers
    # Confluence metadata lines
    r"(?i)last\s+modified\s*:.*$",
    r"(?i)created\s+by\s*:.*$",
    r"(?i)space\s*:.*$",
    # Export artifacts
    r"(?i)exported\s+(from|on)\s+.*$",
    # URLs that are just navigation artifacts
    r"(?m)^https?://[^\s]+confluence[^\s]*$",
    # Repeated separator lines (more than 3 dashes)
    r"(?m)^-{5,}\s*$",
    # Empty markdown links
    r"\[[\s]*\]\([\s]*\)",
]


def clean_text(raw_text: str) -> str:
    """
    Clean extracted PDF text by removing Confluence noise and normalizing whitespace.

    Args:
        raw_text: Raw Markdown text from the PDF extractor

    Returns:
        Cleaned text ready for agent processing
    """
    if not raw_text or not raw_text.strip():
        logger.warning("Received empty text for cleaning")
        return ""

    logger.info(f"Cleaning text: {len(raw_text)} characters input")
    text = raw_text

    # Apply noise removal patterns
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.MULTILINE)

    # Normalize whitespace
    # Collapse multiple blank lines into at most two
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    # Remove trailing whitespace on each line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # Remove leading/trailing whitespace from entire document
    text = text.strip()

    # Fix broken lines (lines that end mid-sentence and continue on next line)
    # Only join lines where the first line doesn't end with a block-level marker
    text = re.sub(
        r"(?<=[a-z,;])\n(?=[a-z])",
        " ",
        text
    )

    cleaned_length = len(text)
    reduction = ((len(raw_text) - cleaned_length) / len(raw_text)) * 100
    logger.info(
        f"Cleaning complete: {cleaned_length} characters output "
        f"({reduction:.1f}% noise removed)"
    )

    return text


def extract_sections(text: str) -> list[dict]:
    """
    Split cleaned text into logical sections based on Markdown headings.

    Args:
        text: Cleaned Markdown text

    Returns:
        List of dicts with 'heading' and 'content' keys
    """
    sections = []
    # Split on markdown headings (# through ####)
    parts = re.split(r"(?m)^(#{1,4}\s+.+)$", text)

    current_heading = "Introduction"
    current_content = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if re.match(r"^#{1,4}\s+", part):
            # Save previous section
            if current_content:
                sections.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content).strip()
                })
            current_heading = re.sub(r"^#+\s*", "", part)
            current_content = []
        else:
            current_content.append(part)

    # Save last section
    if current_content:
        sections.append({
            "heading": current_heading,
            "content": "\n".join(current_content).strip()
        })

    logger.info(f"Extracted {len(sections)} sections from text")
    return sections
