import logging
import sys
from logging.config import dictConfig


def setup_logging(log_level: str = "INFO"):
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": (
                        "%(asctime)s | %(levelname)s | "
                        "%(name)s | %(message)s"
                    )
                },
                "access": {
                    "format": (
                        "%(asctime)s | ACCESS | "
                        "%(client_addr)s | %(request_line)s | %(status_code)s"
                    )
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                },
            },
            "root": {
                "level": log_level,
                "handlers": ["default"],
            },
        }
    )
