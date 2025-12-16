from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from Persistance.crawler import (
    Base, Domain, CrawlJob, Request, Page, Subject, 
    PageSubject, Tag, PageTag, RequestType, engine,
    JobSource, RawJobEntry, JobPosting, Skill, JobPostingSkill,
    PostingMerge, JobRun, JobStatus, EmploymentType
)
from Persistance.createDb import SessionLocal


class Repository:
    """
    Repository pattern for database operations.
    Provides clean interface for CRUD operations and maintains separation of concerns.
    """
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or SessionLocal()
    
    def commit(self):
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    # ────────────────────────────────
    # DOMAIN OPERATIONS
    # ────────────────────────────────
    
    def get_or_create_domain(self, domain_name: str) -> Domain:
        """Get existing domain or create new one."""
        domain = self.session.query(Domain).filter_by(domain=domain_name).first()
        if not domain:
            domain = Domain(domain=domain_name)
            self.session.add(domain)
            self.session.flush()
        return domain
    
    def get_domain_by_name(self, domain_name: str) -> Optional[Domain]:
        """Get domain by name."""
        return self.session.query(Domain).filter_by(domain=domain_name).first()
    
    def get_all_domains(self) -> List[Domain]:
        """Get all domains."""
        return self.session.query(Domain).all()
    
    # ────────────────────────────────
    # CRAWL JOB OPERATIONS
    # ────────────────────────────────
    
    def create_crawl_job(self, search_query: str = None, description: str = None) -> CrawlJob:
        """Create a new crawl job."""
        job = CrawlJob(
            search_query=search_query,
            description=description,
            started=datetime.utcnow()
        )
        self.session.add(job)
        self.session.flush()
        return job
    
    def get_crawl_job(self, job_id: int) -> Optional[CrawlJob]:
        """Get crawl job by ID."""
        return self.session.query(CrawlJob).filter_by(id=job_id).first()
    
    def get_all_crawl_jobs(self) -> List[CrawlJob]:
        """Get all crawl jobs."""
        return self.session.query(CrawlJob).all()
    
    def get_crawl_jobs_by_query(self, search_query: str) -> List[CrawlJob]:
        """Get crawl jobs that match a search query."""
        return self.session.query(CrawlJob).filter(
            CrawlJob.search_query.ilike(f"%{search_query}%")
        ).all()
    
    # ────────────────────────────────
    # REQUEST OPERATIONS
    # ────────────────────────────────
    
    def create_request(
        self, 
        url: str, 
        crawl_job_id: int,
        domain_id: int,
        request_type: RequestType = RequestType.GET,
        parent_request_id: Optional[int] = None,
        status_code: Optional[int] = None
    ) -> Request:
        """Create a new request."""
        request = Request(
            url=url,
            request_type=request_type,
            parent_request_id=parent_request_id,
            domain_id=domain_id,
            crawl_job_id=crawl_job_id,
            status_code=status_code,
            date_requested=datetime.utcnow()
        )
        self.session.add(request)
        self.session.flush()
        return request
    
    def get_request(self, request_id: int) -> Optional[Request]:
        """Get request by ID."""
        return self.session.query(Request).filter_by(id=request_id).first()
    
    def get_requests_by_job(self, job_id: int) -> List[Request]:
        """Get all requests for a crawl job."""
        return self.session.query(Request).filter_by(crawl_job_id=job_id).all()
    
    def update_request_status(self, request_id: int, status_code: int):
        """Update the status code of a request."""
        request = self.get_request(request_id)
        if request:
            request.status_code = status_code
            self.session.flush()
    
    # ────────────────────────────────
    # PAGE OPERATIONS
    # ────────────────────────────────
    
    def create_page(
        self,
        url: str,
        domain_id: int,
        request_id: int,
        title: Optional[str] = None,
        html: Optional[str] = None,
        crawled: bool = False
    ) -> Page:
        """Create a new page."""
        page = Page(
            url=url,
            domain_id=domain_id,
            request_id=request_id,
            title=title,
            html=html,
            crawled=crawled,
            date_found=datetime.utcnow()
        )
        self.session.add(page)
        self.session.flush()
        return page
    
    def get_page(self, page_id: int) -> Optional[Page]:
        """Get page by ID."""
        return self.session.query(Page).filter_by(id=page_id).first()
    
    def get_page_by_url(self, url: str) -> Optional[Page]:
        """Get page by URL."""
        return self.session.query(Page).filter_by(url=url).first()
    
    def get_pages_by_domain(self, domain_id: int) -> List[Page]:
        """Get all pages for a domain."""
        return self.session.query(Page).filter_by(domain_id=domain_id).all()
    
    def update_page_content(self, page_id: int, title: str = None, html: str = None):
        """Update page content."""
        page = self.get_page(page_id)
        if page:
            if title:
                page.title = title
            if html:
                page.html = html
            page.crawled = True
            self.session.flush()
    
    def mark_page_crawled(self, page_id: int):
        """Mark a page as crawled."""
        page = self.get_page(page_id)
        if page:
            page.crawled = True
            self.session.flush()
    
    def get_uncrawled_pages(self, limit: Optional[int] = None) -> List[Page]:
        """Get pages that haven't been crawled yet."""
        query = self.session.query(Page).filter_by(crawled=False)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    # ────────────────────────────────
    # SUBJECT OPERATIONS
    # ────────────────────────────────
    
    def get_or_create_subject(self, name: str) -> Subject:
        """Get existing subject or create new one."""
        subject = self.session.query(Subject).filter_by(name=name).first()
        if not subject:
            subject = Subject(name=name)
            self.session.add(subject)
            self.session.flush()
        return subject
    
    def add_subject_to_page(self, page_id: int, subject_name: str):
        """Add a subject to a page."""
        subject = self.get_or_create_subject(subject_name)
        
        # Check if already exists
        exists = self.session.query(PageSubject).filter_by(
            page_id=page_id, 
            subject_id=subject.id
        ).first()
        
        if not exists:
            page_subject = PageSubject(page_id=page_id, subject_id=subject.id)
            self.session.add(page_subject)
            self.session.flush()
    
    def get_subjects_for_page(self, page_id: int) -> List[Subject]:
        """Get all subjects for a page."""
        return self.session.query(Subject).join(PageSubject).filter(
            PageSubject.page_id == page_id
        ).all()
    
    def get_all_subjects(self) -> List[Subject]:
        """Get all subjects."""
        return self.session.query(Subject).all()
    
    # ────────────────────────────────
    # TAG OPERATIONS
    # ────────────────────────────────
    
    def get_or_create_tag(self, tag_name: str) -> Tag:
        """Get existing tag or create new one."""
        tag = self.session.query(Tag).filter_by(tag=tag_name).first()
        if not tag:
            tag = Tag(tag=tag_name)
            self.session.add(tag)
            self.session.flush()
        return tag
    
    def add_tag_to_page(self, page_id: int, tag_name: str):
        """Add a tag to a page."""
        tag = self.get_or_create_tag(tag_name)
        
        # Check if already exists
        exists = self.session.query(PageTag).filter_by(
            page_id=page_id,
            tag_id=tag.id
        ).first()
        
        if not exists:
            page_tag = PageTag(page_id=page_id, tag_id=tag.id)
            self.session.add(page_tag)
            self.session.flush()
    
    def get_tags_for_page(self, page_id: int) -> List[Tag]:
        """Get all tags for a page."""
        return self.session.query(Tag).join(PageTag).filter(
            PageTag.page_id == page_id
        ).all()
    
    def get_all_tags(self) -> List[Tag]:
        """Get all tags."""
        return self.session.query(Tag).all()
    
    # ────────────────────────────────
    # BULK OPERATIONS
    # ────────────────────────────────
    
    def bulk_create_pages(self, pages_data: List[dict]) -> List[Page]:
        """Create multiple pages at once."""
        pages = []
        for data in pages_data:
            page = Page(**data, date_found=datetime.utcnow())
            pages.append(page)
        
        self.session.bulk_save_objects(pages)
        self.session.flush()
        return pages
    
    def delete_page(self, page_id: int):
        """Delete a page and its relationships."""
        page = self.get_page(page_id)
        if page:
            self.session.delete(page)
            self.session.flush()
    
    # ────────────────────────────────
    # UTILITY METHODS
    # ────────────────────────────────
    
    def count_pages(self) -> int:
        """Get total count of pages."""
        return self.session.query(Page).count()
    
    def count_crawled_pages(self) -> int:
        """Get count of crawled pages."""
        return self.session.query(Page).filter_by(crawled=True).count()
    
    def count_domains(self) -> int:
        """Get total count of domains."""
        return self.session.query(Domain).count()
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        return {
            "total_pages": self.count_pages(),
            "crawled_pages": self.count_crawled_pages(),
            "uncrawled_pages": self.count_pages() - self.count_crawled_pages(),
            "total_domains": self.count_domains(),
            "total_subjects": self.session.query(Subject).count(),
            "total_tags": self.session.query(Tag).count(),
            "total_crawl_jobs": self.session.query(CrawlJob).count(),
        }
    
    # ────────────────────────────────
    # JOB SCRAPING OPERATIONS
    # ────────────────────────────────
    
    def get_or_create_job_source(self, name: str, base_url: str, **kwargs) -> JobSource:
        """Get existing job source or create new one."""
        source = self.session.query(JobSource).filter_by(name=name).first()
        if not source:
            source = JobSource(name=name, base_url=base_url, **kwargs)
            self.session.add(source)
            self.session.flush()
        return source
    
    def save_raw_job_entry(self, raw: Dict) -> RawJobEntry:
        """
        Save raw scraped job entry with idempotent upsert.
        raw dict should contain: job_source_id, external_id, raw_payload, etc.
        """
        # Validate job_source exists
        source = self.session.query(JobSource).filter_by(id=raw['job_source_id']).first()
        if not source:
            raise ValueError(f"Job source {raw['job_source_id']} not found")
        
        # Upsert logic: if external_id exists, update; else insert
        if raw.get('external_id'):
            existing = self.session.query(RawJobEntry).filter_by(
                job_source_id=raw['job_source_id'],
                external_id=raw['external_id']
            ).first()
            
            if existing:
                # Update fields
                for key, value in raw.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                self.session.flush()
                return existing
        
        # Insert new
        entry = RawJobEntry(
            job_source_id=raw['job_source_id'],
            external_id=raw.get('external_id'),
            scraped_at=raw.get('scraped_at', datetime.utcnow()),
            raw_payload=raw['raw_payload'] if isinstance(raw['raw_payload'], str) else json.dumps(raw['raw_payload']),
            query=raw.get('query'),
            location=raw.get('location'),
            http_status=raw.get('http_status'),
            fetch_duration_ms=raw.get('fetch_duration_ms')
        )
        self.session.add(entry)
        self.session.flush()
        return entry
    
    def save_job_posting(self, posting: Dict, idempotency_key: Optional[str] = None) -> JobPosting:
        """
        Save normalized job posting with deduplication and transaction safety.
        Implements ON CONFLICT handling for fingerprint uniqueness.
        """
        # Check idempotency
        if idempotency_key:
            existing_run = self.session.query(JobRun).filter_by(
                idempotency_key=idempotency_key,
                status=JobStatus.COMPLETED
            ).first()
            if existing_run:
                # Return existing posting associated with this run
                existing_posting = self.session.query(JobPosting).filter_by(
                    job_source_id=posting['job_source_id']
                ).order_by(JobPosting.scraped_at.desc()).first()
                if existing_posting:
                    return existing_posting
        
        # Validate required fields
        if not posting.get('title') or not posting.get('fingerprint'):
            raise ValueError("Title and fingerprint are required")
        
        try:
            # Try to find existing by fingerprint
            existing = self.session.query(JobPosting).filter_by(
                fingerprint=posting['fingerprint']
            ).first()
            
            if existing:
                # Merge: update fields, union skills, extend source_references
                existing.description = posting.get('description', existing.description)
                if posting.get('salary_min_cents') and not existing.salary_min_cents:
                    existing.salary_min_cents = posting['salary_min_cents']
                    existing.salary_max_cents = posting.get('salary_max_cents')
                    existing.currency = posting.get('currency')
                
                # Union skills
                existing_skills = json.loads(existing.skills) if existing.skills else []
                new_skills = posting.get('skills', [])
                merged_skills = list(set(existing_skills + new_skills))
                existing.skills = json.dumps(merged_skills)
                
                # Extend source_references
                existing_refs = json.loads(existing.source_references) if existing.source_references else []
                new_refs = posting.get('source_references', [])
                existing_refs.extend(new_refs)
                existing.source_references = json.dumps(existing_refs)
                
                # Choose earliest posted_at
                if posting.get('posted_at'):
                    posted_dt = posting['posted_at'] if isinstance(posting['posted_at'], datetime) else datetime.fromisoformat(posting['posted_at'])
                    if not existing.posted_at or posted_dt < existing.posted_at:
                        existing.posted_at = posted_dt
                
                # Log merge
                merge_record = PostingMerge(
                    canonical_posting_id=existing.id,
                    duplicate_fingerprint=posting['fingerprint'],
                    merge_reason='fingerprint_match',
                    merged_at=datetime.utcnow()
                )
                self.session.add(merge_record)
                self.session.flush()
                return existing
            
            # Insert new posting
            new_posting = JobPosting(
                job_source_id=posting['job_source_id'],
                external_id=posting.get('external_id'),
                title=posting['title'],
                normalized_title=posting['normalized_title'],
                company=posting.get('company'),
                location=posting.get('location'),
                is_remote=posting.get('is_remote'),
                description=posting['description'],
                posted_at=posting.get('posted_at'),
                scraped_at=posting.get('scraped_at', datetime.utcnow()),
                employment_type=posting.get('employment_type'),
                salary_min_cents=posting.get('salary_min_cents'),
                salary_max_cents=posting.get('salary_max_cents'),
                currency=posting.get('currency'),
                skills=json.dumps(posting.get('skills', [])),
                url=posting.get('url'),
                fingerprint=posting['fingerprint'],
                ingest_version=posting['ingest_version'],
                source_references=json.dumps(posting.get('source_references', []))
            )
            
            self.session.add(new_posting)
            self.session.flush()
            
            # Add skills relationships
            if posting.get('skills'):
                for skill_name in posting['skills']:
                    skill = self.get_or_create_skill(skill_name)
                    ps = JobPostingSkill(posting_id=new_posting.id, skill_id=skill.id)
                    self.session.add(ps)
            
            self.session.flush()
            return new_posting
            
        except IntegrityError as e:
            # Handle concurrent inserts - re-fetch and merge
            self.session.rollback()
            existing = self.session.query(JobPosting).filter_by(
                fingerprint=posting['fingerprint']
            ).first()
            if existing:
                return existing
            raise
    
    def get_or_create_skill(self, skill_name: str, category: Optional[str] = None) -> Skill:
        """Get existing skill or create new one."""
        skill = self.session.query(Skill).filter_by(name=skill_name).first()
        if not skill:
            skill = Skill(name=skill_name, category=category)
            self.session.add(skill)
            self.session.flush()
        return skill
    
    def query_job_postings(
        self, 
        filter_params: Dict, 
        page: int = 1, 
        per_page: int = 50
    ) -> Tuple[List[JobPosting], int]:
        """
        Query job postings with filters and pagination.
        filter_params: {'skill', 'company', 'title_keywords', 'location', 'date_from', 'date_to', 'is_remote'}
        """
        # Validate pagination
        if page < 1:
            page = 1
        if per_page > 500:
            per_page = 500
        
        query = self.session.query(JobPosting)
        
        # Apply filters
        if filter_params.get('skill'):
            query = query.join(JobPostingSkill).join(Skill).filter(
                Skill.name.ilike(f"%{filter_params['skill']}%")
            )
        
        if filter_params.get('company'):
            query = query.filter(JobPosting.company.ilike(f"%{filter_params['company']}%"))
        
        if filter_params.get('title_keywords'):
            keywords = filter_params['title_keywords'].split()
            for keyword in keywords:
                query = query.filter(or_(
                    JobPosting.title.ilike(f"%{keyword}%"),
                    JobPosting.normalized_title.ilike(f"%{keyword}%")
                ))
        
        if filter_params.get('location'):
            query = query.filter(JobPosting.location.ilike(f"%{filter_params['location']}%"))
        
        if filter_params.get('is_remote') is not None:
            query = query.filter(JobPosting.is_remote == filter_params['is_remote'])
        
        if filter_params.get('date_from'):
            date_from = datetime.fromisoformat(filter_params['date_from'])
            query = query.filter(JobPosting.posted_at >= date_from)
        
        if filter_params.get('date_to'):
            date_to = datetime.fromisoformat(filter_params['date_to'])
            query = query.filter(JobPosting.posted_at <= date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        results = query.order_by(JobPosting.posted_at.desc()).offset(offset).limit(per_page).all()
        
        return results, total
    
    def aggregate_skill_counts(
        self,
        start_date: datetime,
        end_date: datetime,
        skill: Optional[str] = None
    ) -> List[Tuple[str, int]]:
        """Aggregate job postings by skill within date range."""
        query = self.session.query(
            Skill.name,
            func.count(JobPostingSkill.posting_id).label('count')
        ).join(JobPostingSkill).join(JobPosting).filter(
            JobPosting.posted_at >= start_date,
            JobPosting.posted_at <= end_date
        )
        
        if skill:
            query = query.filter(Skill.name.ilike(f"%{skill}%"))
        
        query = query.group_by(Skill.name).order_by(func.count(JobPostingSkill.posting_id).desc())
        
        return query.all()
    
    def aggregate_company_counts(
        self,
        start_date: datetime,
        end_date: datetime,
        company: Optional[str] = None
    ) -> List[Tuple[str, int]]:
        """Aggregate job postings by company within date range."""
        query = self.session.query(
            JobPosting.company,
            func.count(JobPosting.id).label('count')
        ).filter(
            JobPosting.posted_at >= start_date,
            JobPosting.posted_at <= end_date,
            JobPosting.company.isnot(None)
        )
        
        if company:
            query = query.filter(JobPosting.company.ilike(f"%{company}%"))
        
        query = query.group_by(JobPosting.company).order_by(func.count(JobPosting.id).desc())
        
        return query.all()
    
    def create_job_run(
        self,
        job_source_id: int,
        idempotency_key: Optional[str] = None,
        query: Optional[str] = None,
        location: Optional[str] = None
    ) -> JobRun:
        """Create a new job run record."""
        # Check for existing run with same idempotency key
        if idempotency_key:
            existing = self.session.query(JobRun).filter_by(
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing
        
        run = JobRun(
            job_source_id=job_source_id,
            idempotency_key=idempotency_key,
            query=query,
            location=location,
            status=JobStatus.PENDING,
            started_at=datetime.utcnow()
        )
        self.session.add(run)
        self.session.flush()
        return run
    
    def update_job_run_status(
        self,
        run_id: int,
        status: JobStatus,
        stats: Optional[Dict] = None,
        errors: Optional[List[str]] = None
    ):
        """Update job run status and statistics."""
        run = self.session.query(JobRun).filter_by(id=run_id).first()
        if not run:
            raise ValueError(f"Job run {run_id} not found")
        
        run.status = status
        if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            run.completed_at = datetime.utcnow()
        
        if stats:
            run.processed_count = stats.get('processed', run.processed_count)
            run.inserted_count = stats.get('inserted', run.inserted_count)
            run.merged_count = stats.get('merged', run.merged_count)
            run.error_count = stats.get('errors', run.error_count)
        
        if errors:
            run.errors = json.dumps(errors)
        
        self.session.flush()
    
    def update_job_source_success(self, source_id: int):
        """Update job source after successful scrape."""
        source = self.session.query(JobSource).filter_by(id=source_id).first()
        if source:
            source.last_successful_scrape = datetime.utcnow()
            source.failure_count = 0
            self.session.flush()
    
    def update_job_source_failure(self, source_id: int):
        """Increment failure count for job source."""
        source = self.session.query(JobSource).filter_by(id=source_id).first()
        if source:
            source.failure_count += 1
            self.session.flush()
    
    def get_job_sources_to_scrape(self) -> List[JobSource]:
        """Get enabled job sources that are ready to be scraped."""
        now = datetime.utcnow()
        sources = self.session.query(JobSource).filter_by(enabled=True).all()
        
        ready_sources = []
        for source in sources:
            if not source.last_successful_scrape:
                ready_sources.append(source)
                continue
            
            # Calculate backoff interval
            backoff_multiplier = 2 ** min(source.failure_count, 5)  # Cap at 2^5
            next_scrape = source.last_successful_scrape + timedelta(
                minutes=source.scrape_interval_minutes * backoff_multiplier
            )
            
            if now >= next_scrape:
                ready_sources.append(source)
        
        return ready_sources


# Example usage
if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    repo = Repository()
    
    try:
        # Example: Create a crawl job
        job = repo.create_crawl_job(
            search_query="Python web scraping",
            description="Looking for Python scraping tutorials"
        )
        print(f"Created crawl job: {job.id}")
        
        # Example: Create a domain
        domain = repo.get_or_create_domain("example.com")
        print(f"Domain: {domain.domain} (ID: {domain.id})")
        
        # Example: Create a request
        request = repo.create_request(
            url="https://example.com/page1",
            crawl_job_id=job.id,
            domain_id=domain.id,
            status_code=200
        )
        print(f"Created request: {request.id}")
        
        # Example: Create a page
        page = repo.create_page(
            url="https://example.com/page1",
            domain_id=domain.id,
            request_id=request.id,
            title="Example Page",
            html="<html>...</html>",
            crawled=True
        )
        print(f"Created page: {page.id}")
        
        # Example: Add subjects and tags
        repo.add_subject_to_page(page.id, "Web Scraping")
        repo.add_subject_to_page(page.id, "Python")
        repo.add_tag_to_page(page.id, "tutorial")
        repo.add_tag_to_page(page.id, "beginner")
        print("Added subjects and tags")
        
        # Example: Get statistics
        stats = repo.get_stats()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Commit all changes
        repo.commit()
        print("\nAll changes committed successfully!")
        
    except Exception as e:
        repo.rollback()
        print(f"Error: {e}")
    finally:
        repo.close()
