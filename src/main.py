import logging

from jobnotifier.normalizer import normalize_category
from jobnotifier.services.email_service import Notifier
from jobnotifier.config.logging_config import logging_config
from jobnotifier.scrapers.gozambiajobs import GoZambiaScraper
from jobnotifier.scrapers.jobwebzambia import JobWebaZambiaScraper
from jobnotifier.helpers.filters import filter_by_date, filter_by_location, filter_by_jobtype
from jobnotifier.database.database import init_db, save_job, get_pending_notifications, mark_as_notified

logger = logging_config(__name__, level=logging.DEBUG)


def main() -> None:
    logger.info("Job Notifier starting up...")
    
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

    # 4. Filters
    filtered_jobs = filter_by_date(jobs=raw_jobs)
    filtered_jobs = filter_by_location(jobs=filtered_jobs)
    filtered_jobs = filter_by_jobtype(jobs=filtered_jobs)

    # 5. Normalize categories
    new_jobs_saved = []
    for job in filtered_jobs:
        normalized = normalize_category(
            raw_category=job.category,
            source_site=job.source
        )
        job.normalized_category = normalized

        is_new = save_job(job)
        if is_new:
            new_jobs_saved.append(job)

    logger.info(f"Processed {len(raw_jobs)} total listings. Saved {len(new_jobs_saved)} new matching jobs.")

    # 6. Retrieve all pending notifications (including older unsent ones)
    pending_jobs = get_pending_notifications()

    # 7. Send email notification
    try:
        notifier = Notifier()
        notifier.send_job_alerts(pending_jobs)

        # Mark these jobs as notified
        job_ids = [job.id for job in pending_jobs if job.id is not None]
        mark_as_notified(job_ids)
        logger.info(f"Successfully notified user of {len(pending_jobs)} jobs.")
    except Exception as e:
        logger.critical(f"Failed to send email notifications: {e}")

    logger.info("Job Notifier run completed successfully.")


if __name__ == "__main__":
    main()
