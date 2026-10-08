"""# Logging.

It initializes the logging.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(level: str = "INFO") -> None:
    """Set up logging to stdout and a rotating log file."""
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=100 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=level.upper(),
        handlers=[file_handler, console_handler],
        force=True,
    )
