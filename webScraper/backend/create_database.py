"""
Create the webscraper database if it doesn't exist.
Run this first before setup_database.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the webscraper database."""
    try:
        # Connect to postgres database (default)
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='password',
            host='localhost',
            port='5432'
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='webscraper'")
        exists = cursor.fetchone()
        
        if exists:
            print("✓ Database 'webscraper' already exists")
        else:
            cursor.execute("CREATE DATABASE webscraper")
            print("✓ Created database 'webscraper'")
        
        cursor.close()
        conn.close()
        
        print("\nNow run: python setup_database.py")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"✗ Cannot connect to PostgreSQL: {e}")
        print("\nMake sure PostgreSQL is running:")
        print("  Windows: Get-Service postgresql*")
        print("           Start-Service postgresql-x64-14")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    create_database()
