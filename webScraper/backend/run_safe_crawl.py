"""
Safe Web Crawler with Legal Compliance

Only crawls pre-approved websites that respect Terms of Service.
"""

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Crawler.compliance import ScrapingCompliance
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal


def main():
    print("=" * 60)
    print("SAFE WEB CRAWLER - Legal Compliance Enabled")
    print("=" * 60)
    print()
    
    # Setup with compliance checking
    print("Setting up crawler with compliance checks...")
    client = HttpClient()
    session = SessionLocal()
    repo = Repository(session)
    compliance = ScrapingCompliance()
    
    # Pre-approved URLs (configured in compliance.py)
    approved_sites = [
        ("https://www.theatrecalgary.com", ["theatre", "shows", "events"]),
        ("https://www.toyota.ca", ["cars", "vehicles"]),
        ("https://www.imdb.com", ["movies", "films"]),
    ]
    
    print(f"Found {len(approved_sites)} pre-approved sites")
    print()
    
    # Crawl each approved site
    for url, keywords in approved_sites:
        print("-" * 60)
        print(f"Checking: {url}")
        
        # Check compliance first
        allowed, reason = compliance.check_url_compliance(url)
        
        if allowed:
            print(f"  ✓ ALLOWED - {reason}")
            
            # Get rate limit for this domain
            rate_limit = compliance.get_rate_limit(url)
            print(f"  ⏱  Rate limit: {rate_limit}s between requests")
            print(f"  🏷  Keywords: {', '.join(keywords)}")
            print()
            
            try:
                crawler = ResearchCrawler(client, repo)
                result = crawler.crawl_page(url, keywords)
                
                print(f"  ✓ Success!")
                print(f"    Title: {result['title']}")
                print(f"    Keywords: {len(result.get('keywords', {}))} found")
                print(f"    Links: {len(result.get('links', []))} found")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
            
            # Respect rate limiting
            print(f"  ⏱  Waiting {rate_limit}s (rate limiting)...")
            time.sleep(rate_limit)
            
        else:
            print(f"  ✗ BLOCKED - {reason}")
        
        print()
    
    session.close()
    
    print("=" * 60)
    print("SAFE CRAWLING COMPLETE!")
    print("=" * 60)
    print()
    print("All data collected legally and ethically.")
    print()
    print("View collected data:")
    print("  python db_manager.py stats")
    print("  python db_manager.py domains")
    print()
    print("Add more approved sites by editing:")
    print("  backend/Crawler/compliance.py")
    print()


if __name__ == "__main__":
    main()
