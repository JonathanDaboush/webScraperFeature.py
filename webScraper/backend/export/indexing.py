from typing import List, Dict, Optional
from datetime import datetime
from Persistance.repository import Repository
from Persistance.crawler import Page


class SearchIndexer:
    """
    Create search indices for fast querying.
    Supports Elasticsearch format and simple inverted index.
    """
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
    
    def create_inverted_index(self, page_ids: List[int] = None) -> Dict[str, List[int]]:
        """
        Create inverted index mapping words to page IDs.
        Returns dict: {word: [page_id1, page_id2, ...]}
        """
        from analysis.text_analysis import TextAnalysis
        import re
        
        text_analyzer = TextAnalysis(self.repo)
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        inverted_index = {}
        
        for page in pages:
            text = text_analyzer.extract_text_from_html(page.html)
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Add page ID to each word's posting list
            for word in set(words):  # Use set to avoid duplicates
                if word not in inverted_index:
                    inverted_index[word] = []
                inverted_index[word].append(page.id)
        
        return inverted_index
    
    def export_inverted_index(self, filepath: str, page_ids: List[int] = None):
        """Export inverted index to JSON file."""
        import json
        
        index = self.create_inverted_index(page_ids)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"Exported inverted index with {len(index)} terms to {filepath}")
    
    def export_to_elasticsearch_bulk(self, filepath: str, page_ids: List[int] = None):
        """Export in Elasticsearch bulk API format (NDJSON)."""
        from analysis.text_analysis import TextAnalysis
        
        text_analyzer = TextAnalysis(self.repo)
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        import json
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for page in pages:
                text = text_analyzer.extract_text_from_html(page.html)
                
                # Index action
                action = {
                    "index": {
                        "_index": "pages",
                        "_id": f"page_{page.id}"
                    }
                }
                
                # Document
                document = {
                    "page_id": page.id,
                    "url": page.url,
                    "title": page.title or "",
                    "content": text,
                    "domain": page.domain.domain if page.domain else "",
                    "date_found": page.date_found.isoformat() if page.date_found else None,
                    "crawled": page.crawled,
                    "subjects": [s.subject.name for s in page.subjects],
                    "tags": [t.tag_obj.tag for t in page.tags],
                    "word_count": len(text.split())
                }
                
                # Write as NDJSON (newline-delimited JSON)
                f.write(json.dumps(action, ensure_ascii=False) + '\n')
                f.write(json.dumps(document, ensure_ascii=False) + '\n')
        
        print(f"Exported {len(pages)} documents in Elasticsearch bulk format to {filepath}")
    
    def export_to_solr_format(self, filepath: str, page_ids: List[int] = None):
        """Export in Apache Solr JSON format."""
        from analysis.text_analysis import TextAnalysis
        import json
        
        text_analyzer = TextAnalysis(self.repo)
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        documents = []
        
        for page in pages:
            text = text_analyzer.extract_text_from_html(page.html)
            
            doc = {
                "id": f"page_{page.id}",
                "page_id": page.id,
                "url": page.url,
                "title": page.title or "",
                "content": text,
                "domain": page.domain.domain if page.domain else "",
                "date_found": page.date_found.isoformat() if page.date_found else None,
                "crawled": page.crawled,
                "subjects": [s.subject.name for s in page.subjects],
                "tags": [t.tag_obj.tag for t in page.tags]
            }
            documents.append(doc)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(documents)} documents in Solr format to {filepath}")
    
    def export_to_meilisearch_format(self, filepath: str, page_ids: List[int] = None):
        """Export in Meilisearch JSON format."""
        from analysis.text_analysis import TextAnalysis
        import json
        
        text_analyzer = TextAnalysis(self.repo)
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        documents = []
        
        for page in pages:
            text = text_analyzer.extract_text_from_html(page.html)
            
            doc = {
                "id": page.id,
                "url": page.url,
                "title": page.title or "",
                "content": text[:5000],  # Meilisearch has size limits
                "domain": page.domain.domain if page.domain else "",
                "date_found": page.date_found.isoformat() if page.date_found else None,
                "subjects": [s.subject.name for s in page.subjects],
                "tags": [t.tag_obj.tag for t in page.tags]
            }
            documents.append(doc)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(documents)} documents in Meilisearch format to {filepath}")
    
    def create_term_frequency_index(self, filepath: str, page_ids: List[int] = None):
        """Create and export term frequency index."""
        from analysis.text_analysis import TextAnalysis
        from collections import Counter
        import json
        import re
        
        text_analyzer = TextAnalysis(self.repo)
        
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        tf_index = {}
        
        for page in pages:
            text = text_analyzer.extract_text_from_html(page.html)
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = Counter(words)
            
            tf_index[f"page_{page.id}"] = {
                "page_id": page.id,
                "url": page.url,
                "title": page.title,
                "term_frequencies": dict(word_freq.most_common(100))  # Top 100 terms
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tf_index, f, indent=2, ensure_ascii=False)
        
        print(f"Exported term frequency index for {len(tf_index)} pages to {filepath}")
    
    def create_faceted_search_index(self, filepath: str):
        """Create faceted search index with aggregations."""
        import json
        from collections import defaultdict
        
        pages = self.repo.session.query(Page).all()
        
        # Build facets
        domain_facet = defaultdict(int)
        subject_facet = defaultdict(int)
        tag_facet = defaultdict(int)
        date_facet = defaultdict(int)
        
        documents = []
        
        for page in pages:
            # Aggregate facets
            if page.domain:
                domain_facet[page.domain.domain] += 1
            
            for subject in page.subjects:
                subject_facet[subject.subject.name] += 1
            
            for tag in page.tags:
                tag_facet[tag.tag_obj.tag] += 1
            
            if page.date_found:
                date_key = page.date_found.strftime('%Y-%m')
                date_facet[date_key] += 1
            
            # Add document
            documents.append({
                "page_id": page.id,
                "url": page.url,
                "title": page.title,
                "domain": page.domain.domain if page.domain else None,
                "subjects": [s.subject.name for s in page.subjects],
                "tags": [t.tag_obj.tag for t in page.tags],
                "date_found": page.date_found.isoformat() if page.date_found else None
            })
        
        index_data = {
            "documents": documents,
            "facets": {
                "domains": dict(domain_facet),
                "subjects": dict(subject_facet),
                "tags": dict(tag_facet),
                "dates": dict(sorted(date_facet.items()))
            },
            "statistics": {
                "total_documents": len(documents),
                "total_domains": len(domain_facet),
                "total_subjects": len(subject_facet),
                "total_tags": len(tag_facet)
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported faceted search index with {len(documents)} documents to {filepath}")


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    import os
    
    repo = Repository()
    indexer = SearchIndexer(repo)
    
    # Create exports directory
    export_dir = "exports/indices"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    print("Search Index Export:")
    print("=" * 60)
    
    # Export to different search engine formats
    indexer.export_inverted_index(f"{export_dir}/inverted_index.json")
    indexer.export_to_elasticsearch_bulk(f"{export_dir}/elasticsearch_bulk.ndjson")
    indexer.export_to_solr_format(f"{export_dir}/solr_documents.json")
    indexer.export_to_meilisearch_format(f"{export_dir}/meilisearch_documents.json")
    indexer.create_term_frequency_index(f"{export_dir}/term_frequency_index.json")
    indexer.create_faceted_search_index(f"{export_dir}/faceted_search_index.json")
    
    print("\nAll search indices exported!")
    
    repo.close()
