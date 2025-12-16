from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


def parse_listings(html: str, source_config: Dict) -> List[str]:
    """
    Extract listing fragments from HTML using selectors.
    Never throws - returns empty list on failure.
    
    Args:
        html: Page HTML content
        source_config: Dict with 'listing_selector' key
    
    Returns:
        List of HTML fragment strings (each representing one listing)
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try source-specific selector first
        selector = source_config.get('listing_selector', '.job, article, li.listing')
        
        listings = soup.select(selector)
        
        if not listings:
            # Fallback heuristics
            for fallback_selector in ['.job-card', '.posting', 'article', '[data-job-id]', 'li']:
                listings = soup.select(fallback_selector)
                if listings:
                    logger.info(f"Used fallback selector: {fallback_selector}")
                    break
        
        # Check if JS-rendered content (empty with script tags)
        if not listings and soup.find_all('script'):
            scripts = soup.find_all('script')
            if len(scripts) > 5 and len(soup.get_text(strip=True)) < 200:
                logger.warning("Detected JS-rendered content - may need headless browser")
                return ['__JS_CONTENT_DETECTED__']
        
        fragments = [str(listing) for listing in listings]
        logger.info(f"Extracted {len(fragments)} listings using selector: {selector}")
        
        return fragments
        
    except Exception as e:
        logger.error(f"parse_listings error: {e}")
        return []


def extract_fields(fragment: str, source_config: Dict) -> Dict:
    """
    Extract structured fields from a listing fragment.
    Returns dict with nullable fields - never throws.
    
    Args:
        fragment: HTML fragment string
        source_config: Dict with field selectors
    
    Returns:
        {
            'external_id': str | None,
            'title_html': str | None,
            'company_html': str | None,
            'location_text': str | None,
            'posted_text': str | None,
            'url': str | None,
            'snippet_html': str | None,
            'salary_text': str | None
        }
    """
    result = {
        'external_id': None,
        'title_html': None,
        'company_html': None,
        'location_text': None,
        'posted_text': None,
        'url': None,
        'snippet_html': None,
        'salary_text': None,
        'parse_warning': None
    }
    
    try:
        soup = BeautifulSoup(fragment, 'html.parser')
        
        # External ID (from data attribute or href)
        id_attr = source_config.get('id_attr', 'data-job-id')
        if soup.has_attr(id_attr):
            result['external_id'] = soup[id_attr]
        else:
            # Try to extract from link
            link = soup.find('a', href=True)
            if link:
                # Extract ID from URL pattern like /job/12345
                match = re.search(r'/job[s]?/(\w+)', link['href'])
                if match:
                    result['external_id'] = match.group(1)
        
        # Title
        title_selector = source_config.get('title_selector', 'h2, h3, .title, .job-title')
        title_elem = soup.select_one(title_selector)
        if title_elem:
            result['title_html'] = str(title_elem)[:240]  # Limit length
        
        # Company
        company_selector = source_config.get('company_selector', '.company, .employer')
        company_elem = soup.select_one(company_selector)
        if company_elem:
            result['company_html'] = str(company_elem)[:200]
        
        # Location
        location_selector = source_config.get('location_selector', '.location, .job-location')
        location_elem = soup.select_one(location_selector)
        if location_elem:
            result['location_text'] = location_elem.get_text(strip=True)[:128]
        
        # Posted date
        posted_selector = source_config.get('posted_selector', '.date, .posted, time')
        posted_elem = soup.select_one(posted_selector)
        if posted_elem:
            # Try datetime attribute first
            if posted_elem.has_attr('datetime'):
                result['posted_text'] = posted_elem['datetime']
            else:
                result['posted_text'] = posted_elem.get_text(strip=True)[:64]
        
        # URL
        link = soup.find('a', href=True)
        if link:
            url = link['href']
            # Canonicalize URL - remove tracking params
            url = re.sub(r'[?&](utm_|ref=|source=)[^&]*', '', url)
            result['url'] = url[:512]
        
        # Snippet/Description
        snippet_selector = source_config.get('snippet_selector', '.description, .snippet, p')
        snippet_elem = soup.select_one(snippet_selector)
        if snippet_elem:
            result['snippet_html'] = str(snippet_elem)[:5000]
        
        # Salary
        salary_selector = source_config.get('salary_selector', '.salary, .pay, .compensation')
        salary_elem = soup.select_one(salary_selector)
        if salary_elem:
            result['salary_text'] = salary_elem.get_text(strip=True)[:128]
        
        # Validation warnings
        if not result['title_html']:
            result['parse_warning'] = 'missing_title'
            logger.warning(f"Missing title in fragment: {fragment[:100]}")
        
    except Exception as e:
        logger.error(f"extract_fields error: {e}")
        result['parse_warning'] = f'parse_error: {str(e)[:100]}'
    
    return result


def clean_html(html: str) -> str:
    """
    Remove scripts, styles, and dangerous elements.
    Returns sanitized HTML string.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove dangerous elements
        for element in soup(['script', 'style', 'iframe', 'object', 'embed']):
            element.decompose()
        
        # Remove event handlers
        for tag in soup.find_all(True):
            for attr in list(tag.attrs.keys()):
                if attr.startswith('on'):  # onclick, onerror, etc.
                    del tag.attrs[attr]
        
        return str(soup)
        
    except Exception as e:
        logger.error(f"clean_html error: {e}")
        return html


def extract_text(html: str) -> str:
    """
    Extract plain text from HTML, removing tags.
    Returns clean text string.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove scripts and styles
        for element in soup(['script', 'style']):
            element.decompose()
        
        # Get text with spacing
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    except Exception as e:
        logger.error(f"extract_text error: {e}")
        return ""


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """
    Normalize and canonicalize URL.
    Handles relative URLs, removes tracking params.
    """
    from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
    
    try:
        # Make absolute if relative
        if base_url and not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url)
        
        # Parse URL
        parsed = urlparse(url)
        
        # Remove tracking parameters
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            
            # Filter out tracking params
            tracking_prefixes = ['utm_', 'ref', 'source', 'campaign', 'medium', 'fbclid', 'gclid']
            clean_params = {
                k: v for k, v in params.items()
                if not any(k.startswith(prefix) for prefix in tracking_prefixes)
            }
            
            # Rebuild query string
            clean_query = urlencode(clean_params, doseq=True) if clean_params else ''
            parsed = parsed._replace(query=clean_query)
        
        # Remove fragment (anchor)
        parsed = parsed._replace(fragment='')
        
        return urlunparse(parsed)
        
    except Exception as e:
        logger.error(f"normalize_url error for {url}: {e}")
        return url
