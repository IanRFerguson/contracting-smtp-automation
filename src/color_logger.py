import logging
import os
import sys
from typing import Union

from colorlog import ColoredFormatter
from google.cloud.logging import Client as LoggingClient

#####


def get_logger_by_environment(
    is_prod: bool = False,
) -> Union[logging.Logger, LoggingClient]:
    """
    If we're running in production, we'll persist the logs
    to Google Cloud Logging. Otherwise, we'll log to stdout with
    a nice color logger.
    """

    if is_prod:
        logging_client = LoggingClient()
        logging_client.setup_logging()
        scrub_logger = logging.getLogger("google.cloud.logging")
        scrub_logger.setLevel("INFO")

        return scrub_logger

    scrub_logger = logging.getLogger(__name__)
    _handler = logging.StreamHandler(sys.stdout)

    _formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",  # Example with background color
        },
        style="%",
    )

    _handler.setFormatter(_formatter)
    scrub_logger.addHandler(_handler)
    scrub_logger.setLevel("INFO")

    if os.environ.get("DEBUG") == "true":
        scrub_logger.setLevel("DEBUG")
        scrub_logger.debug("Logging at debug level")

    return scrub_logger


logger = get_logger_by_environment(is_prod=os.environ.get("STAGE") == "production")
