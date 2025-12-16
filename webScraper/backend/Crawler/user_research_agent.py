"""
User Interest Analyzer and Automated Research Tool

Combines browser history analysis with web crawling to automatically
research topics the user is interested in.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

from Crawler.browser_history import BrowserHistory
from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient, RateLimiter
from Crawler.config import get_config
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal as Session

logger = logging.getLogger(__name__)


class UserResearchAgent:
    """
    Automated research agent that:
    1. Analyzes user's browser history
    2. Identifies topics of interest
    3. Crawls related content
    4. Extracts and structures knowledge
    5. Returns research findings
    """
    
    def __init__(self, session = None, config=None):
        self.session = session or Session()
        self.config = config or get_config()
        
        self.browser_history = BrowserHistory()
        self.repo = Repository(self.session)
        
        # Initialize HTTP client
        self.http_client = HttpClient(
            timeout_seconds=self.config.TIMEOUT_SECONDS,
            max_retries=self.config.MAX_RETRIES,
            backoff_base_seconds=self.config.RETRY_BASE_SECONDS,
            user_agents=self.config.USER_AGENT_POOL,
            proxy_pool=self.config.PROXY_POOL,
            rate_limiter=RateLimiter(self.config.REQUESTS_PER_DOMAIN_PER_MINUTE)
        )
        
        self.research_crawler = ResearchCrawler(self.http_client, self.repo)
    
    def analyze_user_interests(self, days_back: int = 30) -> Dict:
        """
        Analyze user's browsing history to identify interests.
        
        Returns:
            {
                'top_domains': {'domain': count},
                'keywords': ['keyword1', ...],
                'categories': ['tech', 'news', ...],
                'urls': [{'url': '...', 'visits': N}, ...],
                'total_entries': int
            }
        """
        logger.info(f"Analyzing user interests from last {days_back} days...")
        
        interests = self.browser_history.get_user_interests(days_back=days_back)
        
        logger.info(f"Found {interests['total_entries']} history entries")
        logger.info(f"Top keywords: {interests['keywords'][:10]}")
        logger.info(f"Categories: {interests['categories']}")
        
        return interests
    
    def research_user_interests(
        self,
        days_back: int = 30,
        topics_limit: int = 5,
        max_depth: int = 2,
        max_pages_per_topic: int = 20
    ) -> Dict:
        """
        Automatically research user's interests based on browser history.
        
        Args:
            days_back: Days of history to analyze
            topics_limit: Number of top topics to research
            max_depth: How deep to crawl for each topic
            max_pages_per_topic: Max pages to crawl per topic
        
        Returns:
            {
                'interests': {...},  # User interest analysis
                'research_results': [
                    {
                        'topic': str,
                        'seed_urls': [str],
                        'pages_crawled': int,
                        'subjects_found': [str],
                        'key_findings': [...]
                    }
                ],
                'summary': {
                    'total_pages_crawled': int,
                    'total_subjects': int,
                    'research_time': float
                }
            }
        """
        start_time = datetime.utcnow()
        
        # Step 1: Analyze interests
        logger.info("Step 1: Analyzing user interests...")
        interests = self.analyze_user_interests(days_back=days_back)
        
        if not interests['keywords']:
            logger.warning("No keywords found in browser history")
            return {
                'interests': interests,
                'research_results': [],
                'summary': {'total_pages_crawled': 0, 'total_subjects': 0}
            }
        
        # Step 2: Select top topics to research
        top_keywords = interests['keywords'][:topics_limit]
        top_urls = interests['urls'][:topics_limit * 2]  # Get more URLs than topics
        
        logger.info(f"Step 2: Researching top {topics_limit} topics: {top_keywords}")
        
        # Step 3: Research each topic
        research_results = []
        total_pages = 0
        all_subjects = set()
        
        for i, keyword in enumerate(top_keywords):
            logger.info(f"Researching topic {i+1}/{topics_limit}: {keyword}")
            
            # Find seed URLs related to this keyword
            seed_urls = [
                url['url'] for url in top_urls
                if keyword.lower() in url['title'].lower() or keyword.lower() in url['url'].lower()
            ][:3]  # Max 3 seed URLs per topic
            
            if not seed_urls:
                # Use top URL as fallback
                seed_urls = [top_urls[i]['url']] if i < len(top_urls) else []
            
            if not seed_urls:
                continue
            
            # Research each seed URL
            topic_results = {
                'topic': keyword,
                'seed_urls': seed_urls,
                'pages_crawled': 0,
                'subjects_found': set(),
                'related_links': [],
                'key_findings': []
            }
            
            for seed_url in seed_urls:
                try:
                    result = self.research_crawler.research_topic(
                        seed_url=seed_url,
                        keywords=top_keywords,  # Use all keywords for relevance
                        max_depth=max_depth,
                        max_pages=max_pages_per_topic
                    )
                    
                    topic_results['pages_crawled'] += result['pages_crawled']
                    topic_results['subjects_found'].update(result['subjects_found'])
                    topic_results['related_links'].extend(result['related_links'])
                    topic_results['key_findings'].extend(result['key_findings'])
                    
                    total_pages += result['pages_crawled']
                    all_subjects.update(result['subjects_found'])
                    
                except Exception as e:
                    logger.error(f"Error researching {seed_url}: {e}")
                    continue
            
            # Convert sets to lists for JSON serialization
            topic_results['subjects_found'] = sorted(list(topic_results['subjects_found']))
            
            # Deduplicate findings by URL
            seen_urls = set()
            unique_findings = []
            for finding in topic_results['key_findings']:
                if finding['url'] not in seen_urls:
                    seen_urls.add(finding['url'])
                    unique_findings.append(finding)
            
            topic_results['key_findings'] = sorted(
                unique_findings,
                key=lambda x: x['relevance'],
                reverse=True
            )[:10]  # Top 10 findings per topic
            
            research_results.append(topic_results)
            
            logger.info(f"Topic '{keyword}': crawled {topic_results['pages_crawled']} pages, "
                       f"found {len(topic_results['subjects_found'])} subjects")
        
        # Calculate summary
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            'total_pages_crawled': total_pages,
            'total_subjects': len(all_subjects),
            'research_time_seconds': duration,
            'topics_researched': len(research_results)
        }
        
        logger.info(f"Research complete: {total_pages} pages crawled, "
                   f"{len(all_subjects)} subjects found in {duration:.1f}s")
        
        return {
            'interests': interests,
            'research_results': research_results,
            'summary': summary
        }
    
    def get_research_report(self, days_back: int = 30) -> str:
        """
        Generate a human-readable research report.
        
        Returns:
            Formatted text report
        """
        results = self.research_user_interests(
            days_back=days_back,
            topics_limit=5,
            max_depth=2,
            max_pages_per_topic=15
        )
        
        # Build report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("USER INTEREST RESEARCH REPORT")
        report_lines.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # User interests section
        interests = results['interests']
        report_lines.append("USER INTERESTS (from browser history)")
        report_lines.append("-" * 80)
        report_lines.append(f"Total history entries analyzed: {interests['total_entries']}")
        report_lines.append(f"Categories: {', '.join(interests['categories'])}")
        report_lines.append("")
        report_lines.append("Top Keywords:")
        for i, keyword in enumerate(interests['keywords'][:10], 1):
            report_lines.append(f"  {i}. {keyword}")
        report_lines.append("")
        report_lines.append("Most Visited Domains:")
        for i, (domain, count) in enumerate(list(interests['top_domains'].items())[:10], 1):
            report_lines.append(f"  {i}. {domain} ({count} visits)")
        report_lines.append("")
        
        # Research results section
        report_lines.append("RESEARCH FINDINGS")
        report_lines.append("-" * 80)
        
        for result in results['research_results']:
            report_lines.append(f"\nTopic: {result['topic'].upper()}")
            report_lines.append(f"Pages crawled: {result['pages_crawled']}")
            report_lines.append(f"Subjects found: {len(result['subjects_found'])}")
            report_lines.append("")
            
            if result['subjects_found']:
                report_lines.append("  Related Subjects:")
                for subject in result['subjects_found'][:10]:
                    report_lines.append(f"    - {subject}")
                report_lines.append("")
            
            if result['key_findings']:
                report_lines.append("  Key Findings:")
                for i, finding in enumerate(result['key_findings'][:5], 1):
                    report_lines.append(f"    {i}. {finding['title']}")
                    report_lines.append(f"       URL: {finding['url']}")
                    report_lines.append(f"       Relevance: {finding['relevance']:.2f}")
                    report_lines.append(f"       Summary: {finding['summary'][:150]}...")
                    report_lines.append("")
        
        # Summary section
        summary = results['summary']
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Total pages crawled: {summary['total_pages_crawled']}")
        report_lines.append(f"Total subjects discovered: {summary['total_subjects']}")
        report_lines.append(f"Topics researched: {summary['topics_researched']}")
        report_lines.append(f"Research time: {summary['research_time_seconds']:.1f} seconds")
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def export_research_data(self, filepath: str, days_back: int = 30):
        """Export research data to JSON file."""
        import json
        
        results = self.research_user_interests(days_back=days_back)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Research data exported to: {filepath}")


def main():
    """Command-line interface for user research agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated User Interest Research Agent')
    parser.add_argument('--days', type=int, default=30, help='Days of history to analyze')
    parser.add_argument('--topics', type=int, default=5, help='Number of topics to research')
    parser.add_argument('--depth', type=int, default=2, help='Crawl depth per topic')
    parser.add_argument('--pages', type=int, default=20, help='Max pages per topic')
    parser.add_argument('--report', action='store_true', help='Generate text report')
    parser.add_argument('--export', type=str, help='Export to JSON file')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create agent
    agent = UserResearchAgent()
    
    try:
        if args.report:
            # Generate and print report
            report = agent.get_research_report(days_back=args.days)
            print(report)
        
        elif args.export:
            # Export to JSON
            agent.export_research_data(args.export, days_back=args.days)
            print(f"Research data exported to: {args.export}")
        
        else:
            # Run research and print summary
            results = agent.research_user_interests(
                days_back=args.days,
                topics_limit=args.topics,
                max_depth=args.depth,
                max_pages_per_topic=args.pages
            )
            
            print(f"\nResearch complete!")
            print(f"Pages crawled: {results['summary']['total_pages_crawled']}")
            print(f"Subjects found: {results['summary']['total_subjects']}")
            print(f"Time: {results['summary']['research_time_seconds']:.1f}s")
            
            print(f"\nTop topics researched:")
            for result in results['research_results']:
                print(f"  - {result['topic']}: {result['pages_crawled']} pages, "
                      f"{len(result['subjects_found'])} subjects")
    
    finally:
        agent.session.close()


if __name__ == '__main__':
    main()
