from typing import List, Dict, Optional
import numpy as np
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis


class VectorDBExporter:
    """
    Export data to vector database formats.
    Supports common vector DB formats like FAISS, Pinecone, and generic embeddings.
    """
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
    
    def create_simple_embeddings(self, text: str, dimension: int = 384) -> List[float]:
        """
        Create simple TF-IDF based embeddings for text.
        Note: For production, use proper embedding models like sentence-transformers.
        """
        from collections import Counter
        import math
        
        # Extract words
        words = text.lower().split()
        word_freq = Counter(words)
        
        # Simple hash-based embedding (demonstration only)
        embedding = np.zeros(dimension)
        for word, freq in word_freq.items():
            # Hash word to dimension indices
            hash_val = hash(word)
            indices = [abs(hash_val + i) % dimension for i in range(3)]
            for idx in indices:
                embedding[idx] += freq
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()
    
    def export_to_numpy(self, filepath: str, page_ids: List[int] = None):
        """Export page embeddings as numpy array with metadata."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        embeddings = []
        metadata = []
        
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            embedding = self.create_simple_embeddings(text)
            
            embeddings.append(embedding)
            metadata.append({
                'page_id': page.id,
                'url': page.url,
                'title': page.title,
                'domain': page.domain.domain if page.domain else None
            })
        
        # Save embeddings and metadata
        np.save(f"{filepath}_embeddings.npy", np.array(embeddings))
        np.save(f"{filepath}_metadata.npy", np.array(metadata, dtype=object))
        
        print(f"Exported {len(embeddings)} page embeddings to {filepath}_embeddings.npy")
        print(f"Exported metadata to {filepath}_metadata.npy")
    
    def export_to_pinecone_format(self, filepath: str, page_ids: List[int] = None):
        """Export in Pinecone upsert format (JSON)."""
        import json
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        vectors = []
        
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            embedding = self.create_simple_embeddings(text)
            
            vector_data = {
                'id': f"page_{page.id}",
                'values': embedding,
                'metadata': {
                    'page_id': page.id,
                    'url': page.url,
                    'title': page.title or '',
                    'domain': page.domain.domain if page.domain else '',
                    'subjects': [s.subject.name for s in page.subjects],
                    'tags': [t.tag_obj.tag for t in page.tags]
                }
            }
            vectors.append(vector_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'vectors': vectors}, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(vectors)} vectors in Pinecone format to {filepath}")
    
    def export_to_weaviate_format(self, filepath: str, page_ids: List[int] = None):
        """Export in Weaviate batch import format (JSON)."""
        import json
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        objects = []
        
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            embedding = self.create_simple_embeddings(text)
            
            obj = {
                'class': 'Page',
                'id': f"page-{page.id}",
                'properties': {
                    'pageId': page.id,
                    'url': page.url,
                    'title': page.title or '',
                    'domain': page.domain.domain if page.domain else '',
                    'content': text[:500],  # Truncate for demo
                    'subjects': [s.subject.name for s in page.subjects],
                    'tags': [t.tag_obj.tag for t in page.tags]
                },
                'vector': embedding
            }
            objects.append(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'objects': objects}, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(objects)} objects in Weaviate format to {filepath}")
    
    def export_to_qdrant_format(self, filepath: str, page_ids: List[int] = None):
        """Export in Qdrant upsert format (JSON)."""
        import json
        from datetime import datetime
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        points = []
        
        for i, page in enumerate(pages):
            text = self.text_analyzer.extract_text_from_html(page.html)
            embedding = self.create_simple_embeddings(text)
            
            point = {
                'id': i + 1,
                'vector': embedding,
                'payload': {
                    'page_id': page.id,
                    'url': page.url,
                    'title': page.title or '',
                    'domain': page.domain.domain if page.domain else '',
                    'date_found': page.date_found.isoformat() if page.date_found else None,
                    'subjects': [s.subject.name for s in page.subjects],
                    'tags': [t.tag_obj.tag for t in page.tags],
                    'content_preview': text[:200]
                }
            }
            points.append(point)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'points': points}, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(points)} points in Qdrant format to {filepath}")
    
    def export_to_chromadb_format(self, filepath: str, page_ids: List[int] = None):
        """Export in ChromaDB format (JSON)."""
        import json
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            embedding = self.create_simple_embeddings(text)
            
            ids.append(f"page_{page.id}")
            embeddings.append(embedding)
            metadatas.append({
                'page_id': str(page.id),
                'url': page.url,
                'title': page.title or '',
                'domain': page.domain.domain if page.domain else '',
                'subjects': ','.join([s.subject.name for s in page.subjects]),
                'tags': ','.join([t.tag_obj.tag for t in page.tags])
            })
            documents.append(text[:1000])  # Truncate for demo
        
        collection_data = {
            'ids': ids,
            'embeddings': embeddings,
            'metadatas': metadatas,
            'documents': documents
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(collection_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(ids)} documents in ChromaDB format to {filepath}")
    
    def export_similarity_matrix(self, filepath: str, page_ids: List[int] = None):
        """Export cosine similarity matrix between pages."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            # Limit to 100 pages for memory efficiency
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).limit(100).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        # Create embeddings
        embeddings = []
        for page in pages:
            text = self.text_analyzer.extract_text_from_html(page.html)
            embedding = self.create_simple_embeddings(text)
            embeddings.append(embedding)
        
        # Calculate similarity matrix
        embeddings_array = np.array(embeddings)
        similarity_matrix = np.dot(embeddings_array, embeddings_array.T)
        
        # Save matrix and page IDs
        np.save(f"{filepath}_similarity.npy", similarity_matrix)
        page_ids = [p.id for p in pages]
        np.save(f"{filepath}_page_ids.npy", np.array(page_ids))
        
        print(f"Exported {len(pages)}x{len(pages)} similarity matrix to {filepath}_similarity.npy")


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    import os
    
    repo = Repository()
    exporter = VectorDBExporter(repo)
    
    # Create exports directory
    export_dir = "exports/vectors"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    print("Vector Database Export:")
    print("=" * 60)
    
    # Export to different formats
    exporter.export_to_numpy(f"{export_dir}/pages_vectors")
    exporter.export_to_pinecone_format(f"{export_dir}/pinecone_data.json")
    exporter.export_to_weaviate_format(f"{export_dir}/weaviate_data.json")
    exporter.export_to_qdrant_format(f"{export_dir}/qdrant_data.json")
    exporter.export_to_chromadb_format(f"{export_dir}/chromadb_data.json")
    exporter.export_similarity_matrix(f"{export_dir}/similarity")
    
    print("\nAll vector exports completed!")
    print("Note: Using simple embeddings for demo. For production, use proper embedding models.")
    
    repo.close()
