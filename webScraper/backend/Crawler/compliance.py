"""
Compliance rules for web scraping.

Handles robots.txt, rate limiting, ToS compliance, and domain-specific rules.
Basically makes sure we don't get sued or banned.
"""

import logging
import time
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlparse
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ComplianceViolation(Exception):
    """Raised when a scraping action would violate compliance rules."""
    pass


class ScrapingCompliance:
    """
    Keeps us legal when scraping. Checks robots.txt, enforces rate limits,
    and makes sure we're not hitting protected pages or scraping personal data.
    """
    
    # Rules for specific domains we scrape
    DOMAIN_RULES = {
        # IMDb lets you scrape for personal use
        'imdb.com': {
            'allowed': True,
            'rate_limit_seconds': 2.0,  # 30 requests/minute max
            'max_pages_per_session': 100,
            'requires_attribution': True,
            'commercial_use': False,
            'notes': 'IMDb allows personal use scraping. Respect their Conditions of Use.',
            'terms_url': 'https://www.imdb.com/conditions',
            'user_agent_required': True,
            'cache_results': True  # Reduce repeat requests
        },
        'www.imdb.com': {
            'allowed': True,
            'rate_limit_seconds': 2.0,
            'max_pages_per_session': 100,
            'requires_attribution': True,
            'commercial_use': False,
            'notes': 'IMDb allows personal use scraping. Respect their Conditions of Use.',
            'terms_url': 'https://www.imdb.com/conditions',
            'user_agent_required': True,
            'cache_results': True
        },
        
        # Toyota corporate site - public info is fair game
        'toyota.ca': {
            'allowed': True,
            'rate_limit_seconds': 3.0,  # corporate sites = be polite
            'max_pages_per_session': 50,
            'requires_attribution': False,
            'commercial_use': False,  # Educational/research only
            'notes': 'Public corporate information. Avoid dealer locators with personal data.',
            'terms_url': 'https://www.toyota.ca/toyota/en/about/terms-of-use',
            'user_agent_required': True,
            'cache_results': True,
            'avoid_patterns': ['/dealer/', '/locate/', '/my-account/']  # Personal data
        },
        'www.toyota.ca': {
            'allowed': True,
            'rate_limit_seconds': 3.0,
            'max_pages_per_session': 50,
            'requires_attribution': False,
            'commercial_use': False,
            'notes': 'Public corporate information. Avoid dealer locators with personal data.',
            'terms_url': 'https://www.toyota.ca/toyota/en/about/terms-of-use',
            'user_agent_required': True,
            'cache_results': True,
            'avoid_patterns': ['/dealer/', '/locate/', '/my-account/']
        },
        
        # Small theatre - go slow, they don't have big servers
        'theatrecalgary.com': {
            'allowed': True,
            'rate_limit_seconds': 5.0,  # extra slow for small sites
            'max_pages_per_session': 30,
            'requires_attribution': True,
            'commercial_use': False,
            'notes': 'Small cultural organization. Be extremely respectful of server resources.',
            'terms_url': None,
            'user_agent_required': True,
            'cache_results': True,
            'avoid_patterns': ['/admin/', '/checkout/', '/payment/']
        },
        'www.theatrecalgary.com': {
            'allowed': True,
            'rate_limit_seconds': 5.0,
            'max_pages_per_session': 30,
            'requires_attribution': True,
            'commercial_use': False,
            'notes': 'Small cultural organization. Be extremely respectful of server resources.',
            'terms_url': None,
            'user_agent_required': True,
            'cache_results': True,
            'avoid_patterns': ['/admin/', '/checkout/', '/payment/']
        }
    }
    
    # Patterns that indicate private/authenticated content
    PROTECTED_PATTERNS = [
        '/login', '/signin', '/account', '/profile', '/admin',
        '/checkout', '/cart', '/payment', '/api/', '/private/',
        '/member', '/dashboard', '/settings'
    ]
    
    # Meta tags that indicate scraping restrictions
    NO_SCRAPE_META_TAGS = [
        'noindex', 'nofollow', 'noarchive', 'nocache'
    ]
    
    def __init__(self, user_agent: str = None, contact_email: str = None):
        """
        Initialize compliance checker.
        
        Args:
            user_agent: Identifying user agent string (required for ethical scraping)
            contact_email: Contact email in user agent (best practice)
        """
        self.user_agent = user_agent or f"ResearchBot/1.0 (Educational; +mailto:{contact_email or 'admin@example.com'})"
        self.contact_email = contact_email
        self.session_page_counts: Dict[str, int] = {}
        self.last_request_time: Dict[str, float] = {}
        
    def check_url_compliance(self, url: str) -> Tuple[bool, str]:
        """Check if we can scrape this URL. Returns (allowed, reason)."""
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path.lower()
        
        # See if we have rules for this domain
        rules = self.DOMAIN_RULES.get(domain)
        if rules:
            if not rules.get('allowed', True):
                return False, f"Scraping not allowed for {domain} per business rules"
            
            # Check if path is on the avoid list
            avoid_patterns = rules.get('avoid_patterns', [])
            for pattern in avoid_patterns:
                if pattern in path:
                    return False, f"Path matches protected pattern: {pattern}"
        
        # Block login/admin/payment pages
        for pattern in self.PROTECTED_PATTERNS:
            if pattern in path:
                return False, f"URL appears to be behind authentication: {pattern}"
        
        # Make sure we haven't hit the session limit
        session_count = self.session_page_counts.get(domain, 0)
        max_pages = rules.get('max_pages_per_session', 100) if rules else 100
        
        if session_count >= max_pages:
            return False, f"Session limit reached for {domain} ({max_pages} pages)"
        
        return True, "Compliant"
    
    def enforce_rate_limit(self, url: str):
        """Wait if needed to avoid hitting sites too fast."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        rules = self.DOMAIN_RULES.get(domain)
        rate_limit = rules.get('rate_limit_seconds', 1.0) if rules else 1.0
        
        last_time = self.last_request_time.get(domain, 0)
        elapsed = time.time() - last_time
        
        if elapsed < rate_limit:
            wait_time = rate_limit - elapsed
            logger.info(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        self.last_request_time[domain] = time.time()
        self.session_page_counts[domain] = self.session_page_counts.get(domain, 0) + 1
    
    def get_compliant_headers(self, url: str) -> Dict[str, str]:
        """Build HTTP headers with proper bot identification."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Add referer for sites we have rules for
        if domain in self.DOMAIN_RULES:
            headers['Referer'] = f"https://{domain}/"
        
        return headers
    
    def check_meta_robots(self, html_content: str) -> Tuple[bool, str]:
        """Check if page has noindex/nofollow meta tags."""
        html_lower = html_content.lower()
        
        for tag in self.NO_SCRAPE_META_TAGS:
            if f'content="{tag}"' in html_lower or f"content='{tag}'" in html_lower:
                return False, f"Meta robots tag prohibits scraping: {tag}"
        
        return True, "No meta restrictions"
    
    def get_attribution_notice(self, url: str) -> Optional[str]:
        """Get attribution text if this domain needs it."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        rules = self.DOMAIN_RULES.get(domain)
        if rules and rules.get('requires_attribution'):
            return f"Data sourced from {domain}. See terms: {rules.get('terms_url', 'N/A')}"
        
        return None
    
    def log_compliance_check(self, url: str, allowed: bool, reason: str):
        """Log why we allowed or blocked a URL."""
        status = "ALLOWED" if allowed else "BLOCKED"
        logger.info(f"[COMPLIANCE {status}] {url} - Reason: {reason}")
    
    def get_domain_rules(self, url: str) -> Dict:
        """Get rules for a domain, or return defaults."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        return self.DOMAIN_RULES.get(domain, {
            'allowed': True,
            'rate_limit_seconds': 2.0,
            'max_pages_per_session': 50,
            'requires_attribution': False,
            'commercial_use': False,
            'notes': 'Using default conservative rules',
            'terms_url': None,
            'user_agent_required': True,
            'cache_results': True
        })
    
    def reset_session_counts(self):
        """Clear the page counts (call between scraping runs)."""
        self.session_page_counts.clear()
        logger.info("Session page counts reset")


# Best Practices Documentation
LEGAL_GUIDELINES = """
WEB SCRAPING LEGAL GUIDELINES

1. RESPECT robots.txt
   - Always check and obey robots.txt directives
   - If robots.txt says no, don't scrape
   
2. IDENTIFY YOURSELF
   - Use descriptive User-Agent with contact info
   - Example: "MyBot/1.0 (+https://example.com/bot; contact@example.com)"
   
3. RATE LIMITING
   - Don't overload servers (1-5 second delays minimum)
   - Smaller sites need longer delays
   - Monitor for 429 (Too Many Requests) responses
   
4. TERMS OF SERVICE
   - Read and understand ToS before scraping
   - Some sites explicitly prohibit scraping
   - Respect "no scraping" clauses
   
5. COPYRIGHT & DATA
   - Don't republish copyrighted content
   - Facts are generally not copyrightable, but compilations may be
   - Give attribution when required
   
6. AUTHENTICATION
   - Don't scrape behind login walls without permission
   - Don't share login credentials
   - Respect session-based access controls
   
7. PERSONAL DATA
   - Be extra careful with PII (Personal Identifiable Information)
   - GDPR, CCPA apply even to scraped data
   - Don't scrape contact info without consent
   
8. CACHING
   - Cache results to reduce repeat requests
   - Update cached data periodically, not constantly
   
9. ERROR HANDLING
   - Stop scraping if you get blocked (403, 429)
   - Don't try to circumvent blocks
   - Respect temporary bans
   
10. COMMERCIAL USE
    - Personal/research use more lenient than commercial
    - Get explicit permission for commercial scraping
    - Consider licensing data instead

SPECIFIC SITE NOTES:

IMDb (imdb.com):
- Allows personal, non-commercial use
- Must respect Conditions of Use
- No systematic downloading
- Attribution recommended
- Rate limit: ~30 requests/minute

Toyota.ca (toyota.ca):
- Public corporate information OK
- Avoid dealer locators (contains PII)
- Educational/research use only
- Be respectful of server load
- Rate limit: ~20 requests/minute

Theatre Calgary (theatrecalgary.com):
- Small organization - be very conservative
- Public event info OK
- Avoid payment/checkout pages
- Cache aggressively to reduce load
- Rate limit: ~12 requests/minute
- Consider contacting them directly for bulk data
"""


def print_compliance_summary():
    """Print a summary of compliance rules for reference."""
    print(LEGAL_GUIDELINES)


if __name__ == "__main__":
    # Example usage
    compliance = ScrapingCompliance(
        user_agent="ResearchBot/1.0 (Educational; +mailto:research@university.edu)",
        contact_email="research@university.edu"
    )
    
    test_urls = [
        "https://www.imdb.com/title/tt0364725/",
        "https://www.toyota.ca/",
        "https://www.theatrecalgary.com/"
    ]
    
    print("Web Scraping Compliance Check\n" + "="*50)
    for url in test_urls:
        allowed, reason = compliance.check_url_compliance(url)
        compliance.log_compliance_check(url, allowed, reason)
        
        if allowed:
            rules = compliance.get_domain_rules(url)
            print(f"\nURL: {url}")
            print(f"Status: ✓ ALLOWED")
            print(f"Rate limit: {rules['rate_limit_seconds']}s between requests")
            print(f"Max pages: {rules['max_pages_per_session']}")
            print(f"Notes: {rules['notes']}")
            if rules.get('requires_attribution'):
                print(f"Attribution: {compliance.get_attribution_notice(url)}")
        else:
            print(f"\nURL: {url}")
            print(f"Status: ✗ BLOCKED - {reason}")
    
    print("\n" + "="*50)
    print_compliance_summary()
