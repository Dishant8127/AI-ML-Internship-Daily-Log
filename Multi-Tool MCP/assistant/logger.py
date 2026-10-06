"""Logging setup for the Multi-Tool MCP AI Assistant."""

import logging
import os
import sys
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_FILE = LOG_DIR / "assistant.log"

_FORMAT = "%(asctime)s | %(levelname)-7s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def setup_logger(level: str | None = None) -> logging.Logger:
    """Create (once) a logger that writes to logs/assistant.log and to the console."""
    logger = logging.getLogger("mcp_assistant")
    if logger.handlers:
        return logger

    logger.setLevel((level or os.environ.get("LOG_LEVEL", "INFO")).upper())
    formatter = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("mcp_assistant")
