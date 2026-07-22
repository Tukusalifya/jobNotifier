import logging
import requests

from lxml import html

from config.settings import Settings
from jobnotifier.models.job import Job
from config.logging_config import logging_config
from jobnotifier.scrapers.base import BaseScraper
from config.constants import JOBWEBZAMBIA_URL, JOBWEBZAMBIA_NAME
from jobnotifier.helpers.data_parsers import format_category, datetime_formatter

logger = logging_config(__name__, level=logging.DEBUG)
session = requests.Session()


class JobWebaZambiaScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return JOBWEBZAMBIA_NAME

    def scrape(self) -> list[Job]:
        """
        Scrapes job listings from JobWebZambia.

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

            for category in Settings.TARGET_CATEGORIES:
                category = format_category(category=category, scraper=self.source_name)

                response = session.get(JOBWEBZAMBIA_URL + f"/{category}")
                data = response.content
                tree = html.fromstring(data)

                container_xpath = "//li[contains(@class, 'job')]"
                container_elements = tree.xpath(container_xpath)

                for element in container_elements:
                    title_company_xpath = ".//div[@id='titlo']/strong/a/text()"
                    title_company = element.xpath(title_company_xpath)[0]

                    title_parts = title_company.split(" at ")
                    company = title_parts[1].strip()
                    title = title_parts[0].strip()

                    url_xpath = ".//div[@id='titlo']/strong/a/@href"
                    url = element.xpath(url_xpath)[0]

                    country_xpath = ".//div[@id='location']/text()"
                    country = element.xpath(country_xpath)[0].strip()

                    job_type_xpath = ".//div[@id='type-tag']/span/text()"
                    job_type = element.xpath(job_type_xpath)[0].strip()

                    posted_date_xpath = ".//div[@id='date']/span/text()"
                    posted_date = element.xpath(posted_date_xpath)[0].strip()

                    response = session.get(url)
                    data = response.content
                    tree = html.fromstring(data)

                    location_xpath = "//a[contains(@href, 'job-location')]/text()"
                    location = tree.xpath(location_xpath)[0] + f", {country}"

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
    scraper = JobWebaZambiaScraper()
    jobs = scraper.scrape()

    for job in jobs:
        logger.debug(job)


if __name__ == "__main__":
    test()
