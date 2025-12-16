# Web Scraping Legal Compliance Implementation

## Overview

This document outlines the legal and ethical web scraping practices implemented as business rules for the webScraper project, with specific configurations for:

1. **Theatre Calgary** (https://www.theatrecalgary.com/)
2. **Toyota Canada** (https://www.toyota.ca/)
3. **IMDb** (https://www.imdb.com/title/tt0364725/)

## Legal Framework Compliance

### 1. Computer Fraud and Abuse Act (CFAA) Compliance
- ✅ **No circumvention of access controls**: Only scrape publicly accessible pages
- ✅ **Respect access restrictions**: Don't scrape behind login/authentication
- ✅ **Honor robots.txt**: Automated checking implemented in `scrapers.py`

### 2. Copyright Law Respect
- ✅ **No republishing copyrighted content**: Data used for research/analysis only
- ✅ **Attribution where required**: Automatic attribution notices for specific domains
- ✅ **Fair use compliance**: Educational/research purposes only

### 3. Terms of Service (ToS) Awareness
- ✅ **Site-specific rules documented**: Each domain has specific business rules
- ✅ **No systematic downloading**: Session limits prevent bulk downloading
- ✅ **Commercial use restrictions**: Flagged as non-commercial educational use

## Implementation Files

### Core Compliance Module
**File**: `backend/Crawler/compliance.py`

This module implements:
- Domain-specific scraping rules
- Rate limiting enforcement
- User-Agent identification
- Session limits
- Protected pattern detection
- Meta robots tag checking
- Attribution requirements

### Integration Points

1. **ResearchCrawler** (`backend/Crawler/research_crawler.py`)
   - Pre-request compliance checks
   - Rate limiting enforcement
   - Meta robots validation
   - Compliant header generation

2. **BaseScraper** (`backend/crawler/scrapers.py`)
   - robots.txt checking (existing)
   - Polite delays between requests

3. **HttpClient** (`backend/Crawler/http_client.py`)
   - Rate limiting (existing)
   - User-Agent rotation (existing)
   - Captcha detection (existing)

## Domain-Specific Rules

### Theatre Calgary (theatrecalgary.com)

**Legal Status**: ✅ Allowed with restrictions

**Business Rules**:
```python
{
    'allowed': True,
    'rate_limit_seconds': 5.0,  # Very conservative for small org
    'max_pages_per_session': 30,
    'requires_attribution': True,
    'commercial_use': False,
    'notes': 'Small cultural organization. Be extremely respectful of server resources.',
    'user_agent_required': True,
    'cache_results': True,
    'avoid_patterns': ['/admin/', '/checkout/', '/payment/']
}
```

**Rationale**:
- Small organization with limited server resources
- Public event information is publicly accessible
- Extra conservative rate limiting (12 requests/minute)
- Avoid e-commerce/payment pages
- Cache aggressively to reduce load

**Legal Considerations**:
- No explicit ToS found, so applying default "respectful use" standards
- Public information (event schedules, descriptions) generally scrapable
- Avoid any payment processing or checkout pages
- Consider contacting directly for bulk data needs

---

### Toyota Canada (toyota.ca)

**Legal Status**: ✅ Allowed with restrictions

**Business Rules**:
```python
{
    'allowed': True,
    'rate_limit_seconds': 3.0,  # Polite for corporate site
    'max_pages_per_session': 50,
    'requires_attribution': False,
    'commercial_use': False,
    'notes': 'Public corporate information. Avoid dealer locators with personal data.',
    'terms_url': 'https://www.toyota.ca/toyota/en/about/terms-of-use',
    'user_agent_required': True,
    'cache_results': True,
    'avoid_patterns': ['/dealer/', '/locate/', '/my-account/']
}
```

**Rationale**:
- Public corporate website with general information
- Product specifications and public data are typically allowed
- Dealer locators contain personal data (names, addresses) - must avoid
- Terms of Use allow reasonable access
- Rate limit: 20 requests/minute

**Legal Considerations**:
- Review ToS: https://www.toyota.ca/toyota/en/about/terms-of-use
- Public product information is factual data (not copyrightable)
- Avoid personal data (dealer information, user accounts)
- Educational/research use only (no commercial reselling)

---

### IMDb (imdb.com)

**Legal Status**: ✅ Allowed for personal/non-commercial use

**Business Rules**:
```python
{
    'allowed': True,
    'rate_limit_seconds': 2.0,  # 30 requests/minute max
    'max_pages_per_session': 100,
    'requires_attribution': True,
    'commercial_use': False,
    'notes': 'IMDb allows personal use scraping. Respect their Conditions of Use.',
    'terms_url': 'https://www.imdb.com/conditions',
    'user_agent_required': True,
    'cache_results': True
}
```

**Rationale**:
- IMDb Conditions of Use allow personal, non-commercial scraping
- Must not systematically download entire database
- Respect rate limits (30 requests/minute)
- Attribution required
- Cache results to minimize repeat requests

**Legal Considerations**:
- Review Conditions of Use: https://www.imdb.com/conditions
- Personal/educational use is allowed
- No commercial use without licensing
- No systematic downloading of entire database
- Must identify bot with User-Agent
- Respect robots.txt (already implemented)

## Technical Implementation

### Compliance Checks (Automated)

Each request goes through these checks:

1. **URL Compliance Check**
   ```python
   allowed, reason = compliance.check_url_compliance(url)
   if not allowed:
       logger.warning(f"[COMPLIANCE] Blocked {url}: {reason}")
       return None
   ```

2. **Rate Limiting Enforcement**
   ```python
   compliance.enforce_rate_limit(url)  # Blocks until safe to request
   ```

3. **Meta Robots Check**
   ```python
   meta_allowed, meta_reason = compliance.check_meta_robots(html)
   if not meta_allowed:
       logger.warning(f"[COMPLIANCE] Meta robots blocks {url}")
       return None
   ```

4. **Compliant Headers**
   ```python
   headers = compliance.get_compliant_headers(url)
   # Includes proper User-Agent with contact email
   ```

### User-Agent Identification

All requests use a clear, identifiable User-Agent:

```
ResearchBot/1.0 (Educational; +mailto:research@example.com)
```

This allows site owners to:
- Identify the bot
- Contact us if there are issues
- Understand the purpose (educational)

### Session Limits

Prevent bulk downloading:
- Theatre Calgary: 30 pages per session
- Toyota Canada: 50 pages per session
- IMDb: 100 pages per session

### Protected Patterns

Automatically block these URL patterns:
- `/login`, `/signin`, `/account` (authentication)
- `/admin`, `/dashboard` (administrative)
- `/checkout`, `/cart`, `/payment` (e-commerce)
- `/api/` (API endpoints)
- `/private/`, `/member/` (private areas)

## Usage Examples

### Basic Scraping with Compliance

```python
from Crawler.http_client import HttpClient
from Crawler.research_crawler import ResearchCrawler
from Persistance.repository import Repository

# Initialize with proper identification
http_client = HttpClient()
repo = Repository()

crawler = ResearchCrawler(
    http_client=http_client,
    repository=repo,
    contact_email="research@university.edu"  # Required!
)

# Scrape with automatic compliance checks
page_data = crawler.crawl_page(
    url="https://www.imdb.com/title/tt0364725/",
    keywords=["movie", "cast"]
)
```

### Running Compliance Demo

```bash
cd backend/Crawler
python compliance.py  # Shows compliance check for all three URLs
```

### Running Full Demo

```bash
cd backend/Crawler
python example_compliance_demo.py  # Full demonstration with examples
```

## Best Practices Checklist

Before scraping any website:

- [ ] Check robots.txt (automated)
- [ ] Read Terms of Service
- [ ] Identify bot with User-Agent + contact email
- [ ] Implement rate limiting (1-5 seconds minimum)
- [ ] Set session limits (avoid bulk downloading)
- [ ] Cache results (reduce repeat requests)
- [ ] Avoid authentication-required pages
- [ ] Don't scrape personal data without consent
- [ ] Give attribution if required
- [ ] Use for educational/research only (not commercial)
- [ ] Monitor for 429 (Too Many Requests) responses
- [ ] Stop if you get blocked (don't circumvent)

## Audit Trail

All compliance decisions are logged:

```
[COMPLIANCE ALLOWED] https://www.imdb.com/title/tt0364725/ - Reason: Compliant
[COMPLIANCE BLOCKED] https://www.toyota.ca/dealer/locator - Reason: Path matches protected pattern: /dealer/
```

## Legal Disclaimer

This implementation follows web scraping best practices and common legal standards. However:

- **Always review each site's Terms of Service**
- **Get explicit permission for commercial use**
- **Consult legal counsel for specific use cases**
- **Laws vary by jurisdiction**
- **This is educational software - use responsibly**

## Attribution Requirements

When using data from these sources:

### Theatre Calgary
```
Data sourced from www.theatrecalgary.com
```

### Toyota Canada
No attribution required (but recommended for transparency)

### IMDb
```
Data sourced from www.imdb.com
See terms: https://www.imdb.com/conditions
```

## Contact for Issues

If site owners have concerns, they can:
1. Check robots.txt (we honor it automatically)
2. Contact via email in User-Agent
3. Return 429 status (we stop scraping)
4. Block User-Agent (we respect it)

## Updates and Maintenance

- Review compliance rules quarterly
- Update based on ToS changes
- Monitor for site owner feedback
- Adjust rate limits if needed
- Add new domains as required

## References

### Legal Resources
- Computer Fraud and Abuse Act (CFAA)
- Copyright Law (Title 17 U.S. Code)
- GDPR (EU) and CCPA (California) for personal data
- robots.txt RFC 9309

### Site-Specific Terms
- IMDb Conditions of Use: https://www.imdb.com/conditions
- Toyota Canada Terms: https://www.toyota.ca/toyota/en/about/terms-of-use
- Theatre Calgary: (No explicit terms found - using conservative defaults)

---

**Last Updated**: December 15, 2025
**Version**: 1.0
**Maintainer**: WebScraper Development Team
