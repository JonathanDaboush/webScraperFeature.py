import csv
from typing import List, Dict, Optional
from datetime import datetime
from Persistance.repository import Repository
from Persistance.crawler import Page
from analysis.text_analysis import TextAnalysis


class CSVExporter:
    """Export scraped data to CSV format."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
        self.text_analyzer = TextAnalysis(self.repo)
    
    def export_pages(self, filepath: str, page_ids: List[int] = None, include_html: bool = False):
        """Export pages to CSV."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p]
        else:
            pages = self.repo.session.query(Page).all()
        
        if not pages:
            print("No pages to export.")
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['page_id', 'url', 'title', 'domain', 'date_found', 'crawled']
            if include_html:
                fieldnames.append('html')
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for page in pages:
                row = {
                    'page_id': page.id,
                    'url': page.url,
                    'title': page.title or '',
                    'domain': page.domain.domain if page.domain else '',
                    'date_found': page.date_found.isoformat() if page.date_found else '',
                    'crawled': page.crawled
                }
                if include_html:
                    row['html'] = page.html or ''
                
                writer.writerow(row)
        
        print(f"Exported {len(pages)} pages to {filepath}")
    
    def export_pages_with_analysis(self, filepath: str, page_ids: List[int] = None):
        """Export pages with text analysis metrics."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        if not pages:
            print("No pages with content to export.")
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'page_id', 'url', 'title', 'domain', 'date_found',
                'word_count', 'character_count', 'sentence_count',
                'average_word_length', 'reading_ease', 'grade_level'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for page in pages:
                analysis = self.text_analyzer.analyze_page(page)
                
                row = {
                    'page_id': analysis['page_id'],
                    'url': analysis['url'],
                    'title': analysis['title'] or '',
                    'domain': page.domain.domain if page.domain else '',
                    'date_found': page.date_found.isoformat() if page.date_found else '',
                    'word_count': analysis.get('word_count', 0),
                    'character_count': analysis.get('character_count', 0),
                    'sentence_count': analysis.get('sentence_count', 0),
                    'average_word_length': analysis.get('average_word_length', 0),
                    'reading_ease': analysis.get('reading_ease', 0),
                    'grade_level': analysis.get('grade_level', 0)
                }
                
                writer.writerow(row)
        
        print(f"Exported {len(pages)} pages with analysis to {filepath}")
    
    def export_domains(self, filepath: str):
        """Export domain statistics to CSV."""
        from analysis.domain_metrics import DomainMetrics
        
        domain_metrics = DomainMetrics(self.repo)
        domains_data = domain_metrics.compare_domains()
        
        if not domains_data:
            print("No domains to export.")
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'domain_id', 'domain', 'total_pages', 'crawled_pages',
                'uncrawled_pages', 'pages_with_content', 'crawl_completion',
                'unique_subjects', 'unique_tags'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for domain_data in domains_data:
                writer.writerow({
                    'domain_id': domain_data['domain_id'],
                    'domain': domain_data['domain'],
                    'total_pages': domain_data['total_pages'],
                    'crawled_pages': domain_data['crawled_pages'],
                    'uncrawled_pages': domain_data['uncrawled_pages'],
                    'pages_with_content': domain_data['pages_with_content'],
                    'crawl_completion': domain_data['crawl_completion'],
                    'unique_subjects': domain_data['unique_subjects'],
                    'unique_tags': domain_data['unique_tags']
                })
        
        print(f"Exported {len(domains_data)} domains to {filepath}")
    
    def export_keywords(self, filepath: str, page_ids: List[int] = None, top_n: int = 20):
        """Export keyword analysis to CSV."""
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['page_id', 'url', 'title', 'keyword', 'frequency']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for page in pages:
                analysis = self.text_analyzer.analyze_page(page)
                
                for keyword, freq in analysis.get('keywords', [])[:top_n]:
                    writer.writerow({
                        'page_id': page.id,
                        'url': page.url,
                        'title': page.title or '',
                        'keyword': keyword,
                        'frequency': freq
                    })
        
        print(f"Exported keywords to {filepath}")
    
    def export_sentiment_analysis(self, filepath: str, page_ids: List[int] = None):
        """Export sentiment analysis results to CSV."""
        from analysis.sentiment import SentimentAnalysis
        
        sentiment = SentimentAnalysis(self.repo)
        results = sentiment.analyze_multiple_pages(page_ids)
        
        if not results:
            print("No sentiment data to export.")
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'page_id', 'url', 'title', 'sentiment', 'score',
                'confidence', 'positive_count', 'negative_count', 'total_words'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'page_id': result['page_id'],
                    'url': result['url'],
                    'title': result['title'] or '',
                    'sentiment': result['sentiment'],
                    'score': result['score'],
                    'confidence': result['confidence'],
                    'positive_count': result['positive_count'],
                    'negative_count': result['negative_count'],
                    'total_words': result['total_words']
                })
        
        print(f"Exported sentiment analysis for {len(results)} pages to {filepath}")
    
    def export_link_network(self, filepath: str):
        """Export link network data to CSV (edge list format)."""
        from analysis.link_network import LinkNetworkAnalysis
        
        network = LinkNetworkAnalysis(self.repo)
        graph = network.build_link_graph()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['source_url', 'target_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for source, targets in graph.items():
                for target in targets:
                    writer.writerow({
                        'source_url': source,
                        'target_url': target
                    })
        
        print(f"Exported link network to {filepath}")


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    import os
    
    repo = Repository()
    exporter = CSVExporter(repo)
    
    # Create exports directory
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("CSV Export:")
    print("=" * 60)
    
    # Export pages
    exporter.export_pages(f"{export_dir}/pages_{timestamp}.csv")
    
    # Export pages with analysis
    exporter.export_pages_with_analysis(f"{export_dir}/pages_analysis_{timestamp}.csv")
    
    # Export domains
    exporter.export_domains(f"{export_dir}/domains_{timestamp}.csv")
    
    # Export sentiment
    exporter.export_sentiment_analysis(f"{export_dir}/sentiment_{timestamp}.csv")
    
    print("\nAll exports completed!")
    
    repo.close()
