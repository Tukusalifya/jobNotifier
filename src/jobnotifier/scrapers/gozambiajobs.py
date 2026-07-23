import re
import json
import logging
import requests

from config.settings import Settings
from jobnotifier.models.job import Job
from config.logging_config import logging_config
from jobnotifier.scrapers.base import BaseScraper
from config.constants import GOZAMBIAJOBS_URL, GOZAMBIAJOBS_NAME
from jobnotifier.helpers.data_parsers import format_category, datetime_formatter

logger = logging_config(__name__, level=logging.INFO)
session = requests.Session()


class GoZambiaScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return GOZAMBIAJOBS_NAME

    def scrape(self) -> list[Job]:
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
        try:
            job_listings, jobs = [], []

            logger.info("Starting GoZambiaJobs Scraper....")

            for category in Settings.GOZAMBIAJOBS_CATEGORIES:
                params = {
                    "category": format_category(category=category, scraper=self.source_name),
                }
                response = session.get(GOZAMBIAJOBS_URL + "/jobs", params=params)
                html = response.text

                match = re.search(
                    r'window\.jobsList\s*=\s*window\.jobsList\.concat\((\[.*?\])\);',
                    html,
                    flags=re.DOTALL
                )

                if match:
                    jobs = json.loads(match.group(1))

                for job in jobs:
                    title = job['title']
                    url = GOZAMBIAJOBS_URL + job['job_details_path']
                    company = job['employer']['name']
                    location = job['location'] if job['location'] else "Not specified"
                    job_type = job['job_type']['title']
                    posted_date = job['posted_at']

                    job_listings.append(
                        Job(
                            title=title,
                            company=company,
                            location=location,
                            url=url,
                            type=job_type,
                            category=category,
                            source=self.source_name,
                            posted_date=datetime_formatter(date_string=posted_date, datetime_object=None,
                                                           scraper_name=self.source_name),
                        )
                    )

            return job_listings

        except Exception as e:
            logger.critical(f"An unexpected error has occurred while scraping from gozambiajobs: {e}", exc_info=True)


def test():
    scraper = GoZambiaScraper()
    jobs = scraper.scrape()

    for job in jobs:
        logger.debug(job)


if __name__ == "__main__":
    test()
