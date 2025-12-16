"""
PostgreSQL Database Setup and Data Persistence

This script handles:
1. Database creation
2. Table initialization
3. Connection verification
4. Data persistence testing
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import logging

from Persistance.createDb import Base, SessionLocal, engine
from Persistance.crawler import (
    Domain, CrawlJob, Request, Page, Subject, Tag,
    PageSubject, PageTag, JobSource, RawJobEntry, JobPosting,
    Skill, JobPostingSkill, PostingMerge, JobRun, ProductSource, ProductRun
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_postgres_connection():
    """Check if PostgreSQL server is running and accessible."""
    try:
        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"✓ Connected to PostgreSQL")
            logger.info(f"  Version: {version}")
            return True
    except OperationalError as e:
        logger.error("✗ Cannot connect to PostgreSQL server")
        logger.error(f"  Error: {e}")
        logger.error("\nMake sure PostgreSQL is running:")
        logger.error("  - Check if PostgreSQL service is started")
        logger.error("  - Verify connection string in createDb.py")
        logger.error("  - Default: postgresql://postgres:password@localhost:5432/webscraper")
        return False


def check_database_exists():
    """Check if the webscraper database exists."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            logger.info(f"✓ Database '{db_name}' exists")
            return True
    except Exception as e:
        logger.error(f"✗ Database check failed: {e}")
        return False


def create_all_tables():
    """Create all tables in the database."""
    try:
        logger.info("\nCreating tables...")
        Base.metadata.create_all(engine)
        logger.info("✓ All tables created successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create tables: {e}")
        return False


def verify_tables():
    """Verify all tables were created."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        'domains', 'crawl_jobs', 'requests', 'pages', 'subjects', 'tags',
        'page_subjects', 'page_tags', 'job_sources', 'raw_job_entries',
        'job_postings', 'skills', 'job_posting_skills', 'posting_merges',
        'job_runs', 'product_sources', 'product_runs'
    ]
    
    logger.info(f"\nVerifying tables...")
    logger.info(f"Found {len(tables)} tables:")
    
    all_present = True
    for table in expected_tables:
        if table in tables:
            logger.info(f"  ✓ {table}")
        else:
            logger.error(f"  ✗ {table} - MISSING")
            all_present = False
    
    return all_present


def test_data_persistence():
    """Test that we can save and retrieve data."""
    logger.info("\nTesting data persistence...")
    
    session = SessionLocal()
    
    try:
        # Test 1: Create a domain
        test_domain = Domain(domain="test.example.com")
        session.add(test_domain)
        session.commit()
        
        domain_id = test_domain.id
        logger.info(f"  ✓ Created domain with ID: {domain_id}")
        
        # Test 2: Query it back
        retrieved = session.query(Domain).filter_by(domain="test.example.com").first()
        if retrieved and retrieved.id == domain_id:
            logger.info(f"  ✓ Retrieved domain: {retrieved.domain}")
        else:
            logger.error("  ✗ Failed to retrieve domain")
            return False
        
        # Test 3: Update it
        retrieved.domain = "updated.example.com"
        session.commit()
        logger.info("  ✓ Updated domain")
        
        # Test 4: Verify update persisted
        updated = session.query(Domain).filter_by(id=domain_id).first()
        if updated.domain == "updated.example.com":
            logger.info(f"  ✓ Update persisted: {updated.domain}")
        else:
            logger.error("  ✗ Update did not persist")
            return False
        
        # Clean up test data
        session.delete(updated)
        session.commit()
        logger.info("  ✓ Cleaned up test data")
        
        logger.info("\n✓ Data persistence test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Data persistence test FAILED: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def show_table_stats():
    """Show row counts for all tables."""
    logger.info("\nTable Statistics:")
    session = SessionLocal()
    
    try:
        stats = {
            'domains': session.query(Domain).count(),
            'crawl_jobs': session.query(CrawlJob).count(),
            'requests': session.query(Request).count(),
            'pages': session.query(Page).count(),
            'subjects': session.query(Subject).count(),
            'tags': session.query(Tag).count(),
            'page_subjects': session.query(PageSubject).count(),
            'page_tags': session.query(PageTag).count(),
        }
        
        total = sum(stats.values())
        
        for table, count in stats.items():
            logger.info(f"  {table}: {count} rows")
        
        logger.info(f"\nTotal rows across main tables: {total}")
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
    finally:
        session.close()


def backup_database_sql():
    """Generate SQL commands to backup current data."""
    logger.info("\nTo backup your database, run:")
    logger.info("  pg_dump -U postgres -d webscraper > backup.sql")
    logger.info("\nTo restore from backup:")
    logger.info("  psql -U postgres -d webscraper < backup.sql")


def main():
    """Main setup function."""
    print("="*60)
    print("PostgreSQL Database Setup for WebScraper")
    print("="*60)
    
    # Step 1: Check PostgreSQL connection
    if not check_postgres_connection():
        print("\n❌ Setup failed: Cannot connect to PostgreSQL")
        print("\nQuick fixes:")
        print("1. Start PostgreSQL service:")
        print("   - Windows: Services -> PostgreSQL -> Start")
        print("   - Linux: sudo systemctl start postgresql")
        print("2. Check your credentials in backend/Persistance/createDb.py")
        return False
    
    # Step 2: Check database exists
    if not check_database_exists():
        print("\n❌ Database 'webscraper' not found")
        print("\nCreate it with:")
        print('  psql -U postgres -c "CREATE DATABASE webscraper;"')
        return False
    
    # Step 3: Create tables
    if not create_all_tables():
        print("\n❌ Failed to create tables")
        return False
    
    # Step 4: Verify tables
    if not verify_tables():
        print("\n⚠ Some tables are missing")
    
    # Step 5: Test persistence
    if not test_data_persistence():
        print("\n❌ Data persistence test failed")
        return False
    
    # Step 6: Show current stats
    show_table_stats()
    
    # Step 7: Backup info
    backup_database_sql()
    
    print("\n" + "="*60)
    print("✓ Database setup complete!")
    print("="*60)
    print("\nYour data will persist in PostgreSQL at:")
    print("  postgresql://postgres@localhost:5432/webscraper")
    print("\nYou can view/manage data with:")
    print("  - pgAdmin 4 (GUI)")
    print("  - psql (command line)")
    print("  - DBeaver (universal DB tool)")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
