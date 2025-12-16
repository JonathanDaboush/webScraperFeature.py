from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from crawler import Base, CrawlJob, Request, Page, Domain, Subject, PageSubject, Tag, PageTag
from datetime import datetime, timedelta

# PostgreSQL connection for pgAdmin
engine = create_engine("postgresql://postgres:password@localhost:5432/webscraper", echo=False)
Session = sessionmaker(bind=engine)


class DataSearch:
    def __init__(self):
        self.session = Session()
    
    def search_pages(self, keywords=None, match_all=False, start_date=None, 
                     end_date=None, subjects=None, tags=None, domains=None):
        """
        Search pages with flexible filtering.
        
        Args:
            keywords (list): List of keywords to search in title/URL
            match_all (bool): If True, ALL keywords must match. If False, ANY keyword matches
            start_date (datetime): Filter pages found after this date
            end_date (datetime): Filter pages found before this date
            subjects (list): Filter by subject names
            tags (list): Filter by tag names
            domains (list): Filter by domain names
        
        Returns:
            List of Page objects matching the criteria
        """
        query = self.session.query(Page)
        
        # Keyword search
        if keywords:
            keyword_filters = []
            for keyword in keywords:
                keyword_filter = or_(
                    Page.title.ilike(f"%{keyword}%"),
                    Page.url.ilike(f"%{keyword}%")
                )
                keyword_filters.append(keyword_filter)
            
            if match_all:
                # ALL keywords must match
                query = query.filter(and_(*keyword_filters))
            else:
                # ANY keyword can match
                query = query.filter(or_(*keyword_filters))
        
        # Date filters
        if start_date:
            query = query.filter(Page.date_found >= start_date)
        if end_date:
            query = query.filter(Page.date_found <= end_date)
        
        # Subject filter
        if subjects:
            query = query.join(Page.subjects).join(PageSubject.subject).filter(
                Subject.name.in_(subjects)
            )
        
        # Tag filter
        if tags:
            query = query.join(Page.tags).join(PageTag.tag_obj).filter(
                Tag.tag.in_(tags)
            )
        
        # Domain filter
        if domains:
            query = query.join(Page.domain).filter(Domain.domain.in_(domains))
        
        return query.all()
    
    def search_by_crawl_job(self, job_id=None, search_query=None):
        """
        Find all pages from a specific crawl job or search query.
        
        Args:
            job_id (int): The crawl job ID
            search_query (str): Search for crawl jobs containing this query string
        
        Returns:
            List of Page objects
        """
        query = self.session.query(Page).join(Page.request).join(Request.crawl_job)
        
        if job_id:
            query = query.filter(CrawlJob.id == job_id)
        
        if search_query:
            query = query.filter(CrawlJob.description.ilike(f"%{search_query}%"))
        
        return query.all()
    
    def get_pages_by_date_range(self, days_ago=7):
        """Get pages found in the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_ago)
        return self.session.query(Page).filter(Page.date_found >= cutoff_date).all()
    
    def get_pages_by_subject(self, subject_name):
        """Get all pages tagged with a specific subject."""
        return (self.session.query(Page)
                .join(Page.subjects)
                .join(PageSubject.subject)
                .filter(Subject.name == subject_name)
                .all())
    
    def get_pages_by_tag(self, tag_name):
        """Get all pages with a specific tag."""
        return (self.session.query(Page)
                .join(Page.tags)
                .join(PageTag.tag_obj)
                .filter(Tag.tag == tag_name)
                .all())
    
    def get_pages_by_domain(self, domain_name):
        """Get all pages from a specific domain."""
        return (self.session.query(Page)
                .join(Page.domain)
                .filter(Domain.domain == domain_name)
                .all())
    
    def get_all_subjects(self):
        """Get list of all subjects in the database."""
        return self.session.query(Subject).all()
    
    def get_all_tags(self):
        """Get list of all tags in the database."""
        return self.session.query(Tag).all()
    
    def get_all_domains(self):
        """Get list of all domains in the database."""
        return self.session.query(Domain).all()
    
    def get_crawl_jobs(self):
        """Get all crawl jobs with their details."""
        return self.session.query(CrawlJob).all()
    
    def print_page_details(self, page):
        """Pretty print a page's details."""
        print(f"\n{'='*80}")
        print(f"Title: {page.title or 'No title'}")
        print(f"URL: {page.url}")
        print(f"Domain: {page.domain.domain if page.domain else 'Unknown'}")
        print(f"Date Found: {page.date_found}")
        print(f"Crawled: {'Yes' if page.crawled else 'No'}")
        
        # Show subjects
        if page.subjects:
            subjects = [ps.subject.name for ps in page.subjects]
            print(f"Subjects: {', '.join(subjects)}")
        
        # Show tags
        if page.tags:
            tags = [pt.tag_obj.tag for pt in page.tags]
            print(f"Tags: {', '.join(tags)}")
        
        # Show crawl job info
        if page.request and page.request.crawl_job:
            job = page.request.crawl_job
            print(f"Crawl Job ID: {job.id}")
            print(f"Job Description: {job.description or 'None'}")
            print(f"Job Started: {job.started}")
        
        print(f"{'='*80}\n")
    
    def close(self):
        """Close the database session."""
        self.session.close()


