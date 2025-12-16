# Crawler Module

Complete web scraping system supporting:
- **Job Postings**: Scrape job boards, track applications
- **E-Commerce Products**: Price tracking, deal detection, product comparison
- **General Web Crawling**: Browser history analysis, topic research

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Scheduler  │────▶│    Worker    │────▶│  Repository │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ├─▶ HTTP Client
                           │   (retries, rate limiting)
                           │
                           ├─▶ Scrapers
                           │   (site-specific logic)
                           │
                           ├─▶ Parsers
                           │   (HTML extraction)
                           │
                           ├─▶ Normalizer
                           │   (canonicalization)
                           │
                           └─▶ Deduper
                               (similarity matching)
```

## Components

### 1. Config (`config.py`)
- Centralized configuration management
- Environment variable loading
- Validation and defaults

### 2. HTTP Client (`http_client.py`)
- Reliable HTTP requests with exponential backoff
- Domain-level rate limiting
- User-agent rotation
- Proxy support
- Captcha detection

### 3. Parsers (`parsers.py`)
- CSS selector-based extraction
- Fallback heuristics for unknown sites
- HTML sanitization
- URL normalization

### 4. Scrapers (`scrapers.py`)
- `BaseScraper`: Abstract base with robots.txt compliance
- `GenericScraper`: Pagination + listing extraction
- `IndeedScraper`: Indeed-specific implementation
- Extensible for new job boards

### 5. Normalizer (`normalizer.py`)
- Transform raw HTML → canonical format
- Title/company canonicalization
- Salary parsing (handles hourly/annual, k suffix)
- Date parsing (relative and absolute)
- Employment type inference
- Skill extraction
- Fingerprint generation (SHA256)

### 6. Deduper (`deduper.py`)
- Token-set similarity for fuzzy matching
- Batch deduplication
- Merge logic with provenance tracking
- Configurable similarity thresholds

### 7. Scheduler (`scheduler.py`)
- Enqueue job sources for scraping
- Respect scrape intervals
- Exponential backoff on failures
- Idempotency keys

### 8. Worker (`worker.py`)
- Pipeline orchestration: scrape → normalize → dedupe → persist
- Continuous or single-pass modes
- Progress tracking and stats
- Error handling and recovery

## Usage

### Quick Start

```python
from crawler.worker import Worker
from Persistance.createDb import Session

# Create worker
session = Session()
worker = Worker(session)

# Option 1: Run once (for cron jobs)
worker.run_once()

# Option 2: Run continuously
worker.run_continuously(poll_interval_seconds=30)
```

### Scheduling Jobs

```python
from crawler.scheduler import Scheduler
from Persistance.createDb import Session

session = Session()
scheduler = Scheduler(session)

# Schedule all due sources
scheduler.schedule_all_sources()

# Schedule specific source
scheduler.enqueue_scrape(source_id=1)

# Force schedule (ignore intervals)
scheduler.schedule_all_sources(force=True)
```

### Command-Line Usage

```bash
# Run worker continuously
python -m crawler.worker

# Run once and exit (for cron)
python -m crawler.worker --once

# Run specific job
python -m crawler.worker --run-id 123

# Custom poll interval
python -m crawler.worker --poll-interval 60
```

### Example Script

```bash
python crawler/example_run.py
```

## Configuration

Create `.env` file from `.env.example`:

```bash
cp crawler/.env.example .env
```

Key settings:
- `DATABASE_URL`: PostgreSQL connection string
- `SCRAPE_CONCURRENCY`: Max concurrent scrapes
- `MAX_SCRAPE_PAGES`: Pages per source
- `REQUESTS_PER_DOMAIN_PER_MINUTE`: Rate limit
- `POLITE_DELAY_SECONDS`: Delay between requests

## Adding New Job Sources

```python
from Persistance.repository import Repository
from Persistance.createDb import Session
import json

session = Session()
repo = Repository(session)

# Add source
source = repo.create_or_update_job_source(
    name='MyJobBoard',
    source_type='generic',
    base_url='https://myjobboard.com/jobs',
    config=json.dumps({
        'pagination_pattern': 'https://myjobboard.com/jobs?page={page}',
        'listing_selector': '.job-card',
        'title_selector': 'h2.title',
        'company_selector': '.company-name',
        'location_selector': '.location',
        'snippet_selector': '.description'
    }),
    scrape_interval_minutes=60
)
```

## Creating Custom Scrapers

```python
from crawler.scrapers import BaseScraper

class MyCustomScraper(BaseScraper):
    def scrape(self, source_config):
        """Implement custom scraping logic."""
        
        # 1. Fetch pages
        response = self.http.get(url)
        
        # 2. Parse listings
        # ... custom parsing logic ...
        
        # 3. Yield results
        for listing in listings:
            yield {
                'external_id': listing.id,
                'source_name': source_config['name'],
                'title_html': listing.title,
                'company_html': listing.company,
                # ... other fields ...
                'raw_payload': str(listing),
                'fetch_metadata': {
                    'status_code': 200,
                    'fetch_duration_ms': 150
                }
            }

# Register in get_scraper()
```

## Pipeline Flow

1. **Schedule**: Scheduler enqueues sources due for scraping
2. **Fetch**: HTTP client retrieves pages with retries and rate limiting
3. **Parse**: Parsers extract structured data from HTML
4. **Normalize**: Normalizer canonicalizes fields and generates fingerprint
5. **Dedupe**: Deduper finds and merges duplicates
6. **Persist**: Repository saves to database with merge tracking

## Error Handling

- **HTTP Errors**: Exponential backoff with max retries
- **Captcha**: Detection and early termination
- **Parse Errors**: Logged but don't stop pipeline
- **Duplicate Keys**: Handled via upserts with idempotency keys
- **Source Failures**: Exponential backoff increases scrape interval

## Monitoring

Worker logs provide visibility:

```
2024-01-15 10:30:15 - crawler.worker - INFO - Starting job run 42 for source 'Indeed'
2024-01-15 10:30:20 - crawler.http_client - INFO - GET https://indeed.com/jobs status=200 duration=250ms
2024-01-15 10:30:25 - crawler.parsers - INFO - Extracted 15 listings using selector: .job_seen_beacon
2024-01-15 10:30:30 - crawler.normalizer - INFO - Normalized 15 postings
2024-01-15 10:30:32 - crawler.deduper - INFO - Deduplicated 15 -> 12 postings
2024-01-15 10:30:35 - crawler.repository - INFO - Persisted: 8 new, 4 merged
2024-01-15 10:30:35 - crawler.worker - INFO - Job run 42 completed successfully
```

## Dependencies

```
requests>=2.31.0
beautifulsoup4>=4.12.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

Install:
```bash
pip install requests beautifulsoup4 sqlalchemy psycopg2-binary
```

## Testing

Create test job sources:

```python
from Persistance.repository import Repository
from Persistance.createDb import Session

session = Session()
repo = Repository(session)

# Add test source
source = repo.create_or_update_job_source(
    name='TestSource',
    source_type='generic',
    base_url='http://localhost:8000/test-jobs',
    config='{"listing_selector": ".job"}',
    scrape_interval_minutes=1
)

print(f"Created test source: {source.id}")
```

## Production Deployment

### Cron Job
```cron
# Run every hour
0 * * * * cd /path/to/project && python -m crawler.worker --once >> /var/log/crawler.log 2>&1
```

### Systemd Service
```ini
[Unit]
Description=Web Scraper Crawler Worker
After=network.target postgresql.service

[Service]
Type=simple
User=scraper
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 -m crawler.worker
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ backend/
COPY crawler/ crawler/

CMD ["python", "-m", "crawler.worker"]
```

## Performance Tuning

- **Concurrency**: Increase `SCRAPE_CONCURRENCY` for more parallel scrapes
- **Rate Limits**: Adjust `REQUESTS_PER_DOMAIN_PER_MINUTE` per site tolerance
- **Pages**: Limit `MAX_SCRAPE_PAGES` to control scrape duration
- **Intervals**: Set appropriate `scrape_interval_minutes` per source freshness needs
- **Dedup Threshold**: Lower threshold (0.7-0.8) for looser matching, higher (0.9+) for strict

## Troubleshooting

**Captcha Detected**
- Reduce rate limits
- Add more user agents
- Use residential proxies
- Implement headless browser (Selenium/Playwright)

**No Listings Found**
- Verify CSS selectors in browser DevTools
- Check for JavaScript-rendered content
- Review robots.txt restrictions

**High Duplicate Rate**
- Check fingerprint generation logic
- Verify canonicalization is working
- Adjust dedup threshold

**Database Locks**
- Ensure proper transaction scoping
- Use connection pooling
- Increase PostgreSQL max_connections
