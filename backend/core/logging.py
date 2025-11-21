"""Configuração de logging estruturado para o backend FastAPI."""

import logging
from logging.config import dictConfig

from .config import get_settings


def configure_logging() -> logging.Logger:
    """Configura logging padronizado e retorna logger raiz do projeto."""
    settings = get_settings()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": settings.log_level.upper(),
                }
            },
            "root": {
                "handlers": ["console"],
                "level": settings.log_level.upper(),
            },
        }
    )
    logger = logging.getLogger("hospicast")
    logger.debug("Logging configurado com nível %s", settings.log_level.upper())
    return logger




