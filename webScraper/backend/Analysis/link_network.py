from typing import List, Dict, Set
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse
from Persistance.repository import Repository
from Persistance.crawler import Page, Domain, Request


class LinkNetworkAnalysis:
    """Analyze link relationships and network structure."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
    
    def extract_links_from_html(self, html: str) -> List[str]:
        """Extract all links from HTML content."""
        # Simple regex to find href attributes
        link_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(link_pattern, html, re.IGNORECASE)
        return links
    
    def build_link_graph(self, page_ids: List[int] = None) -> Dict[str, List[str]]:
        """
        Build a directed graph of page links.
        Returns dict mapping page URL to list of linked URLs.
        """
        if page_ids:
            pages = [self.repo.get_page(pid) for pid in page_ids]
            pages = [p for p in pages if p and p.html]
        else:
            pages = self.repo.session.query(Page).filter(Page.html.isnot(None)).all()
        
        graph = {}
        for page in pages:
            links = self.extract_links_from_html(page.html)
            graph[page.url] = links
        
        return graph
    
    def calculate_in_degree(self, graph: Dict[str, List[str]]) -> Dict[str, int]:
        """Calculate in-degree (number of incoming links) for each page."""
        in_degree = defaultdict(int)
        
        for source, targets in graph.items():
            for target in targets:
                in_degree[target] += 1
        
        return dict(in_degree)
    
    def calculate_out_degree(self, graph: Dict[str, List[str]]) -> Dict[str, int]:
        """Calculate out-degree (number of outgoing links) for each page."""
        return {url: len(links) for url, links in graph.items()}
    
    def find_hub_pages(self, top_n: int = 10) -> List[Dict]:
        """
        Find hub pages (pages with many outgoing links).
        """
        graph = self.build_link_graph()
        out_degree = self.calculate_out_degree(graph)
        
        # Get pages with most outgoing links
        sorted_pages = sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        results = []
        for url, out_links in sorted_pages:
            page = self.repo.get_page_by_url(url)
            results.append({
                "url": url,
                "title": page.title if page else None,
                "outgoing_links": out_links,
                "page_id": page.id if page else None
            })
        
        return results
    
    def find_authority_pages(self, top_n: int = 10) -> List[Dict]:
        """
        Find authority pages (pages with many incoming links).
        """
        graph = self.build_link_graph()
        in_degree = self.calculate_in_degree(graph)
        
        # Get pages with most incoming links
        sorted_pages = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        results = []
        for url, in_links in sorted_pages:
            page = self.repo.get_page_by_url(url)
            results.append({
                "url": url,
                "title": page.title if page else None,
                "incoming_links": in_links,
                "page_id": page.id if page else None
            })
        
        return results
    
    def find_isolated_pages(self) -> List[Dict]:
        """Find pages with no incoming or outgoing links."""
        graph = self.build_link_graph()
        in_degree = self.calculate_in_degree(graph)
        out_degree = self.calculate_out_degree(graph)
        
        isolated = []
        for url in graph.keys():
            if in_degree.get(url, 0) == 0 and out_degree.get(url, 0) == 0:
                page = self.repo.get_page_by_url(url)
                isolated.append({
                    "url": url,
                    "title": page.title if page else None,
                    "page_id": page.id if page else None
                })
        
        return isolated
    
    def analyze_internal_vs_external_links(self, page_id: int) -> Dict:
        """Analyze internal vs external links for a page."""
        page = self.repo.get_page(page_id)
        if not page or not page.html:
            return {}
        
        links = self.extract_links_from_html(page.html)
        page_domain = urlparse(page.url).netloc
        
        internal = []
        external = []
        
        for link in links:
            try:
                link_domain = urlparse(link).netloc
                if link_domain == page_domain or not link_domain:
                    internal.append(link)
                else:
                    external.append(link)
            except:
                continue
        
        return {
            "page_id": page.id,
            "url": page.url,
            "total_links": len(links),
            "internal_links": len(internal),
            "external_links": len(external),
            "internal_ratio": round(len(internal) / len(links), 2) if links else 0,
            "top_internal": internal[:10],
            "top_external": external[:10]
        }
    
    def find_link_clusters(self) -> List[Dict]:
        """Find clusters of interconnected pages."""
        graph = self.build_link_graph()
        
        # Simple clustering: group by domain
        domain_clusters = defaultdict(list)
        
        for url in graph.keys():
            try:
                domain = urlparse(url).netloc
                domain_clusters[domain].append(url)
            except:
                continue
        
        clusters = []
        for domain, urls in domain_clusters.items():
            if len(urls) > 1:  # Only include domains with multiple pages
                clusters.append({
                    "domain": domain,
                    "page_count": len(urls),
                    "pages": urls[:10]  # Limit to 10
                })
        
        return sorted(clusters, key=lambda x: x["page_count"], reverse=True)
    
    def calculate_page_rank_simple(self, iterations: int = 10, damping: float = 0.85) -> Dict[str, float]:
        """
        Simple PageRank implementation.
        Returns dict mapping URL to PageRank score.
        """
        graph = self.build_link_graph()
        
        # Initialize PageRank scores
        page_rank = {url: 1.0 for url in graph.keys()}
        num_pages = len(page_rank)
        
        if num_pages == 0:
            return {}
        
        # Iterate
        for _ in range(iterations):
            new_ranks = {}
            
            for page in graph.keys():
                rank_sum = 0.0
                
                # Sum contributions from pages linking to this page
                for source, targets in graph.items():
                    if page in targets and len(targets) > 0:
                        rank_sum += page_rank[source] / len(targets)
                
                new_ranks[page] = (1 - damping) / num_pages + damping * rank_sum
            
            page_rank = new_ranks
        
        return page_rank
    
    def get_top_ranked_pages(self, top_n: int = 10) -> List[Dict]:
        """Get top pages by PageRank score."""
        page_rank = self.calculate_page_rank_simple()
        
        sorted_pages = sorted(page_rank.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        results = []
        for url, score in sorted_pages:
            page = self.repo.get_page_by_url(url)
            results.append({
                "url": url,
                "title": page.title if page else None,
                "pagerank_score": round(score, 4),
                "page_id": page.id if page else None
            })
        
        return results
    
    def get_network_stats(self) -> Dict:
        """Get overall network statistics."""
        graph = self.build_link_graph()
        in_degree = self.calculate_in_degree(graph)
        out_degree = self.calculate_out_degree(graph)
        
        total_pages = len(graph)
        total_links = sum(len(links) for links in graph.values())
        
        return {
            "total_pages": total_pages,
            "total_links": total_links,
            "average_out_degree": round(total_links / total_pages, 2) if total_pages else 0,
            "max_in_degree": max(in_degree.values()) if in_degree else 0,
            "max_out_degree": max(out_degree.values()) if out_degree else 0,
            "isolated_pages": len(self.find_isolated_pages())
        }


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    network = LinkNetworkAnalysis(repo)
    
    print("Link Network Analysis:")
    print("=" * 60)
    
    # Network stats
    stats = network.get_network_stats()
    print("\nNetwork Statistics:")
    print(f"  Total Pages: {stats['total_pages']}")
    print(f"  Total Links: {stats['total_links']}")
    print(f"  Average Outgoing Links: {stats['average_out_degree']}")
    
    # Hub pages
    print("\nTop Hub Pages (Most Outgoing Links):")
    hubs = network.find_hub_pages(top_n=5)
    for hub in hubs:
        print(f"  {hub['title']}: {hub['outgoing_links']} outgoing links")
    
    # Authority pages
    print("\nTop Authority Pages (Most Incoming Links):")
    authorities = network.find_authority_pages(top_n=5)
    for auth in authorities:
        print(f"  {auth['title']}: {auth['incoming_links']} incoming links")
    
    # PageRank
    print("\nTop Pages by PageRank:")
    top_ranked = network.get_top_ranked_pages(top_n=5)
    for page in top_ranked:
        print(f"  {page['title']}: {page['pagerank_score']}")
    
    repo.close()
