from typing import List, Dict
from collections import Counter
import re
from Persistance.repository import Repository
from Persistance.crawler import Page


class TextAnalysis:
    """Text analysis utilities for scraped pages."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
    
    def extract_text_from_html(self, html: str) -> str:
        """Remove HTML tags and extract plain text."""
        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def word_count(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)
    
    def character_count(self, text: str, include_spaces: bool = True) -> int:
        """Count characters in text."""
        if include_spaces:
            return len(text)
        return len(text.replace(' ', ''))
    
    def average_word_length(self, text: str) -> float:
        """Calculate average word length."""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    def sentence_count(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def extract_keywords(self, text: str, top_n: int = 20, min_length: int = 3) -> List[tuple]:
        """
        Extract most frequent keywords.
        Returns list of (word, frequency) tuples.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter short words and common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 
                      'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
                      'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
                      'can', 'of', 'to', 'in', 'for', 'with', 'by', 'from', 'about'}
        
        filtered_words = [w for w in words if len(w) >= min_length and w not in stop_words]
        counter = Counter(filtered_words)
        return counter.most_common(top_n)
    
    def reading_level(self, text: str) -> Dict[str, float]:
        """
        Calculate readability metrics (Flesch Reading Ease approximation).
        Returns dict with reading metrics.
        """
        words = re.findall(r'\b\w+\b', text)
        sentences = self.sentence_count(text)
        
        if not words or not sentences:
            return {"reading_ease": 0, "grade_level": 0}
        
        total_words = len(words)
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease
        if sentences > 0 and total_words > 0:
            reading_ease = 206.835 - 1.015 * (total_words / sentences) - 84.6 * (total_syllables / total_words)
            # Flesch-Kincaid Grade Level
            grade_level = 0.39 * (total_words / sentences) + 11.8 * (total_syllables / total_words) - 15.59
        else:
            reading_ease = 0
            grade_level = 0
        
        return {
            "reading_ease": max(0, min(100, reading_ease)),  # Clamp between 0-100
            "grade_level": max(0, grade_level)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count for a word."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def analyze_page(self, page: Page) -> Dict:
        """Complete text analysis for a page."""
        if not page.html:
            return {}
        
        text = self.extract_text_from_html(page.html)
        keywords = self.extract_keywords(text)
        readability = self.reading_level(text)
        
        return {
            "page_id": page.id,
            "url": page.url,
            "title": page.title,
            "word_count": self.word_count(text),
            "character_count": self.character_count(text),
            "sentence_count": self.sentence_count(text),
            "average_word_length": round(self.average_word_length(text), 2),
            "keywords": keywords,
            "reading_ease": round(readability["reading_ease"], 2),
            "grade_level": round(readability["grade_level"], 2),
            "text_preview": text[:200] + "..." if len(text) > 200 else text
        }
    
    def analyze_multiple_pages(self, page_ids: List[int] = None) -> List[Dict]:
        """Analyze multiple pages."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        return [self.analyze_page(page) for page in pages]
    
    def compare_pages(self, page_ids: List[int]) -> Dict:
        """Compare text metrics across multiple pages."""
        analyses = [self.analyze_page(self.repo.get_page(pid)) for pid in page_ids]
        
        if not analyses:
            return {}
        
        return {
            "total_pages": len(analyses),
            "avg_word_count": sum(a["word_count"] for a in analyses) / len(analyses),
            "avg_reading_ease": sum(a["reading_ease"] for a in analyses) / len(analyses),
            "avg_grade_level": sum(a["grade_level"] for a in analyses) / len(analyses),
            "total_words": sum(a["word_count"] for a in analyses),
            "pages": analyses
        }


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    analyzer = TextAnalysis(repo)
    
    # Get a sample page
    pages = repo.session.query(Page).filter(Page.html.isnot(None)).limit(1).all()
    
    if pages:
        page = pages[0]
        analysis = analyzer.analyze_page(page)
        
        print("Text Analysis Results:")
        print("=" * 60)
        print(f"URL: {analysis['url']}")
        print(f"Title: {analysis['title']}")
        print(f"Word Count: {analysis['word_count']}")
        print(f"Sentence Count: {analysis['sentence_count']}")
        print(f"Reading Ease: {analysis['reading_ease']}")
        print(f"Grade Level: {analysis['grade_level']}")
        print(f"\nTop Keywords:")
        for word, freq in analysis['keywords'][:10]:
            print(f"  {word}: {freq}")
    else:
        print("No pages with HTML content found.")
    
    repo.close()
