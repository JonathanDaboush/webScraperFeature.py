from typing import List, Dict
from collections import Counter
from Persistance.repository import Repository
from Persistance.crawler import Page


class FrequencyAnalysis:
    """Dedicated frequency analysis utilities."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
    
    def word_frequency_in_content(self, page_ids: List[int] = None, top_n: int = 50) -> List[tuple]:
        """Analyze word frequency across page content."""
        from analysis.text_analysis import TextAnalysis
        import re
        
        text_analyzer = TextAnalysis(self.repo)
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).limit(100).all()
        
        all_words = []
        for page in pages:
            text = text_analyzer.extract_text_from_html(page.html)
            words = re.findall(r'\b\w+\b', text.lower())
            all_words.extend(words)
        
        # Filter stop words and short words
        stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over'
        }
        
        filtered_words = [w for w in all_words if w not in stop_words and len(w) > 3]
        
        return Counter(filtered_words).most_common(top_n)
    
    def bigram_frequency(self, page_ids: List[int] = None, top_n: int = 30) -> List[tuple]:
        """Find most common word pairs (bigrams)."""
        from analysis.text_analysis import TextAnalysis
        import re
        
        text_analyzer = TextAnalysis(self.repo)
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).limit(50).all()
        
        bigrams = []
        for page in pages:
            text = text_analyzer.extract_text_from_html(page.html)
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Create bigrams
            for i in range(len(words) - 1):
                bigrams.append(f"{words[i]} {words[i+1]}")
        
        return Counter(bigrams).most_common(top_n)
    
    def domain_frequency(self) -> List[tuple]:
        """Frequency of pages per domain."""
        from Persistance.crawler import Domain
        
        domains = self.repo.get_all_domains()
        domain_counts = []
        
        for domain in domains:
            page_count = len(self.repo.get_pages_by_domain(domain.id))
            domain_counts.append((domain.domain, page_count))
        
        return sorted(domain_counts, key=lambda x: x[1], reverse=True)
    
    def request_type_frequency(self) -> Dict[str, int]:
        """Frequency of different request types."""
        from Persistance.crawler import Request
        
        requests = self.repo.session.query(Request).all()
        request_types = [r.request_type.value for r in requests if r.request_type]
        
        return dict(Counter(request_types))
    
    def status_code_frequency(self) -> Dict[int, int]:
        """Frequency of HTTP status codes."""
        from Persistance.crawler import Request
        
        requests = self.repo.session.query(Request).filter(
            Request.status_code.isnot(None)
        ).all()
        
        status_codes = [r.status_code for r in requests]
        return dict(Counter(status_codes).most_common())
    
    def pages_per_crawl_job(self) -> List[tuple]:
        """Count pages per crawl job."""
        from Persistance.crawler import CrawlJob
        
        jobs = self.repo.get_all_crawl_jobs()
        job_counts = []
        
        for job in jobs:
            requests = self.repo.get_requests_by_job(job.id)
            page_count = sum(1 for r in requests if r.page)
            job_counts.append((
                f"Job {job.id}: {job.search_query or job.description or 'Unknown'}",
                page_count
            ))
        
        return sorted(job_counts, key=lambda x: x[1], reverse=True)


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    freq = FrequencyAnalysis(repo)
    
    print("Frequency Analysis:")
    print("=" * 60)
    
    # Word frequency
    print("\nMost Common Words:")
    words = freq.word_frequency_in_content(top_n=20)
    for word, count in words:
        print(f"  {word}: {count}")
    
    # Bigrams
    print("\nMost Common Word Pairs (Bigrams):")
    bigrams = freq.bigram_frequency(top_n=15)
    for bigram, count in bigrams[:10]:
        print(f"  '{bigram}': {count}")
    
    # Domain frequency
    print("\nPages Per Domain:")
    domains = freq.domain_frequency()
    for domain, count in domains[:10]:
        print(f"  {domain}: {count} pages")
    
    # Status codes
    print("\nHTTP Status Code Frequency:")
    status_codes = freq.status_code_frequency()
    for code, count in status_codes.items():
        print(f"  {code}: {count}")
    
    repo.close()
