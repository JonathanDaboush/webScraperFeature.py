"""
Web Scraper Crawler Package

Components:
    - config: Configuration management
    - http_client: Reliable HTTP client with retries, rate limiting
    - parsers: HTML/JSON parsing and extraction
    - scrapers: Site-specific scraping logic
    - normalizer: Transform raw data → canonical format
    - deduper: Similarity-based deduplication
    - scheduler: Job scheduling with backoff
    - worker: Pipeline orchestration

Usage:
    from Crawler.worker import Worker
    from Persistance.createDb import SessionLocal as Session
    
    session = Session()
    worker = Worker(session)
    worker.run_continuously()
"""

__version__ = "1.0.0"

from Crawler.config import get_config, Config
from Crawler.http_client import HttpClient, RateLimiter
from Crawler.scrapers import BaseScraper, GenericScraper, get_scraper
from Crawler.normalizer import normalize
from Crawler.deduper import is_duplicate, deduplicate_batch
from Crawler.scheduler import Scheduler
from Crawler.worker import Worker

__all__ = [
    'get_config',
    'Config',
    'HttpClient',
    'RateLimiter',
    'BaseScraper',
    'GenericScraper',
    'get_scraper',
    'normalize',
    'is_duplicate',
    'deduplicate_batch',
    'Scheduler',
    'Worker'
]
