"""
Example: E-Commerce Product Price Tracker

Demonstrates:
1. Setting up product sources (Amazon, eBay, etc.)
2. Scraping products
3. Tracking price changes
4. Finding deals
"""

import sys
import os
import logging
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.product_worker import ProductWorker
from crawler.product_repository import ProductRepository
from Persistance.createDb import Session


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('product_crawler.log')
        ]
    )


def setup_product_sources(repo: ProductRepository):
    """Set up example product sources."""
    print("Setting up product sources...")
    
    # Amazon - Laptops
    amazon_config = {
        'search_query': 'laptop',
        'category': 'computers',
        'min_price': 500,
        'max_price': 2000
    }
    
    amazon = repo.create_or_update_product_source(
        name='Amazon_Laptops',
        source_type='amazon',
        base_url='https://www.amazon.com',
        config=json.dumps(amazon_config),
        scrape_interval_minutes=60
    )
    print(f"✓ Created: {amazon.name}")
    
    # eBay - Laptops
    ebay_config = {
        'search_query': 'laptop computer',
        'condition': 'new'
    }
    
    ebay = repo.create_or_update_product_source(
        name='eBay_Laptops',
        source_type='ebay',
        base_url='https://www.ebay.com',
        config=json.dumps(ebay_config),
        scrape_interval_minutes=120
    )
    print(f"✓ Created: {ebay.name}")
    
    # Walmart - Electronics
    walmart_config = {
        'search_query': 'headphones'
    }
    
    walmart = repo.create_or_update_product_source(
        name='Walmart_Headphones',
        source_type='walmart',
        base_url='https://www.walmart.com',
        config=json.dumps(walmart_config),
        scrape_interval_minutes=180
    )
    print(f"✓ Created: {walmart.name}")
    
    print()
    return [amazon, ebay, walmart]


def display_deals(repo: ProductRepository):
    """Display current deals."""
    print("\n" + "="*80)
    print("TOP DEALS (20%+ off, 4+ stars)")
    print("="*80)
    
    deals = repo.find_deals(min_discount_percent=20, min_rating=4.0, limit=10)
    
    if not deals:
        print("No deals found yet. Run scraper first.")
        return
    
    for i, product in enumerate(deals, 1):
        original = product.original_price_cents / 100
        current = product.current_price_cents / 100
        savings = original - current
        
        print(f"\n{i}. {product.name[:60]}")
        print(f"   Brand: {product.brand or 'N/A'}")
        print(f"   Price: ${current:.2f} (was ${original:.2f}) - SAVE ${savings:.2f} ({product.discount_percent}% off)")
        print(f"   Rating: {product.rating or 'N/A'} ⭐ ({product.review_count} reviews)")
        print(f"   Source: {product.source.name}")
        if product.url:
            print(f"   URL: {product.url[:80]}")


def display_price_drops(repo: ProductRepository):
    """Display recent price drops."""
    print("\n" + "="*80)
    print("RECENT PRICE DROPS (Last 24 hours)")
    print("="*80)
    
    drops = repo.find_price_drops(hours_back=24, min_drop_percent=10, limit=10)
    
    if not drops:
        print("No price drops in last 24 hours.")
        return
    
    for i, drop in enumerate(drops, 1):
        product = drop['product']
        old_price = drop['old_price_cents'] / 100
        new_price = drop['new_price_cents'] / 100
        savings = old_price - new_price
        
        print(f"\n{i}. {product.name[:60]}")
        print(f"   Price dropped: ${old_price:.2f} → ${new_price:.2f}")
        print(f"   SAVE ${savings:.2f} ({drop['drop_percent']}% off)")
        print(f"   Dropped at: {drop['dropped_at'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   URL: {product.url[:80] if product.url else 'N/A'}")


def search_products_example(repo: ProductRepository):
    """Example product search."""
    print("\n" + "="*80)
    print("SEARCH: 'laptop' under $1000")
    print("="*80)
    
    products = repo.search_products(
        query='laptop',
        max_price_cents=100000,  # $1000
        in_stock_only=True,
        limit=5
    )
    
    if not products:
        print("No products found. Run scraper first.")
        return
    
    for i, product in enumerate(products, 1):
        price = product.current_price_cents / 100 if product.current_price_cents else 0
        
        print(f"\n{i}. {product.name[:60]}")
        print(f"   Price: ${price:.2f}")
        print(f"   Rating: {product.rating or 'N/A'} ⭐")
        print(f"   In Stock: {'Yes' if product.in_stock else 'No'}")
        print(f"   Source: {product.source.name}")


def main():
    """Run e-commerce product tracking example."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("="*80)
    print("E-COMMERCE PRODUCT PRICE TRACKER")
    print("="*80)
    print()
    
    session = Session()
    
    try:
        repo = ProductRepository(session)
        worker = ProductWorker(session)
        
        # Step 1: Setup sources
        print("STEP 1: Setting up product sources")
        print("-"*80)
        sources = setup_product_sources(repo)
        
        # Step 2: Run scraper
        print("\nSTEP 2: Scraping products")
        print("-"*80)
        print("This will scrape products from configured sources...")
        print("Note: Amazon/Walmart may require proxies or may get blocked.")
        print()
        
        choice = input("Start scraping? (y/n): ").lower()
        
        if choice == 'y':
            stats = worker.scrape_all_due_sources()
            
            print(f"\n{'='*80}")
            print("SCRAPING COMPLETE!")
            print(f"{'='*80}")
            print(f"Sources scraped: {stats['sources_scraped']}")
            print(f"Total products: {stats['total_products']}")
            print(f"New products: {stats['total_new']}")
            print(f"Updated: {stats['total_updated']}")
            print(f"Price changes: {stats['total_price_changes']}")
        else:
            print("Skipping scrape. Using existing data...")
        
        # Step 3: Display deals
        display_deals(repo)
        
        # Step 4: Display price drops
        display_price_drops(repo)
        
        # Step 5: Search example
        search_products_example(repo)
        
        print("\n" + "="*80)
        print("DONE!")
        print("="*80)
        print()
        print("Next steps:")
        print("  1. Set up cron job: python -m crawler.product_worker")
        print("  2. Query database for price history")
        print("  3. Set up price alerts for specific products")
        print("  4. Export deals to CSV/JSON")
        print()
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\nError: {e}")
    
    finally:
        session.close()


if __name__ == '__main__':
    main()
