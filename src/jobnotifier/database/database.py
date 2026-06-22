import sqlite3
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional
from config.settings import Settings

def init_db() -> None:
    """Initializes the SQLite database and creates the jobs table if it doesn't exist."""
    conn = sqlite3.connect(Settings.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            url TEXT,
            source_site TEXT NOT NULL,
            raw_category TEXT,
            normalized_category TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notified INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def normalize_text(text: Optional[str]) -> str:
    """Helper to convert text to lowercase and strip all non-alphanumeric characters."""
    if not text:
        return ""
    # Lowercase and remove anything that is not a letter or number
    return re.sub(r"[^a-z0-9]", "", text.lower())

def compute_content_hash(title: str, company: str) -> str:
    """Computes a SHA-256 hash from normalized title and company to detect duplicate listings."""
    normalized_title = normalize_text(title)
    normalized_company = normalize_text(company)
    combined = f"{normalized_title}|{normalized_company}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def is_duplicate(content_hash: str) -> bool:
    """Checks if a job hash already exists in the database."""
    conn = sqlite3.connect(Settings.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM jobs WHERE content_hash = ?", (content_hash,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_job(job: Dict) -> bool:
    """
    Saves a job listing to the database.
    Returns True if the job is a new entry (successfully inserted), 
    and False if it is a duplicate (ignored due to UNIQUE constraint).
    """
    conn = sqlite3.connect(Settings.DATABASE_PATH)
    cursor = conn.cursor()
    
    title = job.get("title", "")
    company = job.get("company", "")
    content_hash = compute_content_hash(title, company)
    
    try:
        cursor.execute(
            """
            INSERT INTO jobs (
                content_hash, title, company, location, url, 
                source_site, raw_category, normalized_category, notified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                content_hash,
                title,
                company,
                job.get("location", ""),
                job.get("url", ""),
                job.get("source_site", ""),
                job.get("raw_category", ""),
                job.get("normalized_category", ""),
            )
        )
        conn.commit()
        inserted = True
    except sqlite3.IntegrityError:
        # Unique constraint failed (content_hash already exists)
        inserted = False
    finally:
        conn.close()
        
    return inserted

def get_pending_notifications() -> List[Dict]:
    """Retrieves all jobs that have not been emailed to the user yet."""
    conn = sqlite3.connect(Settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name like dict
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE notified = 0")
    rows = cursor.fetchall()
    
    jobs = []
    for row in rows:
        jobs.append(dict(row))
        
    conn.close()
    return jobs

def mark_as_notified(job_ids: List[int]) -> None:
    """Marks a list of job IDs as notified in the database."""
    if not job_ids:
        return
    conn = sqlite3.connect(Settings.DATABASE_PATH)
    cursor = conn.cursor()
    # Create placeholders (?, ?, ?) based on list size
    placeholders = ",".join("?" for _ in job_ids)
    cursor.execute(
        f"UPDATE jobs SET notified = 1 WHERE id IN ({placeholders})",
        job_ids
    )
    conn.commit()
    conn.close()
