"""
Simple Web Crawler - Quick Start Example

This script demonstrates how to crawl a single webpage and save it to the database.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal


def main():
    print("=" * 60)
    print("SIMPLE WEB CRAWLER - QUICK START")
    print("=" * 60)
    print()
    
    # Setup
    print("Setting up crawler...")
    client = HttpClient()
    session = SessionLocal()
    repo = Repository(session)
    crawler = ResearchCrawler(client, repo)
    
    # URLs to crawl (these respect legal compliance!)
    urls = [
        ("https://www.theatrecalgary.com", ["theatre", "events", "shows"]),
        ("https://www.python.org", ["python", "programming"]),
    ]
    
    print(f"Ready to crawl {len(urls)} websites\n")
    
    # Crawl each URL
    for url, keywords in urls:
        print(f"Crawling: {url}")
        print(f"Keywords: {', '.join(keywords)}")
        
        try:
            result = crawler.crawl_page(url, keywords)
            
            print(f"  ✓ Title: {result['title']}")
            print(f"  ✓ Keywords found: {len(result.get('keywords', {}))}")
            print(f"  ✓ Links found: {len(result.get('links', []))}")
            
            # Show some keywords if found
            if result.get('keywords'):
                tech = result['keywords'].get('tech', [])
                products = result['keywords'].get('products', [])
                
                if tech:
                    print(f"  ✓ Tech keywords: {', '.join(tech[:5])}")
                if products:
                    print(f"  ✓ Product keywords: {', '.join(products[:5])}")
            
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()
    
    session.close()
    
    print("=" * 60)
    print("CRAWLING COMPLETE!")
    print("=" * 60)
    print()
    print("View your data:")
    print("  python db_manager.py stats")
    print("  python db_manager.py recent --table pages --limit 5")
    print()


if __name__ == "__main__":
    main()
