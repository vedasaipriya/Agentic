"""
FastAPI application — main entry point.
Serves the web UI and provides the API for PDF analysis.
"""

import shutil
from pathlib import Path

import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import (
    APP_TITLE, APP_VERSION, APP_DESCRIPTION,
    UPLOAD_DIR, OLLAMA_BASE_URL, OLLAMA_MODEL,
)
from app.orchestrator import run_pipeline
from app.models.schemas import PipelineResult, HealthStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── FastAPI App ────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

# ── Mount static files ────────────────────────────────
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


# ── Routes ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main dashboard UI."""
    index_path = frontend_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return index_path.read_text(encoding="utf-8")


@app.get("/api/health", response_model=HealthStatus)
async def health_check():
    """Check system health including Ollama connectivity."""
    ollama_connected = False
    model_available = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Ollama is running
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                ollama_connected = True
                # Check if the required model is available
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                model_available = any(
                    OLLAMA_MODEL in name for name in model_names
                )
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")

    status = "healthy" if (ollama_connected and model_available) else "degraded"

    return HealthStatus(
        status=status,
        ollama_connected=ollama_connected,
        model_available=model_available,
        model_name=OLLAMA_MODEL,
    )


@app.post("/api/analyze", response_model=PipelineResult)
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF and run the full multi-agent analysis pipeline.

    Returns structured JSON with clarification results and test data.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    logger.info(f"Received PDF upload: {file.filename}")

    # Save uploaded file
    upload_path = UPLOAD_DIR / file.filename
    try:
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"File saved: {upload_path} ({len(content)} bytes)")
    except Exception as e:
        logger.error(f"Failed to save upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    # Run the pipeline
    try:
        result = run_pipeline(upload_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline failed: {str(e)}"
        )
    finally:
        # Clean up uploaded file
        if upload_path.exists():
            upload_path.unlink()
