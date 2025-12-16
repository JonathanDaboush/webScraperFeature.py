import time
import random
import requests
from typing import Dict, Optional, List
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CaptchaDetectedError(Exception):
    """Raised when captcha is detected."""
    pass


class RateLimiter:
    """Domain-level rate limiter."""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.domain_requests: Dict[str, List[float]] = defaultdict(list)
    
    def can_request(self, domain: str) -> bool:
        """Check if request is allowed for domain."""
        now = time.time()
        cutoff = now - 60  # Last minute
        
        # Clean old requests
        self.domain_requests[domain] = [
            ts for ts in self.domain_requests[domain] if ts > cutoff
        ]
        
        return len(self.domain_requests[domain]) < self.requests_per_minute
    
    def record_request(self, domain: str):
        """Record a request for rate limiting."""
        self.domain_requests[domain].append(time.time())
    
    def wait_if_needed(self, domain: str):
        """Block until request is allowed."""
        while not self.can_request(domain):
            time.sleep(1)
        self.record_request(domain)


class HttpClient:
    """HTTP client with retries, rate limiting, and captcha detection."""
    
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        backoff_base_seconds: int = 2,
        user_agents: Optional[List[str]] = None,
        proxy_pool: Optional[List[str]] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
        self.proxy_pool = proxy_pool
        self.rate_limiter = rate_limiter or RateLimiter()
        self._ua_index = 0
    
    def _get_next_user_agent(self) -> str:
        """Cycle through user agents."""
        ua = self.user_agents[self._ua_index % len(self.user_agents)]
        self._ua_index += 1
        return ua
    
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """Pick a random proxy if we have any configured."""
        if not self.proxy_pool:
            return None
        proxy_url = random.choice(self.proxy_pool)
        return {"http": proxy_url, "https": proxy_url}
    
    def is_captcha(self, body: str) -> bool:
        """Check if page looks like a captcha."""
        captcha_markers = [
            "verify you are human",
            "recaptcha",
            "captcha",
            "cloudflare",
            "please complete the security check",
            "access denied",
            "are you a robot",
            "bot detection"
        ]
        
        body_lower = body.lower()
        for marker in captcha_markers:
            if marker in body_lower:
                return True
        
        # recaptcha iframe is a dead giveaway
        if 'google.com/recaptcha' in body_lower:
            return True
        
        return False
    
    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict:
        """
        GET request with retries and error handling.
        
        Returns dict with 'error', 'status_code', 'body', 'headers'.
        """
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return {
                'status_code': 0,
                'error': 'invalid_url',
                'body': '',
                'headers': {},
                'fetch_duration_ms': 0,
                'captcha': False
            }
        
        # Extract domain for rate limiting
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # Rate limit check
        self.rate_limiter.wait_if_needed(domain)
        
        # Build headers
        req_headers = {
            'User-Agent': self._get_next_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        if headers:
            req_headers.update(headers)
        
        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Make request
                response = requests.get(
                    url,
                    params=params,
                    headers=req_headers,
                    timeout=self.timeout_seconds,
                    proxies=self._get_proxy(),
                    allow_redirects=True
                )
                
                fetch_duration_ms = int((time.time() - start_time) * 1000)
                
                # Check body size
                if len(response.content) > 5_000_000:  # 5MB
                    logger.warning(f"Response too large: {len(response.content)} bytes for {url}")
                    return {
                        'status_code': response.status_code,
                        'error': 'response_too_large',
                        'body': '',
                        'headers': dict(response.headers),
                        'fetch_duration_ms': fetch_duration_ms,
                        'captcha': False
                    }
                
                body = response.text
                
                # Check for captcha
                if self.is_captcha(body):
                    logger.error(f"Captcha detected for {url}")
                    return {
                        'status_code': response.status_code,
                        'error': 'captcha_detected',
                        'body': body[:1000],  # Truncate
                        'headers': dict(response.headers),
                        'fetch_duration_ms': fetch_duration_ms,
                        'captcha': True
                    }
                
                # Success
                logger.info(f"GET {url} status={response.status_code} duration={fetch_duration_ms}ms "
                           f"ua={req_headers['User-Agent'][:50]}...")
                
                return {
                    'status_code': response.status_code,
                    'error': None,
                    'body': body,
                    'headers': dict(response.headers),
                    'fetch_duration_ms': fetch_duration_ms,
                    'captcha': False
                }
                
            except requests.Timeout:
                last_error = 'timeout'
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries} for {url}")
            
            except requests.ConnectionError as e:
                last_error = 'connection_error'
                logger.warning(f"Connection error on attempt {attempt + 1}/{self.max_retries} for {url}: {e}")
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error on attempt {attempt + 1}/{self.max_retries} for {url}: {e}")
            
            # Exponential backoff with jitter
            if attempt < self.max_retries - 1:
                backoff = self.backoff_base_seconds * (2 ** attempt)
                jitter = random.uniform(0, backoff * 0.1)
                time.sleep(backoff + jitter)
        
        # All retries failed
        return {
            'status_code': 0,
            'error': last_error or 'max_retries_exceeded',
            'body': '',
            'headers': {},
            'fetch_duration_ms': 0,
            'captcha': False
        }
    
    def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict:
        """Similar to get() but for POST requests."""
        # Extract domain for rate limiting
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        self.rate_limiter.wait_if_needed(domain)
        
        req_headers = {
            'User-Agent': self._get_next_user_agent(),
        }
        if headers:
            req_headers.update(headers)
        
        try:
            start_time = time.time()
            
            response = requests.post(
                url,
                data=data,
                json=json,
                headers=req_headers,
                timeout=self.timeout_seconds,
                proxies=self._get_proxy()
            )
            
            fetch_duration_ms = int((time.time() - start_time) * 1000)
            
            return {
                'status_code': response.status_code,
                'error': None,
                'body': response.text,
                'headers': dict(response.headers),
                'fetch_duration_ms': fetch_duration_ms,
                'captcha': self.is_captcha(response.text)
            }
            
        except Exception as e:
            logger.error(f"POST error for {url}: {e}")
            return {
                'status_code': 0,
                'error': str(e),
                'body': '',
                'headers': {},
                'fetch_duration_ms': 0,
                'captcha': False
            }
