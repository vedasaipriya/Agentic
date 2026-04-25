"""
Pipeline orchestrator.
Coordinates the full workflow: PDF → Extract → Clean → Clarify → Generate Test Data.
"""

import json
import time
from pathlib import Path

from app.config import OUTPUT_DIR
from app.pdf_parser.extractor import extract_text_from_pdf
from app.pdf_parser.cleaner import clean_text
from app.agents.clarifier import ClarificationAgent
from app.agents.test_generator import TestDataGeneratorAgent
from app.models.schemas import PipelineResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_pipeline(pdf_path: str | Path) -> PipelineResult:
    """
    Execute the complete multi-agent QA pipeline.

    Steps:
        1. Extract text from PDF (preserving structure)
        2. Clean text (remove Confluence noise)
        3. Run Requirement Clarification Agent
        4. Run Test Data Generator Agent
        5. Assemble and save results

    Args:
        pdf_path: Path to the uploaded PDF file

    Returns:
        PipelineResult with all agent outputs

    Raises:
        FileNotFoundError: If PDF doesn't exist
        ValueError: If PDF extraction fails
        RuntimeError: If agents fail after retries
    """
    pdf_path = Path(pdf_path)
    start_time = time.time()

    logger.info("=" * 60)
    logger.info(f"PIPELINE START: {pdf_path.name}")
    logger.info("=" * 60)

    # ── Step 1: Extract text from PDF ──────────────────
    logger.info("Step 1/4: Extracting text from PDF...")
    raw_text = extract_text_from_pdf(pdf_path)

    # ── Step 2: Clean text ─────────────────────────────
    logger.info("Step 2/4: Cleaning extracted text...")
    cleaned_text = clean_text(raw_text)

    if not cleaned_text:
        raise ValueError("No usable text could be extracted from the PDF")

    # ── Step 3: Run Clarification Agent ────────────────
    logger.info("Step 3/4: Running Requirement Clarification Agent...")
    clarifier = ClarificationAgent()
    clarification_result = clarifier.analyze(cleaned_text)

    # ── Step 4: Run Test Data Generator Agent ──────────
    logger.info("Step 4/4: Running Test Data Generator Agent...")
    test_gen = TestDataGeneratorAgent()
    test_data_result = test_gen.generate(cleaned_text, clarification_result)

    # ── Assemble Results ───────────────────────────────
    elapsed = time.time() - start_time

    pipeline_result = PipelineResult(
        pdf_filename=pdf_path.name,
        extracted_text=cleaned_text,
        clarification=clarification_result,
        test_data=test_data_result,
        processing_time_seconds=round(elapsed, 2),
    )

    # ── Save to output directory ───────────────────────
    output_filename = f"{pdf_path.stem}_analysis.json"
    output_path = OUTPUT_DIR / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pipeline_result.model_dump_json(indent=2))

    logger.info(f"Results saved to: {output_path}")
    logger.info("=" * 60)
    logger.info(f"PIPELINE COMPLETE in {elapsed:.2f}s")
    logger.info("=" * 60)

    return pipeline_result
