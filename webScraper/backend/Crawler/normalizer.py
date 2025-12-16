from typing import Dict, Optional
from datetime import datetime, timedelta
import re
import hashlib
import logging

from Crawler.parsers import extract_text

logger = logging.getLogger(__name__)


def normalize(raw_entry: Dict, ingest_version: str = "1.0.0") -> Dict:
    """
    Transform RawJobEntry → JobPosting canonical format.
    
    Input (from scrapers):
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
            'raw_payload': str
        }
    
    Output:
        {
            'title': str,
            'company': str,
            'location': str | None,
            'description': str | None,
            'url': str | None,
            'external_id': str | None,
            'source_name': str,
            'posted_date': datetime | None,
            'employment_type': str | None,
            'salary_min_cents': int | None,
            'salary_max_cents': int | None,
            'salary_currency': str | None,
            'fingerprint': str,  # SHA256 hash
            'skills': list[str],
            'ingest_version': str,
            'normalized_at': datetime
        }
    """
    
    # Extract text from HTML fields
    title = extract_text(raw_entry.get('title_html', '')) or 'Unknown Title'
    company = extract_text(raw_entry.get('company_html', '')) or 'Unknown Company'
    location = raw_entry.get('location_text')
    description = extract_text(raw_entry.get('snippet_html', ''))
    
    # Canonicalize title and company
    title = canonicalize_title(title)
    company = canonicalize_company(company)
    
    # Parse posted date
    posted_date = parse_posted_date(raw_entry.get('posted_text'))
    
    # Parse employment type
    employment_type = infer_employment_type(title, description)
    
    # Parse salary
    salary_info = parse_salary(raw_entry.get('salary_text'))
    
    # Extract skills
    skills = extract_skills(description or '')
    
    # Generate fingerprint
    fingerprint = generate_fingerprint(title, company, location, description)
    
    return {
        'title': title[:240],
        'company': company[:200],
        'location': location[:128] if location else None,
        'description': description[:10000] if description else None,
        'url': raw_entry.get('url', '')[:512],
        'external_id': raw_entry.get('external_id', '')[:128],
        'source_name': raw_entry.get('source_name', 'unknown')[:128],
        'posted_date': posted_date,
        'employment_type': employment_type,
        'salary_min_cents': salary_info.get('min_cents'),
        'salary_max_cents': salary_info.get('max_cents'),
        'salary_currency': salary_info.get('currency', 'USD'),
        'fingerprint': fingerprint,
        'skills': skills,
        'ingest_version': ingest_version,
        'normalized_at': datetime.utcnow()
    }


def canonicalize_title(title: str) -> str:
    """
    Normalize job title for deduplication.
    - Lowercase
    - Remove extra whitespace
    - Common abbreviation expansion
    """
    title = title.lower().strip()
    
    # Expand common abbreviations
    replacements = {
        r'\bsr\.?\b': 'senior',
        r'\bjr\.?\b': 'junior',
        r'\beng\.?\b': 'engineer',
        r'\bmgr\.?\b': 'manager',
        r'\bdev\.?\b': 'developer',
        r'\badmin\.?\b': 'administrator',
    }
    
    for pattern, replacement in replacements.items():
        title = re.sub(pattern, replacement, title, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


def canonicalize_company(company: str) -> str:
    """
    Normalize company name.
    - Remove legal suffixes (Inc, LLC, etc.)
    - Trim whitespace
    """
    company = company.strip()
    
    # Remove common legal suffixes
    suffixes = r',?\s*(Inc\.?|LLC\.?|Ltd\.?|Corp\.?|Corporation|Company|Co\.?)$'
    company = re.sub(suffixes, '', company, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    company = re.sub(r'\s+', ' ', company).strip()
    
    return company


def parse_posted_date(posted_text: Optional[str]) -> Optional[datetime]:
    """
    Parse posted date from various formats.
    Returns datetime or None.
    
    Handles:
        - "2 days ago"
        - "Posted 3 hours ago"
        - "2024-01-15"
        - ISO8601
    """
    if not posted_text:
        return None
    
    text = posted_text.lower().strip()
    
    try:
        # Relative dates (X days/hours ago)
        if 'day' in text:
            match = re.search(r'(\d+)\s*day', text)
            if match:
                days = int(match.group(1))
                return datetime.utcnow() - timedelta(days=days)
        
        if 'hour' in text:
            match = re.search(r'(\d+)\s*hour', text)
            if match:
                hours = int(match.group(1))
                return datetime.utcnow() - timedelta(hours=hours)
        
        if 'week' in text:
            match = re.search(r'(\d+)\s*week', text)
            if match:
                weeks = int(match.group(1))
                return datetime.utcnow() - timedelta(weeks=weeks)
        
        if 'month' in text:
            match = re.search(r'(\d+)\s*month', text)
            if match:
                months = int(match.group(1))
                return datetime.utcnow() - timedelta(days=months * 30)
        
        # Absolute dates
        # Try ISO format first
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
            try:
                return datetime.strptime(posted_text, fmt)
            except ValueError:
                continue
        
    except Exception as e:
        logger.warning(f"Could not parse posted date '{posted_text}': {e}")
    
    return None


def infer_employment_type(title: str, description: Optional[str]) -> Optional[str]:
    """
    Infer employment type from title and description.
    Returns: 'full_time', 'part_time', 'contract', 'temporary', 'internship', or None
    """
    text = (title + ' ' + (description or '')).lower()
    
    if any(word in text for word in ['intern', 'internship', 'co-op']):
        return 'internship'
    
    if any(word in text for word in ['contract', 'contractor', 'freelance', 'consulting']):
        return 'contract'
    
    if any(word in text for word in ['part time', 'part-time', 'parttime']):
        return 'part_time'
    
    if any(word in text for word in ['temporary', 'temp ', 'seasonal']):
        return 'temporary'
    
    if any(word in text for word in ['full time', 'full-time', 'fulltime']):
        return 'full_time'
    
    # Default to full_time if not specified
    return 'full_time'


def parse_salary(salary_text: Optional[str]) -> Dict:
    """
    Parse salary into min/max cents.
    
    Examples:
        - "$80,000 - $120,000"
        - "$50k-$70k"
        - "100000"
        - "£40,000 - £60,000"
    
    Returns:
        {
            'min_cents': int | None,
            'max_cents': int | None,
            'currency': str  # USD, EUR, GBP, etc.
        }
    """
    if not salary_text:
        return {'min_cents': None, 'max_cents': None, 'currency': 'USD'}
    
    text = salary_text.strip()
    
    # Detect currency
    currency = 'USD'
    if '£' in text or 'GBP' in text:
        currency = 'GBP'
    elif '€' in text or 'EUR' in text:
        currency = 'EUR'
    
    # Extract numbers
    # Remove currency symbols and commas
    text = re.sub(r'[£$€,]', '', text)
    
    # Find all numbers (handle k/K for thousands)
    numbers = []
    for match in re.finditer(r'(\d+(?:\.\d+)?)\s*[kK]?', text):
        num_str = match.group(1)
        num = float(num_str)
        
        # Handle k/K suffix
        if match.group(0).lower().endswith('k'):
            num *= 1000
        
        numbers.append(int(num))
    
    if not numbers:
        return {'min_cents': None, 'max_cents': None, 'currency': currency}
    
    # Assume range if 2 numbers, single value otherwise
    if len(numbers) >= 2:
        min_val = min(numbers[0], numbers[1])
        max_val = max(numbers[0], numbers[1])
    else:
        min_val = max_val = numbers[0]
    
    # Convert to cents (annualized)
    # If hourly (detect with /hr, per hour), multiply by 2080 hours/year
    if any(marker in salary_text.lower() for marker in ['/hr', 'per hour', 'hourly']):
        min_val = int(min_val * 2080 * 100)
        max_val = int(max_val * 2080 * 100)
    else:
        # Assume annual
        min_val = int(min_val * 100)
        max_val = int(max_val * 100)
    
    return {
        'min_cents': min_val,
        'max_cents': max_val,
        'currency': currency
    }


def extract_skills(text: str) -> list:
    """
    Extract technical skills from job description.
    Returns list of skill strings (lowercase).
    """
    if not text:
        return []
    
    text_lower = text.lower()
    
    # Common technical skills to look for
    skill_patterns = [
        # Programming languages
        r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b',
        r'\bc\+\+\b', r'\bc#\b', r'\bruby\b', r'\bphp\b', r'\bgo\b',
        r'\brust\b', r'\bswift\b', r'\bkotlin\b',
        
        # Web frameworks
        r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bdjango\b',
        r'\bflask\b', r'\bspring\b', r'\bnode\.?js\b',
        
        # Databases
        r'\bsql\b', r'\bpostgresql\b', r'\bmysql\b', r'\bmongodb\b',
        r'\bredis\b', r'\belasticsearch\b',
        
        # Cloud
        r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b',
        r'\bkubernetes\b', r'\bk8s\b',
        
        # ML/Data
        r'\bmachine learning\b', r'\bdeep learning\b', r'\bai\b',
        r'\btensorflow\b', r'\bpytorch\b', r'\bpandas\b', r'\bnumpy\b',
        
        # Tools
        r'\bgit\b', r'\bjenkins\b', r'\bcicd\b', r'\bci/cd\b',
        r'\bagile\b', r'\bscrum\b', r'\bjira\b'
    ]
    
    found_skills = []
    for pattern in skill_patterns:
        if re.search(pattern, text_lower):
            # Extract the matched skill (remove \b markers)
            skill = pattern.replace(r'\b', '').replace('\\', '')
            if skill not in found_skills:
                found_skills.append(skill)
    
    return found_skills[:50]  # Limit to 50 skills


def generate_fingerprint(
    title: str,
    company: str,
    location: Optional[str],
    description: Optional[str]
) -> str:
    """
    Generate deterministic SHA256 fingerprint for deduplication.
    
    Components:
        - Canonical title
        - Canonical company
        - Location (if present)
        - Description snippet (first 500 chars)
    """
    parts = [
        canonicalize_title(title),
        canonicalize_company(company),
        location.lower().strip() if location else '',
        (description or '')[:500].lower().strip()
    ]
    
    fingerprint_input = '|'.join(parts)
    
    return hashlib.sha256(fingerprint_input.encode('utf-8')).hexdigest()
