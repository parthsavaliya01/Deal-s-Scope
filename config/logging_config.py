"""Logging configuration for DealScope.

This module provides a convenience function to configure structured logging to
console and rotating file handlers. It is intentionally non-intrusive; existing
modules may import and call `configure_logging()` at startup.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler


def configure_logging(level: int = logging.INFO, logfile: str = "logs/dealscope.log") -> None:
    """Configure global logging handlers.

    Creates logs directory if missing and sets up a rotating file handler.
    """
    import os

    os.makedirs(os.path.dirname(logfile), exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    root.addHandler(ch)

    # Rotating file handler
    fh = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=5)
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    root.addHandler(fh)
