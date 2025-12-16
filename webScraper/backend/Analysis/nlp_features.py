from typing import Dict, List
import re
from collections import Counter
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis


class NLPFeatures:
    """Extract NLP features from text content."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(email_pattern, text)))
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return list(set(re.findall(url_pattern, text)))
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',     # (123) 456-7890
            r'\+\d{1,3}\s?\d{1,4}\s?\d{1,4}\s?\d{1,9}'  # International
        ]
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        return list(set(phones))
    
    def extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values from text."""
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)
        return [float(n) for n in numbers]
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract date patterns from text."""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # 12/31/2023
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # 2023-12-31
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'  # January 1, 2023
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(dates))
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        hashtag_pattern = r'#\w+'
        return list(set(re.findall(hashtag_pattern, text)))
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text."""
        mention_pattern = r'@\w+'
        return list(set(re.findall(mention_pattern, text)))
    
    def extract_capitalized_words(self, text: str) -> List[str]:
        """Extract words that are fully capitalized (potential acronyms/names)."""
        # Remove common all-caps words
        ignore = {'THE', 'A', 'AN', 'AND', 'OR', 'BUT', 'IN', 'ON', 'AT', 'TO', 'FOR'}
        capitalized_pattern = r'\b[A-Z]{2,}\b'
        words = re.findall(capitalized_pattern, text)
        return [w for w in set(words) if w not in ignore]
    
    def extract_proper_nouns(self, text: str) -> List[str]:
        """Extract words starting with capital letters (potential proper nouns)."""
        # Simple heuristic: words that start with capital and are not sentence starts
        sentences = re.split(r'[.!?]+', text)
        proper_nouns = []
        
        for sentence in sentences:
            words = sentence.split()
            # Skip first word (sentence start)
            for word in words[1:]:
                if word and word[0].isupper() and len(word) > 1:
                    # Clean punctuation
                    clean_word = re.sub(r'[^\w]', '', word)
                    if clean_word:
                        proper_nouns.append(clean_word)
        
        return list(set(proper_nouns))
    
    def calculate_lexical_diversity(self, text: str) -> float:
        """
        Calculate lexical diversity (unique words / total words).
        Higher = more diverse vocabulary.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        return len(set(words)) / len(words)
    
    def pos_distribution(self, text: str) -> Dict[str, int]:
        """
        Simple POS distribution based on heuristics.
        Note: This is a simplified version without proper NLP library.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Simple heuristics
        verbs = sum(1 for w in words if w.endswith(('ing', 'ed', 'es')))
        adjectives = sum(1 for w in words if w.endswith(('ful', 'less', 'ous', 'ive', 'able')))
        adverbs = sum(1 for w in words if w.endswith('ly'))
        
        return {
            "verbs": verbs,
            "adjectives": adjectives,
            "adverbs": adverbs,
            "other": len(words) - verbs - adjectives - adverbs
        }
    
    def extract_all_features(self, page: Page) -> Dict:
        """Extract all NLP features from a page."""
        if not page.html:
            return {"error": "No HTML content"}
        
        text = self.text_analyzer.extract_text_from_html(page.html)
        
        return {
            "page_id": page.id,
            "url": page.url,
            "title": page.title,
            "emails": self.extract_emails(text),
            "urls": self.extract_urls(text),
            "phone_numbers": self.extract_phone_numbers(text),
            "dates": self.extract_dates(text),
            "hashtags": self.extract_hashtags(text),
            "mentions": self.extract_mentions(text),
            "acronyms": self.extract_capitalized_words(text),
            "proper_nouns": self.extract_proper_nouns(text)[:20],  # Limit to 20
            "numeric_values": self.extract_numbers(text)[:10],     # Limit to 10
            "lexical_diversity": round(self.calculate_lexical_diversity(text), 3),
            "pos_distribution": self.pos_distribution(text)
        }
    
    def analyze_contact_info(self, page_ids: List[int] = None) -> List[Dict]:
        """Find pages with contact information."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        contact_pages = []
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            emails = self.extract_emails(text)
            phones = self.extract_phone_numbers(text)
            
            if emails or phones:
                contact_pages.append({
                    "page_id": page.id,
                    "url": page.url,
                    "title": page.title,
                    "emails": emails,
                    "phone_numbers": phones
                })
        
        return contact_pages


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    nlp = NLPFeatures(repo)
    
    # Get a sample page
    pages = repo.session.query(Page).filter(Page.html.isnot(None)).limit(1).all()
    
    if pages:
        page = pages[0]
        features = nlp.extract_all_features(page)
        
        print("NLP Features Extracted:")
        print("=" * 60)
        print(f"URL: {features['url']}")
        print(f"Title: {features['title']}")
        print(f"\nEmails: {features['emails']}")
        print(f"Phone Numbers: {features['phone_numbers']}")
        print(f"Dates: {features['dates'][:5]}")
        print(f"Acronyms: {features['acronyms'][:10]}")
        print(f"Proper Nouns: {features['proper_nouns'][:10]}")
        print(f"Lexical Diversity: {features['lexical_diversity']}")
        print(f"\nPOS Distribution: {features['pos_distribution']}")
        
        # Find pages with contact info
        print("\n\nPages with Contact Information:")
        contact_pages = nlp.analyze_contact_info()
        for cp in contact_pages[:3]:
            print(f"\n{cp['title']}")
            print(f"  Emails: {cp['emails']}")
            print(f"  Phones: {cp['phone_numbers']}")
    else:
        print("No pages with content found.")
    
    repo.close()
