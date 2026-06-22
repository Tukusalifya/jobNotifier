from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Job:
    title: str
    company: str
    location: str
    category: str
    url: str

    normalized_category: str | None = None
    description: str | None = None
    posted_date: str | None = None
    source: str = "gozambiajobs"

    scraped_at: datetime = field(
        default_factory=datetime.now
    )