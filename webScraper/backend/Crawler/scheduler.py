from typing import List, Optional
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session

from Persistance.crawler import JobSource, JobRun
from Persistance.createDb import SessionLocal as DBSession

logger = logging.getLogger(__name__)


class Scheduler:
    """
    Schedule job sources for scraping with backoff logic.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def schedule_all_sources(
        self,
        source_names: Optional[List[str]] = None,
        force: bool = False
    ) -> List[int]:
        """
        Schedule job sources that are due for scraping.
        
        Args:
            source_names: Filter to specific sources, or None for all
            force: Ignore interval and schedule all sources
        
        Returns:
            List of scheduled job_source_ids
        """
        from Persistance.repository import Repository
        repo = Repository(self.session)
        
        # Get sources to scrape
        sources = repo.get_job_sources_to_scrape(
            source_names=source_names,
            limit=100 if not force else None
        )
        
        scheduled_ids = []
        
        for source in sources:
            try:
                # Create JobRun
                job_run = JobRun(
                    job_source_id=source.id,
                    run_key=f"{source.name}_{datetime.utcnow().isoformat()}",
                    status='pending',
                    scheduled_at=datetime.utcnow()
                )
                
                self.session.add(job_run)
                scheduled_ids.append(source.id)
                
                logger.info(f"Scheduled scrape for {source.name} (id={source.id})")
                
            except Exception as e:
                logger.error(f"Error scheduling {source.name}: {e}")
                continue
        
        self.session.commit()
        
        logger.info(f"Scheduled {len(scheduled_ids)} job sources for scraping")
        
        return scheduled_ids
    
    def enqueue_scrape(
        self,
        source_id: int,
        idempotency_key: Optional[str] = None
    ) -> Optional[int]:
        """
        Enqueue a specific source for immediate scraping.
        
        Args:
            source_id: JobSource ID
            idempotency_key: Optional key to prevent duplicate runs
        
        Returns:
            JobRun ID if created, None if already exists
        """
        # Check if already queued
        if idempotency_key:
            existing = self.session.query(JobRun).filter(
                JobRun.run_key == idempotency_key,
                JobRun.status.in_(['pending', 'running'])
            ).first()
            
            if existing:
                logger.info(f"JobRun already exists: {idempotency_key}")
                return existing.id
        
        # Get source
        source = self.session.query(JobSource).filter(
            JobSource.id == source_id
        ).first()
        
        if not source:
            logger.error(f"JobSource not found: {source_id}")
            return None
        
        # Create run
        run_key = idempotency_key or f"{source.name}_{datetime.utcnow().isoformat()}"
        
        job_run = JobRun(
            job_source_id=source_id,
            run_key=run_key,
            status='pending',
            scheduled_at=datetime.utcnow()
        )
        
        self.session.add(job_run)
        self.session.commit()
        
        logger.info(f"Enqueued scrape for {source.name} (run_id={job_run.id})")
        
        return job_run.id
    
    def get_pending_runs(self, limit: int = 10) -> List[JobRun]:
        """
        Get pending job runs ready to execute.
        
        Args:
            limit: Max number of runs to return
        
        Returns:
            List of pending JobRun objects
        """
        return self.session.query(JobRun).filter(
            JobRun.status == 'pending'
        ).order_by(
            JobRun.scheduled_at.asc()
        ).limit(limit).all()
    
    def mark_run_started(self, run_id: int):
        """Mark a job run as started."""
        run = self.session.query(JobRun).filter(JobRun.id == run_id).first()
        if run:
            run.status = 'running'
            run.started_at = datetime.utcnow()
            self.session.commit()
            logger.info(f"Started job run {run_id}")
    
    def mark_run_completed(
        self,
        run_id: int,
        raw_count: int,
        new_count: int,
        merged_count: int,
        error_message: Optional[str] = None
    ):
        """Mark a job run as completed with stats."""
        run = self.session.query(JobRun).filter(JobRun.id == run_id).first()
        if run:
            run.status = 'completed' if not error_message else 'failed'
            run.completed_at = datetime.utcnow()
            run.raw_count = raw_count
            run.new_count = new_count
            run.merged_count = merged_count
            run.error_message = error_message
            
            # Update source last_scraped_at
            source = run.source
            if source:
                source.last_scraped_at = datetime.utcnow()
                
                # Reset failure count on success
                if not error_message:
                    source.failure_count = 0
                else:
                    # Increment failure count
                    source.failure_count = (source.failure_count or 0) + 1
            
            self.session.commit()
            
            status = 'completed' if not error_message else 'failed'
            logger.info(f"Marked run {run_id} as {status}: "
                       f"raw={raw_count}, new={new_count}, merged={merged_count}")
    
    def cleanup_old_runs(self, days: int = 30):
        """Delete old completed runs to save space."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        deleted = self.session.query(JobRun).filter(
            JobRun.status == 'completed',
            JobRun.completed_at < cutoff
        ).delete()
        
        self.session.commit()
        
        logger.info(f"Cleaned up {deleted} old job runs")
        
        return deleted
