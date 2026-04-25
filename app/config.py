"""
Application configuration.
Centralized settings for the multi-agent QA assistant.
"""

import os
from pathlib import Path


# ── Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
UPLOAD_DIR = BASE_DIR / "uploads"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ── Ollama Configuration ──────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# ── Agent Configuration ───────────────────────────────
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "300"))

# ── Application ──────────────────────────────────────
APP_TITLE = "Agentic — Multi-Agent QA Assistant"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Local, privacy-safe multi-agent system for requirement analysis and test data generation"
