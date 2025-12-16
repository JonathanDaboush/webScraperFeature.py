"""
Browser History Integration

Extract browsing history from popular browsers (Chrome, Firefox, Edge)
and analyze user interests for targeted crawling.
"""

import os
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import logging
from urllib.parse import urlparse

from crawler.keyword_extractor import KeywordExtractor

logger = logging.getLogger(__name__)


class BrowserHistory:
    """Extract and analyze browser history."""
    
    def __init__(self):
        self.chrome_paths = self._get_chrome_paths()
        self.firefox_paths = self._get_firefox_paths()
        self.edge_paths = self._get_edge_paths()
        self.keyword_extractor = KeywordExtractor()
    
    def _get_chrome_paths(self) -> List[Path]:
        """Get Chrome history database paths."""
        paths = []
        
        # Windows
        if os.name == 'nt':
            base = Path(os.environ.get('LOCALAPPDATA', ''))
            chrome_dir = base / 'Google' / 'Chrome' / 'User Data'
            
            if chrome_dir.exists():
                # Default profile
                paths.append(chrome_dir / 'Default' / 'History')
                
                # Other profiles
                for profile_dir in chrome_dir.glob('Profile *'):
                    paths.append(profile_dir / 'History')
        
        # macOS
        elif os.name == 'posix' and os.uname().sysname == 'Darwin':
            home = Path.home()
            chrome_dir = home / 'Library' / 'Application Support' / 'Google' / 'Chrome'
            if chrome_dir.exists():
                paths.append(chrome_dir / 'Default' / 'History')
        
        # Linux
        else:
            home = Path.home()
            chrome_dir = home / '.config' / 'google-chrome'
            if chrome_dir.exists():
                paths.append(chrome_dir / 'Default' / 'History')
        
        return [p for p in paths if p.exists()]
    
    def _get_firefox_paths(self) -> List[Path]:
        """Get Firefox history database paths."""
        paths = []
        
        # Windows
        if os.name == 'nt':
            base = Path(os.environ.get('APPDATA', ''))
            firefox_dir = base / 'Mozilla' / 'Firefox' / 'Profiles'
        
        # macOS
        elif os.name == 'posix' and os.uname().sysname == 'Darwin':
            firefox_dir = Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'
        
        # Linux
        else:
            firefox_dir = Path.home() / '.mozilla' / 'firefox'
        
        if firefox_dir.exists():
            for profile_dir in firefox_dir.glob('*.default*'):
                places_db = profile_dir / 'places.sqlite'
                if places_db.exists():
                    paths.append(places_db)
        
        return paths
    
    def _get_edge_paths(self) -> List[Path]:
        """Get Edge history database paths."""
        paths = []
        
        # Windows
        if os.name == 'nt':
            base = Path(os.environ.get('LOCALAPPDATA', ''))
            edge_dir = base / 'Microsoft' / 'Edge' / 'User Data'
            
            if edge_dir.exists():
                paths.append(edge_dir / 'Default' / 'History')
        
        # macOS
        elif os.name == 'posix' and os.uname().sysname == 'Darwin':
            home = Path.home()
            edge_dir = home / 'Library' / 'Application Support' / 'Microsoft Edge'
            if edge_dir.exists():
                paths.append(edge_dir / 'Default' / 'History')
        
        return [p for p in paths if p.exists()]
    
    def _copy_locked_db(self, db_path: Path) -> Optional[Path]:
        """
        Copy locked database to temp location.
        Browser may have DB locked, so we need a copy.
        """
        try:
            temp_path = Path(os.environ.get('TEMP', '/tmp')) / f'history_copy_{db_path.name}'
            shutil.copy2(db_path, temp_path)
            return temp_path
        except Exception as e:
            logger.error(f"Could not copy database {db_path}: {e}")
            return None
    
    def extract_chrome_history(
        self,
        days_back: int = 30,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Extract browsing history from Chrome.
        
        Returns list of:
        {
            'url': str,
            'title': str,
            'visit_count': int,
            'last_visit_time': datetime,
            'browser': 'chrome'
        }
        """
        results = []
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        cutoff_webkit = int((cutoff - datetime(1601, 1, 1)).total_seconds() * 1000000)
        
        for db_path in self.chrome_paths:
            temp_db = self._copy_locked_db(db_path)
            if not temp_db:
                continue
            
            try:
                conn = sqlite3.connect(f'file:{temp_db}?mode=ro', uri=True)
                cursor = conn.cursor()
                
                query = """
                    SELECT url, title, visit_count, last_visit_time
                    FROM urls
                    WHERE last_visit_time > ?
                    ORDER BY last_visit_time DESC
                    LIMIT ?
                """
                
                cursor.execute(query, (cutoff_webkit, limit))
                
                for row in cursor.fetchall():
                    url, title, visit_count, last_visit_webkit = row
                    
                    # Convert WebKit timestamp to datetime
                    last_visit = datetime(1601, 1, 1) + timedelta(
                        microseconds=last_visit_webkit
                    )
                    
                    results.append({
                        'url': url,
                        'title': title or '',
                        'visit_count': visit_count,
                        'last_visit_time': last_visit,
                        'browser': 'chrome'
                    })
                
                conn.close()
                
            except Exception as e:
                logger.error(f"Error reading Chrome history from {db_path}: {e}")
            
            finally:
                # Clean up temp file
                if temp_db and temp_db.exists():
                    try:
                        temp_db.unlink()
                    except:
                        pass
        
        return results
    
    def extract_firefox_history(
        self,
        days_back: int = 30,
        limit: int = 1000
    ) -> List[Dict]:
        """Extract browsing history from Firefox."""
        results = []
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        cutoff_unix = int(cutoff.timestamp() * 1000000)
        
        for db_path in self.firefox_paths:
            temp_db = self._copy_locked_db(db_path)
            if not temp_db:
                continue
            
            try:
                conn = sqlite3.connect(f'file:{temp_db}?mode=ro', uri=True)
                cursor = conn.cursor()
                
                query = """
                    SELECT url, title, visit_count, last_visit_date
                    FROM moz_places
                    WHERE last_visit_date > ?
                    ORDER BY last_visit_date DESC
                    LIMIT ?
                """
                
                cursor.execute(query, (cutoff_unix, limit))
                
                for row in cursor.fetchall():
                    url, title, visit_count, last_visit_unix = row
                    
                    # Convert Unix microseconds to datetime
                    last_visit = datetime.utcfromtimestamp(last_visit_unix / 1000000)
                    
                    results.append({
                        'url': url,
                        'title': title or '',
                        'visit_count': visit_count,
                        'last_visit_time': last_visit,
                        'browser': 'firefox'
                    })
                
                conn.close()
                
            except Exception as e:
                logger.error(f"Error reading Firefox history from {db_path}: {e}")
            
            finally:
                if temp_db and temp_db.exists():
                    try:
                        temp_db.unlink()
                    except:
                        pass
        
        return results
    
    def extract_edge_history(
        self,
        days_back: int = 30,
        limit: int = 1000
    ) -> List[Dict]:
        """Extract browsing history from Edge (same format as Chrome)."""
        results = []
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        cutoff_webkit = int((cutoff - datetime(1601, 1, 1)).total_seconds() * 1000000)
        
        for db_path in self.edge_paths:
            temp_db = self._copy_locked_db(db_path)
            if not temp_db:
                continue
            
            try:
                conn = sqlite3.connect(f'file:{temp_db}?mode=ro', uri=True)
                cursor = conn.cursor()
                
                query = """
                    SELECT url, title, visit_count, last_visit_time
                    FROM urls
                    WHERE last_visit_time > ?
                    ORDER BY last_visit_time DESC
                    LIMIT ?
                """
                
                cursor.execute(query, (cutoff_webkit, limit))
                
                for row in cursor.fetchall():
                    url, title, visit_count, last_visit_webkit = row
                    
                    last_visit = datetime(1601, 1, 1) + timedelta(
                        microseconds=last_visit_webkit
                    )
                    
                    results.append({
                        'url': url,
                        'title': title or '',
                        'visit_count': visit_count,
                        'last_visit_time': last_visit,
                        'browser': 'edge'
                    })
                
                conn.close()
                
            except Exception as e:
                logger.error(f"Error reading Edge history from {db_path}: {e}")
            
            finally:
                if temp_db and temp_db.exists():
                    try:
                        temp_db.unlink()
                    except:
                        pass
        
        return results
    
    def get_all_history(
        self,
        days_back: int = 30,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Extract history from all available browsers.
        Deduplicate by URL and merge visit counts.
        """
        all_history = []
        
        # Extract from each browser
        all_history.extend(self.extract_chrome_history(days_back, limit))
        all_history.extend(self.firefox_history(days_back, limit))
        all_history.extend(self.extract_edge_history(days_back, limit))
        
        # Deduplicate by URL
        url_map = {}
        for entry in all_history:
            url = entry['url']
            if url in url_map:
                # Merge: sum visit counts, keep latest timestamp
                url_map[url]['visit_count'] += entry['visit_count']
                if entry['last_visit_time'] > url_map[url]['last_visit_time']:
                    url_map[url]['last_visit_time'] = entry['last_visit_time']
                    url_map[url]['title'] = entry['title']
            else:
                url_map[url] = entry
        
        # Sort by visit count descending
        deduplicated = sorted(
            url_map.values(),
            key=lambda x: (x['visit_count'], x['last_visit_time']),
            reverse=True
        )
        
        logger.info(f"Extracted {len(deduplicated)} unique URLs from browser history")
        
        return deduplicated[:limit]
    
    def analyze_domains(self, history: List[Dict]) -> Dict[str, int]:
        """
        Analyze which domains user visits most.
        
        Returns:
            {'domain.com': visit_count, ...}
        """
        domain_counts = {}
        
        for entry in history:
            try:
                domain = urlparse(entry['url']).netloc
                domain_counts[domain] = domain_counts.get(domain, 0) + entry['visit_count']
            except:
                continue
        
        return dict(sorted(
            domain_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def extract_keywords(self, history: List[Dict], top_n: int = 50) -> List[str]:
        """
        Extract keywords from page titles and URLs.
        
        Returns:
            List of keywords sorted by frequency
        """
        from collections import Counter
        import re
        
        words = []
        
        # Common stop words to filter
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'http', 'https',
            'www', 'com', 'org', 'net', 'html', 'php', 'asp', 'jsp'
        }
        
        for entry in history:
            # Extract from title
            title = entry.get('title', '')
            if title:
                # Split on non-alphanumeric
                title_words = re.findall(r'\b[a-z]{3,}\b', title.lower())
                words.extend([w for w in title_words if w not in stop_words])
            
            # Extract from URL path
            try:
                path = urlparse(entry['url']).path
                path_words = re.findall(r'\b[a-z]{3,}\b', path.lower())
                words.extend([w for w in path_words if w not in stop_words])
            except:
                continue
        
        # Count and return top keywords
        counter = Counter(words)
        return [word for word, count in counter.most_common(top_n)]
    
    def get_user_interests(self, days_back: int = 30) -> Dict:
        """
        Comprehensive analysis of user interests from browser history.
        
        Returns:
            {
                'top_domains': {'domain': count},
                'keywords': ['keyword1', 'keyword2', ...],
                'categories': ['tech', 'news', ...],
                'urls': [{'url': '...', 'title': '...', 'visits': N}, ...],
                'total_entries': int
            }
        """
        history = self.get_all_history(days_back=days_back, limit=1000)
        
        if not history:
            logger.warning("No browser history found")
            return {
                'top_domains': {},
                'keywords': [],
                'categories': [],
                'urls': [],
                'total_entries': 0
            }
        
        # Analyze domains
        domains = self.analyze_domains(history)
        
        # Extract keywords
        keywords = self.extract_keywords(history, top_n=50)
        
        # Categorize based on domains and keywords
        categories = self._categorize_interests(domains, keywords)
        
        # Enhanced keyword extraction from page titles
        all_text = ' '.join([entry.get('title', '') for entry in history])
        extracted = self.keyword_extractor.extract_all(all_text)
        
        # Get top product categories with scores
        top_product_categories = self.keyword_extractor.get_top_categories(all_text, top_n=10)
        
        return {
            'top_domains': dict(list(domains.items())[:20]),
            'keywords': keywords[:30],
            'categories': categories,
            'urls': [
                {
                    'url': entry['url'],
                    'title': entry['title'],
                    'visits': entry['visit_count']
                }
                for entry in history[:50]
            ],
            'total_entries': len(history),
            'tech_skills': extracted.get('tech_skills', [])[:30],
            'product_interests': extracted.get('product_categories', [])[:30],
            'seasonal_interests': extracted.get('seasonal_themes', [])[:20],
            'demographics': extracted.get('demographics', [])[:20],
            'top_product_categories': top_product_categories
        }
    
    def _categorize_interests(
        self,
        domains: Dict[str, int],
        keywords: List[str]
    ) -> List[str]:
        """Categorize user interests based on domains and keywords."""
        categories = set()
        
        # Category patterns
        patterns = {
            'programming': ['github', 'stackoverflow', 'python', 'javascript', 'code', 'dev', 'api'],
            'news': ['news', 'cnn', 'bbc', 'reuters', 'times', 'post'],
            'social': ['facebook', 'twitter', 'instagram', 'reddit', 'linkedin', 'tiktok'],
            'shopping': ['amazon', 'ebay', 'shop', 'store', 'buy', 'cart'],
            'entertainment': ['youtube', 'netflix', 'spotify', 'music', 'video', 'movie', 'game'],
            'education': ['edu', 'learn', 'course', 'tutorial', 'university', 'school'],
            'finance': ['bank', 'invest', 'stock', 'finance', 'crypto', 'trading'],
            'health': ['health', 'medical', 'fitness', 'doctor', 'hospital'],
            'travel': ['travel', 'flight', 'hotel', 'booking', 'trip', 'vacation'],
            'food': ['recipe', 'restaurant', 'food', 'cooking', 'delivery']
        }
        
        # Check domains
        for domain in domains.keys():
            domain_lower = domain.lower()
            for category, patterns_list in patterns.items():
                if any(pattern in domain_lower for pattern in patterns_list):
                    categories.add(category)
        
        # Check keywords
        keywords_lower = [k.lower() for k in keywords]
        for category, patterns_list in patterns.items():
            if any(pattern in keywords_lower for pattern in patterns_list):
                categories.add(category)
        
        return sorted(list(categories))
