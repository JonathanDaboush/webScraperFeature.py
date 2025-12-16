from typing import List, Dict, Optional
from collections import defaultdict
import math
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis


class TopicModeling:
    """Topic modeling and document clustering using TF-IDF."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
    
    def calculate_tf(self, text: str) -> Dict[str, float]:
        """Calculate Term Frequency for a document."""
        words = text.lower().split()
        word_count = len(words)
        
        if word_count == 0:
            return {}
        
        tf = defaultdict(int)
        for word in words:
            tf[word] += 1
        
        # Normalize by document length
        return {word: count / word_count for word, count in tf.items()}
    
    def calculate_idf(self, documents: List[str]) -> Dict[str, float]:
        """Calculate Inverse Document Frequency across documents."""
        num_docs = len(documents)
        word_doc_count = defaultdict(int)
        
        # Count documents containing each word
        for doc in documents:
            unique_words = set(doc.lower().split())
            for word in unique_words:
                word_doc_count[word] += 1
        
        # Calculate IDF
        idf = {}
        for word, doc_count in word_doc_count.items():
            idf[word] = math.log(num_docs / doc_count)
        
        return idf
    
    def calculate_tfidf(self, documents: List[str]) -> List[Dict[str, float]]:
        """
        Calculate TF-IDF scores for all documents.
        Returns list of {word: tfidf_score} dicts.
        """
        idf = self.calculate_idf(documents)
        tfidf_scores = []
        
        for doc in documents:
            tf = self.calculate_tf(doc)
            tfidf = {word: tf_score * idf.get(word, 0) 
                    for word, tf_score in tf.items()}
            tfidf_scores.append(tfidf)
        
        return tfidf_scores
    
    def extract_topics(self, page_ids: List[int] = None, top_n: int = 10) -> List[Dict]:
        """
        Extract main topics from pages using TF-IDF.
        Returns list of topics with associated keywords.
        """
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            return []
        
        # Extract text from HTML
        documents = []
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            documents.append(text)
        
        # Calculate TF-IDF
        tfidf_scores = self.calculate_tfidf(documents)
        
        # Extract topics for each page
        topics = []
        for i, (page, tfidf) in enumerate(zip(pages, tfidf_scores)):
            # Get top N keywords by TF-IDF score
            sorted_words = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)[:top_n]
            
            topics.append({
                "page_id": page.id,
                "url": page.url,
                "title": page.title,
                "keywords": [(word, round(score, 4)) for word, score in sorted_words]
            })
        
        return topics
    
    def find_similar_pages(self, page_id: int, top_n: int = 5) -> List[Dict]:
        """
        Find pages similar to the given page using cosine similarity.
        """
        target_page = self.repo.get_page(page_id)
        if not target_page or not target_page.html:
            return []
        
        # Get all pages
        all_pages = self.repo.session.query(Page).filter(
            Page.html.isnot(None),
            Page.id != page_id
        ).all()
        
        if not all_pages:
            return []
        
        # Extract texts
        target_text = self.text_analyzer.extract_text_from_html(target_page.html)
        documents = [target_text] + [
            self.text_analyzer.extract_text_from_html(p.html) for p in all_pages
        ]
        
        # Calculate TF-IDF
        tfidf_scores = self.calculate_tfidf(documents)
        target_tfidf = tfidf_scores[0]
        
        # Calculate cosine similarity
        similarities = []
        for i, (page, page_tfidf) in enumerate(zip(all_pages, tfidf_scores[1:]), 1):
            similarity = self._cosine_similarity(target_tfidf, page_tfidf)
            similarities.append({
                "page_id": page.id,
                "url": page.url,
                "title": page.title,
                "similarity": round(similarity, 4)
            })
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_n]
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two TF-IDF vectors."""
        # Get common words
        common_words = set(vec1.keys()) & set(vec2.keys())
        
        if not common_words:
            return 0.0
        
        # Calculate dot product
        dot_product = sum(vec1[word] * vec2[word] for word in common_words)
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(score ** 2 for score in vec1.values()))
        magnitude2 = math.sqrt(sum(score ** 2 for score in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def group_by_topic(self, page_ids: List[int] = None, num_topics: int = 5) -> Dict[int, List[Dict]]:
        """
        Group pages into topics based on content similarity.
        Returns dict mapping topic_id to list of pages.
        """
        topics = self.extract_topics(page_ids)
        
        if not topics:
            return {}
        
        # Simple clustering: group by most similar top keywords
        topic_groups = defaultdict(list)
        
        for topic in topics:
            # Use top 3 keywords to determine topic group
            top_keywords = tuple(sorted([w for w, s in topic["keywords"][:3]]))
            topic_groups[top_keywords].append(topic)
        
        # Convert to numbered topics
        numbered_topics = {}
        for i, (keyword_group, pages) in enumerate(sorted(topic_groups.items()), 1):
            if i > num_topics:
                break
            numbered_topics[i] = {
                "topic_keywords": list(keyword_group),
                "pages": pages
            }
        
        return numbered_topics


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    topic_model = TopicModeling(repo)
    
    # Extract topics from all pages
    topics = topic_model.extract_topics(top_n=10)
    
    if topics:
        print("Topic Modeling Results:")
        print("=" * 60)
        for topic in topics[:3]:  # Show first 3
            print(f"\nPage: {topic['title']}")
            print(f"URL: {topic['url']}")
            print("Top Keywords:")
            for word, score in topic['keywords'][:5]:
                print(f"  {word}: {score}")
        
        # Find similar pages
        if topics:
            first_page_id = topics[0]['page_id']
            similar = topic_model.find_similar_pages(first_page_id, top_n=3)
            print(f"\n\nPages similar to '{topics[0]['title']}':")
            for sim in similar:
                print(f"  {sim['title']} (similarity: {sim['similarity']})")
    else:
        print("No pages with content found.")
    
    repo.close()
