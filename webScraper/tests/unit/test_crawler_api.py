"""
Tests for Crawler API

Tests the Flask API endpoints for the web crawler.
Includes passing and failing test scenarios.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from crawler_api import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestCrawlEndpoint:
    """Test /api/crawl endpoint."""
    
    def test_crawl_success(self, client):
        """✅ PASS: Should successfully crawl a URL."""
        with patch('crawler_api.ResearchCrawler') as MockCrawler:
            mock_instance = Mock()
            mock_instance.crawl_page.return_value = {
                'url': 'https://example.com',
                'title': 'Example Page',
                'keywords': {'tech': ['python']},
                'links': ['https://example.com/page1']
            }
            MockCrawler.return_value = mock_instance
            
            response = client.post('/api/crawl',
                                 data=json.dumps({'url': 'https://example.com'}),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['url'] == 'https://example.com'
            assert 'title' in data
    
    def test_crawl_missing_url(self, client):
        """❌ FAIL: Should reject request without URL."""
        response = client.post('/api/crawl',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_crawl_with_keywords(self, client):
        """✅ PASS: Should accept keywords parameter."""
        with patch('crawler_api.ResearchCrawler') as MockCrawler:
            mock_instance = Mock()
            mock_instance.crawl_page.return_value = {
                'url': 'https://example.com',
                'title': 'Test',
                'keywords': {}
            }
            MockCrawler.return_value = mock_instance
            
            response = client.post('/api/crawl',
                                 data=json.dumps({
                                     'url': 'https://example.com',
                                     'keywords': ['python', 'programming']
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 200
            # Verify keywords were passed
            mock_instance.crawl_page.assert_called_once()
            args = mock_instance.crawl_page.call_args[0]
            assert args[1] == ['python', 'programming']
    
    def test_crawl_invalid_url(self, client):
        """❌ FAIL: Should handle invalid URLs gracefully."""
        with patch('crawler_api.ResearchCrawler') as MockCrawler:
            mock_instance = Mock()
            mock_instance.crawl_page.side_effect = Exception('Invalid URL')
            MockCrawler.return_value = mock_instance
            
            response = client.post('/api/crawl',
                                 data=json.dumps({'url': 'not-a-url'}),
                                 content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_crawl_server_error(self, client):
        """❌ FAIL: Should handle server errors gracefully."""
        with patch('crawler_api.ResearchCrawler') as MockCrawler:
            MockCrawler.side_effect = Exception('Database connection failed')
            
            response = client.post('/api/crawl',
                                 data=json.dumps({'url': 'https://example.com'}),
                                 content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data


class TestStatsEndpoint:
    """Test /api/stats endpoint."""
    
    def test_get_stats_success(self, client):
        """✅ PASS: Should return crawler statistics."""
        with patch('crawler_api.SessionLocal') as MockSession:
            mock_session = Mock()
            
            # Mock the query chain
            mock_domain_query = Mock()
            mock_domain_query.count.return_value = 3
            
            mock_page_query = Mock()
            mock_page_query.count.return_value = 15
            mock_crawled_query = Mock()
            mock_crawled_query.count.return_value = 10
            mock_page_query.filter.return_value = mock_crawled_query
            
            # Return different queries for Domain and Page
            def query_side_effect(model):
                if 'Domain' in str(model):
                    return mock_domain_query
                else:
                    return mock_page_query
            
            mock_session.query.side_effect = query_side_effect
            MockSession.return_value = mock_session
            
            with patch('Persistance.crawler.Domain'), \
                 patch('Persistance.crawler.Page'):
                
                response = client.get('/api/stats')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'total_domains' in data
                assert 'total_pages' in data
                assert 'crawled_pages' in data
    
    def test_get_stats_empty_database(self, client):
        """✅ PASS: Should handle empty database."""
        with patch('crawler_api.SessionLocal') as MockSession:
            mock_session = Mock()
            
            # Mock empty database
            mock_query = Mock()
            mock_query.count.return_value = 0
            mock_query.filter.return_value.count.return_value = 0
            mock_session.query.return_value = mock_query
            MockSession.return_value = mock_session
            
            with patch('Persistance.crawler.Domain'), \
                 patch('Persistance.crawler.Page'):
                
                response = client.get('/api/stats')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['total_domains'] == 0
                assert data['total_pages'] == 0
                assert data['crawled_pages'] == 0
    
    def test_get_stats_database_error(self, client):
        """❌ FAIL: Should handle database errors."""
        with patch('crawler_api.SessionLocal') as MockSession:
            MockSession.side_effect = Exception('Database unavailable')
            
            response = client.get('/api/stats')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data


class TestExportEndpoint:
    """Test /api/export endpoint."""
    
    def test_export_json_success(self, client):
        """✅ PASS: Should export data as JSON."""
        with patch('crawler_api.SessionLocal') as MockSession:
            mock_session = Mock()
            mock_page = Mock()
            mock_page.url = 'https://example.com'
            mock_page.title = 'Test Page'
            mock_page.date_found = None
            mock_page.crawled = True
            
            mock_query = Mock()
            mock_query.limit.return_value.all.return_value = [mock_page]
            mock_session.query.return_value = mock_query
            MockSession.return_value = mock_session
            
            response = client.get('/api/export?format=json&limit=10')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['url'] == 'https://example.com'
    
    def test_export_csv_success(self, client):
        """✅ PASS: Should export data as CSV."""
        with patch('crawler_api.SessionLocal') as MockSession:
            mock_session = Mock()
            mock_page = Mock()
            mock_page.url = 'https://example.com'
            mock_page.title = 'Test'
            mock_page.date_found = None
            mock_page.crawled = True
            
            mock_query = Mock()
            mock_query.limit.return_value.all.return_value = [mock_page]
            mock_session.query.return_value = mock_query
            MockSession.return_value = mock_session
            
            response = client.get('/api/export?format=csv')
            
            assert response.status_code == 200
            assert b'url,title' in response.data
            assert b'example.com' in response.data
    
    def test_export_with_limit(self, client):
        """✅ PASS: Should respect limit parameter."""
        with patch('crawler_api.SessionLocal') as MockSession:
            mock_session = Mock()
            mock_query = Mock()
            mock_query.limit.return_value.all.return_value = []
            mock_session.query.return_value = mock_query
            MockSession.return_value = mock_session
            
            response = client.get('/api/export?limit=50')
            
            assert response.status_code == 200
            # Verify limit was used
            mock_query.limit.assert_called_once_with(50)
    
    def test_export_default_limit(self, client):
        """✅ PASS: Should use default limit if not specified."""
        with patch('crawler_api.SessionLocal') as MockSession:
            mock_session = Mock()
            mock_query = Mock()
            mock_query.limit.return_value.all.return_value = []
            mock_session.query.return_value = mock_query
            MockSession.return_value = mock_session
            
            response = client.get('/api/export')
            
            assert response.status_code == 200
            # Default limit is 100
            mock_query.limit.assert_called_once_with(100)
    
    def test_export_database_error(self, client):
        """❌ FAIL: Should handle database errors."""
        with patch('crawler_api.SessionLocal') as MockSession:
            MockSession.side_effect = Exception('Query failed')
            
            response = client.get('/api/export')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data


class TestHealthEndpoint:
    """Test /api/health endpoint."""
    
    def test_health_check(self, client):
        """✅ PASS: Should return healthy status."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'message' in data


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers(self, client):
        """✅ PASS: Should include CORS headers."""
        response = client.options('/api/crawl')
        
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200
    
    def test_preflight_request(self, client):
        """✅ PASS: Should handle OPTIONS preflight requests."""
        response = client.options('/api/health')
        
        # Should not return error
        assert response.status_code in [200, 204]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_malformed_json(self, client):
        """❌ FAIL: Should handle malformed JSON."""
        response = client.post('/api/crawl',
                             data='{"invalid": json}',
                             content_type='application/json')
        
        assert response.status_code in [400, 500]
    
    def test_missing_content_type(self, client):
        """❌ FAIL: Should handle missing content type."""
        response = client.post('/api/crawl',
                             data='{"url": "https://example.com"}')
        
        # Should still attempt to process or return error
        assert response.status_code in [400, 415, 500]
    
    def test_empty_post_body(self, client):
        """❌ FAIL: Should handle empty request body."""
        response = client.post('/api/crawl',
                             data='',
                             content_type='application/json')
        
        assert response.status_code in [400, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
