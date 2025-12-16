"""
Research Crawler - digs into topics from browsing history.

Crawls pages, extracts data, follows links. Respects robots.txt and rate limits.
"""

from typing import List, Dict, Optional, Set
from datetime import datetime
from urllib.parse import urlparse, urljoin
import logging
import re

from Crawler.http_client import HttpClient
from Crawler.parsers import parse_listings, extract_text, clean_html
from Crawler.keyword_extractor import KeywordExtractor
from Crawler.compliance import ScrapingCompliance, ComplianceViolation
from Persistance.repository import Repository
from Persistance.crawler import Page, Domain, Subject, Tag

logger = logging.getLogger(__name__)


class ResearchCrawler:
    """
    Crawls pages related to what the user's interested in.
    Has compliance checks built in so we don't piss off site owners.
    """
    
    def __init__(
        self, 
        http_client: HttpClient, 
        repository: Repository,
        contact_email: str = "research@example.com"
    ):
        self.http = http_client
        self.repo = repository
        self.visited_urls: Set[str] = set()
        self.keyword_extractor = KeywordExtractor()
        
        # Setup compliance checking
        self.compliance = ScrapingCompliance(
            user_agent=f"ResearchCrawler/1.0 (Educational; +mailto:{contact_email})",
            contact_email=contact_email
        )
    
    def research_topic(
        self,
        seed_url: str,
        keywords: List[str],
        max_depth: int = 3,
        max_pages: int = 50
    ) -> Dict:
        """
        Research a topic starting from seed URL.
        
        Args:
            seed_url: Starting URL for research
            keywords: Keywords to focus research on
            max_depth: Maximum link depth to follow
            max_pages: Maximum pages to crawl
        
        Returns:
            {
                'pages_crawled': int,
                'subjects_found': List[str],
                'related_links': List[str],
                'key_findings': List[Dict]
            }
        """
        logger.info(f"Starting research on: {seed_url} for keywords: {keywords}")
        
        pages_crawled = 0
        subjects_found = set()
        related_links = []
        key_findings = []
        
        # BFS crawl
        queue = [(seed_url, 0)]  # (url, depth)
        
        while queue and pages_crawled < max_pages:
            url, depth = queue.pop(0)
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Skip if too deep
            if depth > max_depth:
                continue
            
            # Fetch page
            try:
                page_data = self.crawl_page(url, keywords)
                
                if not page_data:
                    continue
                
                self.visited_urls.add(url)
                pages_crawled += 1
                
                # Extract subjects
                page_subjects = page_data.get('subjects', [])
                subjects_found.update(page_subjects)
                
                # Extract key findings
                if page_data.get('relevance_score', 0) > 0.5:
                    key_findings.append({
                        'url': url,
                        'title': page_data.get('title'),
                        'summary': page_data.get('summary'),
                        'relevance': page_data['relevance_score']
                    })
                
                # Add outbound links to queue
                for link in page_data.get('outbound_links', [])[:10]:
                    if link not in self.visited_urls:
                        queue.append((link, depth + 1))
                        related_links.append(link)
                
                logger.info(f"Crawled {url} (depth={depth}, relevance={page_data.get('relevance_score', 0):.2f})")
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                continue
        
        return {
            'pages_crawled': pages_crawled,
            'subjects_found': sorted(list(subjects_found)),
            'related_links': related_links[:50],
            'key_findings': sorted(key_findings, key=lambda x: x['relevance'], reverse=True)[:20]
        }
    
    def crawl_page(self, url: str, keywords: List[str]) -> Optional[Dict]:
        """
        Crawl a single page and extract structured data.
        
        Legal compliance checks:
        1. Verify URL is allowed per business rules
        2. Enforce rate limiting
        3. Check meta robots tags
        4. Use compliant headers
        
        Returns:
            {
                'title': str,
                'content': str,
                'summary': str,
                'subjects': List[str],
                'tags': List[str],
                'outbound_links': List[str],
                'relevance_score': float,
                'metadata': Dict,
                'tech_skills': List[str],
                'product_categories': List[str],
                'seasonal_themes': List[str],
                'demographics': List[str],
                'top_categories': List[Tuple[str, float]]
            }
        """
        # Check if we're allowed to scrape this
        try:
            allowed, reason = self.compliance.check_url_compliance(url)
            if not allowed:
                logger.warning(f"[COMPLIANCE] Blocked {url}: {reason}")
                self.compliance.log_compliance_check(url, False, reason)
                return None
            
            self.compliance.log_compliance_check(url, True, "Passed compliance checks")
        except Exception as e:
            logger.error(f"Compliance check failed for {url}: {e}")
            return None
        
        # Wait if we're hitting the site too fast
        try:
            self.compliance.enforce_rate_limit(url)
        except Exception as e:
            logger.error(f"Rate limiting failed for {url}: {e}")
        
        # TODO: make HttpClient take custom headers
        compliant_headers = self.compliance.get_compliant_headers(url)
        response = self.http.get(url)
        
        if response['error'] or response['status_code'] != 200:
            logger.warning(f"Failed to fetch {url}: {response.get('error', response['status_code'])}")
            return None
        
        html = response['body']
        
        # Check if page says don't scrape me
        meta_allowed, meta_reason = self.compliance.check_meta_robots(html)
        if not meta_allowed:
            logger.warning(f"[COMPLIANCE] Meta robots blocks {url}: {meta_reason}")
            return None
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        content = self._extract_main_content(soup)
        summary = description or self._generate_summary(content, max_words=100)
        subjects = self._extract_subjects(title, content, keywords)
        tags = self._extract_tags(soup)
        outbound_links = self._extract_links(soup, url)
        relevance_score = self._calculate_relevance(title, content, keywords)
        
        # Pull out keywords and categories
        extracted_keywords = self.keyword_extractor.extract_all(content, title)
        tech_skills = extracted_keywords.get('tech_skills', [])
        product_categories = extracted_keywords.get('product_categories', [])
        seasonal_themes = extracted_keywords.get('seasonal_themes', [])
        demographics = extracted_keywords.get('demographics', [])
        top_categories = self.keyword_extractor.get_top_categories(content, title, top_n=5)
        
        is_tech = self.keyword_extractor.is_tech_related(content)
        is_ecommerce = self.keyword_extractor.is_ecommerce_related(content)
        
        # Extract metadata
        metadata = {
            'author': self._extract_meta(soup, 'author'),
            'published_date': self._extract_meta(soup, 'article:published_time'),
            'keywords': self._extract_meta(soup, 'keywords'),
            'og_type': self._extract_meta(soup, 'og:type'),
            'word_count': len(content.split()),
            'fetch_time': datetime.utcnow().isoformat(),
            'is_tech_related': is_tech,
            'is_ecommerce_related': is_ecommerce,
            'tech_skill_count': len(tech_skills),
            'product_category_count': len(product_categories),
            'seasonal_theme_count': len(seasonal_themes)
        }
        
        # Save to database with enhanced keywords
        self._save_page(
            url=url,
            title=title,
            content=content,
            summary=summary,
            subjects=subjects,
            tags=tags,
            metadata=metadata,
            tech_skills=tech_skills,
            product_categories=product_categories,
            seasonal_themes=seasonal_themes
        )
        
        return {
            'title': title,
            'content': content,
            'summary': summary,
            'subjects': subjects,
            'tags': tags,
            'outbound_links': outbound_links,
            'relevance_score': relevance_score,
            'metadata': metadata,
            'tech_skills': tech_skills,
            'product_categories': product_categories,
            'seasonal_themes': seasonal_themes,
            'demographics': demographics,
            'top_categories': top_categories
        }
    
    def _extract_main_content(self, soup) -> str:
        """Extract main content from HTML, filtering out boilerplate."""
        # Remove scripts, styles, nav, footer, ads
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Try semantic HTML5 tags
        for tag in ['article', 'main', '[role="main"]']:
            main_content = soup.find(tag)
            if main_content:
                break
        
        # Try body if main/article not found
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            main_content = soup
        
        text = main_content.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:50000]  # cap at 50k chars
    
    def _generate_summary(self, content: str, max_words: int = 100) -> str:
        """Quick summary - just truncate and add ellipsis."""
        words = content.split()[:max_words]
        summary = ' '.join(words)
        
        if len(content.split()) > max_words:
            summary += '...'
        
        return summary
    
    def _extract_subjects(
        self,
        title: str,
        content: str,
        keywords: List[str]
    ) -> List[str]:
        """Pull out topics/subjects from the page."""
        subjects = set()
        
        text = (title + ' ' + content).lower()
        
        # Look for our keywords
        for keyword in keywords:
            if keyword.lower() in text:
                subjects.add(keyword.lower())
        
        # Grab capitalized phrases - usually proper nouns/topics
        # TODO: could use NER here for better accuracy
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', title + ' ' + content[:1000])
        
        for phrase in capitalized:
            if len(phrase) > 3 and phrase not in ['The', 'This', 'That', 'These', 'Those']:
                subjects.add(phrase.lower())
        
        return list(subjects)[:20]  # Limit to 20 subjects
    
    def _extract_tags(self, soup) -> List[str]:
        """Get tags from meta keywords or article tag elements."""
        tags = set()
        
        # Try meta keywords first
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords_content = meta_keywords.get('content', '')
            tags.update([k.strip() for k in keywords_content.split(',') if k.strip()])
        
        # Look for tag/category divs
        for tag_container in soup.find_all(['div', 'ul'], class_=re.compile(r'tag|category', re.I)):
            tag_elements = tag_container.find_all(['a', 'span'])
            for elem in tag_elements:
                tag_text = elem.get_text(strip=True)
                if tag_text and len(tag_text) < 50:
                    tags.add(tag_text.lower())
        
        return list(tags)[:15]
    
    def _extract_links(self, soup, base_url: str) -> List[str]:
        """Extract and normalize outbound links."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Make absolute
            absolute_url = urljoin(base_url, href)
            
            # Filter out common non-content links
            if any(skip in absolute_url.lower() for skip in [
                'javascript:', 'mailto:', 'tel:', '#',
                'login', 'signup', 'cart', 'checkout',
                'facebook.com', 'twitter.com', 'instagram.com'
            ]):
                continue
            
            # Only HTTP(S)
            if not absolute_url.startswith(('http://', 'https://')):
                continue
            
            links.append(absolute_url)
        
        # Deduplicate
        return list(set(links))
    
    def _calculate_relevance(
        self,
        title: str,
        content: str,
        keywords: List[str]
    ) -> float:
        """Calculate relevance score (0.0-1.0) based on keyword matches."""
        if not keywords:
            return 0.5
        
        text = (title + ' ' + content).lower()
        
        matches = 0
        for keyword in keywords:
            # Count occurrences
            matches += text.count(keyword.lower())
        
        # Normalize by content length and keyword count
        words = len(text.split())
        if words == 0:
            return 0.0
        
        # Score based on keyword density
        density = matches / (words * len(keywords))
        
        # Cap at 1.0
        score = min(1.0, density * 1000)
        
        return score
    
    def _extract_meta(self, soup, property_name: str) -> Optional[str]:
        """Extract meta tag content by property or name."""
        # Try property attribute (Open Graph)
        meta = soup.find('meta', property=property_name)
        if meta:
            return meta.get('content', '')
        
        # Try name attribute
        meta = soup.find('meta', attrs={'name': property_name})
        if meta:
            return meta.get('content', '')
        
        return None
    
    def _save_page(
        self,
        url: str,
        title: str,
        content: str,
        summary: str,
        subjects: List[str],
        tags: List[str],
        metadata: Dict,
        tech_skills: List[str] = None,
        product_categories: List[str] = None,
        seasonal_themes: List[str] = None
    ):
        """Save crawled page to database with enhanced keyword extraction."""
        tech_skills = tech_skills or []
        product_categories = product_categories or []
        seasonal_themes = seasonal_themes or []
        try:
            # Parse domain
            parsed = urlparse(url)
            domain_name = parsed.netloc
            
            # Get or create domain
            domain = self.repo.session.query(Domain).filter(
                Domain.domain == domain_name
            ).first()
            
            if not domain:
                domain = Domain(
                    domain=domain_name
                )
                self.repo.session.add(domain)
                self.repo.session.flush()
            
            # Check if page exists
            existing_page = self.repo.session.query(Page).filter(
                Page.url == url
            ).first()
            
            if existing_page:
                # Update
                existing_page.title = title
                existing_page.html = content  # Fixed: use html field
                existing_page.crawled = True
                page = existing_page
            else:
                # Create
                page = Page(
                    url=url,
                    domain_id=domain.id,
                    title=title,
                    html=content,  # Fixed: use html field
                    crawled=True,
                    date_found=datetime.utcnow()
                )
                self.repo.session.add(page)
                self.repo.session.flush()
            
            # Add subjects
            for subject_name in subjects:
                subject = self.repo.session.query(Subject).filter(
                    Subject.name == subject_name
                ).first()
                
                if not subject:
                    subject = Subject(name=subject_name)
                    self.repo.session.add(subject)
                    self.repo.session.flush()
                
                # Link page to subject (if not already linked)
                from Persistance.crawler import PageSubject
                existing_link = self.repo.session.query(PageSubject).filter(
                    PageSubject.page_id == page.id,
                    PageSubject.subject_id == subject.id
                ).first()
                
                if not existing_link:
                    page_subject = PageSubject(
                        page_id=page.id,
                        subject_id=subject.id
                    )
                    self.repo.session.add(page_subject)
            
            # Add tags (including extracted keywords)
            all_tags = set(tags)
            
            # Add tech skills as tags with prefix
            for skill in tech_skills[:20]:  # Limit to top 20
                all_tags.add(f"tech:{skill}")
            
            # Add product categories as tags with prefix
            for category in product_categories[:20]:
                all_tags.add(f"product:{category}")
            
            # Add seasonal themes as tags with prefix
            for theme in seasonal_themes[:10]:
                all_tags.add(f"seasonal:{theme}")
            
            for tag_name in all_tags:
                tag = self.repo.session.query(Tag).filter(
                    Tag.name == tag_name
                ).first()
                
                if not tag:
                    tag = Tag(name=tag_name)
                    self.repo.session.add(tag)
                    self.repo.session.flush()
                
                # Link page to tag
                from Persistance.crawler import PageTag
                existing_link = self.repo.session.query(PageTag).filter(
                    PageTag.page_id == page.id,
                    PageTag.tag_id == tag.id
                ).first()
                
                if not existing_link:
                    page_tag = PageTag(
                        page_id=page.id,
                        tag_id=tag.id
                    )
                    self.repo.session.add(page_tag)
            
            self.repo.session.commit()
            
            logger.info(
                f"Saved page: {url} with {len(subjects)} subjects, {len(all_tags)} tags "
                f"({len(tech_skills)} tech skills, {len(product_categories)} product categories, "
                f"{len(seasonal_themes)} seasonal themes)"
            )
            
        except Exception as e:
            logger.error(f"Error saving page {url}: {e}")
            self.repo.session.rollback()
