"""
Product Normalizer

Transform raw product data into canonical format with fingerprinting.
"""

from typing import Dict, Optional
from datetime import datetime
import re
import hashlib
import logging

logger = logging.getLogger(__name__)


def normalize_product(raw_entry: Dict, ingest_version: str = "1.0.0") -> Dict:
    """
    Transform raw product entry → Product canonical format.
    
    Input (from scrapers):
        {
            'external_id': str,
            'source_name': str,
            'name': str,
            'url': str,
            'price_text': str,
            'original_price_text': str,
            'brand': str,
            'rating_text': str,
            'review_count_text': str,
            'image_url': str,
            'raw_payload': str
        }
    
    Output:
        {
            'name': str,
            'brand': str,
            'sku': str,
            'external_id': str,
            'url': str,
            'image_url': str,
            'current_price_cents': int,
            'original_price_cents': int,
            'currency': str,
            'discount_percent': int,
            'is_on_sale': bool,
            'in_stock': bool,
            'rating': float,
            'review_count': int,
            'fingerprint': str,
            'ingest_version': str,
            'normalized_at': datetime
        }
    """
    
    # Extract and clean name
    name = clean_product_name(raw_entry.get('name', 'Unknown Product'))
    brand = extract_brand(raw_entry.get('brand', ''), name)
    
    # Parse prices
    current_price_info = parse_price(raw_entry.get('price_text', ''))
    original_price_info = parse_price(raw_entry.get('original_price_text', ''))
    
    current_price_cents = current_price_info['cents']
    original_price_cents = original_price_info['cents'] or current_price_cents
    currency = current_price_info['currency']
    
    # Calculate discount
    discount_percent = 0
    is_on_sale = False
    if original_price_cents and current_price_cents and original_price_cents > current_price_cents:
        discount_percent = int(((original_price_cents - current_price_cents) / original_price_cents) * 100)
        is_on_sale = True
    
    # Parse rating
    rating = parse_rating(raw_entry.get('rating_text', ''))
    
    # Parse review count
    review_count = parse_review_count(raw_entry.get('review_count_text', ''))
    
    # Stock status
    in_stock = infer_stock_status(raw_entry)
    
    # Generate fingerprint for deduplication
    fingerprint = generate_product_fingerprint(name, brand, raw_entry.get('external_id', ''))
    
    return {
        'name': name[:500],
        'brand': brand[:200] if brand else None,
        'model': None,  # Would need detailed page scraping
        'sku': None,
        'upc': None,
        'external_id': raw_entry.get('external_id', '')[:128],
        'url': raw_entry.get('url', '')[:512],
        'image_url': raw_entry.get('image_url', '')[:512],
        'current_price_cents': current_price_cents,
        'original_price_cents': original_price_cents,
        'currency': currency,
        'discount_percent': discount_percent,
        'is_on_sale': is_on_sale,
        'in_stock': in_stock,
        'stock_quantity': None,
        'availability_text': raw_entry.get('availability_text'),
        'description': None,  # Would need detail page
        'specifications': None,
        'features': None,
        'rating': rating,
        'review_count': review_count,
        'shipping_cost_cents': parse_shipping_cost(raw_entry.get('shipping_text', '')),
        'free_shipping': 'free' in raw_entry.get('shipping_text', '').lower(),
        'prime_eligible': raw_entry.get('prime_eligible', False),
        'seller_name': extract_seller(raw_entry.get('seller_text', '')),
        'seller_rating': None,
        'fingerprint': fingerprint,
        'ingest_version': ingest_version,
        'normalized_at': datetime.utcnow()
    }


def clean_product_name(name: str) -> str:
    """Clean and normalize product name."""
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Remove common prefixes
    name = re.sub(r'^(New|Used|Refurbished):\s*', '', name, flags=re.IGNORECASE)
    
    # Remove excessive capitalization
    if name.isupper() and len(name) > 10:
        name = name.title()
    
    return name


def extract_brand(brand_text: str, product_name: str) -> Optional[str]:
    """Extract brand from text or product name."""
    if brand_text and brand_text.strip():
        return brand_text.strip()
    
    # Try to extract from name (first word often brand)
    # Common brands
    brands = [
        'Apple', 'Samsung', 'Sony', 'LG', 'Dell', 'HP', 'Lenovo', 'Asus',
        'Microsoft', 'Google', 'Amazon', 'Nike', 'Adidas', 'Puma',
        'Canon', 'Nikon', 'Panasonic', 'Philips', 'Bosch', 'Dyson'
    ]
    
    name_lower = product_name.lower()
    for brand in brands:
        if brand.lower() in name_lower:
            return brand
    
    # Fallback: first word if capitalized
    first_word = product_name.split()[0] if product_name.split() else ''
    if first_word and first_word[0].isupper():
        return first_word
    
    return None


def parse_price(price_text: str) -> Dict:
    """
    Parse price text into cents.
    
    Examples:
        "$19.99" -> 1999
        "£45.50" -> 4550
        "$1,234.56" -> 123456
        "19.99 to 29.99" -> 1999 (take first price)
    
    Returns:
        {'cents': int | None, 'currency': str}
    """
    if not price_text:
        return {'cents': None, 'currency': 'USD'}
    
    # Detect currency
    currency = 'USD'
    if '£' in price_text or 'GBP' in price_text:
        currency = 'GBP'
    elif '€' in price_text or 'EUR' in price_text:
        currency = 'EUR'
    elif '¥' in price_text or 'JPY' in price_text:
        currency = 'JPY'
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[£$€¥,]', '', price_text)
    
    # Extract first number (handle ranges like "19.99 to 29.99")
    match = re.search(r'(\d+(?:\.\d{2})?)', cleaned)
    if not match:
        return {'cents': None, 'currency': currency}
    
    try:
        price_float = float(match.group(1))
        
        # Convert to cents
        if currency == 'JPY':
            # Yen doesn't use decimals
            cents = int(price_float)
        else:
            cents = int(price_float * 100)
        
        return {'cents': cents, 'currency': currency}
    
    except (ValueError, AttributeError):
        return {'cents': None, 'currency': currency}


def parse_rating(rating_text: str) -> Optional[float]:
    """
    Parse rating text.
    
    Examples:
        "4.5 out of 5 stars" -> 4.5
        "4.5 stars" -> 4.5
        "4.5" -> 4.5
    """
    if not rating_text:
        return None
    
    # Extract decimal number
    match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
    if match:
        try:
            rating = float(match.group(1))
            # Validate range
            if 0 <= rating <= 5:
                return rating
        except ValueError:
            pass
    
    return None


def parse_review_count(review_text: str) -> int:
    """
    Parse review count text.
    
    Examples:
        "1,234 reviews" -> 1234
        "(500)" -> 500
        "1.2K ratings" -> 1200
    """
    if not review_text:
        return 0
    
    # Remove commas
    cleaned = review_text.replace(',', '')
    
    # Handle K/M suffixes
    match = re.search(r'(\d+(?:\.\d+)?)\s*([KkMm])', cleaned)
    if match:
        num = float(match.group(1))
        suffix = match.group(2).upper()
        if suffix == 'K':
            return int(num * 1000)
        elif suffix == 'M':
            return int(num * 1000000)
    
    # Regular number
    match = re.search(r'(\d+)', cleaned)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    
    return 0


def parse_shipping_cost(shipping_text: str) -> Optional[int]:
    """
    Parse shipping cost.
    
    Examples:
        "Free shipping" -> None
        "$5.99 shipping" -> 599
    """
    if not shipping_text:
        return None
    
    if 'free' in shipping_text.lower():
        return None
    
    # Extract price
    price_info = parse_price(shipping_text)
    return price_info['cents']


def extract_seller(seller_text: str) -> Optional[str]:
    """Extract seller name from text."""
    if not seller_text:
        return None
    
    # Remove common prefixes
    seller = re.sub(r'^(Sold by|Seller:)\s*', '', seller_text, flags=re.IGNORECASE)
    
    # Remove ratings like "(98.5%)"
    seller = re.sub(r'\([0-9.]+%\)', '', seller)
    
    return seller.strip()[:200] or None


def infer_stock_status(raw_entry: Dict) -> bool:
    """Infer if product is in stock based on various signals."""
    # Check explicit availability text
    availability = raw_entry.get('availability_text', '').lower()
    if availability:
        out_of_stock_indicators = ['out of stock', 'unavailable', 'sold out', 'not available']
        if any(indicator in availability for indicator in out_of_stock_indicators):
            return False
        
        in_stock_indicators = ['in stock', 'available', 'ships']
        if any(indicator in availability for indicator in in_stock_indicators):
            return True
    
    # If price exists, likely in stock
    if raw_entry.get('price_text'):
        return True
    
    # Default to True
    return True


def generate_product_fingerprint(name: str, brand: Optional[str], external_id: str) -> str:
    """
    Generate SHA256 fingerprint for product deduplication.
    
    Components:
        - Normalized name (lowercase, no special chars)
        - Brand (if present)
        - External ID (if present)
    """
    # Normalize name: lowercase, remove special chars
    normalized_name = re.sub(r'[^a-z0-9\s]', '', name.lower())
    normalized_name = re.sub(r'\s+', ' ', normalized_name).strip()
    
    parts = [
        normalized_name,
        (brand or '').lower().strip(),
        external_id[:50]  # Use part of external ID
    ]
    
    fingerprint_input = '|'.join(parts)
    
    return hashlib.sha256(fingerprint_input.encode('utf-8')).hexdigest()


def calculate_price_change_percent(old_price_cents: int, new_price_cents: int) -> int:
    """Calculate percentage price change."""
    if not old_price_cents or not new_price_cents:
        return 0
    
    if old_price_cents == new_price_cents:
        return 0
    
    change = ((new_price_cents - old_price_cents) / old_price_cents) * 100
    
    return int(change)
