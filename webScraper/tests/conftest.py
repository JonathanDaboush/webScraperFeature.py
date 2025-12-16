"""
Test Configuration and Fixtures

Shared test configuration, fixtures, and utilities for the test suite.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Test Database Configuration
TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5432/webscraper_test"


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a new database session for a test."""
    from Persistance.crawler import Base
    
    # Create all tables
    Base.metadata.create_all(test_engine)
    
    # Create session
    Session = sessionmaker(bind=test_engine)
    session = Session()
    
    yield session
    
    # Cleanup
    session.rollback()
    session.close()
    
    # Drop all tables after test
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing without network calls."""
    client = MagicMock()
    client.get.return_value = {
        'error': None,
        'status_code': 200,
        'body': '''
            <html>
                <head>
                    <title>Test Page</title>
                    <meta name="description" content="Test description">
                </head>
                <body>
                    <h1>Test Content</h1>
                    <p>This is test content for Python development</p>
                </body>
            </html>
        '''
    }
    return client


@pytest.fixture
def sample_html():
    """Sample HTML for testing parsers."""
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sample Page - Python Development</title>
            <meta name="description" content="Learn Python programming">
            <meta name="keywords" content="python, programming, development">
        </head>
        <body>
            <main>
                <h1>Python Programming Tutorial</h1>
                <p>This tutorial covers Python, Django, Flask, and React.</p>
                <a href="https://example.com/page1">Link 1</a>
                <a href="https://example.com/page2">Link 2</a>
            </main>
        </body>
        </html>
    '''


@pytest.fixture
def sample_tech_text():
    """Sample text with tech skills."""
    return """
    Senior Full Stack Developer needed for startup.
    Requirements:
    - Python, JavaScript, TypeScript
    - React, Django, Flask
    - PostgreSQL, MongoDB, Redis
    - AWS, Docker, Kubernetes
    - Git, CI/CD
    Experience with machine learning is a plus.
    """


@pytest.fixture
def sample_ecommerce_text():
    """Sample text with product categories."""
    return """
    Gaming Laptop Sale - Best Deals!
    Features:
    - High performance laptop with RTX 4080
    - Mechanical keyboard included
    - Gaming mouse and headphones
    - Perfect for students and professionals
    - Free shipping on all electronics
    """


@pytest.fixture
def sample_seasonal_text():
    """Sample text with seasonal themes."""
    return """
    Christmas Sale! Holiday Shopping Deals
    - Christmas trees and ornaments
    - Gifts for kids and adults
    - Halloween costumes clearance
    - Valentine's Day special
    - Black Friday prices all week!
    """


# Helper Functions

def assert_keywords_found(result, expected_keywords, keyword_type='tech_skills'):
    """Assert that expected keywords are found in results."""
    found_keywords = result.get(keyword_type, [])
    for keyword in expected_keywords:
        assert keyword in found_keywords, f"Expected '{keyword}' in {keyword_type}"


def assert_no_keywords(result, keyword_type='tech_skills'):
    """Assert that no keywords of a specific type are found."""
    found_keywords = result.get(keyword_type, [])
    assert len(found_keywords) == 0, f"Expected no {keyword_type}, but found: {found_keywords}"


def create_mock_page_response(title, content, url="https://example.com"):
    """Create a mock HTTP response for a page."""
    return {
        'error': None,
        'status_code': 200,
        'body': f'''
            <html>
                <head><title>{title}</title></head>
                <body><p>{content}</p></body>
            </html>
        '''
    }
