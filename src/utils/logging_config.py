"""
AeroSense AI — Logging Configuration
Provides structured, coloured console logging and rotating file logging.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

# Try coloured output; fall back gracefully
try:
    import colorlog
    _HAS_COLORLOG = True
except ImportError:
    _HAS_COLORLOG = False

def setup_logging(
    level: str = "INFO",
    log_dir: Path | None = None,
    app_name: str = "aerosense",
) -> logging.Logger:
    """Configure root logger with console + optional rotating file handler."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Avoid adding duplicate handlers on Streamlit reruns
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    logging.getLogger("tornado").setLevel(logging.WARNING)
    if root.handlers:
        return logging.getLogger(app_name)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Console handler
    if _HAS_COLORLOG:
        colour_fmt = (
            "%(log_color)s%(asctime)s | %(levelname)-8s%(reset)s | "
            "%(cyan)s%(name)s%(reset)s | %(message)s"
        )
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            colorlog.ColoredFormatter(colour_fmt, datefmt=datefmt)
        )
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    root.addHandler(console_handler)

    # File handler (optional)
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            log_dir / f"{app_name}.log",
            maxBytes=5 * 1024 * 1024,   # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        fh.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
        root.addHandler(fh)

    return logging.getLogger(app_name)

def get_logger(name: str) -> logging.Logger:
    """Return a named child logger."""
    return logging.getLogger(name)
