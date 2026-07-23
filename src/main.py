import logging

from config.logging_config import logging_config
from jobnotifier.normalizer import normalize_category
from jobnotifier.services.email_service import Notifier
from jobnotifier.scrapers.gozambiajobs import GoZambiaScraper
from jobnotifier.scrapers.jobwebzambia import JobWebaZambiaScraper
from jobnotifier.database.database import init_db, save_job, get_pending_notifications, mark_as_notified

logger = logging_config(__name__, level=logging.DEBUG)


def main() -> None:
    logger.info("Job Mailer starting up...")
    
    # 1. Initialize SQLite Database
    init_db()
    
    # 2. Instantiate scrapers
    scrapers = [
        GoZambiaScraper(), JobWebaZambiaScraper()
    ]
    
    # 3. Collect jobs from all sources
    raw_jobs = []
    for scraper in scrapers:
        try:
            listings = scraper.scrape()
            raw_jobs.extend(listings)
        except Exception as e:
            logger.error(f"running scraper {scraper.source_name}: {e}")
            continue

    # 4. Normalize categories
    new_jobs_saved = []
    for job in raw_jobs:
        normalized = normalize_category(
            raw_category=job.category,
            source_site=job.source
        )
        job.normalized_category = normalized

    # 5. TODO: Add filter by date.
        is_new = save_job(job)
        if is_new:
            new_jobs_saved.append(job)

    logger.info(f"Processed {len(raw_jobs)} total listings. Saved {len(new_jobs_saved)} new matching jobs.")

    # # 5. Retrieve all pending notifications (including older unsent ones)
    # pending_jobs = get_pending_notifications()
    #
    # # 6. Send email notification
    # if pending_jobs:
    #     try:
    #         notifier = Notifier()
    #         notifier.send_job_alerts(pending_jobs)
    #
    #         # Mark these jobs as notified
    #         job_ids = [job["id"] for job in pending_jobs if "id" in job]
    #         mark_as_notified(job_ids)
    #         print(f"Successfully notified user of {len(pending_jobs)} jobs.")
    #     except Exception as e:
    #         print(f"Failed to send email notifications: {e}")
    #
    # print("Job Mailer run completed successfully.")


if __name__ == "__main__":
    main()
