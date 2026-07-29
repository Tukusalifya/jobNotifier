# Job Notifier

A modular, automated Python job aggregation and alerting system that scrapes Zambian job listings, filters and normalizes them, and emails the fresh matching listings directly to you.

I built this project because looking for jobs meant opening multiple websites every day and checking each one manually. That gets exhausting pretty quickly. If something repetitive can be automated, why not automate it? Instead of jumping between tabs, this script scrapes, normalizes, and filters the newest jobs, saving them in a database so you never receive the same notification twice.

---

## How It Works

Here is a quick look at the lifecycle of a single run:

```
[ Scrapers ] (GoZambiaJobs & JobWebZambia)
      │
      ▼
[ Filter Jobs ] (By Date, Location, and Job Type)
      │
      ▼
[ Normalize Categories ] (Translates raw categories using category_mappings.yaml)
      │
      ▼
[ Save to SQLite ] (Computes unique content_hash; ignores duplicates)
      │
      ▼
[ Detect New Jobs ] (Queries all jobs where notified = 0)
      │
      ▼
[ Generate HTML Email ] (Splices jobs into job_mailer_template.html)
      │
      ▼
[ SMTP TLS Dispatch ] (Sends consolidated alert to your inbox)
      │
      ▼
[ Mark as Notified ] (Updates database to set notified = 1)
```

1. **Scraping**: The script invokes a collection of site-specific scrapers to fetch HTML or JSON endpoints.
2. **Filtering**: The raw listings are pre-filtered based on date, location, and job type criteria specified in your `.env`.
3. **Normalization**: Dynamic category names (e.g. `"IT/Telecom Jobs in Zambia"` vs `"IT & Telecoms"`) are mapped into a standardized set using the rules in `category_mappings.yaml`.
4. **Deduplication**: A unique cryptographic hash (`SHA-256`) of the normalized `title` + `company` is computed. If the hash already exists in the SQLite database, it is skipped.
5. **Alerting**: All newly found jobs are formatted using an elegant HTML template and dispatched via TLS-encrypted SMTP. Once sent successfully, their database status is updated.

---

## Features

* **Multi-Site Scraping**: Integrated scrapers for major Zambian job portals (**GoZambiaJobs** and **JobWebZambia**).
* **Smart Content Normalization**: Dynamic raw category names map cleanly to a consistent, internal taxonomy via YAML configuration.
* **Granular Filtering**: Pre-filters scraped jobs by location, contract type (e.g., Full-Time, Part-Time), and age (days since posted).
* **Robust Deduplication**: Enforces a `UNIQUE` database constraint on a content-based hash (`title + company`) to prevent alerting you about the same listing posted on different sites.
* **Premium Email Alerts**: Formats listings inside a responsive, modern HTML email template with support for text fallback.
* **Rich Console & File Logging**: Uses `rich` to output beautifully styled log messages in the console, while appending tracebacks to local log files under `logs/`.
* **Extensible Scraper Architecture**: Adding a new job board is as simple as inheriting from a base class and implementing a single method.

---

## Project Structure

```
jobNotifier/
├── pyproject.toml             # Project metadata and dependencies (managed by uv)
├── category_mappings.yaml     # Maps source categories to standard internal taxonomy
├── .env                       # Secret parameters (credentials, database, filters)
├── .env.example               # Template environment settings
├── data/
│   └── jobs.db                # SQLite database (auto-created on first run)
├── templates/
│   └── job_mailer_template.html # Responsive HTML template for email alerts
├── logs/                      # Executions logs directory (auto-created)
└── src/
    ├── main.py                # Main orchestrator script
    └── jobnotifier/
        ├── config/
        │   ├── constants.py           # Site URLs and identifier constants
        │   ├── logging_config.py      # Dual rich-console and file logger configuration
        │   └── settings.py            # Environment variable loader
        ├── database/
        │   └── database.py    # SQLite CRUD operations & content hash math
        ├── helpers/
        │   ├── data_parsers.py# String formatters for dates and URLs
        │   └── filters.py     # Filter engines (by date, location, type)
        ├── models/
        │   └── job.py         # Standard Job dataclass schema
        ├── normalizer/
        │   └── normalizer.py  # YAML mappings loader and translator
        └── scrapers/
            ├── base.py        # Abstract Base Class contract for scrapers
            ├── gozambiajobs.py# GoZambiaJobs JSON scraper
            └── jobwebzambia.py# JobWebZambia XPath scraper (requests + lxml)
```

---

## Requirements

* **Python**: `^3.12`
* **Local Storage**: SQLite (built-in)
* **SMTP Credentials**: Standard email configuration (e.g., Gmail App Password)

---

## Packages / Dependencies

The project uses the following key libraries:

| Package | Purpose |
| :--- | :--- |
| `requests` | Handles session-based HTTP requests to fetch page contents and API JSON payloads. |
| `lxml` | High-performance HTML parsing using XPath queries to extract elements from scraped HTML. |
| `pyyaml` | Parses `category_mappings.yaml` to dynamically map raw categories to normalized titles. |
| `python-dotenv` | Loads parameters from `.env` directly into environment variables. |
| `rich` | Standard terminal output formatter giving clean colored logs and beautiful tracebacks. |

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Tukusalifya/jobNotifier.git
cd jobNotifier
```

### 2. Set Up Virtual Environment & Dependencies
We recommend using the modern [uv](https://github.com/astral-sh/uv) package manager for instant setups:
```bash
# Using uv:
uv sync
```
Or you can use standard Python toolings:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r pyproject.toml

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

### 3. Setup Configuration
Copy the template `.env.example` into a local `.env` file:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Open `.env` and fill in your SMTP credentials, target filter preferences, and destination email address (see the [Configuration](#configuration) section below).

---

## Configuration

The system is configured using variables in your `.env` file:

### SMTP / Notifier Settings
* `SMTP_SERVER`: The SMTP host of your provider (default: `smtp.gmail.com`).
* `SMTP_PORT`: The TLS SMTP port (default: `587`).
* `SMTP_USERNAME`: The sender email address.
* `SMTP_PASSWORD`: The app password / email password (use an App Password if using Gmail).
* `EMAIL_SENDER`: The email address showing in the "From" header.
* `EMAIL_RECIPIENT`: The target inbox where notifications will be sent.

### Filter Settings
* `GOZAMBIAJOBS_CATEGORIES`: Comma-separated raw categories to query from GoZambiaJobs (e.g., `IT & Telecoms, Engineering & Construction`).
* `JOBWEBZAMBIA_CATEGORIES`: Comma-separated raw categories to query from JobWebZambia (e.g., `IT/Telecom Jobs in Zambia`).
* `TARGET_LOCATION`: Substring match to filter jobs by location (e.g., `Lusaka`). Leave blank to disable location filtering.
* `TARGET_JOBTYPE`: Substring match to filter jobs by job type (e.g., `Full-Time`, `Contract`). Leave blank to disable.
* `TARGET_PAST_DAYS`: Set to `n` to only process jobs posted within the last `n` days. Set to `0` to process all listings.

### Path Settings
* `DATABASE_PATH`: Relative or absolute path to SQLite file (default: `data/jobs.db`).
* `MAPPINGS_FILE_PATH`: Path to mappings configuration (default: `category_mappings.yaml`).

---

## Usage

### Option 1 — Run Manually
To run the scraper and notifier immediately:
```bash
# Using uv:
uv run src/main.py

# Using standard virtualenv:
python src/main.py
```

### Option 2 — Schedule on Windows (Windows Task Scheduler)
1. Open **Task Scheduler** and click **Create Basic Task**.
2. Set a Name (e.g., `Job Notifier Daily`) and set the trigger to **Daily**.
3. Choose the action **Start a program**.
4. In **Program/script**, select the Python executable inside your virtual environment, e.g.:
   `C:\Users\YourUser\PycharmProjects\jobNotifier\.venv\Scripts\python.exe`
5. In **Add arguments**, enter the path to the orchestrator:
   `src/main.py`
6. In **Start in**, enter the absolute path to your repository root, e.g.:
   `C:\Users\YourUser\PycharmProjects\jobNotifier`
7. Save the task and check **Run whether user is logged on or not** if running on a persistent Windows server.

### Option 3 — Schedule on Linux (cron)
You can schedule the script using crontab. Open your crontab editor:
```bash
crontab -e
```
Add a daily job run at 08:00 AM:
```cron
0 8 * * * cd /home/user/jobNotifier && /home/user/jobNotifier/.venv/bin/python src/main.py >> /home/user/jobNotifier/logs/cron.log 2>&1
```

---

## Database Schema

The script uses a simple SQLite database located at `data/jobs.db` with a single table `jobs`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key (auto-incrementing) |
| `content_hash` | `TEXT` | Cryptographic SHA-256 hash unique to `title + company` |
| `title` | `TEXT` | Raw job title |
| `company` | `TEXT` | Employer name |
| `job_type` | `TEXT` | Job type tag (e.g., Full-Time, Contract) |
| `location` | `TEXT` | Location metadata |
| `url` | `TEXT` | Link to listing details page |
| `source_site` | `TEXT` | Scraped source board (`GoZambiaJobs` or `JobWebZambia`) |
| `raw_category` | `TEXT` | Unmodified category name returned from source |
| `normalized_category`| `TEXT` | Translated category taxonomy name |
| `posted_date` | `TEXT` | Formatted posting date (`YYYY-MM-DD`) |
| `scraped_at` | `TIMESTAMP`| Timestamp of ingestion (`DEFAULT CURRENT_TIMESTAMP`) |
| `notified` | `INTEGER` | Notification state flag (`0` = pending, `1` = email sent) |

### Uniqueness and Deduplication
The database schema enforces a `UNIQUE` constraint on the `content_hash` column. During saves, the application calculates the hash and checks if it exists in SQLite using a fast index query. If it exists, the entry is skipped, avoiding repeated emails.

---

## Email Notifications

Alerts are sent as TLS-encrypted multi-part MIME emails (carrying plain text fallback and formatted HTML). 

The template is parsed from `templates/job_mailer_template.html`. The notifier extracts the HTML template between:
```html
<!-- JOB_CARD_START -->
...
<!-- JOB_CARD_END -->
```
For each unsent job, placeholders are replaced:
* `{{title}}` -> The Job Title
* `{{category}}` -> Normalized Category
* `{{company}}` -> Company Name
* `{{location}}` -> Job Location
* `{{type}}` -> Job Contract Type
* `{{date_added}}` -> Posted Date
* `{{url}}` -> Link to apply

Once sent, those job records are marked as `notified = 1` in SQLite.

---

## Adding New Job Sources

You can easily add new job sites to the aggregator:

1. Create a new scraper file in `src/jobnotifier/scrapers/`, e.g., `newsite.py`.
2. Create a scraper class that inherits from `BaseScraper`:
   ```python
   from jobnotifier.scrapers.base import BaseScraper
   from jobnotifier.models.job import Job

   class NewSiteScraper(BaseScraper):
       @property
       def source_name(self) -> str:
           return "NewSiteName"

       def scrape(self) -> list[Job]:
           # 1. Fetch data using requests
           # 2. Parse details using lxml / XPath / JSON
           # 3. Yield Job instances
           return []
   ```
3. Open `src/main.py` and import your new scraper:
   ```python
   from jobnotifier.scrapers.newsite import NewSiteScraper
   ```
4. Append your class instance to the `scrapers` list:
   ```python
   scrapers = [
       GoZambiaScraper(),
       JobWebaZambiaScraper(),
       NewSiteScraper()
   ]
   ```
5. Open `category_mappings.yaml` and add category translations under your new site source key:
   ```yaml
   mappings:
     NewSiteName:
       "Raw Category String": "Normalized Taxonomy Category"
   ```

---

## Logging

Logging is initialized via `config/logging_config.py`. 
* Console logs print in color using `rich.logging.RichHandler`, presenting clear time logs, logging levels, and traceback details.
* Standard logs are appended to local files in the `logs/` directory, formatted as:
  `logs/<module_name>_YYYYMMDD.log`
* This setup helps track network issues, scraper exceptions, database queries, and email delivery failures.

---

## Future Improvements

* **Docker Support**: Containerize the runner for easier execution on NAS or cloud instances.
* **Dashboard Integration**: Add a lightweight FastAPI dashboard to view database logs and run stats directly.
* **Notification Webhooks**: Extend notifications to Discord or Telegram channels.
* **Keyword Matching**: Allow users to filter jobs using a list of title keywords (e.g., "React", "Python").

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
