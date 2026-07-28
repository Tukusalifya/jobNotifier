import html
import smtplib
import logging

from typing import List
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.settings import Settings
from jobnotifier.models.job import Job
from config.logging_config import logging_config

logger = logging_config(__name__, level=logging.DEBUG)

TEMPLATE_PATH = Path(__file__).parents[3] / "templates" / "job_mailer_template.html"


class Notifier:
    def __init__(self) -> None:
        self.smtp_server = Settings.SMTP_SERVER
        self.smtp_port = Settings.SMTP_PORT
        self.sender_email = Settings.EMAIL_SENDER
        self.sender_password = Settings.SMTP_PASSWORD
        self.recipient_email = Settings.EMAIL_RECIPIENT

    def send_email(self, subject: str, html_content: str) -> None:
        """
        Sends an HTML email using SMTP configuration.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Job Mailer <{self.sender_email}>"
        msg["To"] = self.recipient_email

        # Attach the HTML version of the email body
        text_content = ("New job listings are available. Please view this email in an HTML-compatible client to see "
                        "the full listing.")
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # upgrades the connection to an encrypted one
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())

            logger.info(f"Email sent to {self.recipient_email} with subject: {subject}")

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed — check email/password or app password.")
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email: {e}")

    def format_jobs_html(self, jobs: List[Job]) -> str:
        """
        Builds a clean HTML template listing the newly scraped jobs.
        """
        template = TEMPLATE_PATH.read_text(encoding="utf-8")

        # Pull out the single reusable card block from between the markers
        start_marker = "<!-- JOB_CARD_START -->"
        end_marker = "<!-- JOB_CARD_END -->"
        start = template.index(start_marker)
        end = template.index(end_marker) + len(end_marker)
        card_block = template[start:end]

        # No new jobs — return an empty state instead of a blank list of cards
        # if not jobs:
        #     empty_state = (
        #         '<tr><td style="padding:24px 32px; text-align:center; '
        #         'font-size:14px; color:#999999;">No new listings found today.</td></tr>'
        #     )
        #     return template[:start] + empty_state + template[end:]

        # Build one card per job by substituting placeholders
        cards_html = ""
        for job in jobs:
            card = card_block
            replacements = {
                "{{title}}": html.escape(job.title),
                "{{category}}": html.escape(job.category),
                "{{company}}": html.escape(job.company),
                "{{url}}": job.url,
                "{{type}}": html.escape(job.type),
                "{{location}}": html.escape(job.location),
                "{{date_added}}": job.posted_date.strftime("%d %b %Y")
                if hasattr(job.posted_date, "strftime") else str(job.posted_date),
            }
            for placeholder, value in replacements.items():
                card = card.replace(placeholder, value)
            cards_html += card

        # Splice the built cards back into the full template
        return template[:start] + cards_html + template[end:]

    def send_job_alerts(self, jobs: List[Job]) -> None:
        """
        Compiles the matching jobs and emails them to the user.
        """
        if not jobs:
            logger.critical("Notifier: No new jobs to notify.")
            return

        subject = f"Job Mailer: {len(jobs)} New Job Opportunities Found "
        html_content = self.format_jobs_html(jobs)
        self.send_email(subject, html_content)
