import logging
from datetime import datetime
from typing import Optional

from config.logging_config import logging_config

logger = logging_config(__name__, level=logging.INFO)

def format_category(category: str) -> str:
    """
    Formats the category string to match the expected format for the GoZambia Jobs API.

    Args:
        category: The raw category string.

    Returns:
        The formatted category string.
    """
    return category.lower().replace(" & ", "-")


def datetime_formatter(date_string: Optional[str], datetime_object: Optional[datetime]) -> str:
    """
    Formats a date string or datetime object into a standardized string format.

    Args:
        date_string: The date string to format.
        datetime_object: The datetime object to format.

    Returns:
        A formatted date string in the format "YYYY-MM-DD HH:MM:SS".
    """
    if date_string:
        try:
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")

            return date.strftime("%Y-%m-%d %H:%M:%S")

        except Exception as e:
            logger.error(f"An unexpected error has occurred while formatting the date string: {e}", exc_info=True)
            return ""

    elif datetime_object:
        return datetime_object.strftime("%Y-%m-%d %H:%M:%S")

