from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Returns the unique identifier of the job board source (e.g., 'gozambiajobs')."""
        pass
        
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrapes job listings from the target site.
        
        Returns:
            A list of dictionaries. Each dict should have keys:
            - 'title': str (required)
            - 'company': str (required)
            - 'location': str (optional)
            - 'url': str (optional)
            - 'raw_category': str (optional)
            - 'source_site': str (required)
        """
        pass
