from typing import List, Dict
from config.settings import Settings


class Notifier:
    def __init__(self) -> None:
        # TODO: Load SMTP configuration from Config class
        pass

    def send_email(self, subject: str, html_content: str) -> None:
        """
        Sends an HTML email using SMTP configuration.
        """
        # TODO: Implement email sending logic using smtplib and email.mime modules
        print(f"Notifier: Sending email to {Settings.EMAIL_RECIPIENT} with subject: {subject}")
        pass

    def format_jobs_html(self, jobs: List[Dict]) -> str:
        """
        Builds a clean HTML template listing the newly scraped jobs.
        """
        # TODO: Format the list of jobs into a premium HTML table or cards list
        return ""

    def send_job_alerts(self, jobs: List[Dict]) -> None:
        """
        Compiles the matching jobs and emails them to the user.
        """
        if not jobs:
            print("Notifier: No new jobs to notify.")
            return

        subject = f"Job Mailer: {len(jobs)} New Job Opportunities Found"
        html_content = self.format_jobs_html(jobs)
        self.send_email(subject, html_content)
