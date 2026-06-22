import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project directory
load_dotenv()

# Find project base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "test@example.com")
    EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "recipient@example.com")

    # Target categories to filter (comma-separated list)
    _raw_categories = os.getenv("TARGET_CATEGORIES", "IT & Telecoms,Finance,Engineering")
    TARGET_CATEGORIES = [c.strip() for c in _raw_categories.split(",") if c.strip()]

    # Database path (resolve relative to project base if needed)
    _db_path = os.getenv("DATABASE_PATH", "jobs.db")
    DATABASE_PATH = str(BASE_DIR / _db_path) if not Path(_db_path).is_absolute() else _db_path

    # Mappings file path (resolve relative to project base if needed)
    _mappings_path = os.getenv("MAPPINGS_FILE_PATH", "category_mappings.yaml")
    MAPPINGS_FILE_PATH = str(BASE_DIR / _mappings_path) if not Path(_mappings_path).is_absolute() else _mappings_path
