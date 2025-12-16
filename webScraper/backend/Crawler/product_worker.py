"""
E-Commerce Product Crawler Worker

Orchestrates product scraping, normalization, and price tracking.
"""

import logging
import time
from typing import Optional, Dict
from datetime import datetime

from sqlalchemy.orm import Session

from crawler.config import get_config
from crawler.http_client import HttpClient, RateLimiter
from crawler.product_scrapers import get_product_scraper
from crawler.product_normalizer import normalize_product
from crawler.product_repository import ProductRepository

from Persistance.createDb import Session as DBSession
from Persistance.crawler import ProductRun, ProductSource

logger = logging.getLogger(__name__)


class ProductWorker:
    """
    Worker for e-commerce product scraping and price tracking.
    """
    
    def __init__(self, session: Session, config=None):
        self.session = session
        self.config = config or get_config()
        self.repo = ProductRepository(session)
        
        # Initialize HTTP client
        self.http_client = HttpClient(
            timeout_seconds=self.config.TIMEOUT_SECONDS,
            max_retries=self.config.MAX_RETRIES,
            backoff_base_seconds=self.config.RETRY_BASE_SECONDS,
            user_agents=self.config.USER_AGENT_POOL,
            proxy_pool=self.config.PROXY_POOL,
            rate_limiter=RateLimiter(self.config.REQUESTS_PER_DOMAIN_PER_MINUTE)
        )
    
    def run_scrape(self, source_id: int) -> Dict:
        """
        Scrape products from a source.
        
        Returns:
            {
                'raw_count': int,
                'new_count': int,
                'updated_count': int,
                'price_changes': int,
                'error': str | None
            }
        """
        stats = {
            'raw_count': 0,
            'new_count': 0,
            'updated_count': 0,
            'price_changes': 0,
            'error': None
        }
        
        try:
            # Get source
            source = self.session.query(ProductSource).filter(
                ProductSource.id == source_id
            ).first()
            
            if not source:
                raise ValueError(f"ProductSource not found: {source_id}")
            
            logger.info(f"Starting product scrape for: {source.name}")
            
            # Create run record
            run_key = f"{source.name}_{datetime.utcnow().isoformat()}"
            run = ProductRun(
                source_id=source_id,
                run_key=run_key,
                status='running',
                scheduled_at=datetime.utcnow(),
                started_at=datetime.utcnow()
            )
            self.session.add(run)
            self.session.commit()
            
            # Parse source config
            import json
            source_config = json.loads(source.config or '{}')
            source_config['name'] = source.name
            
            # Get scraper
            scraper = get_product_scraper(
                source.source_type,
                self.http_client,
                polite_delay_seconds=self.config.POLITE_DELAY_SECONDS,
                max_pages=self.config.MAX_SCRAPE_PAGES
            )
            
            # Scrape products
            logger.info(f"Scraping products from {source.name}...")
            
            for raw_product in scraper.scrape(source_config):
                try:
                    # Save raw entry
                    raw_entry = self.repo.save_raw_product_entry(
                        source_id=source.id,
                        external_id=raw_product.get('external_id', ''),
                        raw_payload=raw_product.get('raw_payload', ''),
                        fetch_metadata=raw_product.get('fetch_metadata', {}),
                        run_key=run_key
                    )
                    
                    stats['raw_count'] += 1
                    
                    # Normalize product
                    normalized = normalize_product(raw_product, self.config.INGEST_VERSION)
                    normalized['source_id'] = source.id
                    normalized['raw_product_entry_id'] = raw_entry.id
                    
                    # Save product (with price tracking)
                    result = self.repo.save_product(normalized)
                    
                    if result['created']:
                        stats['new_count'] += 1
                    else:
                        stats['updated_count'] += 1
                    
                    if result['price_changed']:
                        stats['price_changes'] += 1
                    
                    # Log progress
                    if stats['raw_count'] % 10 == 0:
                        logger.info(f"Progress: {stats['raw_count']} products scraped")
                
                except Exception as e:
                    logger.error(f"Error processing product: {e}")
                    continue
            
            # Update run record
            run.status = 'completed'
            run.completed_at = datetime.utcnow()
            run.raw_count = stats['raw_count']
            run.new_count = stats['new_count']
            run.updated_count = stats['updated_count']
            run.price_changes = stats['price_changes']
            
            # Update source
            source.last_scraped_at = datetime.utcnow()
            source.failure_count = 0
            
            self.session.commit()
            
            logger.info(f"Scrape completed: {stats['new_count']} new, "
                       f"{stats['updated_count']} updated, {stats['price_changes']} price changes")
        
        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            stats['error'] = str(e)
            
            # Update run as failed
            if 'run' in locals():
                run.status = 'failed'
                run.completed_at = datetime.utcnow()
                run.error_message = str(e)
                
                # Increment failure count
                if 'source' in locals():
                    source.failure_count = (source.failure_count or 0) + 1
                
                self.session.commit()
        
        return stats
    
    def scrape_all_due_sources(self) -> Dict:
        """Scrape all sources that are due."""
        sources = self.repo.get_product_sources_to_scrape()
        
        if not sources:
            logger.info("No sources due for scraping")
            return {'sources_scraped': 0, 'total_products': 0}
        
        logger.info(f"Scraping {len(sources)} sources...")
        
        total_stats = {
            'sources_scraped': 0,
            'total_products': 0,
            'total_new': 0,
            'total_updated': 0,
            'total_price_changes': 0
        }
        
        for source in sources:
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping: {source.name}")
            logger.info(f"{'='*60}")
            
            stats = self.run_scrape(source.id)
            
            if not stats['error']:
                total_stats['sources_scraped'] += 1
                total_stats['total_products'] += stats['raw_count']
                total_stats['total_new'] += stats['new_count']
                total_stats['total_updated'] += stats['updated_count']
                total_stats['total_price_changes'] += stats['price_changes']
        
        logger.info(f"\n{'='*60}")
        logger.info("ALL SOURCES COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Sources: {total_stats['sources_scraped']}/{len(sources)}")
        logger.info(f"Products: {total_stats['total_products']}")
        logger.info(f"New: {total_stats['total_new']}")
        logger.info(f"Updated: {total_stats['total_updated']}")
        logger.info(f"Price changes: {total_stats['total_price_changes']}")
        
        return total_stats
    
    def run_continuously(self, poll_interval_seconds: int = 300):
        """Run worker continuously, checking for due sources."""
        logger.info(f"Product worker starting (poll interval={poll_interval_seconds}s)")
        
        while True:
            try:
                self.scrape_all_due_sources()
                
                logger.info(f"Sleeping for {poll_interval_seconds}s...")
                time.sleep(poll_interval_seconds)
            
            except KeyboardInterrupt:
                logger.info("Worker stopped by user")
                break
            
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(poll_interval_seconds)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='E-commerce product crawler')
    parser.add_argument('--source-id', type=int, help='Scrape specific source')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--poll-interval', type=int, default=300, help='Poll interval in seconds')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    session = DBSession()
    
    try:
        worker = ProductWorker(session)
        
        if args.source_id:
            # Scrape specific source
            stats = worker.run_scrape(args.source_id)
            logger.info(f"Stats: {stats}")
        
        elif args.continuous:
            # Continuous mode
            worker.run_continuously(args.poll_interval)
        
        else:
            # One-time scrape of all due sources
            stats = worker.scrape_all_due_sources()
            logger.info(f"Total stats: {stats}")
    
    finally:
        session.close()


if __name__ == '__main__':
    main()
