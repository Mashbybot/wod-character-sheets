"""Logging configuration for WoD Character Sheets

Provides structured logging with appropriate levels and formatting for production use.
"""

import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
try:
    LOG_DIR.mkdir(exist_ok=True)
except OSError as e:
    # Fallback to console-only logging if directory creation fails
    print(f"WARNING: Unable to create log directory at {LOG_DIR}: {e}", file=sys.stderr)
    print("Falling back to console-only logging", file=sys.stderr)
    LOG_DIR = None

# Define log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the application

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Always add console handler
    root_logger.addHandler(console_handler)

    # Add file handlers only if LOG_DIR is available
    if LOG_DIR is not None:
        try:
            # File handler for general logs
            file_handler = logging.FileHandler(LOG_DIR / "app.log")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            # File handler for errors
            error_handler = logging.FileHandler(LOG_DIR / "error.log")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)
        except (OSError, PermissionError) as e:
            # Log to console if file handlers fail
            console_handler.stream.write(
                f"WARNING: Unable to create file log handlers: {e}\n"
            )

    # Reduce verbosity of third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the specified module

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
