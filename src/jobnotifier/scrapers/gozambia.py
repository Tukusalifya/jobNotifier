from typing import List, Dict
from jobnotifier.scrapers.base import BaseScraper

class GoZambiaScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "gozambiajobs"
        
    def scrape(self) -> List[Dict]:
        """
        Scrapes job listings from GoZambia Jobs.
        
        Returns:
            A list of dictionaries. Each dict should have keys:
            - 'title': str
            - 'company': str
            - 'location': str
            - 'url': str
            - 'raw_category': str
            - 'source_site': str
        """
        # TODO: Implement scraping logic using requests and lxml
        print("GoZambiaScraper: Scraping listings...")
        return []
