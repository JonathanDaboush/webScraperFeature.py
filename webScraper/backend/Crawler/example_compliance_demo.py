"""
Legal Web Scraping Demonstration

This script demonstrates compliant scraping of:
1. https://www.theatrecalgary.com/
2. https://www.toyota.ca/
3. https://www.imdb.com/title/tt0364725/

Following all legal and ethical guidelines.
"""

import sys
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from Crawler.http_client import HttpClient, RateLimiter
from Crawler.research_crawler import ResearchCrawler
from Crawler.compliance import ScrapingCompliance, print_compliance_summary
from Persistance.createDb import SessionLocal
from Persistance.repository import Repository

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demonstrate_compliance_checks():
    """
    Demonstrate compliance checks before scraping.
    """
    print("\n" + "="*70)
    print("WEB SCRAPING LEGAL COMPLIANCE DEMONSTRATION")
    print("="*70 + "\n")
    
    # Initialize compliance checker
    compliance = ScrapingCompliance(
        user_agent="ResearchBot/1.0 (Educational Research; +mailto:research@university.edu)",
        contact_email="research@university.edu"
    )
    
    # Test URLs
    urls = [
        "https://www.theatrecalgary.com/",
        "https://www.toyota.ca/",
        "https://www.imdb.com/title/tt0364725/"
    ]
    
    print("COMPLIANCE PRE-CHECK FOR TARGET URLS\n")
    
    for url in urls:
        print(f"\n{'='*70}")
        print(f"URL: {url}")
        print(f"{'='*70}")
        
        # Check compliance
        allowed, reason = compliance.check_url_compliance(url)
        
        if allowed:
            print(f"✓ STATUS: ALLOWED TO SCRAPE")
            print(f"  Reason: {reason}")
            
            # Get domain-specific rules
            rules = compliance.get_domain_rules(url)
            
            print(f"\n  DOMAIN-SPECIFIC RULES:")
            print(f"  - Rate Limit: {rules['rate_limit_seconds']} seconds between requests")
            print(f"  - Max Pages/Session: {rules['max_pages_per_session']}")
            print(f"  - Commercial Use: {'Yes' if rules['commercial_use'] else 'No - Educational/Personal Only'}")
            print(f"  - Attribution Required: {'Yes' if rules['requires_attribution'] else 'No'}")
            print(f"  - Cache Results: {'Yes' if rules['cache_results'] else 'No'}")
            
            if rules.get('notes'):
                print(f"\n  NOTES: {rules['notes']}")
            
            if rules.get('terms_url'):
                print(f"  Terms of Service: {rules['terms_url']}")
            
            if rules.get('avoid_patterns'):
                print(f"  Avoid Patterns: {', '.join(rules['avoid_patterns'])}")
            
            # Attribution notice
            attribution = compliance.get_attribution_notice(url)
            if attribution:
                print(f"\n  REQUIRED ATTRIBUTION:")
                print(f"  {attribution}")
            
            # Compliant headers
            headers = compliance.get_compliant_headers(url)
            print(f"\n  COMPLIANT HEADERS:")
            print(f"  User-Agent: {headers['User-Agent']}")
            print(f"  DNT: {headers['DNT']} (Do Not Track)")
            
        else:
            print(f"✗ STATUS: BLOCKED")
            print(f"  Reason: {reason}")
    
    print(f"\n{'='*70}\n")


def demonstrate_rate_limiting():
    """
    Demonstrate rate limiting in action.
    """
    print("\nRATE LIMITING DEMONSTRATION\n")
    print("="*70)
    
    compliance = ScrapingCompliance(
        contact_email="research@university.edu"
    )
    
    test_url = "https://www.theatrecalgary.com/"
    
    print(f"Demonstrating rate limiting for: {test_url}")
    print(f"(Theatre Calgary has 5-second rate limit for respectful scraping)\n")
    
    import time
    
    for i in range(3):
        start = time.time()
        compliance.enforce_rate_limit(test_url)
        elapsed = time.time() - start
        
        print(f"Request {i+1}: Waited {elapsed:.2f} seconds")
    
    print("\n" + "="*70)


def scrape_with_compliance(url: str, keywords: list = None):
    """
    Scrape a URL with full compliance checks.
    """
    print(f"\n\nSCRAPING: {url}")
    print("="*70)
    
    # Initialize components
    http_client = HttpClient(
        timeout_seconds=30,
        rate_limiter=RateLimiter(requests_per_minute=20)
    )
    
    # Mock repository for demo (don't actually save)
    class MockRepo:
        def __init__(self):
            self.session = None
    
    repo = MockRepo()
    
    # Initialize crawler with compliance
    crawler = ResearchCrawler(
        http_client=http_client,
        repository=repo,
        contact_email="research@university.edu"
    )
    
    # Crawl page
    try:
        page_data = crawler.crawl_page(url, keywords or [])
        
        if page_data:
            print(f"\n✓ Successfully scraped: {url}")
            print(f"\nExtracted Data:")
            print(f"  Title: {page_data.get('title', 'N/A')[:80]}...")
            print(f"  Content Length: {len(page_data.get('content', ''))} chars")
            print(f"  Subjects Found: {len(page_data.get('subjects', []))}")
            print(f"  Tags Found: {len(page_data.get('tags', []))}")
            print(f"  Tech Skills: {len(page_data.get('tech_skills', []))}")
            print(f"  Product Categories: {len(page_data.get('product_categories', []))}")
            
            # Show compliance was followed
            print(f"\n  COMPLIANCE SUMMARY:")
            print(f"  ✓ robots.txt checked")
            print(f"  ✓ Rate limiting enforced")
            print(f"  ✓ Meta robots tags checked")
            print(f"  ✓ Proper User-Agent used")
            print(f"  ✓ Session limits respected")
        else:
            print(f"\n✗ Could not scrape {url} (compliance block or fetch error)")
    
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        print(f"\n✗ Error: {e}")
    
    print("="*70)


def main():
    """
    Main demonstration function.
    """
    print("\n" + "="*70)
    print("LEGAL WEB SCRAPING BEST PRACTICES DEMONSTRATION")
    print("="*70)
    
    print("\nThis demonstration shows how to scrape websites legally and ethically.")
    print("We will check compliance for three specific URLs:\n")
    print("1. Theatre Calgary - Small cultural organization")
    print("2. Toyota Canada - Corporate website")
    print("3. IMDb - Large database with specific ToS")
    
    # Step 1: Show compliance checks
    demonstrate_compliance_checks()
    
    # Step 2: Show rate limiting
    demonstrate_rate_limiting()
    
    # Step 3: Show legal guidelines
    print("\n\nLEGAL GUIDELINES SUMMARY")
    print("="*70)
    print_compliance_summary()
    
    # Step 4: Offer to perform actual scraping (commented out for safety)
    print("\n\nACTUAL SCRAPING (Demo Mode)")
    print("="*70)
    print("\nTo perform actual scraping, uncomment the scraping calls below.")
    print("Make sure you have reviewed and agree to each site's Terms of Service.\n")
    
    # Uncomment these to perform actual scraping:
    # from typing import List
    # scrape_with_compliance("https://www.theatrecalgary.com/", ["theatre", "events"])
    # scrape_with_compliance("https://www.toyota.ca/", ["vehicles", "cars"])
    # scrape_with_compliance("https://www.imdb.com/title/tt0364725/", ["movie", "cast"])
    
    print("\nDemonstration complete!")
    print("\nKEY TAKEAWAYS:")
    print("✓ Always check robots.txt")
    print("✓ Use domain-specific rate limits")
    print("✓ Identify your bot clearly")
    print("✓ Read and respect Terms of Service")
    print("✓ Be extra cautious with small websites")
    print("✓ Cache results to reduce server load")
    print("✓ Give attribution when required")
    print("✓ Never scrape personal data without consent")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user.")
    except Exception as e:
        logger.error(f"Demonstration error: {e}")
        raise
