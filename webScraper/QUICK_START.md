# 🚀 Quick Start Guide - Web Scraper Setup & Usage

## Installation & Setup

### Step 1: Install Python Dependencies

Open PowerShell in the webScraper directory and run:

```powershell
# Install all required Python packages
pip install psycopg2-binary sqlalchemy requests beautifulsoup4 pytest

# Or install from requirements if available
pip install -r requirements.txt
```

### Step 2: Setup PostgreSQL Database

The database is already created! Just verify it's running:

```powershell
cd backend
python create_database.py
```

You should see: `✓ Database 'webscraper' already exists`

### Step 3: Create Tables (Already Done!)

Tables are already created, but you can verify:

```powershell
python -c "from Persistance.crawler import Base, engine; print('Tables ready!')"
```

### Step 4: Verify Installation

```powershell
python db_manager.py stats
```

You should see statistics for all tables (domains, pages, etc.)

---

## 🎯 How to Collect Data

### Option 1: Simple Research Crawl (Recommended for Beginners)

Create a simple script to crawl websites:

**File: `run_simple_crawl.py`**
```python
from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal

# Setup
client = HttpClient()
session = SessionLocal()
repo = Repository(session)
crawler = ResearchCrawler(client, repo)

# Crawl a website (respects legal compliance rules!)
print("Crawling Theatre Calgary...")
result = crawler.crawl_page("https://www.theatrecalgary.com", ["theatre", "events"])

print(f"✓ Crawled: {result['url']}")
print(f"✓ Title: {result['title']}")
print(f"✓ Keywords: {len(result.get('keywords', {}))} found")
print(f"✓ Links: {len(result.get('links', []))} found")

session.close()
```

Run it:
```powershell
cd backend
python run_simple_crawl.py
```

### Option 2: Research a Topic

Crawl multiple pages about a specific topic:

**File: `run_topic_research.py`**
```python
from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal

# Setup
client = HttpClient()
session = SessionLocal()
repo = Repository(session)
crawler = ResearchCrawler(client, repo)

# Research "Python programming"
print("Researching Python programming...")
results = crawler.research_topic(
    start_url="https://www.python.org",
    search_terms=["python", "programming", "tutorial"],
    max_pages=5  # Crawl up to 5 pages
)

print(f"\n✓ Researched {len(results)} pages")
for page in results:
    print(f"  - {page['title']} ({page['url']})")

session.close()
```

Run it:
```powershell
cd backend
python run_topic_research.py
```

### Option 3: Crawl with Legal Compliance (Respects ToS)

The crawler automatically checks if scraping is allowed:

**File: `run_safe_crawl.py`**
```python
from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Crawler.compliance import ScrapingCompliance
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal

# Setup with compliance
client = HttpClient()
session = SessionLocal()
repo = Repository(session)
compliance = ScrapingCompliance()

# These URLs are pre-configured as safe to scrape:
safe_urls = [
    "https://www.theatrecalgary.com",
    "https://www.toyota.ca",
    "https://www.imdb.com"
]

for url in safe_urls:
    # Check compliance first
    allowed, reason = compliance.check_url_compliance(url)
    
    if allowed:
        print(f"✓ Scraping {url} (Allowed)")
        crawler = ResearchCrawler(client, repo)
        result = crawler.crawl_page(url, [])
        print(f"  Title: {result['title']}")
    else:
        print(f"✗ Skipping {url} - {reason}")

session.close()
```

---

## 📊 View Collected Data

### Check What's Been Collected

```powershell
cd backend

# View statistics
python db_manager.py stats

# View recent pages
python db_manager.py recent --table pages --limit 10

# View all domains
python db_manager.py domains

# Export to CSV
python db_manager.py export --output data.csv

# Export to JSON backup
python db_manager.py backup --output backup.json
```

### Query Specific Data

```powershell
# Custom SQL queries
python db_manager.py query --sql "SELECT COUNT(*) FROM pages WHERE crawled = true"
```

---

## 🔧 Advanced Usage

### Schedule Automated Crawling

**File: `run_scheduled_crawl.py`**
```python
import time
from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal

def crawl_daily():
    """Run daily crawl of monitored sites."""
    client = HttpClient()
    session = SessionLocal()
    repo = Repository(session)
    crawler = ResearchCrawler(client, repo)
    
    sites = [
        ("https://www.theatrecalgary.com", ["theatre", "shows"]),
        ("https://www.toyota.ca/vehicles", ["cars", "vehicles"]),
    ]
    
    for url, keywords in sites:
        print(f"Crawling {url}...")
        try:
            result = crawler.crawl_page(url, keywords)
            print(f"  ✓ Success: {result['title']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        time.sleep(5)  # Rate limiting - be nice!
    
    session.close()
    print("\n✓ Daily crawl complete!")

if __name__ == "__main__":
    crawl_daily()
```

Run it:
```powershell
cd backend
python run_scheduled_crawl.py
```

### Monitor and Analyze

```powershell
# View crawler logs
Get-Content crawler.log -Tail 50

# Watch real-time
Get-Content crawler.log -Wait
```

---

## 🎨 Access the Web Dashboard (Optional)

If you want the React frontend:

```powershell
cd frontend
npm install
npm start
```

Then open: http://localhost:3000

---

## 📝 Common Tasks

### Task: Find all pages about Python
```powershell
python db_manager.py query --sql "SELECT url, title FROM pages WHERE title LIKE '%Python%'"
```

### Task: Export today's crawled data
```python
from datetime import datetime
from Persistance.crawler import Page
from Persistance.createDb import SessionLocal

session = SessionLocal()
today = datetime.now().date()

pages = session.query(Page).filter(
    Page.date_found >= today
).all()

print(f"Found {len(pages)} pages today")
for page in pages:
    print(f"- {page.title}: {page.url}")

session.close()
```

### Task: Clear old data
```powershell
# Clear all data (careful!)
python db_manager.py clear --yes

# Or manually delete old pages
python -c "from Persistance.crawler import Page; from Persistance.createDb import SessionLocal; session = SessionLocal(); session.query(Page).delete(); session.commit(); print('Cleared!')"
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution:**
```powershell
cd backend
pip install -r ../requirements.txt
```

### Problem: "Database connection failed"
**Solution:**
```powershell
# Check PostgreSQL is running
Get-Service postgresql*

# Restart if needed
Restart-Service postgresql-x64-16
```

### Problem: "Permission denied" when scraping
**Solution:** Check `compliance.py` - only these domains are pre-approved:
- theatrecalgary.com
- toyota.ca  
- imdb.com

### Problem: "No data collected"
**Solution:**
```powershell
# Verify tables exist
python db_manager.py stats

# Try a simple test crawl
python -c "from Crawler.http_client import HttpClient; c = HttpClient(); r = c.get('https://example.com'); print(r)"
```

---

## 🎯 Next Steps

1. **Start Small**: Run `run_simple_crawl.py` to test basic functionality
2. **Check Data**: Use `python db_manager.py stats` to verify data is saving
3. **Explore**: Try researching your favorite topics
4. **Automate**: Set up scheduled crawls with Windows Task Scheduler
5. **Analyze**: Export data and analyze with your favorite tools

---

## 📚 Additional Resources

- **Legal Compliance**: See `LEGAL_COMPLIANCE.md`
- **Database Guide**: See `POSTGRESQL_GUIDE.md`
- **Test Coverage**: See `PERSISTENCE_VERIFICATION_COMPLETE.md`
- **API Documentation**: See `README.md` sections on endpoints

---

## ⚡ Quick Command Reference

```powershell
# View data
python db_manager.py stats
python db_manager.py recent --table pages --limit 10
python db_manager.py domains

# Export data
python db_manager.py export --output mydata.csv
python db_manager.py backup --output backup.json

# Run tests
python -m pytest tests/unit/test_persistence.py -v

# Simple crawl
python run_simple_crawl.py

# Topic research
python run_topic_research.py
```

**You're ready to start collecting data! 🚀**
