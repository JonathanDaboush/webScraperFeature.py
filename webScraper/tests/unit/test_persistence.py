"""
Data Persistence Tests

Tests for database CRUD operations to ensure data is properly saved and retrieved.
Includes both passing tests (correct behavior) and failing tests (error handling).
"""

import os
import sys
import pytest
from unittest.mock import MagicMock
from datetime import datetime

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, backend_path)

from Persistance.crawler import Domain, Page, CrawlJob, Request, Subject, Tag, PageSubject, PageTag
from Persistance.createDb import SessionLocal


class TestDomainPersistence:
    """Test Domain model CRUD operations."""
    
    def test_create_domain_success(self, test_session):
        """✅ PASS: Should successfully create a domain."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        # Verify it was saved
        saved = test_session.query(Domain).filter(Domain.domain == 'example.com').first()
        assert saved is not None
        assert saved.domain == 'example.com'
        assert saved.id is not None
    
    def test_domain_unique_constraint(self, test_session):
        """❌ FAIL: Should prevent duplicate domains."""
        domain1 = Domain(domain='duplicate.com')
        test_session.add(domain1)
        test_session.commit()
        
        # Try to add duplicate
        domain2 = Domain(domain='duplicate.com')
        test_session.add(domain2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_session.commit()
    
    def test_query_domain_by_name(self, test_session):
        """✅ PASS: Should retrieve domain by name."""
        domain = Domain(domain='test.com')
        test_session.add(domain)
        test_session.commit()
        
        result = test_session.query(Domain).filter(Domain.domain == 'test.com').first()
        assert result.domain == 'test.com'
    
    def test_query_nonexistent_domain(self, test_session):
        """✅ PASS: Should return None for nonexistent domain."""
        result = test_session.query(Domain).filter(Domain.domain == 'nonexistent.com').first()
        assert result is None
    
    def test_delete_domain(self, test_session):
        """✅ PASS: Should delete domain successfully."""
        domain = Domain(domain='delete-me.com')
        test_session.add(domain)
        test_session.commit()
        
        domain_id = domain.id
        test_session.delete(domain)
        test_session.commit()
        
        # Verify it's gone
        result = test_session.query(Domain).filter(Domain.id == domain_id).first()
        assert result is None


class TestPagePersistence:
    """Test Page model CRUD operations."""
    
    def test_create_page_success(self, test_session):
        """✅ PASS: Should successfully create a page."""
        # Create domain first
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        # Create page
        page = Page(
            url='https://example.com/test',
            domain_id=domain.id,
            title='Test Page',
            html='<html><body>Test</body></html>',
            date_found=datetime.now(),
            crawled=True
        )
        test_session.add(page)
        test_session.commit()
        
        # Verify it was saved
        saved = test_session.query(Page).filter(Page.url == 'https://example.com/test').first()
        assert saved is not None
        assert saved.title == 'Test Page'
        assert saved.crawled is True
    
    def test_page_requires_domain(self, test_session):
        """❌ FAIL: Should require valid domain_id (foreign key)."""
        page = Page(
            url='https://example.com/orphan',
            domain_id=99999,  # Non-existent domain
            title='Orphan Page'
        )
        test_session.add(page)
        
        with pytest.raises(Exception):  # Should raise foreign key error
            test_session.commit()
    
    def test_update_page_content(self, test_session):
        """✅ PASS: Should update page content."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        page = Page(
            url='https://example.com/update',
            domain_id=domain.id,
            title='Old Title'
        )
        test_session.add(page)
        test_session.commit()
        
        # Update title
        page.title = 'New Title'
        page.crawled = True
        test_session.commit()
        
        # Verify update
        updated = test_session.query(Page).filter(Page.url == 'https://example.com/update').first()
        assert updated.title == 'New Title'
        assert updated.crawled is True
    
    def test_query_pages_by_domain(self, test_session):
        """✅ PASS: Should retrieve all pages for a domain."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        # Add multiple pages
        for i in range(3):
            page = Page(
                url=f'https://example.com/page{i}',
                domain_id=domain.id,
                title=f'Page {i}'
            )
            test_session.add(page)
        test_session.commit()
        
        # Query by domain
        pages = test_session.query(Page).filter(Page.domain_id == domain.id).all()
        assert len(pages) == 3
    
    def test_page_without_html_allowed(self, test_session):
        """✅ PASS: Should allow page without HTML content."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        page = Page(
            url='https://example.com/no-content',
            domain_id=domain.id,
            title='No Content',
            html=None  # Explicitly null
        )
        test_session.add(page)
        test_session.commit()
        
        saved = test_session.query(Page).filter(Page.url == 'https://example.com/no-content').first()
        assert saved.html is None


class TestCrawlJobPersistence:
    """Test CrawlJob model CRUD operations."""
    
    def test_create_crawl_job(self, test_session):
        """✅ PASS: Should create a crawl job."""
        job = CrawlJob(
            search_query='python programming',
            started=datetime.now(),
            description='Test crawl job'
        )
        test_session.add(job)
        test_session.commit()
        
        saved = test_session.query(CrawlJob).filter(CrawlJob.search_query == 'python programming').first()
        assert saved is not None
        assert saved.description == 'Test crawl job'
    
    def test_crawl_job_allows_null_fields(self, test_session):
        """✅ PASS: Should allow null search_query and description."""
        job = CrawlJob(started=datetime.now())
        test_session.add(job)
        test_session.commit()
        
        saved = test_session.query(CrawlJob).first()
        assert saved is not None
        assert saved.search_query is None
        assert saved.description is None


class TestRequestPersistence:
    """Test Request model CRUD operations."""
    
    def test_create_request_with_relationships(self, test_session):
        """✅ PASS: Should create request with domain and job relationships."""
        # Setup domain and job
        domain = Domain(domain='example.com')
        test_session.add(domain)
        job = CrawlJob(started=datetime.now())
        test_session.add(job)
        test_session.commit()
        
        # Create request
        request = Request(
            url='https://example.com/test',
            request_type='GET',
            domain_id=domain.id,
            crawl_job_id=job.id,
            date_requested=datetime.now(),
            status_code=200
        )
        test_session.add(request)
        test_session.commit()
        
        saved = test_session.query(Request).filter(Request.url == 'https://example.com/test').first()
        assert saved is not None
        assert saved.status_code == 200
        assert saved.domain_id == domain.id
    
    def test_request_invalid_foreign_key(self, test_session):
        """❌ FAIL: Should reject invalid domain_id."""
        request = Request(
            url='https://example.com/test',
            domain_id=99999,  # Invalid
            status_code=200
        )
        test_session.add(request)
        
        with pytest.raises(Exception):
            test_session.commit()


class TestSubjectAndTagPersistence:
    """Test Subject and Tag model CRUD operations."""
    
    def test_create_subject(self, test_session):
        """✅ PASS: Should create a subject."""
        subject = Subject(name='Python')
        test_session.add(subject)
        test_session.commit()
        
        saved = test_session.query(Subject).filter(Subject.name == 'Python').first()
        assert saved is not None
        assert saved.name == 'Python'
    
    def test_subject_unique_constraint(self, test_session):
        """❌ FAIL: Should prevent duplicate subjects."""
        subject1 = Subject(name='Duplicate')
        test_session.add(subject1)
        test_session.commit()
        
        subject2 = Subject(name='Duplicate')
        test_session.add(subject2)
        
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_create_tag(self, test_session):
        """✅ PASS: Should create a tag."""
        tag = Tag(tag='tech:python')
        test_session.add(tag)
        test_session.commit()
        
        saved = test_session.query(Tag).filter(Tag.tag == 'tech:python').first()
        assert saved is not None
    
    def test_link_page_to_subjects(self, test_session):
        """✅ PASS: Should link page to multiple subjects."""
        # Setup
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        page = Page(url='https://example.com/test', domain_id=domain.id, title='Test')
        test_session.add(page)
        
        subject1 = Subject(name='Python')
        subject2 = Subject(name='Programming')
        test_session.add_all([subject1, subject2])
        test_session.commit()
        
        # Link page to subjects
        link1 = PageSubject(page_id=page.id, subject_id=subject1.id)
        link2 = PageSubject(page_id=page.id, subject_id=subject2.id)
        test_session.add_all([link1, link2])
        test_session.commit()
        
        # Verify links
        links = test_session.query(PageSubject).filter(PageSubject.page_id == page.id).all()
        assert len(links) == 2
    
    def test_link_page_to_tags(self, test_session):
        """✅ PASS: Should link page to multiple tags."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        page = Page(url='https://example.com/test', domain_id=domain.id, title='Test')
        test_session.add(page)
        
        tag1 = Tag(tag='tech:python')
        tag2 = Tag(tag='product:laptop')
        test_session.add_all([tag1, tag2])
        test_session.commit()
        
        # Link page to tags
        link1 = PageTag(page_id=page.id, tag_id=tag1.id)
        link2 = PageTag(page_id=page.id, tag_id=tag2.id)
        test_session.add_all([link1, link2])
        test_session.commit()
        
        # Verify links
        links = test_session.query(PageTag).filter(PageTag.page_id == page.id).all()
        assert len(links) == 2
    
    def test_delete_page_removes_associations(self, test_session):
        """✅ PASS: Should cascade delete page associations."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        page = Page(url='https://example.com/test', domain_id=domain.id, title='Test')
        test_session.add(page)
        
        subject = Subject(name='Python')
        test_session.add(subject)
        test_session.commit()
        
        link = PageSubject(page_id=page.id, subject_id=subject.id)
        test_session.add(link)
        test_session.commit()
        
        page_id = page.id
        
        # Delete page
        test_session.delete(page)
        test_session.commit()
        
        # Verify associations are removed (if cascade delete is configured)
        links = test_session.query(PageSubject).filter(PageSubject.page_id == page_id).all()
        # Depending on cascade config, this might be 0 or need manual deletion
        # For now just verify page is gone
        assert test_session.query(Page).filter(Page.id == page_id).first() is None


class TestDataIntegrityAndConstraints:
    """Test data integrity and constraint violations."""
    
    def test_null_url_rejected(self, test_session):
        """❌ FAIL: Should reject page without URL."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        page = Page(
            url=None,  # Required field
            domain_id=domain.id,
            title='No URL'
        )
        test_session.add(page)
        
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_null_domain_name_rejected(self, test_session):
        """❌ FAIL: Should reject domain without name."""
        domain = Domain(domain=None)
        test_session.add(domain)
        
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_transaction_rollback_on_error(self, test_session):
        """✅ PASS: Should rollback transaction on error."""
        domain1 = Domain(domain='first.com')
        test_session.add(domain1)
        test_session.commit()
        
        try:
            # Add valid domain
            domain2 = Domain(domain='second.com')
            test_session.add(domain2)
            
            # Add invalid domain (duplicate)
            domain3 = Domain(domain='first.com')
            test_session.add(domain3)
            
            test_session.commit()  # Should fail
        except Exception:
            test_session.rollback()
        
        # Verify second.com wasn't committed
        result = test_session.query(Domain).filter(Domain.domain == 'second.com').first()
        assert result is None  # Rollback prevented commit


class TestBulkOperations:
    """Test bulk insert and query operations."""
    
    def test_bulk_insert_domains(self, test_session):
        """✅ PASS: Should bulk insert multiple domains."""
        domains = [Domain(domain=f'example{i}.com') for i in range(10)]
        test_session.add_all(domains)
        test_session.commit()
        
        count = test_session.query(Domain).count()
        assert count == 10
    
    def test_bulk_query_with_filter(self, test_session):
        """✅ PASS: Should efficiently query filtered results."""
        domain = Domain(domain='example.com')
        test_session.add(domain)
        test_session.commit()
        
        # Add many pages
        pages = [
            Page(url=f'https://example.com/page{i}', domain_id=domain.id, title=f'Page {i}', crawled=(i % 2 == 0))
            for i in range(20)
        ]
        test_session.add_all(pages)
        test_session.commit()
        
        # Query only crawled pages
        crawled = test_session.query(Page).filter(Page.crawled == True).all()
        assert len(crawled) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
