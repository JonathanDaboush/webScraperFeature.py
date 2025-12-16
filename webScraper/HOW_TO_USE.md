# ✅ YOU'RE READY TO COLLECT DATA!

## What You Have Installed

✅ **PostgreSQL Database** - Running and configured  
✅ **Python Web Scraper** - Fully functional  
✅ **Legal Compliance System** - Respects Terms of Service  
✅ **25 Passing Tests** - Quality assured  

---

## 🎯 HOW TO USE IT (3 Steps)

### Step 1: Open PowerShell in this folder
```powershell
cd C:\Users\USER\Documents\webScraper\backend
```

### Step 2: Run a crawler script

**Option A - Simple Crawl (Easiest)**
```powershell
python run_simple_crawl.py
```
This will crawl 2 pre-approved websites and save the data.

**Option B - Research a Topic**
```powershell
python run_topic_research.py
```
Follow the prompts to research any topic.

**Option C - Safe Crawl (Legal Compliance)**
```powershell
python run_safe_crawl.py
```
Only crawls websites that are pre-approved.

### Step 3: View your collected data
```powershell
python db_manager.py stats
python db_manager.py recent --table pages --limit 5
```

---

## 📊 What Data Gets Collected?

When you crawl a website, the scraper saves:

- ✅ **Page Title** - The title of the webpage
- ✅ **Page Content** - Main text content
- ✅ **Keywords** - Tech skills, products, seasonal themes (848+ keywords)
- ✅ **Links** - All links found on the page
- ✅ **Domain** - The website domain
- ✅ **Timestamp** - When it was crawled
- ✅ **Subjects & Tags** - Categorized topics

All data is stored in your **PostgreSQL database** (`webscraper`).

---

## 🚀 Quick Commands

### View Data
```powershell
# See overall statistics
python db_manager.py stats

# See recent pages
python db_manager.py recent --table pages --limit 10

# See all domains
python db_manager.py domains
```

### Export Data
```powershell
# Export to CSV
python db_manager.py export --output mydata.csv

# Backup to JSON
python db_manager.py backup --output backup.json
```

### Clear Data
```powershell
# Clear all data (WARNING: deletes everything!)
python db_manager.py clear --yes
```

---

## ⚙️ How It Works

1. **You run a script** → Tells the crawler which websites to visit
2. **Crawler checks compliance** → Makes sure scraping is allowed
3. **Fetches the webpage** → Downloads HTML content
4. **Extracts data** → Pulls out title, content, keywords, links
5. **Saves to PostgreSQL** → Stores everything in the database
6. **You view the data** → Use `db_manager.py` to see what was collected

---

## 🎯 Example Usage

### Crawl Python.org and save data:
```powershell
cd backend
python run_simple_crawl.py
```

**Output:**
```
Crawling: https://www.python.org
✓ Title: Welcome to Python.org
✓ Keywords found: 15
✓ Links found: 42
```

### Check what was saved:
```powershell
python db_manager.py recent --table pages --limit 1
```

**Output:**
```
ID: 1
URL: https://www.python.org
Title: Welcome to Python.org
Date: 2025-12-15 16:32:40
Crawled: True
```

---

## 🛡️ Legal & Ethical Scraping

The scraper includes **built-in compliance checks**:

- ✅ Respects `robots.txt` files
- ✅ Rate limiting (delays between requests)
- ✅ Pre-approved website list
- ✅ Checks Terms of Service rules
- ✅ User-agent identification

**Pre-approved websites:**
- theatrecalgary.com
- toyota.ca
- imdb.com

To add more sites, edit: `backend/Crawler/compliance.py`

---

## 🔧 Troubleshooting

### "No module named X"
**Fix:** Install dependencies
```powershell
pip install psycopg2-binary sqlalchemy requests beautifulsoup4
```

### "Database connection failed"
**Fix:** Start PostgreSQL
```powershell
Get-Service postgresql* | Start-Service
```

### "No data collected"
**Fix:** Check if tables exist
```powershell
python db_manager.py stats
```

---

## 📚 More Information

- **Quick Start Guide**: `QUICK_START.md`
- **Legal Compliance**: `LEGAL_COMPLIANCE.md`
- **Database Guide**: `POSTGRESQL_GUIDE.md`
- **Test Results**: `PERSISTENCE_VERIFICATION_COMPLETE.md`

---

## 🎉 You're All Set!

Try it now:
```powershell
cd C:\Users\USER\Documents\webScraper\backend
python run_simple_crawl.py
python db_manager.py stats
```

**Happy scraping! 🚀**
