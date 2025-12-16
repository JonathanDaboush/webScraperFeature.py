"""
E-Commerce Product Repository

Extended repository with product-specific operations.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import json
import logging

from Persistance.crawler import (
    ProductSource, RawProductEntry, Product, PriceHistory,
    Category, ProductCategory, ProductReview, ProductMerge, ProductRun
)

logger = logging.getLogger(__name__)


class ProductRepository:
    """Repository for e-commerce product operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_or_update_product_source(
        self,
        name: str,
        source_type: str,
        base_url: str,
        config: str,
        scrape_interval_minutes: int = 60
    ) -> ProductSource:
        """Create or update a product source."""
        source = self.session.query(ProductSource).filter(
            ProductSource.name == name
        ).first()
        
        if source:
            source.source_type = source_type
            source.base_url = base_url
            source.config = config
            source.scrape_interval_minutes = scrape_interval_minutes
        else:
            source = ProductSource(
                name=name,
                source_type=source_type,
                base_url=base_url,
                config=config,
                scrape_interval_minutes=scrape_interval_minutes
            )
            self.session.add(source)
        
        self.session.commit()
        return source
    
    def save_raw_product_entry(
        self,
        source_id: int,
        external_id: str,
        raw_payload: str,
        fetch_metadata: Dict,
        run_key: str
    ) -> RawProductEntry:
        """Save raw scraped product data."""
        entry = RawProductEntry(
            source_id=source_id,
            external_id=external_id,
            raw_payload=raw_payload,
            fetch_metadata=json.dumps(fetch_metadata),
            run_key=run_key
        )
        
        self.session.add(entry)
        self.session.flush()
        
        return entry
    
    def save_product(self, product_data: Dict) -> Dict:
        """
        Save or update product with price tracking.
        
        Returns:
            {
                'product_id': int,
                'created': bool,
                'price_changed': bool,
                'old_price_cents': int | None,
                'new_price_cents': int
            }
        """
        fingerprint = product_data['fingerprint']
        
        # Check if product exists
        existing = self.session.query(Product).filter(
            Product.fingerprint == fingerprint
        ).first()
        
        result = {
            'product_id': None,
            'created': False,
            'price_changed': False,
            'old_price_cents': None,
            'new_price_cents': product_data.get('current_price_cents')
        }
        
        if existing:
            # Update existing product
            old_price = existing.current_price_cents
            new_price = product_data.get('current_price_cents')
            
            # Update fields
            existing.name = product_data['name']
            existing.current_price_cents = new_price
            existing.original_price_cents = product_data.get('original_price_cents')
            existing.discount_percent = product_data.get('discount_percent')
            existing.is_on_sale = product_data.get('is_on_sale', False)
            existing.in_stock = product_data.get('in_stock', True)
            existing.rating = product_data.get('rating')
            existing.review_count = product_data.get('review_count', 0)
            existing.last_seen_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
            
            # Track price change
            if old_price != new_price:
                result['price_changed'] = True
                result['old_price_cents'] = old_price
                
                # Add price history entry
                price_history = PriceHistory(
                    product_id=existing.id,
                    price_cents=new_price,
                    original_price_cents=product_data.get('original_price_cents'),
                    discount_percent=product_data.get('discount_percent'),
                    in_stock=product_data.get('in_stock', True)
                )
                self.session.add(price_history)
                
                logger.info(f"Price changed for {existing.name}: ${old_price/100:.2f} -> ${new_price/100:.2f}")
            
            result['product_id'] = existing.id
        
        else:
            # Create new product
            product = Product(
                source_id=product_data['source_id'],
                raw_product_entry_id=product_data.get('raw_product_entry_id'),
                name=product_data['name'],
                brand=product_data.get('brand'),
                model=product_data.get('model'),
                sku=product_data.get('sku'),
                upc=product_data.get('upc'),
                external_id=product_data.get('external_id'),
                url=product_data.get('url'),
                image_url=product_data.get('image_url'),
                current_price_cents=product_data.get('current_price_cents'),
                original_price_cents=product_data.get('original_price_cents'),
                currency=product_data.get('currency', 'USD'),
                discount_percent=product_data.get('discount_percent'),
                is_on_sale=product_data.get('is_on_sale', False),
                in_stock=product_data.get('in_stock', True),
                stock_quantity=product_data.get('stock_quantity'),
                availability_text=product_data.get('availability_text'),
                description=product_data.get('description'),
                specifications=product_data.get('specifications'),
                features=product_data.get('features'),
                rating=product_data.get('rating'),
                review_count=product_data.get('review_count', 0),
                shipping_cost_cents=product_data.get('shipping_cost_cents'),
                free_shipping=product_data.get('free_shipping', False),
                prime_eligible=product_data.get('prime_eligible', False),
                seller_name=product_data.get('seller_name'),
                seller_rating=product_data.get('seller_rating'),
                fingerprint=fingerprint,
                ingest_version=product_data.get('ingest_version', '1.0.0')
            )
            
            self.session.add(product)
            self.session.flush()
            
            # Add initial price history
            price_history = PriceHistory(
                product_id=product.id,
                price_cents=product_data.get('current_price_cents'),
                original_price_cents=product_data.get('original_price_cents'),
                discount_percent=product_data.get('discount_percent'),
                in_stock=product_data.get('in_stock', True)
            )
            self.session.add(price_history)
            
            result['product_id'] = product.id
            result['created'] = True
            
            logger.info(f"Created new product: {product.name}")
        
        self.session.commit()
        
        return result
    
    def get_price_history(
        self,
        product_id: int,
        days_back: int = 30
    ) -> List[PriceHistory]:
        """Get price history for a product."""
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        return self.session.query(PriceHistory).filter(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= cutoff
        ).order_by(PriceHistory.recorded_at.asc()).all()
    
    def find_deals(
        self,
        min_discount_percent: int = 20,
        min_rating: float = 4.0,
        limit: int = 50
    ) -> List[Product]:
        """Find products with significant discounts."""
        return self.session.query(Product).filter(
            Product.is_on_sale == True,
            Product.discount_percent >= min_discount_percent,
            Product.in_stock == True,
            Product.rating >= min_rating
        ).order_by(
            desc(Product.discount_percent)
        ).limit(limit).all()
    
    def find_price_drops(
        self,
        hours_back: int = 24,
        min_drop_percent: int = 10,
        limit: int = 50
    ) -> List[Dict]:
        """Find products with recent price drops."""
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Subquery for previous price
        from sqlalchemy import and_
        
        products = self.session.query(Product).filter(
            Product.updated_at >= cutoff
        ).all()
        
        price_drops = []
        
        for product in products:
            # Get price history
            history = self.session.query(PriceHistory).filter(
                PriceHistory.product_id == product.id,
                PriceHistory.recorded_at >= cutoff - timedelta(days=7)
            ).order_by(PriceHistory.recorded_at.desc()).limit(2).all()
            
            if len(history) >= 2:
                current = history[0]
                previous = history[1]
                
                if previous.price_cents > current.price_cents:
                    drop_percent = int(((previous.price_cents - current.price_cents) / previous.price_cents) * 100)
                    
                    if drop_percent >= min_drop_percent:
                        price_drops.append({
                            'product': product,
                            'old_price_cents': previous.price_cents,
                            'new_price_cents': current.price_cents,
                            'drop_percent': drop_percent,
                            'dropped_at': current.recorded_at
                        })
        
        # Sort by drop percent
        price_drops.sort(key=lambda x: x['drop_percent'], reverse=True)
        
        return price_drops[:limit]
    
    def get_product_sources_to_scrape(
        self,
        source_names: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[ProductSource]:
        """Get product sources due for scraping."""
        query = self.session.query(ProductSource).filter(
            ProductSource.is_active == True
        )
        
        if source_names:
            query = query.filter(ProductSource.name.in_(source_names))
        
        sources = query.all()
        
        # Filter by scrape interval with exponential backoff on failures
        due_sources = []
        now = datetime.utcnow()
        
        for source in sources:
            if not source.last_scraped_at:
                # Never scraped - add it
                due_sources.append(source)
                continue
            
            # Calculate next scrape time with backoff
            interval_minutes = source.scrape_interval_minutes
            if source.failure_count:
                # Exponential backoff: 2^failures * interval
                interval_minutes *= (2 ** min(source.failure_count, 5))
            
            next_scrape = source.last_scraped_at + timedelta(minutes=interval_minutes)
            
            if now >= next_scrape:
                due_sources.append(source)
        
        if limit:
            due_sources = due_sources[:limit]
        
        return due_sources
    
    def search_products(
        self,
        query: str,
        min_price_cents: Optional[int] = None,
        max_price_cents: Optional[int] = None,
        source_name: Optional[str] = None,
        in_stock_only: bool = True,
        limit: int = 100
    ) -> List[Product]:
        """Search products by name."""
        search_query = self.session.query(Product).filter(
            Product.name.ilike(f'%{query}%')
        )
        
        if in_stock_only:
            search_query = search_query.filter(Product.in_stock == True)
        
        if min_price_cents:
            search_query = search_query.filter(Product.current_price_cents >= min_price_cents)
        
        if max_price_cents:
            search_query = search_query.filter(Product.current_price_cents <= max_price_cents)
        
        if source_name:
            search_query = search_query.join(ProductSource).filter(
                ProductSource.name == source_name
            )
        
        return search_query.order_by(
            desc(Product.rating),
            Product.current_price_cents.asc()
        ).limit(limit).all()
