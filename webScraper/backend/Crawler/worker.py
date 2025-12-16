import logging
import time
from typing import Optional, Dict
from datetime import datetime

from sqlalchemy.orm import Session

from Crawler.config import get_config
from Crawler.http_client import HttpClient, RateLimiter
from Crawler.scrapers import get_scraper
from Crawler.normalizer import normalize
from Crawler.deduper import deduplicate_batch
from Crawler.scheduler import Scheduler

from Persistance.createDb import SessionLocal as DBSession
from Persistance.repository import Repository
from Persistance.crawler import JobRun, JobSource

logger = logging.getLogger(__name__)


class Worker:
    """
    Worker to orchestrate scrape → normalize → dedupe → persist pipeline.
    """
    
    def __init__(self, session: Session, config=None):
        self.session = session
        self.config = config or get_config()
        self.repo = Repository(session)
        self.scheduler = Scheduler(session)
        
        # Initialize HTTP client
        self.http_client = HttpClient(
            timeout_seconds=self.config.TIMEOUT_SECONDS,
            max_retries=self.config.MAX_RETRIES,
            backoff_base_seconds=self.config.RETRY_BASE_SECONDS,
            user_agents=self.config.USER_AGENT_POOL,
            proxy_pool=self.config.PROXY_POOL,
            rate_limiter=RateLimiter(self.config.REQUESTS_PER_DOMAIN_PER_MINUTE)
        )
    
    def run_job(self, run_id: int) -> Dict:
        """
        Execute a single job run: scrape → normalize → dedupe → persist.
        
        Args:
            run_id: JobRun ID to execute
        
        Returns:
            Stats dict: {
                'raw_count': int,
                'new_count': int,
                'merged_count': int,
                'error': str | None
            }
        """
        stats = {
            'raw_count': 0,
            'new_count': 0,
            'merged_count': 0,
            'error': None
        }
        
        try:
            # Get job run
            run = self.session.query(JobRun).filter(JobRun.id == run_id).first()
            if not run:
                raise ValueError(f"JobRun not found: {run_id}")
            
            source = run.source
            if not source:
                raise ValueError(f"JobSource not found for run {run_id}")
            
            logger.info(f"Starting job run {run_id} for source '{source.name}'")
            
            # Mark as started
            self.scheduler.mark_run_started(run_id)
            
            # Parse source config
            import json
            source_config = json.loads(source.config or '{}')
            source_config['name'] = source.name
            
            # Get appropriate scraper
            scraper = get_scraper(
                source.source_type,
                self.http_client,
                polite_delay_seconds=self.config.POLITE_DELAY_SECONDS,
                max_pages=self.config.MAX_SCRAPE_PAGES
            )
            
            # Scrape raw entries
            raw_entries = []
            normalized_postings = []
            
            logger.info(f"Scraping {source.name}...")
            
            for raw_entry in scraper.scrape(source_config):
                try:
                    # Validate size
                    if len(raw_entry.get('raw_payload', '')) > self.config.MAX_RAW_PAYLOAD_BYTES:
                        logger.warning(f"Skipping oversized payload: {len(raw_entry['raw_payload'])} bytes")
                        continue
                    
                    # Save raw entry
                    raw_job = self.repo.save_raw_job_entry(
                        source_id=source.id,
                        external_id=raw_entry.get('external_id'),
                        raw_payload=raw_entry.get('raw_payload', ''),
                        fetch_metadata=raw_entry.get('fetch_metadata', {}),
                        run_key=run.run_key
                    )
                    
                    stats['raw_count'] += 1
                    
                    # Normalize
                    normalized = normalize(raw_entry, self.config.INGEST_VERSION)
                    normalized['source_id'] = source.id
                    normalized['raw_job_entry_id'] = raw_job.id
                    normalized_postings.append(normalized)
                    
                    # Log progress every 10 items
                    if stats['raw_count'] % 10 == 0:
                        logger.info(f"Progress: {stats['raw_count']} raw entries scraped")
                    
                except Exception as e:
                    logger.error(f"Error processing raw entry: {e}")
                    continue
            
            logger.info(f"Scraped {stats['raw_count']} raw entries from {source.name}")
            
            # Deduplicate batch
            if normalized_postings:
                logger.info(f"Deduplicating {len(normalized_postings)} postings...")
                deduplicated = deduplicate_batch(normalized_postings, threshold=0.85)
                
                # Persist deduplicated postings
                for posting in deduplicated:
                    result = self.repo.save_job_posting(posting)
                    
                    if result['created']:
                        stats['new_count'] += 1
                    elif result['merged']:
                        stats['merged_count'] += 1
                
                logger.info(f"Persisted: {stats['new_count']} new, {stats['merged_count']} merged")
            
            # Mark as completed
            self.scheduler.mark_run_completed(
                run_id=run_id,
                raw_count=stats['raw_count'],
                new_count=stats['new_count'],
                merged_count=stats['merged_count'],
                error_message=None
            )
            
            logger.info(f"Job run {run_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job run {run_id} failed: {e}")
            stats['error'] = str(e)
            
            # Mark as failed
            self.scheduler.mark_run_completed(
                run_id=run_id,
                raw_count=stats['raw_count'],
                new_count=stats['new_count'],
                merged_count=stats['merged_count'],
                error_message=str(e)
            )
        
        return stats
    
    def run_continuously(self, poll_interval_seconds: Optional[int] = None):
        """
        Continuously poll for and execute pending jobs.
        
        Args:
            poll_interval_seconds: How often to check for jobs (default from config)
        """
        poll_interval = poll_interval_seconds or self.config.WORKER_POLL_INTERVAL_SECONDS
        
        logger.info(f"Worker starting continuous mode (poll interval={poll_interval}s)")
        
        while True:
            try:
                # Get pending runs
                pending_runs = self.scheduler.get_pending_runs(limit=5)
                
                if not pending_runs:
                    logger.debug("No pending jobs - sleeping")
                    time.sleep(poll_interval)
                    continue
                
                # Process each run
                for run in pending_runs:
                    logger.info(f"Processing job run {run.id}")
                    stats = self.run_job(run.id)
                    
                    logger.info(f"Run {run.id} stats: {stats}")
                
            except KeyboardInterrupt:
                logger.info("Worker stopped by user")
                break
            
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(poll_interval)
    
    def run_once(self):
        """
        Process all pending jobs once and exit.
        Useful for scheduled/cron execution.
        """
        logger.info("Worker running in single-pass mode")
        
        pending_runs = self.scheduler.get_pending_runs(limit=100)
        
        if not pending_runs:
            logger.info("No pending jobs")
            return
        
        for run in pending_runs:
            stats = self.run_job(run.id)
            logger.info(f"Run {run.id} completed: {stats}")
        
        logger.info(f"Processed {len(pending_runs)} job runs")


def main():
    """
    Main entry point for worker process.
    Can be run as: python -m crawler.worker
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Job scraper worker')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--run-id', type=int, help='Run specific job run ID')
    parser.add_argument('--poll-interval', type=int, default=5, help='Poll interval in seconds')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create session
    session = DBSession()
    
    try:
        worker = Worker(session)
        
        if args.run_id:
            # Run specific job
            logger.info(f"Running specific job: {args.run_id}")
            stats = worker.run_job(args.run_id)
            logger.info(f"Job stats: {stats}")
        
        elif args.once:
            # Single pass
            worker.run_once()
        
        else:
            # Continuous mode
            worker.run_continuously(args.poll_interval)
    
    finally:
        session.close()


if __name__ == '__main__':
    main()
