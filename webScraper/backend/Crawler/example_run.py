"""
Example: Run crawler for all scheduled job sources

This script demonstrates how to:
1. Initialize the crawler worker
2. Schedule job sources for scraping
3. Execute scraping jobs
4. Monitor progress and results
"""

import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.worker import Worker
from crawler.scheduler import Scheduler
from Persistance.createDb import SessionLocal as Session


def setup_logging():
    """Configure logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('crawler.log')
        ]
    )


def main():
    """Run crawler example."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting crawler example")
    
    # Create database session
    session = Session()
    
    try:
        # Initialize scheduler
        scheduler = Scheduler(session)
        
        # Schedule all sources that are due for scraping
        logger.info("Scheduling job sources...")
        scheduled_ids = scheduler.schedule_all_sources(force=False)
        
        if not scheduled_ids:
            logger.info("No sources scheduled (all up to date)")
            return
        
        logger.info(f"Scheduled {len(scheduled_ids)} sources")
        
        # Initialize worker
        worker = Worker(session)
        
        # Option 1: Run once (process all pending jobs and exit)
        logger.info("Running worker in single-pass mode...")
        worker.run_once()
        
        # Option 2: Run continuously (uncomment to use)
        # logger.info("Running worker in continuous mode...")
        # worker.run_continuously(poll_interval_seconds=30)
        
        logger.info("Crawler example completed")
        
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    
    except Exception as e:
        logger.error(f"Error in crawler example: {e}", exc_info=True)
    
    finally:
        session.close()


if __name__ == '__main__':
    main()
