from jobnotifier.config import Config
from jobnotifier.database.database import init_db, save_job, get_pending_notifications, mark_as_notified
from jobnotifier.normalizer import normalize_category
from jobnotifier.scrapers.gozambia import GoZambiaScraper
from jobnotifier.services.email_service import Notifier

def main() -> None:
    print("Job Mailer starting up...")
    
    # 1. Initialize SQLite Database
    init_db()
    
    # 2. Instantiate scrapers
    scrapers = [
        GoZambiaScraper()
    ]
    
    # 3. Collect jobs from all sources
    raw_jobs = []
    for scraper in scrapers:
        try:
            listings = scraper.scrape()
            raw_jobs.extend(listings)
        except Exception as e:
            print(f"Error running scraper {scraper.source_name}: {e}")
            
    # 4. Normalize categories and check against user preferences
    new_jobs_saved = []
    for job in raw_jobs:
        # Normalize category
        normalized = normalize_category(
            raw_category=job.get("raw_category"),
            job_title=job.get("title", ""),
            source_site=job.get("source_site", "")
        )
        job["normalized_category"] = normalized
        
        # Check if user is interested in this category
        if normalized in Config.TARGET_CATEGORIES:
            # Attempt to save job (save_job handles deduplication via content_hash)
            is_new = save_job(job)
            if is_new:
                new_jobs_saved.append(job)
                
    print(f"Processed {len(raw_jobs)} total listings. Saved {len(new_jobs_saved)} new matching jobs.")
    
    # 5. Retrieve all pending notifications (including older unsent ones)
    pending_jobs = get_pending_notifications()
    
    # 6. Send email notification
    if pending_jobs:
        try:
            notifier = Notifier()
            notifier.send_job_alerts(pending_jobs)
            
            # Mark these jobs as notified
            job_ids = [job["id"] for job in pending_jobs if "id" in job]
            mark_as_notified(job_ids)
            print(f"Successfully notified user of {len(pending_jobs)} jobs.")
        except Exception as e:
            print(f"Failed to send email notifications: {e}")
            
    print("Job Mailer run completed successfully.")

if __name__ == "__main__":
    main()
