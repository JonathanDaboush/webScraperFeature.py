import json
from typing import List, Dict, Optional
from datetime import datetime
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis


class JSONExporter:
    """Export scraped data to JSON format."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
    
    def _serialize_datetime(self, obj):
        """Helper to serialize datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    def export_pages(self, filepath: str, page_ids: List[int] = None, include_html: bool = False, pretty: bool = True):
        """Export pages to JSON."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p]
        else:
            pages = self.repo.session.query(Page).all()
        
        if not pages:
            print("No pages to export.")
            return
        
        pages_data = []
        for page in pages:
            page_dict = {
                'page_id': page.id,
                'url': page.url,
                'title': page.title,
                'domain': page.domain.domain if page.domain else None,
                'date_found': self._serialize_datetime(page.date_found),
                'crawled': page.crawled,
                'subjects': [s.subject.name for s in page.subjects],
                'tags': [t.tag_obj.tag for t in page.tags]
            }
            
            if include_html:
                page_dict['html'] = page.html
            
            pages_data.append(page_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(pages_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(pages_data, f, ensure_ascii=False)
        
        print(f"Exported {len(pages)} pages to {filepath}")
    
    def export_pages_with_analysis(self, filepath: str, page_ids: List[int] = None, pretty: bool = True):
        """Export pages with full analysis data."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        pages_data = []
        for page in pages:
            analysis = self.text_analyzer.analyze_page(page)
            
            page_dict = {
                'page_id': page.id,
                'url': page.url,
                'title': page.title,
                'domain': page.domain.domain if page.domain else None,
                'date_found': self._serialize_datetime(page.date_found),
                'analysis': {
                    'word_count': analysis.get('word_count'),
                    'character_count': analysis.get('character_count'),
                    'sentence_count': analysis.get('sentence_count'),
                    'average_word_length': analysis.get('average_word_length'),
                    'reading_ease': analysis.get('reading_ease'),
                    'grade_level': analysis.get('grade_level'),
                    'keywords': analysis.get('keywords', [])[:20]
                },
                'subjects': [s.subject.name for s in page.subjects],
                'tags': [t.tag_obj.tag for t in page.tags]
            }
            
            pages_data.append(page_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(pages_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(pages_data, f, ensure_ascii=False)
        
        print(f"Exported {len(pages)} pages with analysis to {filepath}")
    
    def export_complete_dataset(self, filepath: str, pretty: bool = True):
        """Export complete dataset including pages, domains, and statistics."""
        from analysis.domain_metrics import DomainMetrics
        from analysis.frequency import FrequencyAnalysis
        
        domain_metrics = DomainMetrics(self.repo)
        freq_analysis = FrequencyAnalysis(self.repo)
        
        # Get all data
        pages = self.repo.session.query(Page).all()
        domains = domain_metrics.compare_domains()
        stats = self.repo.get_stats()
        
        dataset = {
            'metadata': {
                'exported_at': self._serialize_datetime(datetime.utcnow()),
                'total_pages': len(pages),
                'statistics': stats
            },
            'domains': domains,
            'pages': [
                {
                    'page_id': p.id,
                    'url': p.url,
                    'title': p.title,
                    'domain': p.domain.domain if p.domain else None,
                    'date_found': self._serialize_datetime(p.date_found),
                    'crawled': p.crawled,
                    'subjects': [s.subject.name for s in p.subjects],
                    'tags': [t.tag_obj.tag for t in p.tags]
                }
                for p in pages
            ],
            'frequency_analysis': {
                'common_subjects': freq_analysis.most_common_subjects(top_n=20),
                'common_tags': freq_analysis.most_common_tags(top_n=20),
                'domain_distribution': freq_analysis.domain_frequency()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            else:
                json.dump(dataset, f, ensure_ascii=False)
        
        print(f"Exported complete dataset to {filepath}")
    
    def export_sentiment_analysis(self, filepath: str, page_ids: List[int] = None, pretty: bool = True):
        """Export sentiment analysis to JSON."""
        from analysis.sentiment import SentimentAnalysis
        
        sentiment = SentimentAnalysis(self.repo)
        summary = sentiment.get_sentiment_summary(page_ids)
        
        if not summary:
            print("No sentiment data to export.")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            else:
                json.dump(summary, f, ensure_ascii=False)
        
        print(f"Exported sentiment analysis to {filepath}")
    
    def export_topic_model(self, filepath: str, page_ids: List[int] = None, pretty: bool = True):
        """Export topic modeling results to JSON."""
        from analysis.topic_modeling import TopicModeling
        
        topic_model = TopicModeling(self.repo)
        topics = topic_model.extract_topics(page_ids, top_n=15)
        
        if not topics:
            print("No topic data to export.")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(topics, f, indent=2, ensure_ascii=False)
            else:
                json.dump(topics, f, ensure_ascii=False)
        
        print(f"Exported {len(topics)} topics to {filepath}")
    
    def export_rankings(self, filepath: str, pretty: bool = True):
        """Export page rankings to JSON."""
        from analysis.ranking import PageRanking
        
        ranking = PageRanking(self.repo)
        
        rankings_data = {
            'by_quality': ranking.rank_by_quality_score(top_n=20),
            'by_pagerank': ranking.rank_by_pagerank(top_n=20),
            'by_authority': ranking.rank_by_authority(top_n=20),
            'by_recency': ranking.rank_by_recency(top_n=20),
            'composite': ranking.get_top_pages_composite(top_n=20)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(rankings_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(rankings_data, f, ensure_ascii=False)
        
        print(f"Exported page rankings to {filepath}")
    
    def export_link_network(self, filepath: str, pretty: bool = True):
        """Export link network as JSON graph."""
        from analysis.link_network import LinkNetworkAnalysis
        
        network = LinkNetworkAnalysis(self.repo)
        graph = network.build_link_graph()
        stats = network.get_network_stats()
        
        # Convert to nodes and edges format
        nodes = []
        edges = []
        node_ids = {}
        
        for i, url in enumerate(graph.keys()):
            node_ids[url] = i
            page = self.repo.get_page_by_url(url)
            nodes.append({
                'id': i,
                'url': url,
                'title': page.title if page else None
            })
        
        for source_url, targets in graph.items():
            source_id = node_ids[source_url]
            for target_url in targets:
                if target_url in node_ids:
                    edges.append({
                        'source': source_id,
                        'target': node_ids[target_url]
                    })
        
        network_data = {
            'statistics': stats,
            'nodes': nodes,
            'edges': edges
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(network_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(network_data, f, ensure_ascii=False)
        
        print(f"Exported link network to {filepath}")


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    import os
    
    repo = Repository()
    exporter = JSONExporter(repo)
    
    # Create exports directory
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("JSON Export:")
    print("=" * 60)
    
    # Export pages
    exporter.export_pages(f"{export_dir}/pages_{timestamp}.json")
    
    # Export complete dataset
    exporter.export_complete_dataset(f"{export_dir}/complete_dataset_{timestamp}.json")
    
    # Export sentiment
    exporter.export_sentiment_analysis(f"{export_dir}/sentiment_{timestamp}.json")
    
    # Export rankings
    exporter.export_rankings(f"{export_dir}/rankings_{timestamp}.json")
    
    print("\nAll JSON exports completed!")
    
    repo.close()
