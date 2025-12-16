# Quick Reference: Legal Web Scraping

## ✅ What's Already Implemented

### Automatic Compliance Features
1. **robots.txt checking** - Built into BaseScraper
2. **Rate limiting** - Domain-specific delays enforced
3. **User-Agent identification** - Clear bot identification with contact
4. **Session limits** - Prevents bulk downloading
5. **Protected patterns** - Blocks /login, /admin, /checkout, etc.
6. **Meta robots checking** - Respects noindex, nofollow tags
7. **Audit logging** - All compliance decisions logged

### Configured Domains

| Domain | Rate Limit | Max Pages | Attribution | Commercial |
|--------|------------|-----------|-------------|------------|
| **theatrecalgary.com** | 5s (12/min) | 30 | Yes | No |
| **toyota.ca** | 3s (20/min) | 50 | No | No |
| **imdb.com** | 2s (30/min) | 100 | Yes | No |

## 🚀 Quick Start

### Scrape a Single Page

```python
from Crawler.http_client import HttpClient
from Crawler.research_crawler import ResearchCrawler
from Persistance.repository import Repository

# Initialize
http = HttpClient()
repo = Repository()
crawler = ResearchCrawler(
    http_client=http,
    repository=repo,
    contact_email="your-email@example.com"  # REQUIRED!
)

# Scrape (compliance checks automatic)
data = crawler.crawl_page(
    url="https://www.imdb.com/title/tt0364725/",
    keywords=["movie"]
)
```

### Run Compliance Demo

```bash
# Check compliance for all three URLs
python backend/Crawler/compliance.py

# Full demonstration
python backend/Crawler/example_compliance_demo.py
```

## ⚠️ Important Rules

### ALWAYS
- ✅ Identify bot with User-Agent + contact email
- ✅ Respect robots.txt (automatic)
- ✅ Rate limit (1-5 seconds minimum)
- ✅ Read Terms of Service
- ✅ Cache results to reduce requests
- ✅ Give attribution if required
- ✅ Use for educational/research only

### NEVER
- ❌ Scrape behind login/authentication
- ❌ Circumvent access controls
- ❌ Scrape personal data without consent
- ❌ Ignore 429 (Too Many Requests) responses
- ❌ Use for commercial purposes without permission
- ❌ Republish copyrighted content

## 🎯 Specific Site Rules

### Theatre Calgary
```python
# Small organization - be very respectful
rate_limit = 5 seconds  # Very conservative
max_pages = 30 per session
avoid = ['/admin/', '/checkout/', '/payment/']
attribution = "Data from www.theatrecalgary.com"
```

### Toyota Canada
```python
# Corporate site - public info OK
rate_limit = 3 seconds
max_pages = 50 per session
avoid = ['/dealer/', '/locate/', '/my-account/']  # PII
commercial_use = False  # Educational only
```

### IMDb
```python
# Allows personal use per ToS
rate_limit = 2 seconds
max_pages = 100 per session
attribution = "Data from www.imdb.com"
terms = "https://www.imdb.com/conditions"
commercial_use = False  # Personal/educational only
```

## 🛡️ Protected URL Patterns

These are automatically blocked:
- `/login`, `/signin`, `/account`, `/profile`
- `/admin`, `/dashboard`, `/settings`
- `/checkout`, `/cart`, `/payment`
- `/api/`, `/private/`, `/member/`

## 📝 Required User-Agent Format

```
BotName/Version (Purpose; +mailto:contact@example.com)
```

Example:
```
ResearchBot/1.0 (Educational; +mailto:research@university.edu)
```

## 🔍 Compliance Checks (Automatic)

Every request goes through:
1. URL compliance check (domain rules)
2. Rate limiting enforcement (delays)
3. Meta robots check (HTML tags)
4. Session limit check (max pages)
5. Protected pattern check (URLs)

## 📊 Logging

All decisions logged:
```
[COMPLIANCE ALLOWED] url - Reason: Compliant
[COMPLIANCE BLOCKED] url - Reason: Protected pattern
```

## 🆘 What to Do If Blocked

1. **Check robots.txt** - We honor it automatically
2. **Review rate limits** - May be too aggressive
3. **Check ToS** - Site may prohibit scraping
4. **Contact site owner** - Ask for permission
5. **Consider API** - Official data access

## 📧 Contact Info

Make sure to set your contact email:
```python
crawler = ResearchCrawler(
    ...,
    contact_email="your-actual-email@domain.com"
)
```

This lets site owners contact you if needed.

## 📚 Full Documentation

See `LEGAL_COMPLIANCE.md` for complete details.

---

**Remember**: When in doubt, be MORE conservative, not less!
