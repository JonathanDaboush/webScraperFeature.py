from typing import Dict, List, Optional
from collections import Counter
import re
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis


class SentimentAnalysis:
    """Basic sentiment analysis using lexicon-based approach."""
    
    # Simple sentiment lexicons
    POSITIVE_WORDS = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'best',
        'love', 'loved', 'awesome', 'perfect', 'brilliant', 'outstanding', 'superb',
        'happy', 'pleased', 'delighted', 'satisfied', 'enjoy', 'enjoyed', 'beautiful',
        'nice', 'pleasant', 'positive', 'success', 'successful', 'win', 'winner',
        'benefit', 'advantage', 'improve', 'improved', 'better', 'quality', 'recommend'
    }
    
    NEGATIVE_WORDS = {
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'hated', 'poor',
        'disappointed', 'disappointing', 'sad', 'angry', 'frustrated', 'annoying',
        'useless', 'waste', 'fail', 'failed', 'failure', 'problem', 'issue', 'error',
        'broken', 'wrong', 'negative', 'difficult', 'hard', 'complicated', 'confusing',
        'slow', 'expensive', 'weak', 'lacking', 'missing', 'unfortunately', 'regret'
    }
    
    INTENSIFIERS = {
        'very', 'extremely', 'absolutely', 'completely', 'totally', 'really',
        'incredibly', 'exceptionally', 'particularly', 'especially'
    }
    
    NEGATIONS = {
        'not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere',
        "n't", 'barely', 'hardly', 'scarcely', 'rarely'
    }
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text.
        Returns dict with positive/negative counts and overall sentiment.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        i = 0
        while i < len(words):
            word = words[i]
            
            # Check for intensifier
            intensity = 1.0
            if i > 0 and words[i-1] in self.INTENSIFIERS:
                intensity = 1.5
            
            # Check for negation
            is_negated = False
            if i > 0 and words[i-1] in self.NEGATIONS:
                is_negated = True
            
            # Score the word
            if word in self.POSITIVE_WORDS:
                if is_negated:
                    negative_count += intensity
                else:
                    positive_count += intensity
            elif word in self.NEGATIVE_WORDS:
                if is_negated:
                    positive_count += intensity
                else:
                    negative_count += intensity
            else:
                neutral_count += 1
            
            i += 1
        
        total_scored = positive_count + negative_count
        
        if total_scored == 0:
            sentiment = "neutral"
            score = 0.0
            confidence = 0.0
        else:
            score = (positive_count - negative_count) / total_scored
            confidence = total_scored / len(words) if words else 0
            
            if score > 0.1:
                sentiment = "positive"
            elif score < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(score, 3),
            "confidence": round(confidence, 3),
            "positive_count": int(positive_count),
            "negative_count": int(negative_count),
            "neutral_count": neutral_count,
            "total_words": len(words)
        }
    
    def analyze_page_sentiment(self, page: Page) -> Dict:
        """Analyze sentiment of a page."""
        if not page.html:
            return {"error": "No HTML content"}
        
        text = self.text_analyzer.extract_text_from_html(page.html)
        sentiment_result = self.analyze_sentiment(text)
        
        return {
            "page_id": page.id,
            "url": page.url,
            "title": page.title,
            **sentiment_result
        }
    
    def analyze_multiple_pages(self, page_ids: List[int] = None) -> List[Dict]:
        """Analyze sentiment for multiple pages."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        return [self.analyze_page_sentiment(page) for page in pages]
    
    def get_sentiment_summary(self, page_ids: List[int] = None) -> Dict:
        """Get overall sentiment summary across pages."""
        results = self.analyze_multiple_pages(page_ids)
        
        if not results:
            return {}
        
        sentiment_counts = Counter(r["sentiment"] for r in results)
        avg_score = sum(r["score"] for r in results) / len(results)
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        
        return {
            "total_pages": len(results),
            "positive_pages": sentiment_counts["positive"],
            "negative_pages": sentiment_counts["negative"],
            "neutral_pages": sentiment_counts["neutral"],
            "average_score": round(avg_score, 3),
            "average_confidence": round(avg_confidence, 3),
            "overall_sentiment": "positive" if avg_score > 0.1 else "negative" if avg_score < -0.1 else "neutral",
            "pages": results
        }
    
    def compare_domain_sentiments(self) -> List[Dict]:
        """Compare sentiment across different domains."""
        domains = self.repo.get_all_domains()
        domain_sentiments = []
        
        for domain in domains:
            pages = self.repo.get_pages_by_domain(domain.id)
            page_ids = [p.id for p in pages if p.html]
            
            if page_ids:
                summary = self.get_sentiment_summary(page_ids)
                domain_sentiments.append({
                    "domain": domain.domain,
                    "total_pages": len(page_ids),
                    "average_score": summary.get("average_score", 0),
                    "overall_sentiment": summary.get("overall_sentiment", "neutral"),
                    "positive_pages": summary.get("positive_pages", 0),
                    "negative_pages": summary.get("negative_pages", 0)
                })
        
        return sorted(domain_sentiments, key=lambda x: x["average_score"], reverse=True)
    
    def find_most_positive_pages(self, top_n: int = 10) -> List[Dict]:
        """Find the most positive pages."""
        results = self.analyze_multiple_pages()
        positive_pages = [r for r in results if r["sentiment"] == "positive"]
        return sorted(positive_pages, key=lambda x: x["score"], reverse=True)[:top_n]
    
    def find_most_negative_pages(self, top_n: int = 10) -> List[Dict]:
        """Find the most negative pages."""
        results = self.analyze_multiple_pages()
        negative_pages = [r for r in results if r["sentiment"] == "negative"]
        return sorted(negative_pages, key=lambda x: x["score"])[:top_n]


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    sentiment_analyzer = SentimentAnalysis(repo)
    
    # Get sentiment summary
    summary = sentiment_analyzer.get_sentiment_summary()
    
    if summary:
        print("Sentiment Analysis Summary:")
        print("=" * 60)
        print(f"Total Pages: {summary['total_pages']}")
        print(f"Overall Sentiment: {summary['overall_sentiment'].upper()}")
        print(f"Average Score: {summary['average_score']}")
        print(f"Positive Pages: {summary['positive_pages']}")
        print(f"Negative Pages: {summary['negative_pages']}")
        print(f"Neutral Pages: {summary['neutral_pages']}")
        
        # Show most positive
        print("\nMost Positive Pages:")
        positive = sentiment_analyzer.find_most_positive_pages(top_n=3)
        for page in positive:
            print(f"  {page['title']} (score: {page['score']})")
        
        # Show most negative
        print("\nMost Negative Pages:")
        negative = sentiment_analyzer.find_most_negative_pages(top_n=3)
        for page in negative:
            print(f"  {page['title']} (score: {page['score']})")
    else:
        print("No pages with content found.")
    
    repo.close()
