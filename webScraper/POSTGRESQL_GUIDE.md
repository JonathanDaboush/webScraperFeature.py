# PostgreSQL Data Persistence Guide

## Quick Setup

### 1. Start PostgreSQL

**Windows:**
```powershell
# Check if running
Get-Service -Name postgresql*

# Start if needed
Start-Service postgresql-x64-14  # adjust version number
```

**Linux/Mac:**
```bash
sudo systemctl start postgresql
```

### 2. Create Database (First Time Only)

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE webscraper;"

# Or in psql shell
psql -U postgres
CREATE DATABASE webscraper;
\q
```

### 3. Initialize Tables

```bash
cd backend
python setup_database.py
```

This will:
- ✓ Check PostgreSQL connection
- ✓ Verify database exists
- ✓ Create all tables
- ✓ Test data persistence
- ✓ Show current stats

## Database Connection

Your data is stored at:
```
postgresql://postgres:password@localhost:5432/webscraper
```

**To change connection settings:**
Edit `backend/Persistance/createDb.py`:
```python
engine = create_engine(
    "postgresql://YOUR_USER:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/YOUR_DATABASE",
    echo=True
)
```

## Using the Database

### Save Data in Your Code

```python
from Persistance.createDb import SessionLocal
from Persistance.crawler import Domain, Page

# Create session
session = SessionLocal()

# Save a domain
domain = Domain(domain="example.com")
session.add(domain)
session.commit()

# Save a page
page = Page(
    url="https://example.com/page",
    title="Example Page",
    domain_id=domain.id,
    html="<html>...</html>"
)
session.add(page)
session.commit()

# Query data
all_pages = session.query(Page).all()
recent = session.query(Page).order_by(Page.date_found.desc()).limit(10).all()

# Close when done
session.close()
```

### Research Crawler Auto-Saves

The `ResearchCrawler` automatically saves to PostgreSQL:

```python
from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Persistance.repository import Repository

http = HttpClient()
repo = Repository()  # Uses PostgreSQL automatically

crawler = ResearchCrawler(http, repo)

# This automatically saves to database
page_data = crawler.crawl_page(url, keywords)
```

## Database Management Commands

### Show Statistics
```bash
python db_manager.py stats
```

### Show Recent Pages
```bash
python db_manager.py recent --limit 20
```

### Show All Domains
```bash
python db_manager.py domains
```

### Export Table to CSV
```bash
python db_manager.py export --table pages --output pages.csv
python db_manager.py export --table domains --output domains.csv
```

### Backup to JSON
```bash
python db_manager.py backup
```

### Clear Table
```bash
# Will ask for confirmation
python db_manager.py clear --table pages

# Skip confirmation
python db_manager.py clear --table pages --yes
```

### Custom SQL Query
```bash
python db_manager.py query --sql "SELECT * FROM domains LIMIT 5"
python db_manager.py query --sql "SELECT COUNT(*) FROM pages WHERE crawled = true"
```

## Viewing Your Data

### Option 1: pgAdmin 4 (GUI)
1. Download: https://www.pgadmin.org/
2. Connect to: `localhost:5432`
3. Username: `postgres`
4. Password: `password` (or your password)
5. Browse database: `webscraper`

### Option 2: psql (Command Line)
```bash
# Connect to database
psql -U postgres -d webscraper

# Show tables
\dt

# Query data
SELECT * FROM domains;
SELECT COUNT(*) FROM pages;
SELECT * FROM pages ORDER BY date_found DESC LIMIT 10;

# Exit
\q
```

### Option 3: DBeaver (Universal)
1. Download: https://dbeaver.io/
2. New Connection → PostgreSQL
3. Host: `localhost`, Port: `5432`, Database: `webscraper`

## Backup & Restore

### Full Database Backup
```bash
# Backup
pg_dump -U postgres -d webscraper > backup.sql

# Restore
psql -U postgres -d webscraper < backup.sql
```

### Backup with Date
```bash
pg_dump -U postgres -d webscraper > backup_$(date +%Y%m%d).sql
```

### Backup Specific Tables
```bash
pg_dump -U postgres -d webscraper -t pages -t domains > partial_backup.sql
```

## Data Persistence Features

✓ **Automatic Persistence**: All data saved through Repository/ResearchCrawler persists
✓ **ACID Compliance**: PostgreSQL ensures data integrity
✓ **Transactions**: Rollback on errors, commit on success
✓ **Relationships**: Foreign keys maintain data consistency
✓ **Indexes**: Fast queries on urls, domains, dates
✓ **Backup Ready**: Standard PostgreSQL backup tools work

## Table Structure

### Main Tables
- `domains` - Websites being crawled
- `pages` - Individual web pages
- `crawl_jobs` - Tracking crawl sessions
- `requests` - HTTP requests made
- `subjects` - Topics/subjects extracted
- `tags` - Tags from pages

### Job Tables
- `job_sources` - Job board configurations
- `raw_job_entries` - Raw scraped job data
- `job_postings` - Normalized job postings
- `skills` - Skills mentioned in jobs
- `job_runs` - Job scraping runs

### Product Tables
- `product_sources` - Product scraping configs
- `product_runs` - Product scraping sessions

## Troubleshooting

### "Can't connect to PostgreSQL"
```bash
# Check if running
Get-Service postgresql*  # Windows
sudo systemctl status postgresql  # Linux

# Start it
Start-Service postgresql-x64-14  # Windows
sudo systemctl start postgresql  # Linux
```

### "Database does not exist"
```bash
psql -U postgres -c "CREATE DATABASE webscraper;"
```

### "Permission denied"
Update password in `createDb.py` to match your PostgreSQL password.

### "Table already exists"
This is fine - it means tables are already set up.

### Check Connection Manually
```python
from Persistance.createDb import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(result.fetchone())
```

## Data is Persisted When...

✓ You call `session.commit()`
✓ ResearchCrawler saves a page
✓ Repository methods complete successfully
✓ Script exits normally after commits

## Data is NOT Persisted When...

✗ You forget `session.commit()`
✗ Exception occurs before commit
✗ You call `session.rollback()`
✗ PostgreSQL server crashes (rare)

## Best Practices

1. **Always use sessions properly:**
   ```python
   session = SessionLocal()
   try:
       # do work
       session.commit()
   except:
       session.rollback()
       raise
   finally:
       session.close()
   ```

2. **Use Repository pattern (already in place):**
   ```python
   repo = Repository()  # Handles sessions for you
   repo.save_page(page_data)
   ```

3. **Backup regularly:**
   ```bash
   # Add to cron/scheduled task
   pg_dump -U postgres -d webscraper > backup_$(date +%Y%m%d).sql
   ```

4. **Monitor disk space** - database grows with scraped data

5. **Index important queries** - already done for common lookups

## Need Help?

```bash
# Quick health check
python setup_database.py

# Show what's in your database
python db_manager.py stats
python db_manager.py domains
python db_manager.py recent

# Test persistence
python setup_database.py  # includes persistence test
```

---

Your data is safe in PostgreSQL and will persist across:
- ✓ Script restarts
- ✓ Computer reboots
- ✓ Code changes
- ✓ Python environment changes

Just make sure PostgreSQL service is running!
