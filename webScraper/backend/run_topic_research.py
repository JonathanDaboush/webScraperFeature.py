"""
Topic Research Example

Research a specific topic by crawling multiple related pages.
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
    print("TOPIC RESEARCH CRAWLER")
    print("=" * 60)
    print()
    
    # Setup
    print("Setting up researcher...")
    client = HttpClient()
    session = SessionLocal()
    repo = Repository(session)
    crawler = ResearchCrawler(client, repo)
    
    # Choose a topic to research
    topic = input("Enter topic to research (or press Enter for 'Python'): ").strip()
    if not topic:
        topic = "Python"
    
    # Starting URL
    start_url = input(f"Enter starting URL (or press Enter for python.org): ").strip()
    if not start_url:
        start_url = "https://www.python.org"
    
    # How many pages to crawl
    try:
        max_pages = int(input("How many pages to crawl? (1-10, default 3): ").strip() or "3")
        max_pages = min(max(1, max_pages), 10)  # Limit between 1-10
    except ValueError:
        max_pages = 3
    
    print()
    print(f"Researching: {topic}")
    print(f"Starting at: {start_url}")
    print(f"Max pages: {max_pages}")
    print()
    print("Starting research...")
    print("-" * 60)
    
    try:
        results = crawler.research_topic(
            start_url=start_url,
            search_terms=[topic.lower()],
            max_pages=max_pages
        )
        
        print()
        print("=" * 60)
        print(f"RESEARCH COMPLETE - Found {len(results)} pages")
        print("=" * 60)
        print()
        
        for i, page in enumerate(results, 1):
            print(f"{i}. {page['title']}")
            print(f"   URL: {page['url']}")
            
            if page.get('keywords'):
                total_keywords = sum(len(v) for v in page['keywords'].values())
                print(f"   Keywords: {total_keywords} found")
            
            if page.get('links'):
                print(f"   Links: {len(page['links'])} found")
            
            print()
        
        print("-" * 60)
        print("Data saved to database!")
        print()
        print("View your research:")
        print("  python db_manager.py recent --table pages --limit 10")
        print(f"  python db_manager.py query --sql \"SELECT * FROM pages WHERE title LIKE '%{topic}%'\"")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during research: {e}")
        print()
    
    finally:
        session.close()


if __name__ == "__main__":
    main()
