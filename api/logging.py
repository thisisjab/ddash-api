import os
from logging.config import dictConfig
from api.config import settings


def configure_logging() -> None:
    if not os.path.exists(settings.LOGGING_FILE_DIR):
        os.makedirs(settings.LOGGING_FILE_DIR)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                #
                # This is like using:
                # filter = asgi_correlation_id.CorrelationFilter(uuid_length=8, default_value="-")
                #
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": settings.LOGGING_CORRELATION_ID_LENGTH,
                    "default_value": "-",
                }
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s -- %(name)s:%(lineno)d -- %(levelname)s: %(message)s [%(correlation_id)s]",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s  %(correlation_id)s %(msecs)d %(levelname)s %(name)s %(lineno)d %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "filters": ["correlation_id"],
                    "level": "DEBUG",
                    "formatter": "console",
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file",
                    "filters": ["correlation_id"],
                    "level": settings.LOGGING_FILE_LEVEL,
                    "filename": os.path.join(
                        settings.LOGGING_FILE_DIR, settings.LOGGING_FILE_NAME
                    ),
                    "maxBytes": settings.LOGGING_FILE_MAX_BYTES,
                    "backupCount": settings.LOGGING_FILE_BACKUP_COUNT,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "api": {
                    "handlers": ["default", "rotating_file"],
                    "level": settings.LOGGING_LEVEL,
                    "propagate": False,
                },
            },
        }
    )
