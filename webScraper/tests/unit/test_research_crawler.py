"""
Unit Tests for Research Crawler

Tests for the ResearchCrawler class including:
- Page crawling
- Keyword extraction integration
- Subject extraction
- Link extraction
- Metadata extraction
- Database persistence
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from Crawler.research_crawler import ResearchCrawler
from Crawler.keyword_extractor import KeywordExtractor


class TestResearchCrawlerInit:
    """Test research crawler initialization."""
    
    def test_crawler_initializes(self):
        """✅ PASS: Crawler should initialize successfully."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        assert crawler is not None
        assert crawler.http == mock_http
        assert crawler.repo == mock_repo
        assert isinstance(crawler.visited_urls, set)
        assert isinstance(crawler.keyword_extractor, KeywordExtractor)
    
    def test_visited_urls_starts_empty(self):
        """✅ PASS: visited_urls should start empty."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        assert len(crawler.visited_urls) == 0


class TestExtractMainContent:
    """Test _extract_main_content method."""
    
    def test_extract_from_article_tag(self):
        """✅ PASS: Should extract from article tag."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <nav>Navigation</nav>
                    <article>
                        <h1>Article Content</h1>
                        <p>This is the main content.</p>
                    </article>
                    <footer>Footer</footer>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        content = crawler._extract_main_content(soup)
        
        assert 'Article Content' in content
        assert 'main content' in content
        assert 'Navigation' not in content
        assert 'Footer' not in content
    
    def test_extract_from_main_tag(self):
        """✅ PASS: Should extract from main tag."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <header>Header</header>
                    <main>
                        <h1>Main Content</h1>
                        <p>This is the main content.</p>
                    </main>
                    <aside>Sidebar</aside>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        content = crawler._extract_main_content(soup)
        
        assert 'Main Content' in content
        assert 'Header' not in content
        assert 'Sidebar' not in content
    
    def test_removes_scripts_and_styles(self):
        """✅ PASS: Should remove script and style tags."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <script>alert('test');</script>
                    <style>.class { color: red; }</style>
                    <p>Real content</p>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        content = crawler._extract_main_content(soup)
        
        assert 'Real content' in content
        assert 'alert' not in content
        assert 'color: red' not in content
    
    def test_content_length_limit(self):
        """✅ PASS: Should limit content to 50k chars."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '<html><body>' + ('x' * 100000) + '</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        content = crawler._extract_main_content(soup)
        
        assert len(content) <= 50000


class TestExtractSubjects:
    """Test _extract_subjects method."""
    
    def test_extract_provided_keywords(self):
        """✅ PASS: Should extract provided keywords."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        title = "Python Programming"
        content = "Learn Python and Django for web development"
        keywords = ["python", "django"]
        
        subjects = crawler._extract_subjects(title, content, keywords)
        
        assert 'python' in subjects
        assert 'django' in subjects
    
    def test_extract_capitalized_phrases(self):
        """✅ PASS: Should extract capitalized phrases."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        title = "Machine Learning Tutorial"
        content = "Learn about Neural Networks and Deep Learning"
        keywords = []
        
        subjects = crawler._extract_subjects(title, content, keywords)
        
        # Should extract "Machine Learning", "Neural Networks", "Deep Learning"
        assert len(subjects) > 0
    
    def test_limits_to_20_subjects(self):
        """✅ PASS: Should limit to 20 subjects."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        # Create text with many capitalized phrases
        content = ' '.join([f"Topic{i}" for i in range(100)])
        
        subjects = crawler._extract_subjects("Title", content, [])
        
        assert len(subjects) <= 20


class TestExtractTags:
    """Test _extract_tags method."""
    
    def test_extract_meta_keywords(self):
        """✅ PASS: Should extract meta keywords."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <head>
                    <meta name="keywords" content="python, programming, tutorial">
                </head>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        tags = crawler._extract_tags(soup)
        
        assert 'python' in tags
        assert 'programming' in tags
        assert 'tutorial' in tags
    
    def test_extract_article_tags(self):
        """✅ PASS: Should extract article tags."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <div class="tags">
                        <a>python</a>
                        <a>web development</a>
                    </div>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        tags = crawler._extract_tags(soup)
        
        assert 'python' in tags
        assert 'web development' in tags
    
    def test_limits_to_15_tags(self):
        """✅ PASS: Should limit to 15 tags."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '<html><head><meta name="keywords" content="' + ','.join([f"tag{i}" for i in range(50)]) + '"></head></html>'
        soup = BeautifulSoup(html, 'html.parser')
        tags = crawler._extract_tags(soup)
        
        assert len(tags) <= 15


class TestExtractLinks:
    """Test _extract_links method."""
    
    def test_extract_absolute_urls(self):
        """✅ PASS: Should extract absolute URLs."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <a href="https://example.com/page1">Link 1</a>
                    <a href="https://example.com/page2">Link 2</a>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = crawler._extract_links(soup, "https://example.com")
        
        assert 'https://example.com/page1' in links
        assert 'https://example.com/page2' in links
    
    def test_convert_relative_to_absolute(self):
        """✅ PASS: Should convert relative URLs to absolute."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <a href="/page1">Link 1</a>
                    <a href="page2">Link 2</a>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = crawler._extract_links(soup, "https://example.com")
        
        assert 'https://example.com/page1' in links
        assert 'https://example.com/page2' in links
    
    def test_filter_non_http_links(self):
        """✅ PASS: Should filter out non-HTTP links."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <a href="javascript:void(0)">JS Link</a>
                    <a href="mailto:test@example.com">Email</a>
                    <a href="tel:123456">Phone</a>
                    <a href="https://example.com/page1">Valid</a>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = crawler._extract_links(soup, "https://example.com")
        
        assert 'https://example.com/page1' in links
        assert len([l for l in links if 'javascript:' in l]) == 0
        assert len([l for l in links if 'mailto:' in l]) == 0
        assert len([l for l in links if 'tel:' in l]) == 0
    
    def test_filter_social_media_links(self):
        """✅ PASS: Should filter out social media links."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <a href="https://facebook.com/page">Facebook</a>
                    <a href="https://twitter.com/user">Twitter</a>
                    <a href="https://example.com/page">Valid</a>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = crawler._extract_links(soup, "https://example.com")
        
        assert 'https://example.com/page' in links
        assert len([l for l in links if 'facebook.com' in l]) == 0
        assert len([l for l in links if 'twitter.com' in l]) == 0
    
    def test_deduplicates_links(self):
        """✅ PASS: Should deduplicate links."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <body>
                    <a href="https://example.com/page1">Link 1</a>
                    <a href="https://example.com/page1">Link 1 Again</a>
                    <a href="https://example.com/page1">Link 1 Third</a>
                </body>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = crawler._extract_links(soup, "https://example.com")
        
        assert links.count('https://example.com/page1') == 1


class TestCalculateRelevance:
    """Test _calculate_relevance method."""
    
    def test_relevance_with_keywords(self):
        """✅ PASS: Should calculate relevance based on keywords."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        title = "Python Programming"
        content = "Learn Python programming with our Python tutorials"
        keywords = ["python"]
        
        score = crawler._calculate_relevance(title, content, keywords)
        
        assert 0 <= score <= 1.0
        assert score > 0  # Should have some relevance
    
    def test_relevance_without_keywords(self):
        """✅ PASS: Should return 0.5 with no keywords."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        title = "Test"
        content = "Content"
        keywords = []
        
        score = crawler._calculate_relevance(title, content, keywords)
        
        assert score == 0.5
    
    def test_relevance_caps_at_one(self):
        """✅ PASS: Should cap relevance at 1.0."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        title = "Python " * 100
        content = "Python " * 1000
        keywords = ["python"]
        
        score = crawler._calculate_relevance(title, content, keywords)
        
        assert score <= 1.0


class TestExtractMeta:
    """Test _extract_meta method."""
    
    def test_extract_og_meta(self):
        """✅ PASS: Should extract Open Graph meta tags."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <head>
                    <meta property="og:type" content="article">
                </head>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        og_type = crawler._extract_meta(soup, 'og:type')
        
        assert og_type == 'article'
    
    def test_extract_name_meta(self):
        """✅ PASS: Should extract name attribute meta tags."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '''
            <html>
                <head>
                    <meta name="author" content="John Doe">
                </head>
            </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        author = crawler._extract_meta(soup, 'author')
        
        assert author == 'John Doe'
    
    def test_returns_none_if_not_found(self):
        """✅ PASS: Should return None if meta tag not found."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        html = '<html><head></head></html>'
        soup = BeautifulSoup(html, 'html.parser')
        result = crawler._extract_meta(soup, 'nonexistent')
        
        assert result is None


class TestGenerateSummary:
    """Test _generate_summary method."""
    
    def test_summary_truncates_long_text(self):
        """✅ PASS: Should truncate long text."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        content = ' '.join(['word'] * 200)
        summary = crawler._generate_summary(content, max_words=100)
        
        assert len(summary.split()) <= 101  # 100 words + '...'
        assert summary.endswith('...')
    
    def test_summary_keeps_short_text(self):
        """✅ PASS: Should keep short text as is."""
        mock_http = MagicMock()
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http, mock_repo)
        
        content = "Short content"
        summary = crawler._generate_summary(content, max_words=100)
        
        assert summary == content
        assert not summary.endswith('...')


class TestCrawlPageIntegration:
    """Test crawl_page method with mocked HTTP."""
    
    def test_crawl_page_returns_data(self, mock_http_client, sample_html):
        """✅ PASS: Should return structured data."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': sample_html
        }
        
        mock_repo = MagicMock()
        mock_repo.session = MagicMock()
        
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", ["python"])
        
        assert result is not None
        assert 'title' in result
        assert 'content' in result
        assert 'tech_skills' in result
        assert 'product_categories' in result
        assert 'seasonal_themes' in result
        assert 'metadata' in result
    
    def test_crawl_page_extracts_tech_skills(self, mock_http_client, sample_html):
        """✅ PASS: Should extract tech skills from page."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': sample_html
        }
        
        mock_repo = MagicMock()
        mock_repo.session = MagicMock()
        
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert 'python' in result['tech_skills']
    
    def test_crawl_page_returns_none_on_error(self, mock_http_client):
        """✅ PASS: Should return None on HTTP error."""
        mock_http_client.get.return_value = {
            'error': 'Connection failed',
            'status_code': 500,
            'body': ''
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is None
    
    def test_crawl_page_returns_none_on_404(self, mock_http_client):
        """✅ PASS: Should return None on 404."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 404,
            'body': ''
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is None


class TestFailureScenarios:
    """Test failure scenarios."""
    
    def test_malformed_html(self, mock_http_client):
        """❌ EXPECTED FAIL: Should handle malformed HTML gracefully."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test</title></head><body><p>Unclosed paragraph'
        }
        
        mock_repo = MagicMock()
        mock_repo.session = MagicMock()
        
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        # Should not crash, BeautifulSoup handles malformed HTML
        result = crawler.crawl_page("https://example.com", [])
        assert result is not None
    
    def test_empty_html(self, mock_http_client):
        """❌ EXPECTED FAIL: Should handle empty HTML."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': ''
        }
        
        mock_repo = MagicMock()
        mock_repo.session = MagicMock()
        
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        # Should return data but with empty fields
        assert result is not None
        assert result['title'] == ''
        assert result['content'] == ''
    
    def test_database_error_handling(self, mock_http_client, sample_html):
        """❌ EXPECTED FAIL: Should handle database errors."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': sample_html
        }
        
        mock_repo = MagicMock()
        mock_repo.session.query.side_effect = Exception("Database error")
        
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        # Should not crash, should log error
        # The _save_page method has try/except
        result = crawler.crawl_page("https://example.com", [])
        
        # Should still return data even if save fails
        assert result is not None


class TestResearchTopic:
    """Test research_topic method - main entry point."""
    
    def test_research_topic_basic_crawl(self, mock_http_client):
        """✅ PASS: Should crawl pages starting from seed URL."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test Page</title></head><body><main>Python programming tutorial</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=['python'],
            max_depth=1,
            max_pages=5
        )
        
        assert result is not None
        assert 'pages_crawled' in result
        assert 'subjects_found' in result
        assert 'related_links' in result
        assert 'key_findings' in result
        assert result['pages_crawled'] >= 1
    
    def test_research_topic_respects_max_depth(self, mock_http_client):
        """✅ PASS: Should not crawl deeper than max_depth."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test</title></head><body><main><a href="https://example.com/link1">Link</a></main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=[],
            max_depth=0,  # Only seed URL
            max_pages=100
        )
        
        # Should only crawl the seed URL
        assert result['pages_crawled'] == 1
    
    def test_research_topic_respects_max_pages(self, mock_http_client):
        """✅ PASS: Should stop after max_pages crawled."""
        # Return HTML with many links
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '''<html><body><main>
                <a href="https://example.com/1">Link 1</a>
                <a href="https://example.com/2">Link 2</a>
                <a href="https://example.com/3">Link 3</a>
                <a href="https://example.com/4">Link 4</a>
                <a href="https://example.com/5">Link 5</a>
            </main></body></html>'''
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=[],
            max_depth=5,
            max_pages=3  # Limit to 3 pages
        )
        
        # Should stop at 3 pages
        assert result['pages_crawled'] == 3
    
    def test_research_topic_tracks_visited_urls(self, mock_http_client):
        """✅ PASS: Should not crawl same URL twice."""
        call_count = 0
        
        def get_with_links(url):
            nonlocal call_count
            call_count += 1
            # Return HTML that links back to seed (circular)
            return {
                'error': None,
                'status_code': 200,
                'body': '<html><body><main><a href="https://example.com">Back to home</a></main></body></html>'
            }
        
        mock_http_client.get.side_effect = get_with_links
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=[],
            max_depth=3,
            max_pages=10
        )
        
        # Should only crawl example.com once despite circular link
        assert result['pages_crawled'] == 1
        assert 'https://example.com' in crawler.visited_urls
    
    def test_research_topic_extracts_subjects(self, mock_http_client):
        """✅ PASS: Should aggregate subjects from all pages."""
        responses = [
            '<html><head><title>Python Tutorial</title></head><body><main><h1>Python Basics</h1><a href="https://example.com/django">Django Guide</a></main></body></html>',
            '<html><head><title>Django Guide</title></head><body><main><h1>Django Framework</h1></main></body></html>',
        ]
        
        call_count = [0]
        
        def get_response(url):
            idx = call_count[0] % len(responses)
            call_count[0] += 1
            return {
                'error': None,
                'status_code': 200,
                'body': responses[idx]
            }
        
        mock_http_client.get.side_effect = get_response
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=['python', 'django'],
            max_depth=1,
            max_pages=2
        )
        
        # Should find subjects from both pages
        assert len(result['subjects_found']) > 0
        assert result['pages_crawled'] == 2
    
    def test_research_topic_finds_relevant_pages(self, mock_http_client):
        """✅ PASS: Should include pages with relevance > 0.5 in findings."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Python Programming</title></head><body><main>Python Python Python Django Flask</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=['python', 'django'],  # Keywords that appear in content
            max_depth=1,
            max_pages=5
        )
        
        # Should have key findings for relevant page
        assert len(result['key_findings']) > 0
        finding = result['key_findings'][0]
        assert 'url' in finding
        assert 'title' in finding
        assert 'relevance' in finding
        assert finding['relevance'] > 0.5
    
    def test_research_topic_sorts_by_relevance(self, mock_http_client):
        """✅ PASS: Should return findings sorted by relevance score."""
        responses = [
            '<html><head><title>High Relevance</title></head><body><main>Python Python Python Python Django Django</main></body></html>',
            '<html><head><title>Low Relevance</title></head><body><main>Something else</main></body></html>',
            '<html><head><title>Medium Relevance</title></head><body><main>Python tutorial</main></body></html>',
        ]
        
        call_count = [0]
        
        def get_response(url):
            idx = call_count[0]
            call_count[0] += 1
            if idx < len(responses):
                return {'error': None, 'status_code': 200, 'body': responses[idx]}
            return {'error': 'Not found', 'status_code': 404, 'body': ''}
        
        mock_http_client.get.side_effect = get_response
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=['python'],
            max_depth=0,
            max_pages=3
        )
        
        # Findings should be sorted by relevance (high to low)
        if len(result['key_findings']) >= 2:
            for i in range(len(result['key_findings']) - 1):
                assert result['key_findings'][i]['relevance'] >= result['key_findings'][i + 1]['relevance']
    
    def test_research_topic_limits_results(self, mock_http_client):
        """✅ PASS: Should limit findings to 20 and links to 50."""
        # Return HTML with many links
        links_html = ''.join([f'<a href="https://example.com/link{i}">Link {i}</a>' for i in range(100)])
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': f'<html><head><title>Test</title></head><body><main>Python content {links_html}</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=['python'],
            max_depth=2,
            max_pages=30
        )
        
        # Should limit findings to 20
        assert len(result['key_findings']) <= 20
        # Should limit related links to 50
        assert len(result['related_links']) <= 50
    
    def test_research_topic_handles_errors(self, mock_http_client):
        """✅ PASS: Should continue after individual page failures."""
        call_count = [0]
        
        def get_with_errors(url):
            call_count[0] += 1
            # Fail on second call, succeed on others
            if call_count[0] == 2:
                return {'error': 'Connection timeout', 'status_code': 500, 'body': ''}
            return {
                'error': None,
                'status_code': 200,
                'body': '<html><head><title>Test</title></head><body><main><a href="https://example.com/next">Link</a></main></body></html>'
            }
        
        mock_http_client.get.side_effect = get_with_errors
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=[],
            max_depth=2,
            max_pages=5
        )
        
        # Should have crawled some pages despite error
        assert result['pages_crawled'] >= 1
    
    def test_research_topic_follows_links(self, mock_http_client):
        """✅ PASS: Should follow outbound links to specified depth."""
        call_count = [0]
        
        def get_with_depth(url):
            call_count[0] += 1
            return {
                'error': None,
                'status_code': 200,
                'body': f'<html><head><title>Page {call_count[0]}</title></head><body><main><a href="https://example.com/page{call_count[0]+1}">Next</a></main></body></html>'
            }
        
        mock_http_client.get.side_effect = get_with_depth
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        result = crawler.research_topic(
            seed_url='https://example.com',
            keywords=[],
            max_depth=2,
            max_pages=10
        )
        
        # Should have followed links
        assert result['pages_crawled'] > 1


class TestCrawlPageEnhancements:
    """Test enhanced crawl_page functionality with keyword extraction."""
    
    def test_crawl_page_extracts_product_categories(self, mock_http_client):
        """✅ PASS: Should extract product categories from content."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Shop Electronics</title></head><body><main>Buy laptop smartphone and camera at great prices!</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert 'product_categories' in result
        assert isinstance(result['product_categories'], list)
        # Should find laptop, smartphone, camera
        assert len(result['product_categories']) > 0
    
    def test_crawl_page_extracts_seasonal_themes(self, mock_http_client):
        """✅ PASS: Should extract seasonal themes from content."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Holiday Sale</title></head><body><main>Christmas deals and Black Friday specials!</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert 'seasonal_themes' in result
        assert isinstance(result['seasonal_themes'], list)
        # Should find christmas, black friday
        assert len(result['seasonal_themes']) > 0
    
    def test_crawl_page_extracts_demographics(self, mock_http_client):
        """✅ PASS: Should extract demographics from content."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Products for Everyone</title></head><body><main>Great gifts for kids, teenagers, and professionals!</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert 'demographics' in result
        assert isinstance(result['demographics'], list)
    
    def test_crawl_page_detects_tech_pages(self, mock_http_client):
        """✅ PASS: Should set is_tech_related flag for tech content."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Python Tutorial</title></head><body><main>Learn Python programming with Django and Flask frameworks</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert 'metadata' in result
        assert result['metadata']['is_tech_related'] == True
    
    def test_crawl_page_detects_ecommerce_pages(self, mock_http_client):
        """✅ PASS: Should set is_ecommerce_related flag for shopping content."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Buy Products</title></head><body><main>Shop laptop smartphone tablet camera speaker keyboard mouse monitor at great prices! Add to cart and buy now!</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert 'metadata' in result
        assert result['metadata']['is_ecommerce_related'] == True
    
    def test_crawl_page_calculates_top_categories(self, mock_http_client):
        """✅ PASS: Should return top 5 product categories with scores."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Electronics Store</title></head><body><main>Buy laptops, smartphones, tablets, cameras, and headphones</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert 'top_categories' in result
        assert isinstance(result['top_categories'], list)
        assert len(result['top_categories']) <= 5
        # Each should be a tuple of (category, score)
        if len(result['top_categories']) > 0:
            assert isinstance(result['top_categories'][0], tuple)
            assert len(result['top_categories'][0]) == 2
    
    def test_crawl_page_extracts_metadata_fields(self, mock_http_client):
        """✅ PASS: Should extract all metadata fields."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '''<html>
                <head>
                    <title>Test Article</title>
                    <meta name="author" content="John Doe">
                    <meta name="keywords" content="python, tutorial">
                    <meta property="article:published_time" content="2025-01-01">
                    <meta property="og:type" content="article">
                </head>
                <body><main>Content here</main></body>
            </html>'''
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert 'metadata' in result
        metadata = result['metadata']
        assert 'author' in metadata
        assert 'published_date' in metadata
        assert 'keywords' in metadata
        assert 'og_type' in metadata
        assert 'word_count' in metadata
        assert 'fetch_time' in metadata
    
    def test_crawl_page_calculates_word_count(self, mock_http_client):
        """✅ PASS: Should calculate word count correctly."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test</title></head><body><main>One two three four five words here</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", [])
        
        assert result is not None
        assert result['metadata']['word_count'] > 0
    
    def test_crawl_page_return_structure_complete(self, mock_http_client):
        """✅ PASS: Should return complete dictionary structure."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Complete Test</title></head><body><main>Python Django Flask</main></body></html>'
        }
        
        mock_repo = MagicMock()
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        result = crawler.crawl_page("https://example.com", ['python'])
        
        # Verify all expected keys are present
        expected_keys = [
            'title', 'content', 'summary', 'subjects', 'tags',
            'outbound_links', 'relevance_score', 'metadata',
            'tech_skills', 'product_categories', 'seasonal_themes',
            'demographics', 'top_categories'
        ]
        
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"


@pytest.mark.skip(reason="Requires database connection")
class TestSavePageMethod:
    """Test _save_page database persistence."""
    
    def test_save_page_creates_domain(self, mock_http_client, test_session):
        """✅ PASS: Should create domain if it doesn't exist."""
        from Persistance.crawler import Domain
        
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test</title></head><body>Content</body></html>'
        }
        
        from Persistance.repository import Repository
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http_client, repo)
        
        crawler.crawl_page("https://newdomain.com/page", [])
        
        # Check domain was created
        domain = test_session.query(Domain).filter(Domain.name == 'newdomain.com').first()
        assert domain is not None
    
    def test_save_page_inserts_page(self, mock_http_client, test_session):
        """✅ PASS: Should insert page with all fields."""
        from Persistance.crawler import Page
        
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test Page</title></head><body><main>Test content here</main></body></html>'
        }
        
        from Persistance.repository import Repository
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http_client, repo)
        
        crawler.crawl_page("https://example.com/test", [])
        
        # Check page was inserted
        page = test_session.query(Page).filter(Page.url == 'https://example.com/test').first()
        assert page is not None
        assert page.title == 'Test Page'
        assert 'Test content' in page.content
    
    def test_save_page_creates_subjects(self, mock_http_client, test_session):
        """✅ PASS: Should create and link subjects to page."""
        from Persistance.crawler import Page, Subject, PageSubject
        
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Python Tutorial</title></head><body><main><h1>Python Programming</h1></main></body></html>'
        }
        
        from Persistance.repository import Repository
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http_client, repo)
        
        crawler.crawl_page("https://example.com/python", ['python'])
        
        # Check page was created
        page = test_session.query(Page).filter(Page.url == 'https://example.com/python').first()
        assert page is not None
        
        # Check subjects were linked
        page_subjects = test_session.query(PageSubject).filter(PageSubject.page_id == page.id).all()
        assert len(page_subjects) > 0
    
    def test_save_page_creates_tags_with_prefixes(self, mock_http_client, test_session):
        """✅ PASS: Should create tags with tech:, product:, seasonal: prefixes."""
        from Persistance.crawler import Page, Tag, PageTag
        
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Shop Tech</title></head><body><main>Python programming laptops for Christmas</main></body></html>'
        }
        
        from Persistance.repository import Repository
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http_client, repo)
        
        crawler.crawl_page("https://example.com/shop", [])
        
        # Check page was created
        page = test_session.query(Page).filter(Page.url == 'https://example.com/shop').first()
        assert page is not None
        
        # Check tags were created with prefixes
        tags = test_session.query(Tag).join(PageTag).filter(PageTag.page_id == page.id).all()
        tag_names = [tag.name for tag in tags]
        
        # Should have at least some prefixed tags
        has_tech_tag = any(tag.startswith('tech:') for tag in tag_names)
        has_product_tag = any(tag.startswith('product:') for tag in tag_names)
        has_seasonal_tag = any(tag.startswith('seasonal:') for tag in tag_names)
        
        # At least one type should be present
        assert has_tech_tag or has_product_tag or has_seasonal_tag
    
    def test_save_page_handles_duplicate_urls(self, mock_http_client, test_session):
        """✅ PASS: Should handle duplicate page URLs gracefully."""
        from Persistance.crawler import Page
        
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test</title></head><body>Content</body></html>'
        }
        
        from Persistance.repository import Repository
        repo = Repository(test_session)
        crawler = ResearchCrawler(mock_http_client, repo)
        
        # Crawl same URL twice
        crawler.crawl_page("https://example.com/duplicate", [])
        crawler.crawl_page("https://example.com/duplicate", [])
        
        # Should only have one page entry (or handle gracefully)
        pages = test_session.query(Page).filter(Page.url == 'https://example.com/duplicate').all()
        # Implementation may update or skip, but should not crash
        assert len(pages) >= 1
    
    def test_save_page_handles_save_errors(self, mock_http_client):
        """✅ PASS: Should handle database save errors gracefully."""
        mock_http_client.get.return_value = {
            'error': None,
            'status_code': 200,
            'body': '<html><head><title>Test</title></head><body>Content</body></html>'
        }
        
        mock_repo = MagicMock()
        mock_repo.session.commit.side_effect = Exception("Database error")
        
        crawler = ResearchCrawler(mock_http_client, mock_repo)
        
        # Should not crash, should handle error
        result = crawler.crawl_page("https://example.com", [])
        
        # Should still return data even if save fails
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
