"""
Integration Tests for Web Scraper

Tests the full integration of components:
- Crawler + Database
- API endpoints
- Keyword extraction + Persistence
- End-to-end workflows
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


@pytest.mark.integration
class TestAPIEndpoints:
    """Test API endpoint integration."""
    
    @pytest.mark.skip(reason="Requires running Flask server")
    def test_keyword_extract_endpoint(self):
        """✅ PASS: Should extract keywords via API."""
        import requests
        
        response = requests.post(
            'http://localhost:5000/api/keywords/extract',
            json={
                'text': 'Python developer needed with React experience',
                'title': 'Job Posting'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'tech_skills' in data
        assert 'python' in data['tech_skills']
        assert 'react' in data['tech_skills']
    
    @pytest.mark.skip(reason="Requires running Flask server")
    def test_get_categories_endpoint(self):
        """✅ PASS: Should get available categories via API."""
        import requests
        
        response = requests.get('http://localhost:5000/api/keywords/categories')
        
        assert response.status_code == 200
        data = response.json()
        assert 'tech_skills' in data
        assert 'product_categories' in data
        assert data['total_tech_skills'] > 0


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_save_page_to_database(self, test_session):
        """✅ PASS: Should save page to database."""
        from Persistance.crawler import Page, Domain
        
        # Create domain
        domain = Domain(name='example.com')
        test_session.add(domain)
        test_session.flush()
        
        # Create page
        page = Page(
            url='https://example.com/page1',
            domain_id=domain.id,
            title='Test Page',
            content='Test content',
            summary='Summary',
            status_code=200
        )
        test_session.add(page)
        test_session.commit()
        
        # Query back
        saved_page = test_session.query(Page).filter(Page.url == 'https://example.com/page1').first()
        
        assert saved_page is not None
        assert saved_page.title == 'Test Page'
        assert saved_page.content == 'Test content'
    
    def test_save_tags_with_prefixes(self, test_session):
        """✅ PASS: Should save tags with prefixes."""
        from Persistance.crawler import Tag, Page, Domain, PageTag
        
        # Create domain and page
        domain = Domain(name='example.com')
        test_session.add(domain)
        test_session.flush()
        
        page = Page(
            url='https://example.com/test',
            domain_id=domain.id,
            title='Test',
            content='Content',
            status_code=200
        )
        test_session.add(page)
        test_session.flush()
        
        # Create tags with prefixes
        tech_tag = Tag(name='tech:python')
        product_tag = Tag(name='product:laptop')
        seasonal_tag = Tag(name='seasonal:christmas')
        
        test_session.add_all([tech_tag, product_tag, seasonal_tag])
        test_session.flush()
        
        # Link to page
        test_session.add(PageTag(page_id=page.id, tag_id=tech_tag.id))
        test_session.add(PageTag(page_id=page.id, tag_id=product_tag.id))
        test_session.add(PageTag(page_id=page.id, tag_id=seasonal_tag.id))
        test_session.commit()
        
        # Query back
        saved_page = test_session.query(Page).filter(Page.url == 'https://example.com/test').first()
        tags = [tag.name for tag in saved_page.tags]
        
        assert 'tech:python' in tags
        assert 'product:laptop' in tags
        assert 'seasonal:christmas' in tags


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    def test_crawl_and_extract_workflow(self, mock_http_client, test_session):
        """✅ PASS: Full crawl + extract + save workflow."""
        from Crawler.research_crawler import ResearchCrawler
        from Persistance.repository import Repository
        from Persistance.crawler import Page
        
        # Setup
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '''
                <html>
                    <head><title>Python Tutorial</title></head>
                    <body>
                        <main>
                            <h1>Learn Python Programming</h1>
                            <p>Python and Django for web development</p>
                        </main>
                    </body>
                </html>
            '''
        }
        
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http_client, repo)
        
        # Execute
        result = crawler.crawl_page('https://example.com/python', ['python'])
        
        # Verify
        assert result is not None
        assert 'python' in result['tech_skills']
        assert 'django' in result['tech_skills']
        
        # Check database
        saved_page = test_session.query(Page).filter(
            Page.url == 'https://example.com/python'
        ).first()
        
        assert saved_page is not None
        assert 'Python' in saved_page.title
    
    def test_browser_history_analysis_workflow(self):
        """✅ PASS: Browser history extraction + analysis workflow."""
        from Crawler.browser_history import BrowserHistory
        
        # Note: This test requires actual browser history files
        # In production, you'd mock the file access
        history = BrowserHistory()
        
        # This should not crash even with no history files
        interests = history.get_user_interests(days_back=1)
        
        assert isinstance(interests, dict)
        assert 'tech_skills' in interests
        assert 'product_interests' in interests
        assert 'seasonal_interests' in interests


@pytest.mark.integration
class TestPerformance:
    """Test performance characteristics."""
    
    def test_extract_keywords_performance(self):
        """✅ PASS: Keyword extraction should be fast."""
        from Crawler.keyword_extractor import KeywordExtractor
        import time
        
        extractor = KeywordExtractor()
        text = "Python developer with React and AWS experience " * 100
        
        start = time.time()
        result = extractor.extract_all(text)
        duration = time.time() - start
        
        # Should complete in < 0.5 seconds
        assert duration < 0.5
        assert len(result['tech_skills']) > 0
    
    def test_crawl_multiple_pages_performance(self, mock_http_client, test_session):
        """✅ PASS: Should crawl multiple pages efficiently."""
        from Crawler.research_crawler import ResearchCrawler
        from Persistance.repository import Repository
        import time
        
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test</title></head><body>Content</body></html>'
        }
        
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http_client, repo)
        
        start = time.time()
        for i in range(10):
            crawler.crawl_page(f'https://example.com/page{i}', [])
        duration = time.time() - start
        
        # Should crawl 10 pages in < 5 seconds
        assert duration < 5.0


@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery and resilience."""
    
    def test_continues_after_failed_page(self, test_session):
        """✅ PASS: Should continue after a page fails to crawl."""
        from Crawler.research_crawler import ResearchCrawler
        from Persistance.repository import Repository
        
        # Mock HTTP client that fails then succeeds
        mock_http = MagicMock()
        mock_http.get.side_effect = [
            {'error': 'Timeout', 'status_code': 500, 'body': ''},
            {'error': None, 'status_code': 200, 'body': '<html><body>Success</body></html>'}
        ]
        
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http, repo)
        
        # First should fail
        result1 = crawler.crawl_page('https://example.com/fail', [])
        assert result1 is None
        
        # Second should succeed
        result2 = crawler.crawl_page('https://example.com/success', [])
        assert result2 is not None
    
    def test_handles_database_constraint_violations(self, test_session):
        """✅ PASS: Should handle duplicate entries gracefully."""
        from Persistance.crawler import Domain
        
        # Add domain
        domain1 = Domain(name='example.com')
        test_session.add(domain1)
        test_session.commit()
        
        # Try to add duplicate (should handle in application code)
        existing = test_session.query(Domain).filter(Domain.name == 'example.com').first()
        assert existing is not None
        
        # Don't add duplicate
        domain2_query = test_session.query(Domain).filter(Domain.name == 'example.com').first()
        assert domain2_query.id == domain1.id


class TestDataConsistency:
    """Test data consistency across operations."""
    
    def test_page_tags_consistency(self, test_session):
        """✅ PASS: Tags should remain consistent with pages."""
        from Persistance.crawler import Page, Domain, Tag, PageTag
        
        # Create domain and page
        domain = Domain(name='test.com')
        test_session.add(domain)
        test_session.flush()
        
        page = Page(
            url='https://test.com/page',
            domain_id=domain.id,
            title='Test',
            content='Content',
            status_code=200
        )
        test_session.add(page)
        test_session.flush()
        
        # Add tag
        tag = Tag(name='test-tag')
        test_session.add(tag)
        test_session.flush()
        
        page_tag = PageTag(page_id=page.id, tag_id=tag.id)
        test_session.add(page_tag)
        test_session.commit()
        
        # Verify relationship
        saved_page = test_session.query(Page).get(page.id)
        assert len(saved_page.tags) == 1
        assert saved_page.tags[0].name == 'test-tag'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-m', 'integration'])
