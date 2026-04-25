"""
Structured logging module.
Provides file + console logging with timestamps and module context.
"""

import logging
import sys
from pathlib import Path

from app.config import LOG_DIR


def get_logger(name: str) -> logging.Logger:
    """
    Create a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured logging.Logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Formatter ──────────────────────────────────
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Console Handler (INFO+) ───────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── File Handler (DEBUG+) ─────────────────────
    log_file = LOG_DIR / "agentic.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
