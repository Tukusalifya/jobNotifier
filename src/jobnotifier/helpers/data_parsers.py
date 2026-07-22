import logging
from datetime import datetime
from typing import Optional

from config.constants import JOBWEBZAMBIA_NAME, GOZAMBIAJOBS_NAME
from config.logging_config import logging_config

logger = logging_config(__name__, level=logging.INFO)


def format_category(category: str, scraper: str) -> str:
    """
    Formats the category string to match the expected format for the selected Scraper API.

    Args:
        category: The raw category string.
        scraper: The string representing the scraper

    Returns:
        The formatted category string.
    """

    if scraper == GOZAMBIAJOBS_NAME:
        return category.lower().replace(" & ", "-")

    elif scraper == JOBWEBZAMBIA_NAME:
        return (category.lower().replace("/", "")
                .replace(".", "").replace("(", "")
                .replace(")", "").replace(" ", "-"))


def datetime_formatter(date_string: Optional[str],
                       datetime_object: Optional[datetime],
                       scraper_name: Optional[str]
                       ) -> str:
    """
    Formats a date string or datetime object into a standardized string format.

    Args:
        date_string: The date string to format.
        datetime_object: The datetime object to format.
        scraper_name: The scraper name.

    Returns:
        A formatted date string in the format "YYYY-MM-DD HH:MM:SS".
    """
    if scraper_name == GOZAMBIAJOBS_NAME:
        if date_string:
            try:
                date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")

                return date.strftime("%Y-%m-%d")

            except Exception as e:
                logger.error(f"An unexpected error has occurred while formatting the date string: {e}", exc_info=True)
                return ""

    elif scraper_name == JOBWEBZAMBIA_NAME:
        if date_string:
            try:
                date = datetime.strptime(date_string, "%d/%b/%Y")

                return date.strftime("%Y-%m-%d")

            except Exception as e:
                logger.error(f"An unexpected error has occurred while formatting the date string: {e}", exc_info=True)
                return ""

    elif scraper_name is None:
        if datetime_object:
            return datetime_object.strftime("%Y-%m-%d %H:%M:%S")



