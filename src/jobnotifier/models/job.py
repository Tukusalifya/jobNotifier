from dataclasses import dataclass, field
from datetime import datetime

from jobnotifier.helpers.data_parsers import datetime_formatter


@dataclass
class Job:
    title: str
    company: str
    location: str
    category: str
    url: str
    type: str
    source: str

    normalized_category: str | None = None
    posted_date: str | None = None

    scraped_at: str = field(
        default_factory=lambda: datetime_formatter(datetime_object=datetime.now(),
                                                   date_string=None, scraper_name=None),)
