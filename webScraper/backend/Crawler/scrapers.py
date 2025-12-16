from typing import Generator, Dict, Optional, List
from urllib.parse import urlparse, urljoin
import logging
import time
import urllib.robotparser
from abc import ABC, abstractmethod

from Crawler.http_client import HttpClient
from Crawler.parsers import parse_listings, extract_fields, normalize_url

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base scraper with common functionality.
    Concrete scrapers implement source-specific logic.
    """
    
    def __init__(
        self,
        http_client: HttpClient,
        polite_delay_seconds: float = 2.0,
        max_pages: int = 10
    ):
        self.http = http_client
        self.polite_delay_seconds = polite_delay_seconds
        self.max_pages = max_pages
        self._robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
    
    def _get_robots_parser(self, base_url: str) -> Optional[urllib.robotparser.RobotFileParser]:
        """
        Get cached robots.txt parser for domain.
        Returns None if cannot fetch or parse.
        """
        domain = urlparse(base_url).netloc
        
        if domain in self._robots_cache:
            return self._robots_cache[domain]
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            
            # Fetch with timeout
            response = self.http.get(robots_url)
            if response['status_code'] == 200:
                from io import StringIO
                rp.parse(StringIO(response['body']).readlines())
            else:
                # Allow if robots.txt not found
                rp.allow_all = True
            
            self._robots_cache[domain] = rp
            return rp
            
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt for {base_url}: {e}")
            return None
    
    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """
        Check if URL can be fetched per robots.txt.
        Defaults to allowing if robots.txt cannot be checked.
        """
        try:
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            rp = self._get_robots_parser(base_url)
            
            if rp is None:
                return True  # Conservative: allow if cannot check
            
            return rp.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow on error
    
    def polite_delay(self):
        """Sleep for polite delay."""
        time.sleep(self.polite_delay_seconds)
    
    @abstractmethod
    def scrape(self, source_config: Dict) -> Generator[Dict, None, None]:
        """
        Scrape job listings from source.
        Must be implemented by concrete scrapers.
        
        Yields dicts with structure:
        {
            'external_id': str | None,
            'source_name': str,
            'title_html': str | None,
            'company_html': str | None,
            'location_text': str | None,
            'posted_text': str | None,
            'url': str | None,
            'snippet_html': str | None,
            'salary_text': str | None,
            'raw_payload': str,  # Full HTML fragment
            'fetch_metadata': dict  # HTTP response metadata
        }
        """
        pass


class GenericScraper(BaseScraper):
    """
    Generic scraper for job boards with pagination.
    Handles list pages → detail pages pattern.
    """
    
    def scrape(self, source_config: Dict) -> Generator[Dict, None, None]:
        """
        Scrape using generic pagination + listing extraction.
        
        source_config keys:
            - name: Source name
            - base_url: Starting URL
            - pagination_pattern: URL pattern with {page} placeholder
            - listing_selector: CSS selector for listings
            - field selectors: title_selector, company_selector, etc.
        """
        source_name = source_config.get('name', 'unknown')
        base_url = source_config['base_url']
        pagination_pattern = source_config.get('pagination_pattern', base_url)
        
        logger.info(f"Starting scrape for {source_name}: {base_url}")
        
        page_num = 1
        listings_found = 0
        
        while page_num <= self.max_pages:
            # Build page URL
            page_url = pagination_pattern.format(page=page_num)
            
            # Check robots.txt
            if not self.can_fetch(page_url):
                logger.warning(f"robots.txt disallows {page_url} - skipping")
                break
            
            # Polite delay before request
            if page_num > 1:
                self.polite_delay()
            
            # Fetch page
            logger.info(f"Fetching page {page_num}: {page_url}")
            response = self.http.get(page_url)
            
            if response['error']:
                logger.error(f"HTTP error on page {page_num}: {response['error']}")
                if response['captcha']:
                    logger.error(f"Captcha detected - stopping scrape for {source_name}")
                    break
                # Continue to next page on other errors
                page_num += 1
                continue
            
            if response['status_code'] != 200:
                logger.warning(f"Non-200 status on page {page_num}: {response['status_code']}")
                if response['status_code'] == 404:
                    logger.info("Reached end of pagination (404)")
                    break
                page_num += 1
                continue
            
            # Parse listings
            html = response['body']
            fragments = parse_listings(html, source_config)
            
            if not fragments:
                logger.info(f"No listings found on page {page_num} - stopping")
                break
            
            # Process each listing
            for fragment in fragments:
                try:
                    fields = extract_fields(fragment, source_config)
                    
                    # Normalize URL if relative
                    if fields['url'] and not fields['url'].startswith('http'):
                        fields['url'] = normalize_url(fields['url'], page_url)
                    
                    # Build result
                    result = {
                        'external_id': fields['external_id'],
                        'source_name': source_name,
                        'title_html': fields['title_html'],
                        'company_html': fields['company_html'],
                        'location_text': fields['location_text'],
                        'posted_text': fields['posted_text'],
                        'url': fields['url'],
                        'snippet_html': fields['snippet_html'],
                        'salary_text': fields['salary_text'],
                        'raw_payload': fragment,
                        'fetch_metadata': {
                            'status_code': response['status_code'],
                            'fetch_duration_ms': response['fetch_duration_ms'],
                            'page_url': page_url,
                            'page_num': page_num
                        }
                    }
                    
                    listings_found += 1
                    yield result
                    
                except Exception as e:
                    logger.error(f"Error processing listing fragment: {e}")
                    continue
            
            logger.info(f"Page {page_num}: extracted {len(fragments)} listings")
            page_num += 1
        
        logger.info(f"Scrape complete for {source_name}: {listings_found} listings across {page_num - 1} pages")


class IndeedScraper(BaseScraper):
    """Indeed-specific scraper with their URL patterns."""
    
    def scrape(self, source_config: Dict) -> Generator[Dict, None, None]:
        """
        Scrape Indeed with their specific pagination.
        
        Indeed uses start parameter: ?q=python&l=remote&start=0
        """
        source_name = source_config.get('name', 'Indeed')
        base_url = source_config.get('base_url', 'https://www.indeed.com/jobs')
        search_params = source_config.get('search_params', {})
        
        logger.info(f"Starting Indeed scrape: {search_params}")
        
        start = 0
        listings_per_page = 15  # Indeed shows ~15 per page
        
        for page_num in range(1, self.max_pages + 1):
            # Build URL with pagination
            params = search_params.copy()
            params['start'] = start
            
            url = base_url
            
            if not self.can_fetch(url):
                logger.warning(f"robots.txt disallows Indeed scraping")
                break
            
            if page_num > 1:
                self.polite_delay()
            
            response = self.http.get(url, params=params)
            
            if response['error'] or response['status_code'] != 200:
                logger.error(f"Indeed page {page_num} error: {response.get('error', response['status_code'])}")
                break
            
            # Parse Indeed-specific structure
            fragments = parse_listings(response['body'], {
                'listing_selector': '.job_seen_beacon, .jobsearch-SerpJobCard'
            })
            
            if not fragments:
                break
            
            for fragment in fragments:
                fields = extract_fields(fragment, {
                    'id_attr': 'data-jk',
                    'title_selector': 'h2.jobTitle',
                    'company_selector': '.companyName',
                    'location_selector': '.companyLocation',
                    'snippet_selector': '.job-snippet'
                })
                
                yield {
                    'external_id': fields['external_id'],
                    'source_name': source_name,
                    'title_html': fields['title_html'],
                    'company_html': fields['company_html'],
                    'location_text': fields['location_text'],
                    'posted_text': fields['posted_text'],
                    'url': normalize_url(fields['url'], 'https://www.indeed.com'),
                    'snippet_html': fields['snippet_html'],
                    'salary_text': fields['salary_text'],
                    'raw_payload': fragment,
                    'fetch_metadata': {
                        'status_code': response['status_code'],
                        'fetch_duration_ms': response['fetch_duration_ms']
                    }
                }
            
            start += listings_per_page


class LinkedInScraper(BaseScraper):
    """
    LinkedIn scraper (requires authentication).
    Placeholder for authenticated scraping.
    """
    
    def scrape(self, source_config: Dict) -> Generator[Dict, None, None]:
        """
        LinkedIn requires authentication - this is a placeholder.
        Production implementation would need Selenium + login flow.
        """
        logger.warning("LinkedIn scraping requires authentication - not implemented")
        return
        yield  # Make it a generator


def get_scraper(source_type: str, http_client: HttpClient, **kwargs) -> BaseScraper:
    """
    Factory to get appropriate scraper for source type.
    
    Args:
        source_type: 'generic', 'indeed', 'linkedin', etc.
        http_client: HTTP client instance
        **kwargs: Additional scraper config (polite_delay_seconds, max_pages)
    
    Returns:
        Scraper instance
    """
    scrapers = {
        'generic': GenericScraper,
        'indeed': IndeedScraper,
        'linkedin': LinkedInScraper,
    }
    
    scraper_class = scrapers.get(source_type.lower(), GenericScraper)
    
    return scraper_class(http_client, **kwargs)
