import logging
import os
import sys
from datetime import datetime, timedelta

# Define project logger
logger = logging.getLogger(__name__)

_handler = logging.StreamHandler(sys.stdout)
_formatter = logging.Formatter("%(levelname)s %(message)s")
_handler.setFormatter(_formatter)

logger.addHandler(_handler)

if os.environ.get("DEBUG", "false") == "true":
    logger.setLevel(level=10)
    logger.debug("** DEBUGGER ACTIVE **")
else:
    logger.setLevel(level=20)


##########


def generate_attachment_naming_convention(days_back: int, client_name: str) -> str:
    """
    Creates the file name that will be attached to the outgoing email

    Example - `FERGUSON_ACLU_hours__2025-01-01__2025-01-13.csv`
    """

    _today = datetime.now()
    _preceding_boundary = _today - timedelta(days=days_back)

    _date_formatted = (
        f"{_preceding_boundary.strftime('%Y-%m-%d')}__{_today.strftime('%Y-%m-%d')}"
    )

    return f"FERGUSON_{client_name.upper().strip().replace(' ', '_')}_hours__{_date_formatted}.csv"
