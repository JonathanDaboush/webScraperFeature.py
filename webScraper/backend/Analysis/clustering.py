from typing import List, Dict, Set
import math
from collections import defaultdict
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis
from analysis.topic_modeling import TopicModeling


class Clustering:
    """Cluster pages based on content similarity."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
        self.topic_model = TopicModeling(self.repo)
    
    def kmeans_clustering(self, page_ids: List[int], k: int = 5, max_iterations: int = 10) -> Dict[int, List[Dict]]:
        """
        Simple K-means clustering of pages based on TF-IDF vectors.
        Returns dict mapping cluster_id to list of pages.
        """
        if not page_ids or len(page_ids) < k:
            return {}
        
        # Get pages
        pages = [self.repo.get_page(pid) for pid in page_ids]
        pages = [p for p in pages if p and p.html]
        
        if len(pages) < k:
            return {}
        
        # Extract texts and calculate TF-IDF
        documents = [self.text_analyzer.extract_text_from_html(p.html) for p in pages]
        tfidf_vectors = self.topic_model.calculate_tfidf(documents)
        
        # Initialize centroids randomly
        import random
        centroids = random.sample(range(len(pages)), k)
        centroid_vectors = [tfidf_vectors[i] for i in centroids]
        
        # K-means iterations
        for _ in range(max_iterations):
            # Assign pages to nearest centroid
            clusters = defaultdict(list)
            for i, (page, vec) in enumerate(zip(pages, tfidf_vectors)):
                distances = [
                    1 - self.topic_model._cosine_similarity(vec, centroid)
                    for centroid in centroid_vectors
                ]
                nearest = distances.index(min(distances))
                clusters[nearest].append((i, page, vec))
            
            # Update centroids
            new_centroids = []
            for cluster_id in range(k):
                if cluster_id in clusters:
                    cluster_vecs = [item[2] for item in clusters[cluster_id]]
                    # Average the vectors
                    centroid = self._average_vectors(cluster_vecs)
                    new_centroids.append(centroid)
                else:
                    new_centroids.append(centroid_vectors[cluster_id])
            
            centroid_vectors = new_centroids
        
        # Format results
        result_clusters = {}
        for cluster_id in range(k):
            if cluster_id in clusters:
                result_clusters[cluster_id] = [
                    {
                        "page_id": page.id,
                        "url": page.url,
                        "title": page.title
                    }
                    for _, page, _ in clusters[cluster_id]
                ]
        
        return result_clusters
    
    def _average_vectors(self, vectors: List[Dict[str, float]]) -> Dict[str, float]:
        """Average multiple TF-IDF vectors."""
        if not vectors:
            return {}
        
        avg_vector = defaultdict(float)
        num_vectors = len(vectors)
        
        for vec in vectors:
            for word, score in vec.items():
                avg_vector[word] += score
        
        return {word: score / num_vectors for word, score in avg_vector.items()}
    
    def hierarchical_clustering(self, page_ids: List[int], threshold: float = 0.5) -> List[List[Dict]]:
        """
        Simple agglomerative hierarchical clustering.
        Returns list of clusters (each cluster is a list of pages).
        """
        if not page_ids:
            return []
        
        # Get pages
        pages = [self.repo.get_page(pid) for pid in page_ids]
        pages = [p for p in pages if p and p.html]
        
        if not pages:
            return []
        
        # Calculate TF-IDF
        documents = [self.text_analyzer.extract_text_from_html(p.html) for p in pages]
        tfidf_vectors = self.topic_model.calculate_tfidf(documents)
        
        # Start with each page in its own cluster
        clusters = [[{
            "page_id": page.id,
            "url": page.url,
            "title": page.title,
            "vector": vec
        }] for page, vec in zip(pages, tfidf_vectors)]
        
        # Merge clusters iteratively
        while len(clusters) > 1:
            # Find most similar pair of clusters
            max_similarity = -1
            merge_i, merge_j = 0, 1
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    similarity = self._cluster_similarity(clusters[i], clusters[j])
                    if similarity > max_similarity:
                        max_similarity = similarity
                        merge_i, merge_j = i, j
            
            # Stop if similarity is too low
            if max_similarity < threshold:
                break
            
            # Merge the two most similar clusters
            clusters[merge_i].extend(clusters[merge_j])
            del clusters[merge_j]
        
        # Remove vector data from results
        for cluster in clusters:
            for page in cluster:
                del page["vector"]
        
        return clusters
    
    def _cluster_similarity(self, cluster1: List[Dict], cluster2: List[Dict]) -> float:
        """Calculate average similarity between two clusters."""
        similarities = []
        
        for page1 in cluster1:
            for page2 in cluster2:
                sim = self.topic_model._cosine_similarity(
                    page1["vector"],
                    page2["vector"]
                )
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def cluster_by_subject(self) -> Dict[str, List[Dict]]:
        """Cluster pages by their assigned subjects."""
        from Persistance.crawler import Subject, PageSubject
        
        subjects = self.repo.get_all_subjects()
        clusters = {}
        
        for subject in subjects:
            pages = self.repo.session.query(Page).join(PageSubject).filter(
                PageSubject.subject_id == subject.id
            ).all()
            
            if pages:
                clusters[subject.name] = [
                    {
                        "page_id": p.id,
                        "url": p.url,
                        "title": p.title
                    }
                    for p in pages
                ]
        
        return clusters
    
    def cluster_by_domain(self) -> Dict[str, List[Dict]]:
        """Cluster pages by domain."""
        domains = self.repo.get_all_domains()
        clusters = {}
        
        for domain in domains:
            pages = self.repo.get_pages_by_domain(domain.id)
            
            if pages:
                clusters[domain.domain] = [
                    {
                        "page_id": p.id,
                        "url": p.url,
                        "title": p.title
                    }
                    for p in pages
                ]
        
        return clusters
    
    def auto_cluster(self, page_ids: List[int] = None, max_clusters: int = 10) -> Dict[int, List[Dict]]:
        """
        Automatically determine optimal number of clusters and cluster pages.
        Uses simple heuristic based on dataset size.
        """
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        page_ids = [p.id for p in pages]
        
        if not page_ids:
            return {}
        
        # Determine k based on dataset size (simple heuristic)
        num_pages = len(page_ids)
        k = min(max_clusters, max(2, int(math.sqrt(num_pages / 2))))
        
        return self.kmeans_clustering(page_ids, k=k)


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    clustering = Clustering(repo)
    
    # Get some pages
    pages = repo.session.query(Page).filter(Page.html.isnot(None)).limit(20).all()
    page_ids = [p.id for p in pages]
    
    if len(page_ids) >= 3:
        print("Clustering Analysis:")
        print("=" * 60)
        
        # K-means clustering
        print("\nK-Means Clustering (k=3):")
        clusters = clustering.kmeans_clustering(page_ids, k=3)
        for cluster_id, pages in clusters.items():
            print(f"\nCluster {cluster_id} ({len(pages)} pages):")
            for page in pages[:3]:
                print(f"  - {page['title']}")
        
        # Cluster by subject
        print("\n\nClustering by Subject:")
        subject_clusters = clustering.cluster_by_subject()
        for subject, pages in list(subject_clusters.items())[:5]:
            print(f"\n{subject} ({len(pages)} pages):")
            for page in pages[:3]:
                print(f"  - {page['title']}")
    else:
        print("Not enough pages with content for clustering.")
    
    repo.close()
