"""
End-to-end pipeline test.
Tests the full flow from PDF extraction through both agents.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.pdf_parser.extractor import extract_text_from_pdf
from app.pdf_parser.cleaner import clean_text, extract_sections
from app.models.schemas import PipelineResult


def test_pdf_extraction():
    """Test that we can extract text from the sample PDF."""
    sample_pdf = Path(__file__).parent / "sample_requirements.pdf"

    if not sample_pdf.exists():
        print("[!] Sample PDF not found. Generating...")
        from tests.generate_sample_pdf import create_sample_pdf
        create_sample_pdf()

    # Extract
    raw_text = extract_text_from_pdf(sample_pdf)
    assert raw_text, "Extraction returned empty text"
    assert len(raw_text) > 100, f"Extraction too short: {len(raw_text)} chars"
    print(f"[PASS] PDF extraction: {len(raw_text)} characters")

    # Clean
    cleaned = clean_text(raw_text)
    assert cleaned, "Cleaning returned empty text"
    assert "Powered by" not in cleaned, "Confluence noise not removed"
    print(f"[PASS] Text cleaning: {len(cleaned)} characters")

    # Sections
    sections = extract_sections(cleaned)
    assert len(sections) > 0, "No sections extracted"
    print(f"[PASS] Section extraction: {len(sections)} sections")

    for s in sections:
        print(f"   -> {s['heading']}")

    return cleaned


def test_full_pipeline():
    """Test the full pipeline including agents (requires Ollama)."""
    from app.orchestrator import run_pipeline

    sample_pdf = Path(__file__).parent / "sample_requirements.pdf"

    if not sample_pdf.exists():
        from tests.generate_sample_pdf import create_sample_pdf
        create_sample_pdf()

    print("\n>> Running full pipeline...")
    result = run_pipeline(sample_pdf)

    # Validate result
    assert isinstance(result, PipelineResult)
    assert result.pdf_filename == "sample_requirements.pdf"
    assert result.clarification.summary
    assert result.clarification.risk_level in ["low", "medium", "high", "critical"]
    assert len(result.test_data.valid_cases) > 0

    total_tests = (
        len(result.test_data.valid_cases)
        + len(result.test_data.invalid_cases)
        + len(result.test_data.edge_cases)
        + len(result.test_data.boundary_values)
        + len(result.test_data.security_cases)
    )

    print(f"\n[PASS] Pipeline complete in {result.processing_time_seconds}s")
    print(f"   Risk Level: {result.clarification.risk_level}")
    print(f"   Missing Requirements: {len(result.clarification.missing_requirements)}")
    print(f"   Ambiguities: {len(result.clarification.ambiguities)}")
    print(f"   Total Test Cases: {total_tests}")


if __name__ == "__main__":
    print("=" * 50)
    print("AGENTIC - Pipeline Test")
    print("=" * 50)

    # Always run extraction test
    cleaned_text = test_pdf_extraction()

    # Run full pipeline if --full flag is passed
    if "--full" in sys.argv:
        test_full_pipeline()
    else:
        print("\n[TIP] Run with --full to test the complete pipeline (requires Ollama)")
