"""
E-Commerce Product Scrapers

Site-specific scrapers for major e-commerce platforms.
"""

from typing import Generator, Dict, Optional, List
from urllib.parse import urlparse, urljoin, quote_plus
import logging
import re
import json

from Crawler.http_client import HttpClient
from Crawler.parsers import extract_text
from Crawler.scrapers import BaseScraper

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """
    Amazon product scraper.
    
    Note: Amazon heavily rate-limits and blocks scrapers.
    Consider using Amazon Product Advertising API for production.
    """
    
    def scrape(self, source_config: Dict) -> Generator[Dict, None, None]:
        """
        Scrape Amazon products.
        
        source_config keys:
            - name: 'Amazon'
            - search_query: Search term
            - category: Optional category filter
            - min_price: Optional minimum price
            - max_price: Optional maximum price
        """
        source_name = source_config.get('name', 'Amazon')
        search_query = source_config.get('search_query', '')
        category = source_config.get('category', 'aps')  # 'aps' = all departments
        
        logger.info(f"Starting Amazon scrape for: {search_query}")
        
        base_url = 'https://www.amazon.com/s'
        
        for page_num in range(1, min(self.max_pages + 1, 20)):  # Amazon limits to ~20 pages
            # Build search URL
            params = {
                'k': search_query,
                'i': category,
                'page': page_num
            }
            
            if source_config.get('min_price'):
                params['low-price'] = source_config['min_price']
            if source_config.get('max_price'):
                params['high-price'] = source_config['max_price']
            
            # Amazon blocks standard requests - need good headers
            headers = {
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.amazon.com/'
            }
            
            if page_num > 1:
                self.polite_delay()
            
            response = self.http.get(base_url, params=params, headers=headers)
            
            if response['error'] or response['status_code'] != 200:
                logger.error(f"Amazon page {page_num} error: {response.get('error', response['status_code'])}")
                if response['captcha']:
                    logger.error("CAPTCHA detected - Amazon blocking. Consider using API or rotating proxies.")
                    break
                continue
            
            # Parse Amazon's product cards
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response['body'], 'html.parser')
            
            # Amazon uses data-component-type="s-search-result"
            products = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            if not products:
                logger.info(f"No products found on page {page_num}")
                break
            
            logger.info(f"Found {len(products)} products on page {page_num}")
            
            for product in products:
                try:
                    # Extract ASIN (Amazon Standard Identification Number)
                    asin = product.get('data-asin')
                    if not asin:
                        continue
                    
                    # Title
                    title_elem = product.find('h2')
                    title = extract_text(str(title_elem)) if title_elem else ''
                    
                    # URL
                    link_elem = title_elem.find('a') if title_elem else None
                    url = urljoin('https://www.amazon.com', link_elem['href']) if link_elem and link_elem.get('href') else ''
                    
                    # Price
                    price_elem = product.find('span', class_='a-price')
                    price_text = ''
                    if price_elem:
                        price_whole = price_elem.find('span', class_='a-price-whole')
                        price_fraction = price_elem.find('span', class_='a-price-fraction')
                        if price_whole:
                            price_text = price_whole.get_text(strip=True)
                            if price_fraction:
                                price_text += price_fraction.get_text(strip=True)
                    
                    # Original price (if on sale)
                    original_price_elem = product.find('span', class_='a-price a-text-price')
                    original_price_text = ''
                    if original_price_elem:
                        original_price_text = original_price_elem.get_text(strip=True)
                    
                    # Rating
                    rating_elem = product.find('span', class_='a-icon-alt')
                    rating_text = rating_elem.get_text(strip=True) if rating_elem else ''
                    
                    # Review count
                    review_elem = product.find('span', {'class': 'a-size-base', 'dir': 'auto'})
                    review_count_text = review_elem.get_text(strip=True) if review_elem else ''
                    
                    # Image
                    img_elem = product.find('img', class_='s-image')
                    image_url = img_elem.get('src', '') if img_elem else ''
                    
                    # Prime eligible
                    prime_elem = product.find('i', class_='a-icon-prime')
                    prime_eligible = prime_elem is not None
                    
                    yield {
                        'external_id': asin,
                        'source_name': source_name,
                        'name': title,
                        'url': url,
                        'price_text': price_text,
                        'original_price_text': original_price_text,
                        'rating_text': rating_text,
                        'review_count_text': review_count_text,
                        'image_url': image_url,
                        'prime_eligible': prime_eligible,
                        'brand': '',  # Not in search results
                        'raw_payload': str(product),
                        'fetch_metadata': {
                            'status_code': response['status_code'],
                            'fetch_duration_ms': response['fetch_duration_ms'],
                            'page_num': page_num
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Error parsing Amazon product: {e}")
                    continue


class EbayScraper(BaseScraper):
    """eBay product scraper."""
    
    def scrape(self, source_config: Dict) -> Generator[Dict, None, None]:
        """
        Scrape eBay products.
        
        source_config keys:
            - search_query: Search term
            - category: Optional category ID
            - condition: 'new' or 'used'
        """
        source_name = source_config.get('name', 'eBay')
        search_query = source_config.get('search_query', '')
        
        logger.info(f"Starting eBay scrape for: {search_query}")
        
        base_url = 'https://www.ebay.com/sch/i.html'
        
        for page_num in range(1, self.max_pages + 1):
            params = {
                '_nkw': search_query,
                '_pgn': page_num
            }
            
            if source_config.get('condition') == 'new':
                params['LH_ItemCondition'] = '1000'  # New
            
            if page_num > 1:
                self.polite_delay()
            
            response = self.http.get(base_url, params=params)
            
            if response['error'] or response['status_code'] != 200:
                logger.error(f"eBay page {page_num} error")
                continue
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response['body'], 'html.parser')
            
            # eBay uses li.s-item
            products = soup.find_all('li', class_='s-item')
            
            if not products:
                break
            
            logger.info(f"Found {len(products)} eBay listings on page {page_num}")
            
            for product in products:
                try:
                    # Skip promoted/ad listings
                    if 'SPONSORED' in product.get_text():
                        continue
                    
                    # Item ID
                    link = product.find('a', class_='s-item__link')
                    if not link or not link.get('href'):
                        continue
                    
                    url = link['href']
                    
                    # Extract item ID from URL
                    match = re.search(r'/itm/(\d+)', url)
                    item_id = match.group(1) if match else ''
                    
                    # Title
                    title_elem = product.find('div', class_='s-item__title')
                    title = extract_text(str(title_elem)) if title_elem else ''
                    
                    # Price
                    price_elem = product.find('span', class_='s-item__price')
                    price_text = price_elem.get_text(strip=True) if price_elem else ''
                    
                    # Shipping
                    shipping_elem = product.find('span', class_='s-item__shipping')
                    shipping_text = shipping_elem.get_text(strip=True) if shipping_elem else ''
                    
                    # Condition
                    condition_elem = product.find('span', class_='SECONDARY_INFO')
                    condition_text = condition_elem.get_text(strip=True) if condition_elem else ''
                    
                    # Image
                    img_elem = product.find('img')
                    image_url = img_elem.get('src', '') if img_elem else ''
                    
                    # Seller info
                    seller_elem = product.find('span', class_='s-item__seller-info-text')
                    seller_text = seller_elem.get_text(strip=True) if seller_elem else ''
                    
                    yield {
                        'external_id': item_id,
                        'source_name': source_name,
                        'name': title,
                        'url': url.split('?')[0],  # Remove query params
                        'price_text': price_text,
                        'shipping_text': shipping_text,
                        'condition_text': condition_text,
                        'seller_text': seller_text,
                        'image_url': image_url,
                        'raw_payload': str(product),
                        'fetch_metadata': {
                            'status_code': response['status_code'],
                            'fetch_duration_ms': response['fetch_duration_ms'],
                            'page_num': page_num
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Error parsing eBay listing: {e}")
                    continue


class WalmartScraper(BaseScraper):
    """Walmart product scraper."""
    
    def scrape(self, source_config: Dict) -> Generator[Dict, None, None]:
        """
        Scrape Walmart products.
        
        Note: Walmart uses dynamic JavaScript. This may need headless browser.
        """
        source_name = source_config.get('name', 'Walmart')
        search_query = source_config.get('search_query', '')
        
        logger.info(f"Starting Walmart scrape for: {search_query}")
        
        base_url = 'https://www.walmart.com/search'
        
        for page_num in range(1, self.max_pages + 1):
            params = {
                'q': search_query,
                'page': page_num
            }
            
            if page_num > 1:
                self.polite_delay()
            
            response = self.http.get(base_url, params=params)
            
            if response['error'] or response['status_code'] != 200:
                logger.error(f"Walmart page {page_num} error")
                continue
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response['body'], 'html.parser')
            
            # Walmart uses data-item-id attribute
            products = soup.find_all('div', {'data-item-id': True})
            
            if not products:
                # Try alternative selector
                products = soup.find_all('div', class_=re.compile(r'search-result-gridview-item'))
            
            if not products:
                logger.warning(f"Walmart may require JavaScript rendering - found {len(products)} products")
                break
            
            logger.info(f"Found {len(products)} Walmart products on page {page_num}")
            
            for product in products:
                try:
                    item_id = product.get('data-item-id', '')
                    
                    # Title
                    title_elem = product.find('span', class_=re.compile(r'product-title'))
                    title = extract_text(str(title_elem)) if title_elem else ''
                    
                    # Link
                    link_elem = product.find('a', href=True)
                    url = urljoin('https://www.walmart.com', link_elem['href']) if link_elem else ''
                    
                    # Price
                    price_elem = product.find('span', class_=re.compile(r'price-characteristic'))
                    price_text = price_elem.get_text(strip=True) if price_elem else ''
                    
                    # Rating
                    rating_elem = product.find('span', class_=re.compile(r'rating'))
                    rating_text = rating_elem.get_text(strip=True) if rating_elem else ''
                    
                    # Image
                    img_elem = product.find('img')
                    image_url = img_elem.get('src', '') if img_elem else ''
                    
                    yield {
                        'external_id': item_id,
                        'source_name': source_name,
                        'name': title,
                        'url': url,
                        'price_text': price_text,
                        'rating_text': rating_text,
                        'image_url': image_url,
                        'raw_payload': str(product),
                        'fetch_metadata': {
                            'status_code': response['status_code'],
                            'fetch_duration_ms': response['fetch_duration_ms'],
                            'page_num': page_num
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Error parsing Walmart product: {e}")
                    continue


def get_product_scraper(source_type: str, http_client: HttpClient, **kwargs) -> BaseScraper:
    """
    Factory to get appropriate product scraper.
    
    Args:
        source_type: 'amazon', 'ebay', 'walmart', 'generic'
        http_client: HTTP client instance
        **kwargs: Additional scraper config
    
    Returns:
        Product scraper instance
    """
    from crawler.scrapers import GenericScraper
    
    scrapers = {
        'amazon': AmazonScraper,
        'ebay': EbayScraper,
        'walmart': WalmartScraper,
        'generic': GenericScraper
    }
    
    scraper_class = scrapers.get(source_type.lower(), GenericScraper)
    
    return scraper_class(http_client, **kwargs)
