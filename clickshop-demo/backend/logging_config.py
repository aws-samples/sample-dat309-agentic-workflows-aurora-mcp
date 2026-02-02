"""
Structured logging configuration for ClickShop backend.

Provides JSON-formatted logs for production and readable logs for development.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "phase"):
            log_entry["phase"] = record.phase
        if hasattr(record, "query"):
            log_entry["query"] = record.query
        if hasattr(record, "results_count"):
            log_entry["results_count"] = record.results_count
        if hasattr(record, "execution_time_ms"):
            log_entry["execution_time_ms"] = record.execution_time_ms
        if hasattr(record, "product_id"):
            log_entry["product_id"] = record.product_id
        if hasattr(record, "order_id"):
            log_entry["order_id"] = record.order_id
        if hasattr(record, "error"):
            log_entry["error"] = record.error

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class ReadableFormatter(logging.Formatter):
    """Human-readable formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]

        # Build extra info string
        extras = []
        if hasattr(record, "phase"):
            extras.append(f"phase={record.phase}")
        if hasattr(record, "query"):
            query = record.query[:50] + "..." if len(record.query) > 50 else record.query
            extras.append(f'query="{query}"')
        if hasattr(record, "results_count"):
            extras.append(f"results={record.results_count}")
        if hasattr(record, "execution_time_ms"):
            extras.append(f"time={record.execution_time_ms}ms")

        extra_str = f" [{', '.join(extras)}]" if extras else ""

        return f"{color}[{record.levelname}]{reset} {record.name}: {record.getMessage()}{extra_str}"


def setup_logging(debug: bool = False, json_output: bool = False) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        debug: Enable debug level logging
        json_output: Use JSON format (for production)

    Returns:
        Configured root logger
    """
    logger = logging.getLogger("clickshop")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)

    # Set formatter based on mode
    if json_output:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(ReadableFormatter())

    logger.addHandler(handler)

    return logger


# Create default logger
logger = setup_logging()


def log_search(
    phase: int,
    query: str,
    results_count: int,
    execution_time_ms: int,
    search_type: str = "keyword"
) -> None:
    """Log a search operation."""
    logger.info(
        f"Search completed: {search_type}",
        extra={
            "phase": phase,
            "query": query,
            "results_count": results_count,
            "execution_time_ms": execution_time_ms,
        }
    )


def log_order(
    phase: int,
    product_id: str,
    order_id: Optional[str] = None,
    total: Optional[float] = None,
    status: str = "started",
    error: Optional[str] = None
) -> None:
    """Log an order operation."""
    extra: Dict[str, Any] = {
        "phase": phase,
        "product_id": product_id,
    }
    if order_id:
        extra["order_id"] = order_id
    if total is not None:
        extra["total"] = total
    if error:
        extra["error"] = error
        logger.error(f"Order {status}", extra=extra)
    else:
        logger.info(f"Order {status}", extra=extra)


def log_error(context: str, error: str, **kwargs: Any) -> None:
    """Log an error with context."""
    logger.error(
        f"Error in {context}: {error}",
        extra={"error": error, "context": context, **kwargs}
    )
