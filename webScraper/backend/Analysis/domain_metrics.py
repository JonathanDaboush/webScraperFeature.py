from typing import List, Dict
from collections import Counter, defaultdict
from Persistance.repository import Repository
from Persistance.crawler import Page, Domain


class DomainMetrics:
    """Analyze metrics and statistics per domain."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
    
    def get_domain_summary(self, domain_id: int) -> Dict:
        """Get comprehensive summary for a domain."""
        domain = self.repo.session.query(Domain).filter_by(id=domain_id).first()
        if not domain:
            return {}
        
        pages = self.repo.get_pages_by_domain(domain_id)
        
        total_pages = len(pages)
        crawled_pages = sum(1 for p in pages if p.crawled)
        pages_with_content = sum(1 for p in pages if p.html)
        
        # Get subjects
        subjects = []
        for page in pages:
            subjects.extend(self.repo.get_subjects_for_page(page.id))
        subject_counts = Counter(s.name for s in subjects)
        
        # Get tags
        tags = []
        for page in pages:
            tags.extend(self.repo.get_tags_for_page(page.id))
        tag_counts = Counter(t.tag for t in tags)
        
        return {
            "domain_id": domain.id,
            "domain": domain.domain,
            "total_pages": total_pages,
            "crawled_pages": crawled_pages,
            "uncrawled_pages": total_pages - crawled_pages,
            "pages_with_content": pages_with_content,
            "crawl_completion": round(crawled_pages / total_pages * 100, 2) if total_pages else 0,
            "top_subjects": subject_counts.most_common(10),
            "top_tags": tag_counts.most_common(10),
            "unique_subjects": len(subject_counts),
            "unique_tags": len(tag_counts)
        }
    
    def compare_domains(self) -> List[Dict]:
        """Compare metrics across all domains."""
        domains = self.repo.get_all_domains()
        
        comparisons = []
        for domain in domains:
            summary = self.get_domain_summary(domain.id)
            if summary:
                comparisons.append(summary)
        
        return sorted(comparisons, key=lambda x: x["total_pages"], reverse=True)
    
    def get_domain_by_pages(self, top_n: int = 10) -> List[Dict]:
        """Get domains ranked by number of pages."""
        domains = self.repo.get_all_domains()
        
        domain_pages = []
        for domain in domains:
            page_count = len(self.repo.get_pages_by_domain(domain.id))
            if page_count > 0:
                domain_pages.append({
                    "domain": domain.domain,
                    "page_count": page_count
                })
        
        return sorted(domain_pages, key=lambda x: x["page_count"], reverse=True)[:top_n]
    
    def get_domain_health_score(self, domain_id: int) -> Dict:
        """
        Calculate a health score for a domain based on various metrics.
        Score ranges from 0-100.
        """
        summary = self.get_domain_summary(domain_id)
        if not summary:
            return {}
        
        score = 0.0
        factors = []
        
        # Factor 1: Crawl completion (40 points)
        crawl_score = summary["crawl_completion"] * 0.4
        score += crawl_score
        factors.append({"factor": "Crawl Completion", "score": round(crawl_score, 2)})
        
        # Factor 2: Content availability (30 points)
        if summary["total_pages"] > 0:
            content_score = (summary["pages_with_content"] / summary["total_pages"]) * 30
            score += content_score
            factors.append({"factor": "Content Availability", "score": round(content_score, 2)})
        
        # Factor 3: Content diversity (20 points)
        diversity_score = min(20, summary["unique_subjects"] * 2)
        score += diversity_score
        factors.append({"factor": "Content Diversity", "score": round(diversity_score, 2)})
        
        # Factor 4: Tagging completeness (10 points)
        if summary["total_pages"] > 0:
            tag_score = min(10, summary["unique_tags"])
            score += tag_score
            factors.append({"factor": "Tagging", "score": round(tag_score, 2)})
        
        return {
            "domain": summary["domain"],
            "health_score": round(score, 2),
            "rating": self._get_rating(score),
            "score_breakdown": factors,
            "total_pages": summary["total_pages"]
        }
    
    def _get_rating(self, score: float) -> str:
        """Convert score to rating."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Very Poor"
    
    def get_all_domain_health(self) -> List[Dict]:
        """Get health scores for all domains."""
        domains = self.repo.get_all_domains()
        
        health_scores = []
        for domain in domains:
            health = self.get_domain_health_score(domain.id)
            if health:
                health_scores.append(health)
        
        return sorted(health_scores, key=lambda x: x["health_score"], reverse=True)
    
    def find_underperforming_domains(self, threshold: float = 50.0) -> List[Dict]:
        """Find domains with health score below threshold."""
        all_health = self.get_all_domain_health()
        return [h for h in all_health if h["health_score"] < threshold]
    
    def get_domain_activity(self, days: int = 30) -> List[Dict]:
        """Get recent activity per domain."""
        from datetime import datetime, timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        domains = self.repo.get_all_domains()
        
        activity = []
        for domain in domains:
            pages = self.repo.session.query(Page).filter(
                Page.domain_id == domain.id,
                Page.date_found >= cutoff
            ).all()
            
            if pages:
                activity.append({
                    "domain": domain.domain,
                    "recent_pages": len(pages),
                    "crawled_recently": sum(1 for p in pages if p.crawled),
                    "last_activity": max(p.date_found for p in pages)
                })
        
        return sorted(activity, key=lambda x: x["recent_pages"], reverse=True)


class FrequencyAnalysis:
    """Analyze frequency of various elements across pages."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
    
    def most_common_subjects(self, top_n: int = 20) -> List[tuple]:
        """Find most frequently used subjects."""
        from Persistance.crawler import Subject, PageSubject
        
        subjects = self.repo.session.query(
            Subject.name,
            self.repo.session.query(PageSubject).filter(
                PageSubject.subject_id == Subject.id
            ).count().label('count')
        ).all()
        
        subject_counts = Counter({s.name: s.count for s in subjects})
        return subject_counts.most_common(top_n)
    
    def most_common_tags(self, top_n: int = 20) -> List[tuple]:
        """Find most frequently used tags."""
        from Persistance.crawler import Tag, PageTag
        
        tags = self.repo.session.query(
            Tag.tag,
            self.repo.session.query(PageTag).filter(
                PageTag.tag_id == Tag.id
            ).count().label('count')
        ).all()
        
        tag_counts = Counter({t.tag: t.count for t in tags})
        return tag_counts.most_common(top_n)
    
    def title_word_frequency(self, top_n: int = 50) -> List[tuple]:
        """Analyze word frequency in page titles."""
        import re
        
        pages = self.repo.session.query(Page).filter(Page.title.isnot(None)).all()
        
        words = []
        for page in pages:
            title_words = re.findall(r'\b\w+\b', page.title.lower())
            words.extend(title_words)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        
        return Counter(filtered).most_common(top_n)
    
    def url_pattern_frequency(self) -> Dict[str, int]:
        """Analyze common URL patterns."""
        import re
        
        pages = self.repo.session.query(Page).all()
        
        patterns = defaultdict(int)
        for page in pages:
            # Extract path segments
            url_parts = re.findall(r'/([^/]+)', page.url)
            for part in url_parts:
                # Generalize numbers
                part = re.sub(r'\d+', 'N', part)
                patterns[part] += 1
        
        return dict(Counter(patterns).most_common(30))
    
    def crawl_job_query_frequency(self) -> List[tuple]:
        """Analyze frequency of search queries."""
        from Persistance.crawler import CrawlJob
        
        jobs = self.repo.session.query(CrawlJob).filter(
            CrawlJob.search_query.isnot(None)
        ).all()
        
        queries = [job.search_query for job in jobs]
        return Counter(queries).most_common(20)


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    domain_metrics = DomainMetrics(repo)
    freq_analysis = FrequencyAnalysis(repo)
    
    print("Domain Metrics Analysis:")
    print("=" * 60)
    
    # Top domains by pages
    print("\nTop Domains by Page Count:")
    top_domains = domain_metrics.get_domain_by_pages(top_n=5)
    for domain in top_domains:
        print(f"  {domain['domain']}: {domain['page_count']} pages")
    
    # Domain health scores
    print("\nDomain Health Scores:")
    health_scores = domain_metrics.get_all_domain_health()
    for health in health_scores[:5]:
        print(f"  {health['domain']}: {health['health_score']} ({health['rating']})")
    
    # Frequency Analysis
    print("\n\nFrequency Analysis:")
    print("=" * 60)
    
    # Most common subjects
    print("\nMost Common Subjects:")
    subjects = freq_analysis.most_common_subjects(top_n=10)
    for subject, count in subjects:
        print(f"  {subject}: {count} pages")
    
    # Most common tags
    print("\nMost Common Tags:")
    tags = freq_analysis.most_common_tags(top_n=10)
    for tag, count in tags:
        print(f"  {tag}: {count} pages")
    
    repo.close()
