import logging
import os
import sys
from typing import Union

from colorlog import ColoredFormatter
from google.cloud.logging import Client as LoggingClient

#####


def get_logger_by_environment(is_prod: bool = False) -> logging.Logger:
    application_logger = logging.getLogger(__name__)
    application_logger.propagate = False

    if application_logger.hasHandlers():
        application_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if is_prod:
        client = LoggingClient()
        # This attaches a handler that sends logs directly to GCP with correct severity
        client.setup_logging()
        application_logger.setLevel(logging.INFO)

        return application_logger

    # Set up colored logging for non-production environments
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        style="%",
    )
    application_logger.setLevel(logging.DEBUG if os.environ.get("DEBUG") == "true" else logging.INFO)

    handler.setFormatter(formatter)
    application_logger.addHandler(handler)

    return application_logger


application_logger = get_logger_by_environment(is_prod=os.environ.get("STAGE") == "production")
