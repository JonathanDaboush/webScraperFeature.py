"""
Example: Automated User Interest Research

This example demonstrates how to:
1. Extract and analyze user's browser history
2. Identify topics of interest
3. Automatically crawl and research those topics
4. Generate findings report
"""

import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.user_research_agent import UserResearchAgent


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('user_research.log')
        ]
    )


def main():
    """Run user research example."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("AUTOMATED USER INTEREST RESEARCH")
    print("=" * 80)
    print()
    
    # Create research agent
    agent = UserResearchAgent()
    
    try:
        # Step 1: Analyze user interests
        print("Step 1: Analyzing your browser history...")
        print("-" * 80)
        
        interests = agent.analyze_user_interests(days_back=30)
        
        if interests['total_entries'] == 0:
            print("No browser history found. Make sure browsers are closed.")
            return
        
        print(f"✓ Analyzed {interests['total_entries']} history entries")
        print(f"✓ Categories: {', '.join(interests['categories'])}")
        print()
        
        print("Top Keywords:")
        for i, keyword in enumerate(interests['keywords'][:10], 1):
            print(f"  {i}. {keyword}")
        print()
        
        print("Most Visited Domains:")
        for i, (domain, count) in enumerate(list(interests['top_domains'].items())[:10], 1):
            print(f"  {i}. {domain} ({count} visits)")
        print()
        
        # Step 2: Research topics
        print("\nStep 2: Researching your interests...")
        print("-" * 80)
        
        results = agent.research_user_interests(
            days_back=30,
            topics_limit=3,  # Research top 3 topics
            max_depth=2,
            max_pages_per_topic=10
        )
        
        print(f"✓ Research complete!")
        print(f"✓ Total pages crawled: {results['summary']['total_pages_crawled']}")
        print(f"✓ Subjects discovered: {results['summary']['total_subjects']}")
        print(f"✓ Time: {results['summary']['research_time_seconds']:.1f} seconds")
        print()
        
        # Step 3: Display findings
        print("\nStep 3: Key Findings")
        print("-" * 80)
        
        for result in results['research_results']:
            print(f"\nTopic: {result['topic'].upper()}")
            print(f"Pages: {result['pages_crawled']}, Subjects: {len(result['subjects_found'])}")
            
            if result['key_findings']:
                print("\nTop Findings:")
                for i, finding in enumerate(result['key_findings'][:3], 1):
                    print(f"\n  {i}. {finding['title']}")
                    print(f"     {finding['url']}")
                    print(f"     Relevance: {finding['relevance']:.2f}")
                    print(f"     {finding['summary'][:150]}...")
        
        print()
        print("=" * 80)
        
        # Option to export
        export_choice = input("\nExport research data to JSON? (y/n): ").lower()
        if export_choice == 'y':
            filename = f"research_export_{results['summary']['topics_researched']}_topics.json"
            agent.export_research_data(filename, days_back=30)
            print(f"✓ Exported to: {filename}")
        
        print("\nResearch complete! Check the database for detailed page data.")
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\nError: {e}")
    
    finally:
        agent.session.close()


if __name__ == '__main__':
    main()
