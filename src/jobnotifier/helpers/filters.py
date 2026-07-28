from datetime import date, datetime, timedelta

from config.settings import Settings
from jobnotifier.models.job import Job


def filter_by_date(jobs: list[Job]) -> list[Job]:
    """
    Function that takes in a list of jobs and returns
    a list of filtered jobs by date.

    :param jobs: list of scraped jobs
    :return: list of jobs filtered by date
    """
    TARGET_PAST_DAYS = Settings.TARGET_PAST_DAYS

    if TARGET_PAST_DAYS:
        today = date.today()
        start_date = today - timedelta(days=7)

        filtered_jobs = [
            job for job in jobs
            if datetime.strptime(job.posted_date, "%Y-%m-%d").date() >= start_date
        ]

        return filtered_jobs

    else:
        return jobs


def filter_by_location(jobs: list[Job]) -> list[Job]:
    """
    Function that takes in a list of jobs and returns
    a list of filtered jobs by location.

    :param jobs: list of scraped jobs
    :return: list of jobs filtered by location
    """

    TARGET_LOCATION = Settings.TARGET_LOCATION

    if TARGET_LOCATION:
        filtered_jobs = [
            job for job in jobs
            if TARGET_LOCATION.lower() in job.location.lower()
        ]

        return filtered_jobs

    else:
        return jobs


def filter_by_jobtype(jobs: list[Job]) -> list[Job]:
    """
    Function that takes in a list of jobs and returns
    a list of filtered jobs by job type.

    :param jobs: list of scraped jobs
    :return: list of jobs filtered by job type
    """

    TARGET_JOBTYPE = Settings.TARGET_JOBTYPE

    if TARGET_JOBTYPE:
        filtered_jobs = [
            job for job in jobs
            if TARGET_JOBTYPE.lower() in job.type.lower()
        ]

        return filtered_jobs

    else:
        return jobs
