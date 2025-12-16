from typing import List, Dict, Optional
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis
from analysis.sentiment import SentimentAnalysis
from analysis.link_network import LinkNetworkAnalysis
from analysis.topic_modeling import TopicModeling


class PageRanking:
    """Rank pages using various algorithms and metrics."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
        self.sentiment_analyzer = SentimentAnalysis(self.repo)
        self.network_analyzer = LinkNetworkAnalysis(self.repo)
        self.topic_model = TopicModeling(self.repo)
    
    def rank_by_pagerank(self, page_ids: List[int] = None, top_n: int = 20) -> List[Dict]:
        """Rank pages using PageRank algorithm."""
        return self.network_analyzer.get_top_ranked_pages(top_n)
    
    def rank_by_quality_score(self, page_ids: List[int] = None, top_n: int = 20) -> List[Dict]:
        """
        Rank pages by quality score based on multiple factors:
        - Content length
        - Readability
        - Link count
        - Sentiment
        """
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            return []
        
        ranked_pages = []
        
        for page in pages:
            score = self._calculate_quality_score(page)
            ranked_pages.append({
                "page_id": page.id,
                "url": page.url,
                "title": page.title,
                "quality_score": score["total_score"],
                "score_breakdown": score
            })
        
        ranked_pages.sort(key=lambda x: x["quality_score"], reverse=True)
        return ranked_pages[:top_n]
    
    def _calculate_quality_score(self, page: Page) -> Dict:
        """Calculate quality score for a page."""
        text = self.text_analyzer.extract_text_from_html(page.html)
        
        # Factor 1: Content length (0-25 points)
        word_count = self.text_analyzer.word_count(text)
        length_score = min(25, word_count / 40)  # Max at 1000 words
        
        # Factor 2: Readability (0-25 points)
        readability = self.text_analyzer.reading_level(text)
        # Score higher for reading ease between 30-70 (optimal range)
        reading_ease = readability.get("reading_ease", 0)
        if 30 <= reading_ease <= 70:
            readability_score = 25
        else:
            readability_score = max(0, 25 - abs(reading_ease - 50) / 2)
        
        # Factor 3: Link richness (0-25 points)
        links = self.network_analyzer.extract_links_from_html(page.html)
        link_score = min(25, len(links) / 2)  # Max at 50 links
        
        # Factor 4: Sentiment positivity (0-25 points)
        sentiment = self.sentiment_analyzer.analyze_page_sentiment(page)
        sentiment_score = (sentiment.get("score", 0) + 1) / 2 * 25  # Convert -1 to 1 range to 0-25
        
        total = length_score + readability_score + link_score + sentiment_score
        
        return {
            "total_score": round(total, 2),
            "content_length": round(length_score, 2),
            "readability": round(readability_score, 2),
            "link_richness": round(link_score, 2),
            "sentiment": round(sentiment_score, 2)
        }
    
    def rank_by_recency(self, top_n: int = 20) -> List[Dict]:
        """Rank pages by most recently found."""
        pages = self.repo.session.query(Page).order_by(
            Page.date_found.desc()
        ).limit(top_n).all()
        
        return [
            {
                "page_id": p.id,
                "url": p.url,
                "title": p.title,
                "date_found": p.date_found
            }
            for p in pages
        ]
    
    def rank_by_relevance(self, query: str, top_n: int = 20) -> List[Dict]:
        """Rank pages by relevance to a search query."""
        pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            return []
        
        # Calculate relevance scores
        ranked = []
        query_lower = query.lower()
        
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            text_lower = text.lower()
            
            # Count query term occurrences
            query_terms = query_lower.split()
            relevance_score = sum(text_lower.count(term) for term in query_terms)
            
            # Boost if in title
            if page.title and query_lower in page.title.lower():
                relevance_score += 10
            
            # Boost if in URL
            if query_lower in page.url.lower():
                relevance_score += 5
            
            if relevance_score > 0:
                ranked.append({
                    "page_id": page.id,
                    "url": page.url,
                    "title": page.title,
                    "relevance_score": relevance_score
                })
        
        ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
        return ranked[:top_n]
    
    def rank_by_authority(self, top_n: int = 20) -> List[Dict]:
        """Rank pages by authority (incoming links)."""
        return self.network_analyzer.find_authority_pages(top_n)
    
    def rank_by_hub(self, top_n: int = 20) -> List[Dict]:
        """Rank pages by hub score (outgoing links)."""
        return self.network_analyzer.find_hub_pages(top_n)
    
    def rank_by_sentiment(self, sentiment_type: str = "positive", top_n: int = 20) -> List[Dict]:
        """Rank pages by sentiment (positive or negative)."""
        if sentiment_type == "positive":
            return self.sentiment_analyzer.find_most_positive_pages(top_n)
        else:
            return self.sentiment_analyzer.find_most_negative_pages(top_n)
    
    def get_top_pages_composite(self, weights: Dict[str, float] = None, top_n: int = 20) -> List[Dict]:
        """
        Rank pages using composite score from multiple ranking methods.
        
        Default weights:
        - quality: 0.3
        - pagerank: 0.3
        - authority: 0.2
        - sentiment: 0.2
        """
        if weights is None:
            weights = {
                "quality": 0.3,
                "pagerank": 0.3,
                "authority": 0.2,
                "sentiment": 0.2
            }
        
        pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            return []
        
        # Get rankings from different methods
        quality_ranks = {p["page_id"]: i for i, p in enumerate(self.rank_by_quality_score())}
        pagerank_ranks = {p["page_id"]: i for i, p in enumerate(self.rank_by_pagerank())}
        authority_ranks = {p["page_id"]: i for i, p in enumerate(self.rank_by_authority())}
        sentiment_ranks = {p["page_id"]: i for i, p in enumerate(self.rank_by_sentiment())}
        
        # Calculate composite scores
        composite_scores = []
        for page in pages:
            # Normalize ranks (lower is better, so invert)
            max_rank = len(pages)
            quality_score = (max_rank - quality_ranks.get(page.id, max_rank)) / max_rank
            pagerank_score = (max_rank - pagerank_ranks.get(page.id, max_rank)) / max_rank
            authority_score = (max_rank - authority_ranks.get(page.id, max_rank)) / max_rank
            sentiment_score = (max_rank - sentiment_ranks.get(page.id, max_rank)) / max_rank
            
            composite = (
                quality_score * weights.get("quality", 0) +
                pagerank_score * weights.get("pagerank", 0) +
                authority_score * weights.get("authority", 0) +
                sentiment_score * weights.get("sentiment", 0)
            )
            
            composite_scores.append({
                "page_id": page.id,
                "url": page.url,
                "title": page.title,
                "composite_score": round(composite, 4),
                "quality_rank": quality_ranks.get(page.id),
                "pagerank_rank": pagerank_ranks.get(page.id),
                "authority_rank": authority_ranks.get(page.id),
                "sentiment_rank": sentiment_ranks.get(page.id)
            })
        
        composite_scores.sort(key=lambda x: x["composite_score"], reverse=True)
        return composite_scores[:top_n]


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    ranking = PageRanking(repo)
    
    print("Page Ranking:")
    print("=" * 60)
    
    # Quality ranking
    print("\nTop Pages by Quality Score:")
    quality = ranking.rank_by_quality_score(top_n=5)
    for page in quality:
        print(f"  {page['title']}: {page['quality_score']}")
    
    # PageRank
    print("\nTop Pages by PageRank:")
    pagerank = ranking.rank_by_pagerank(top_n=5)
    for page in pagerank:
        print(f"  {page['title']}: {page['pagerank_score']}")
    
    # Composite ranking
    print("\nTop Pages by Composite Score:")
    composite = ranking.get_top_pages_composite(top_n=5)
    for page in composite:
        print(f"  {page['title']}: {page['composite_score']}")
    
    repo.close()
