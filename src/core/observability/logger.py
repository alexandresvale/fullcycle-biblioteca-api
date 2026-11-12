import sys
from typing import Any

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    """Configura o structlog para emissão de logs estruturados em JSON."""
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger() -> Any:
    """Retorna a instância configurada do structlog."""
    return structlog.get_logger()
