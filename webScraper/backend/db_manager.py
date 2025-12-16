"""
Database Management Helper

Quick commands for managing your PostgreSQL data.
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from Persistance.createDb import SessionLocal, engine
from Persistance.crawler import *
import argparse


def show_stats():
    """Show database statistics."""
    session = SessionLocal()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    stats = [
        ("Domains", Domain),
        ("Pages", Page),
        ("Crawl Jobs", CrawlJob),
        ("Requests", Request),
        ("Subjects", Subject),
        ("Tags", Tag),
        ("Job Postings", JobPosting),
        ("Raw Job Entries", RawJobEntry),
    ]
    
    for name, model in stats:
        try:
            count = session.query(model).count()
            print(f"{name:20s}: {count:>6d} rows")
        except:
            print(f"{name:20s}: Error")
    
    session.close()
    print("="*60 + "\n")


def show_recent_pages(limit=10):
    """Show recently crawled pages."""
    session = SessionLocal()
    
    print(f"\n{'='*80}")
    print(f"RECENT PAGES (Last {limit})")
    print("="*80)
    
    pages = session.query(Page).order_by(Page.date_found.desc()).limit(limit).all()
    
    for page in pages:
        print(f"\nID: {page.id}")
        print(f"URL: {page.url}")
        print(f"Title: {page.title or 'N/A'}")
        print(f"Date: {page.date_found}")
        print(f"Crawled: {page.crawled}")
    
    session.close()
    print("="*80 + "\n")


def show_domains():
    """Show all domains."""
    session = SessionLocal()
    
    print("\n" + "="*60)
    print("DOMAINS")
    print("="*60)
    
    domains = session.query(Domain).all()
    
    for domain in domains:
        page_count = len(domain.pages)
        print(f"{domain.domain:40s} - {page_count} pages")
    
    session.close()
    print("="*60 + "\n")


def export_to_csv(table_name, output_file):
    """Export table to CSV."""
    import csv
    from sqlalchemy import inspect
    
    session = SessionLocal()
    
    # Get table model
    tables = {
        'domains': Domain,
        'pages': Page,
        'subjects': Subject,
        'tags': Tag,
        'crawl_jobs': CrawlJob,
    }
    
    if table_name not in tables:
        print(f"Unknown table: {table_name}")
        print(f"Available: {', '.join(tables.keys())}")
        return
    
    model = tables[table_name]
    
    # Get columns
    inspector = inspect(model)
    columns = [col.name for col in inspector.columns]
    
    # Query data
    rows = session.query(model).all()
    
    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        
        for row in rows:
            writer.writerow([getattr(row, col) for col in columns])
    
    print(f"✓ Exported {len(rows)} rows to {output_file}")
    session.close()


def clear_table(table_name, confirm=False):
    """Clear all data from a table."""
    tables = {
        'domains': Domain,
        'pages': Page,
        'subjects': Subject,
        'tags': Tag,
        'crawl_jobs': CrawlJob,
        'requests': Request,
        'page_subjects': PageSubject,
        'page_tags': PageTag,
    }
    
    if table_name not in tables:
        print(f"Unknown table: {table_name}")
        return
    
    if not confirm:
        print(f"⚠ This will delete all data from {table_name}!")
        response = input("Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("Cancelled")
            return
    
    session = SessionLocal()
    
    try:
        count = session.query(tables[table_name]).count()
        session.query(tables[table_name]).delete()
        session.commit()
        print(f"✓ Deleted {count} rows from {table_name}")
    except Exception as e:
        print(f"✗ Error: {e}")
        session.rollback()
    finally:
        session.close()


def backup_to_json():
    """Export all data to JSON."""
    import json
    from datetime import datetime as dt
    
    session = SessionLocal()
    
    backup = {
        'backup_date': dt.now().isoformat(),
        'domains': [],
        'pages': [],
        'subjects': [],
        'tags': []
    }
    
    # Export domains
    for domain in session.query(Domain).all():
        backup['domains'].append({
            'id': domain.id,
            'domain': domain.domain
        })
    
    # Export pages (limited fields)
    for page in session.query(Page).all():
        backup['pages'].append({
            'id': page.id,
            'url': page.url,
            'title': page.title,
            'date_found': page.date_found.isoformat() if page.date_found else None,
            'crawled': page.crawled
        })
    
    filename = f"backup_{dt.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(backup, f, indent=2)
    
    print(f"✓ Backup saved to {filename}")
    session.close()


def query_custom(sql_query):
    """Execute custom SQL query."""
    session = SessionLocal()
    
    try:
        result = session.execute(text(sql_query))
        
        if result.returns_rows:
            rows = result.fetchall()
            print(f"\nResults: {len(rows)} rows\n")
            
            for row in rows[:20]:  # Show first 20
                print(row)
            
            if len(rows) > 20:
                print(f"\n... and {len(rows) - 20} more rows")
        else:
            session.commit()
            print("Query executed successfully")
            
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description='Database Management Helper')
    parser.add_argument('command', choices=[
        'stats', 'recent', 'domains', 'export', 'clear', 'backup', 'query'
    ], help='Command to execute')
    parser.add_argument('--table', help='Table name for export/clear')
    parser.add_argument('--output', help='Output file for export')
    parser.add_argument('--limit', type=int, default=10, help='Limit for recent pages')
    parser.add_argument('--sql', help='SQL query to execute')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    
    args = parser.parse_args()
    
    if args.command == 'stats':
        show_stats()
    
    elif args.command == 'recent':
        show_recent_pages(args.limit)
    
    elif args.command == 'domains':
        show_domains()
    
    elif args.command == 'export':
        if not args.table or not args.output:
            print("Error: --table and --output required")
            return
        export_to_csv(args.table, args.output)
    
    elif args.command == 'clear':
        if not args.table:
            print("Error: --table required")
            return
        clear_table(args.table, args.yes)
    
    elif args.command == 'backup':
        backup_to_json()
    
    elif args.command == 'query':
        if not args.sql:
            print("Error: --sql required")
            return
        query_custom(args.sql)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
