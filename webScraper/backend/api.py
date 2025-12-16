"""
Flask API for WebScraper frontend
Provides REST endpoints for product tracking, price monitoring, browser history, and research
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Persistance'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crawler'))

from Persistance.crawler import (
    Base, ProductSource, Product, PriceHistory, 
    Category, ProductReview, ProductRun,
    Domain, Page, Request, CrawlJob, Subject, Tag,
    JobSource, RawJobEntry, JobPosting, Skill, JobRun
)
from crawler.product_worker import ProductWorker
from crawler.browser_history import BrowserHistoryExtractor
from crawler.user_research_agent import UserResearchAgent
from crawler.worker import Worker
from crawler.scheduler import Scheduler
from crawler.keyword_extractor import KeywordExtractor

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database setup
DATABASE_URL = "postgresql://postgres:password@localhost:5432/webscraper"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Initialize workers and extractors
product_worker = ProductWorker(DATABASE_URL)
keyword_extractor = KeywordExtractor()


# ============ STATS ENDPOINTS ============

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    session = Session()
    try:
        total_products = session.query(Product).count()
        
        # Active deals (products with discount > 10%)
        active_deals = session.query(Product).filter(
            Product.discount_percent > 10
        ).count()
        
        # Average savings calculation
        products_with_discount = session.query(
            func.avg(Product.original_price - Product.current_price)
        ).filter(
            Product.original_price > Product.current_price
        ).scalar()
        avg_savings = round(products_with_discount or 0, 2)
        
        # Products tracked (enabled sources)
        products_tracked = session.query(Product).filter(
            Product.in_stock == True
        ).count()
        
        return jsonify({
            'totalProducts': total_products,
            'activeDeals': active_deals,
            'avgSavings': avg_savings,
            'productsTracked': products_tracked
        })
    finally:
        session.close()


@app.route('/api/price-trends', methods=['GET'])
def get_price_trends():
    """Get 7-day price trend data"""
    session = Session()
    try:
        # Get average prices by day for last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        trends = session.query(
            func.date(PriceHistory.timestamp).label('date'),
            func.avg(PriceHistory.price).label('avgPrice')
        ).filter(
            PriceHistory.timestamp >= seven_days_ago
        ).group_by(
            func.date(PriceHistory.timestamp)
        ).order_by('date').all()
        
        return jsonify([
            {
                'date': trend.date.strftime('%m/%d'),
                'avgPrice': round(trend.avgPrice, 2)
            }
            for trend in trends
        ])
    finally:
        session.close()


# ============ PRODUCTS ENDPOINTS ============

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with current prices"""
    session = Session()
    try:
        products = session.query(Product).order_by(desc(Product.created_at)).all()
        
        return jsonify([
            {
                'id': p.id,
                'name': p.name,
                'brand': p.brand,
                'category': p.category,
                'currentPrice': float(p.current_price or 0),
                'originalPrice': float(p.original_price or 0) if p.original_price else None,
                'priceChange': float(p.discount_percent or 0),
                'source': p.source,
                'url': p.url,
                'imageUrl': p.image_url,
                'inStock': p.in_stock,
                'rating': float(p.rating or 0),
                'reviewCount': p.review_count,
                'updatedAt': p.updated_at.isoformat() if p.updated_at else None
            }
            for p in products
        ])
    finally:
        session.close()


@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product to track"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Trigger product scraping
        product_worker.scrape_url(url)
        
        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/price-history', methods=['GET'])
def get_product_price_history(product_id):
    """Get price history for a specific product"""
    days = request.args.get('days', 7, type=int)
    session = Session()
    
    try:
        since = datetime.now() - timedelta(days=days)
        
        history = session.query(PriceHistory).filter(
            PriceHistory.product_id == product_id,
            PriceHistory.timestamp >= since
        ).order_by(PriceHistory.timestamp).all()
        
        return jsonify([
            {
                'date': h.timestamp.strftime('%m/%d'),
                'price': float(h.price),
                'inStock': h.in_stock
            }
            for h in history
        ])
    finally:
        session.close()


# ============ DEALS ENDPOINTS ============

@app.route('/api/deals', methods=['GET'])
def get_deals():
    """Get current deals (discounted products)"""
    limit = request.args.get('limit', 10, type=int)
    min_discount = request.args.get('min_discount', 10, type=int)
    
    session = Session()
    try:
        deals = session.query(Product).filter(
            Product.discount_percent >= min_discount,
            Product.in_stock == True
        ).order_by(desc(Product.discount_percent)).limit(limit).all()
        
        return jsonify([
            {
                'name': d.name,
                'brand': d.brand,
                'currentPrice': float(d.current_price),
                'originalPrice': float(d.original_price),
                'discount': float(d.discount_percent),
                'url': d.url,
                'source': d.source
            }
            for d in deals
        ])
    finally:
        session.close()


@app.route('/api/price-drops', methods=['GET'])
def get_price_drops():
    """Get recent price drops"""
    days = request.args.get('days', 7, type=int)
    session = Session()
    
    try:
        since = datetime.now() - timedelta(days=days)
        
        # Find products with recent price drops
        products = session.query(Product).filter(
            Product.updated_at >= since,
            Product.discount_percent > 0
        ).order_by(desc(Product.discount_percent)).limit(20).all()
        
        drops = []
        for product in products:
            if product.original_price and product.current_price < product.original_price:
                savings = product.original_price - product.current_price
                drops.append({
                    'productName': product.name,
                    'oldPrice': float(product.original_price),
                    'newPrice': float(product.current_price),
                    'savings': float(savings),
                    'percentDrop': float(product.discount_percent)
                })
        
        return jsonify(drops)
    finally:
        session.close()


# ============ ALERTS ENDPOINTS ============

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get price alerts (placeholder - implement PriceAlert model)"""
    # This is a placeholder - you would need to create a PriceAlert model
    return jsonify([])


@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create a price alert"""
    data = request.json
    # Placeholder - implement with PriceAlert model
    return jsonify({'message': 'Alert created'}), 201


# ============ BROWSER HISTORY ENDPOINTS ============

@app.route('/api/browser-history', methods=['GET'])
def get_browser_history():
    """Get extracted browser history"""
    # Placeholder - return empty for now
    return jsonify([])


@app.route('/api/browser-history/categories', methods=['GET'])
def get_history_categories():
    """Get browsing interest categories"""
    # Placeholder - return sample data
    return jsonify([
        {'name': 'Electronics', 'value': 35},
        {'name': 'Fashion', 'value': 25},
        {'name': 'Home & Garden', 'value': 20},
        {'name': 'Sports', 'value': 15},
        {'name': 'Books', 'value': 5}
    ])


@app.route('/api/browser-history/domains', methods=['GET'])
def get_top_domains():
    """Get most visited domains"""
    # Placeholder - return sample data
    return jsonify([
        {'domain': 'amazon.com', 'visits': 45},
        {'domain': 'ebay.com', 'visits': 32},
        {'domain': 'walmart.com', 'visits': 28},
        {'domain': 'target.com', 'visits': 15},
        {'domain': 'bestbuy.com', 'visits': 12}
    ])


@app.route('/api/browser-history/analyze', methods=['POST'])
def analyze_browser_history():
    """Analyze browser history for product URLs"""
    data = request.json
    browser = data.get('browser', 'chrome')
    
    try:
        extractor = BrowserHistoryExtractor()
        
        if browser == 'chrome':
            urls = extractor.extract_chrome_history()
        elif browser == 'firefox':
            urls = extractor.extract_firefox_history()
        elif browser == 'edge':
            urls = extractor.extract_edge_history()
        else:
            return jsonify({'error': 'Unsupported browser'}), 400
        
        return jsonify({
            'message': f'Analyzed {len(urls)} URLs from {browser}',
            'count': len(urls)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ RESEARCH ENDPOINTS ============

@app.route('/api/research/history', methods=['GET'])
def get_research_history():
    """Get research history"""
    # Placeholder - return empty for now
    return jsonify([])


@app.route('/api/research/start', methods=['POST'])
def start_research():
    """Start a new research task"""
    data = request.json
    query = data.get('query')
    max_depth = data.get('maxDepth', 2)
    max_pages = data.get('maxPages', 50)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        # Initialize research agent
        agent = UserResearchAgent(DATABASE_URL)
        
        # Run research (this would be async in production)
        results = agent.research(query, max_depth=max_depth, max_pages=max_pages)
        
        return jsonify({
            'query': query,
            'pagesFound': len(results.get('pages', [])),
            'summary': results.get('summary', 'Research completed'),
            'keyFindings': results.get('findings', []),
            'productUrls': results.get('products', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/research/<int:research_id>', methods=['GET'])
def get_research(research_id):
    """Get specific research results"""
    # Placeholder - implement with Research model
    return jsonify({
        'id': research_id,
        'query': 'Sample research',
        'pagesFound': 0,
        'summary': 'No data yet'
    })


# ============ SOURCES ENDPOINTS ============

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Get all product sources"""
    session = Session()
    try:
        sources = session.query(ProductSource).all()
        
        return jsonify([
            {
                'id': s.id,
                'name': s.name,
                'type': s.site_type,
                'url': s.base_url,
                'enabled': s.enabled,
                'lastScrape': s.last_scrape_time.isoformat() if s.last_scrape_time else None
            }
            for s in sources
        ])
    finally:
        session.close()


@app.route('/api/sources', methods=['POST'])
def add_source():
    """Add a new product source"""
    data = request.json
    session = Session()
    
    try:
        source = ProductSource(
            name=data['name'],
            base_url=data['url'],
            site_type=data['type'],
            enabled=True
        )
        
        session.add(source)
        session.commit()
        
        return jsonify({
            'id': source.id,
            'name': source.name,
            'type': source.site_type,
            'url': source.base_url,
            'enabled': source.enabled
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/sources/<int:source_id>', methods=['DELETE'])
def delete_source(source_id):
    """Delete a product source"""
    session = Session()
    try:
        source = session.query(ProductSource).filter_by(id=source_id).first()
        if not source:
            return jsonify({'error': 'Source not found'}), 404
        
        session.delete(source)
        session.commit()
        
        return jsonify({'message': 'Source deleted'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/sources/<int:source_id>/scrape', methods=['POST'])
def scrape_source(source_id):
    """Trigger immediate scrape for a source"""
    session = Session()
    try:
        source = session.query(ProductSource).filter_by(id=source_id).first()
        if not source:
            return jsonify({'error': 'Source not found'}), 404
        
        # Trigger scraping
        product_worker.scrape_source(source_id)
        
        return jsonify({'message': 'Scraping started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ============ SETTINGS ENDPOINTS ============

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get application settings"""
    # Placeholder - implement with Settings model
    return jsonify({
        'scrapeInterval': 3600,
        'maxConcurrent': 5,
        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'enableNotifications': True,
        'priceDropThreshold': 10
    })


@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update application settings"""
    data = request.json
    # Placeholder - implement with Settings model
    return jsonify({'message': 'Settings updated'}), 200


# ============ ANALYSIS ENDPOINTS ============

@app.route('/api/analysis/<analysis_type>', methods=['POST'])
def run_analysis(analysis_type):
    """Run specified analysis on data"""
    data = request.json
    source = data.get('source', 'products')
    filters = data.get('filters', {})
    
    session = Session()
    try:
        # Import analysis modules dynamically
        import sys
        import os
        analysis_path = os.path.join(os.path.dirname(__file__), 'analysis')
        sys.path.insert(0, analysis_path)
        
        # Map analysis types to modules
        analysis_modules = {
            'text': 'text_analysis',
            'sentiment': 'sentiment',
            'topics': 'topic_modeling',
            'nlp': 'nlp_features',
            'time-series': 'time_series',
            'network': 'link_network',
            'metrics': 'domain_metrics',
            'frequency': 'frequency',
            'clustering': 'clustering',
            'ranking': 'ranking'
        }
        
        if analysis_type not in analysis_modules:
            return jsonify({'error': 'Invalid analysis type'}), 400
        
        # Get data based on source
        if source == 'products':
            items = session.query(Product).all()
            data_text = ' '.join([p.name + ' ' + (p.description or '') for p in items])
        elif source == 'reviews':
            reviews = session.query(ProductReview).all()
            data_text = ' '.join([r.review_text for r in reviews])
        else:
            data_text = ''
        
        # Run analysis (simplified - actual modules need proper integration)
        try:
            module_name = analysis_modules[analysis_type]
            module = __import__(module_name)
            
            # Call analyze function if available
            if hasattr(module, 'analyze'):
                results = module.analyze(data_text)
            else:
                results = {'status': 'Analysis module loaded', 'type': analysis_type}
        except Exception as e:
            # Return mock data for now
            results = {
                'status': 'Analysis completed',
                'type': analysis_type,
                'note': 'Using mock data - integrate modules for real analysis',
                'error': str(e)
            }
        
        return jsonify(results)
    finally:
        session.close()


# ============ EXPORT ENDPOINTS ============

@app.route('/api/export/<format_type>', methods=['POST'])
def export_data(format_type):
    """Export analysis results in specified format"""
    data = request.json
    source = data.get('source', 'products')
    filters = data.get('filters', {})
    analysis_type = data.get('analysisType', 'products')
    
    session = Session()
    try:
        # Get data based on source
        if source == 'products':
            items = session.query(Product).all()
            export_data = [
                {
                    'id': p.id,
                    'name': p.name,
                    'brand': p.brand,
                    'category': p.category,
                    'price': float(p.current_price or 0),
                    'url': p.url,
                    'source': p.source
                }
                for p in items
            ]
        else:
            export_data = []
        
        # Import export modules dynamically
        import sys
        import os
        export_path = os.path.join(os.path.dirname(__file__), 'export')
        sys.path.insert(0, export_path)
        
        if format_type == 'csv':
            from flask import make_response
            import csv
            from io import StringIO
            
            si = StringIO()
            if export_data:
                writer = csv.DictWriter(si, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
            
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = f"attachment; filename=export_{analysis_type}.csv"
            output.headers["Content-type"] = "text/csv"
            return output
        
        elif format_type == 'json':
            from flask import make_response
            import json
            
            output = make_response(json.dumps(export_data, indent=2))
            output.headers["Content-Disposition"] = f"attachment; filename=export_{analysis_type}.json"
            output.headers["Content-type"] = "application/json"
            return output
        
        elif format_type == 'vector':
            # Vector DB export would require embeddings
            return jsonify({'message': 'Vector export requires embedding model', 'items': len(export_data)}), 200
        
        elif format_type == 'search':
            # Elasticsearch format
            return jsonify({'message': 'Search index export prepared', 'items': len(export_data)}), 200
        
        else:
            return jsonify({'error': 'Invalid export format'}), 400
            
    finally:
        session.close()


# ============ CRAWLER MANAGEMENT ENDPOINTS ============

@app.route('/api/crawler/stats', methods=['GET'])
def get_crawler_stats():
    """Get crawler statistics"""
    session = Session()
    try:
        total_pages = session.query(Page).count()
        total_domains = session.query(Domain).count()
        active_crawls = session.query(CrawlJob).filter(CrawlJob.status == 'active').count()
        
        # Pages today
        from datetime import datetime, timedelta
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_pages = session.query(Page).filter(Page.crawled_at >= today_start).count()
        
        # Pages per day (last 7 days)
        pages_per_day = []
        for i in range(6, -1, -1):
            day_start = today_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            count = session.query(Page).filter(
                Page.crawled_at >= day_start,
                Page.crawled_at < day_end
            ).count()
            pages_per_day.append({
                'date': day_start.strftime('%m/%d'),
                'pages': count
            })
        
        return jsonify({
            'totalPages': total_pages,
            'totalDomains': total_domains,
            'activeCrawls': active_crawls,
            'todayPages': today_pages,
            'pagesPerDay': pages_per_day
        })
    finally:
        session.close()


@app.route('/api/crawler/jobs', methods=['GET'])
def get_crawl_jobs():
    """Get all crawl jobs"""
    session = Session()
    try:
        jobs = session.query(CrawlJob).order_by(desc(CrawlJob.created_at)).all()
        
        return jsonify([
            {
                'id': j.id,
                'name': j.name or f"Job {j.id}",
                'subject': j.subject.name if j.subject else 'General',
                'searchQuery': j.search_query,
                'status': 'active' if j.enabled else 'paused',
                'lastRun': j.last_run_time.isoformat() if j.last_run_time else None,
                'pagesFound': session.query(Page).join(Request).filter(Request.crawl_job_id == j.id).count()
            }
            for j in jobs
        ])
    finally:
        session.close()


@app.route('/api/crawler/jobs', methods=['POST'])
def create_crawl_job():
    """Create a new crawl job"""
    data = request.json
    session = Session()
    
    try:
        # Get or create subject
        subject = session.query(Subject).filter_by(name=data['subject']).first()
        if not subject:
            subject = Subject(name=data['subject'])
            session.add(subject)
            session.flush()
        
        # Create crawl job
        job = CrawlJob(
            subject_id=subject.id,
            search_query=data.get('searchQuery'),
            enabled=True,
            interval_seconds=3600  # Default 1 hour
        )
        session.add(job)
        session.commit()
        
        # Add start URLs as requests
        for url in data.get('startUrls', []):
            req = Request(
                url=url,
                crawl_job_id=job.id,
                priority=1
            )
            session.add(req)
        session.commit()
        
        return jsonify({
            'id': job.id,
            'message': 'Crawl job created successfully'
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/crawler/jobs/<int:job_id>/start', methods=['POST'])
def start_crawl_job(job_id):
    """Start a crawl job"""
    session = Session()
    try:
        job = session.query(CrawlJob).filter_by(id=job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Initialize worker and start crawling in background
        # In production, this would use Celery or similar
        job.last_run_time = datetime.now()
        job.enabled = True
        session.commit()
        
        # Start worker (simplified - should be async)
        try:
            worker = Worker(session)
            # This would normally be run in a background task
            # worker.run_job(job_id)
        except Exception as e:
            logger.error(f"Worker error: {e}")
        
        return jsonify({'message': 'Crawl job started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/crawler/runs/active', methods=['GET'])
def get_active_runs():
    """Get active crawler runs"""
    session = Session()
    try:
        # Get recent crawl jobs that are running
        jobs = session.query(CrawlJob).filter(
            CrawlJob.enabled == True,
            CrawlJob.last_run_time != None
        ).all()
        
        runs = []
        for job in jobs:
            # Check if run is recent (within last hour)
            if job.last_run_time:
                time_diff = datetime.now() - job.last_run_time
                if time_diff.total_seconds() < 3600:
                    runs.append({
                        'id': job.id,
                        'jobName': job.subject.name if job.subject else f'Job {job.id}',
                        'startTime': job.last_run_time.isoformat(),
                        'progress': 50,  # Simplified - would track actual progress
                        'pagesCrawled': session.query(Page).join(Request).filter(
                            Request.crawl_job_id == job.id
                        ).count(),
                        'errors': 0,
                        'status': 'running'
                    })
        
        return jsonify(runs)
    finally:
        session.close()


@app.route('/api/crawler/runs/<int:run_id>/pause', methods=['POST'])
def pause_crawl_run(run_id):
    """Pause a running crawl"""
    session = Session()
    try:
        job = session.query(CrawlJob).filter_by(id=run_id).first()
        if not job:
            return jsonify({'error': 'Run not found'}), 404
        
        job.enabled = False
        session.commit()
        
        return jsonify({'message': 'Crawl paused'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/crawler/pages', methods=['GET'])
def get_crawled_pages():
    """Get recently crawled pages"""
    limit = request.args.get('limit', 50, type=int)
    session = Session()
    
    try:
        pages = session.query(Page).order_by(desc(Page.crawled_at)).limit(limit).all()
        
        return jsonify([
            {
                'url': p.url,
                'title': p.title,
                'domain': p.domain.name if p.domain else 'Unknown',
                'statusCode': p.status_code,
                'crawledAt': p.crawled_at.isoformat() if p.crawled_at else None,
                'contentLength': p.content_length
            }
            for p in pages
        ])
    finally:
        session.close()


@app.route('/api/crawler/domains', methods=['GET'])
def get_crawled_domains():
    """Get all crawled domains"""
    session = Session()
    try:
        domains = session.query(Domain).all()
        
        return jsonify([
            {
                'name': d.name,
                'pageCount': session.query(Page).filter(Page.domain_id == d.id).count(),
                'firstSeen': d.created_at.isoformat() if d.created_at else None,
                'lastCrawled': session.query(func.max(Page.crawled_at)).filter(
                    Page.domain_id == d.id
                ).scalar()
            }
            for d in domains
        ])
    finally:
        session.close()


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============ KEYWORD EXTRACTION ENDPOINTS ============

@app.route('/api/keywords/extract', methods=['POST'])
def extract_keywords():
    """
    Extract structured keywords from text.
    
    Request body:
        {
            "text": "Page content...",
            "title": "Page title (optional)"
        }
    
    Returns:
        {
            "tech_skills": [...],
            "product_categories": [...],
            "seasonal_themes": [...],
            "demographics": [...],
            "top_categories": [("electronics", 0.85), ...],
            "is_tech_related": true,
            "is_ecommerce_related": false
        }
    """
    data = request.json
    text = data.get('text', '')
    title = data.get('title', '')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    # Extract all keyword types
    results = keyword_extractor.extract_all(text, title)
    
    # Get category scores
    top_categories = keyword_extractor.get_top_categories(text, title, top_n=10)
    
    # Check page type
    is_tech = keyword_extractor.is_tech_related(text)
    is_ecommerce = keyword_extractor.is_ecommerce_related(text)
    
    return jsonify({
        'tech_skills': results.get('tech_skills', []),
        'product_categories': results.get('product_categories', []),
        'seasonal_themes': results.get('seasonal_themes', []),
        'demographics': results.get('demographics', []),
        'all_keywords': results.get('all_keywords', []),
        'top_categories': [{'category': cat, 'score': score} for cat, score in top_categories],
        'is_tech_related': is_tech,
        'is_ecommerce_related': is_ecommerce,
        'total_keywords_found': len(results.get('all_keywords', []))
    })


@app.route('/api/keywords/analyze-page', methods=['POST'])
def analyze_page_keywords():
    """
    Fetch and analyze keywords from a URL.
    
    Request body:
        {
            "url": "https://example.com/page"
        }
    
    Returns:
        Enhanced keyword analysis with page metadata
    """
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Fetch page using research crawler
        from crawler.http_client import HttpClient
        from Persistance.repository import Repository
        from crawler.research_crawler import ResearchCrawler
        
        session = Session()
        repo = Repository(session)
        http_client = HttpClient()
        crawler = ResearchCrawler(http_client, repo)
        
        # Crawl and analyze page
        result = crawler.crawl_page(url, keywords=[])
        
        session.close()
        
        if not result:
            return jsonify({'error': 'Failed to fetch page'}), 400
        
        return jsonify({
            'url': url,
            'title': result.get('title', ''),
            'summary': result.get('summary', ''),
            'tech_skills': result.get('tech_skills', []),
            'product_categories': result.get('product_categories', []),
            'seasonal_themes': result.get('seasonal_themes', []),
            'demographics': result.get('demographics', []),
            'top_categories': [
                {'category': cat, 'score': score} 
                for cat, score in result.get('top_categories', [])
            ],
            'metadata': result.get('metadata', {}),
            'subjects': result.get('subjects', []),
            'tags': result.get('tags', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/keywords/categories', methods=['GET'])
def get_available_categories():
    """
    Get all available keyword categories and their items.
    
    Returns:
        {
            "tech_skills": {
                "languages": [...],
                "frameworks": [...],
                ...
            },
            "product_categories": {
                "electronics": [...],
                "fashion": [...],
                ...
            },
            "seasonal_themes": {
                "christmas": [...],
                "halloween": [...],
                ...
            }
        }
    """
    return jsonify({
        'tech_skills': keyword_extractor.TECH_SKILLS,
        'product_categories': keyword_extractor.PRODUCT_CATEGORIES,
        'seasonal_themes': keyword_extractor.SEASONAL_THEMES,
        'demographics': keyword_extractor.DEMOGRAPHICS,
        'total_tech_skills': sum(len(v) for v in keyword_extractor.TECH_SKILLS.values()),
        'total_product_keywords': sum(len(v) for v in keyword_extractor.PRODUCT_CATEGORIES.values()),
        'total_seasonal_keywords': sum(len(v) for v in keyword_extractor.SEASONAL_THEMES.values())
    })


# ============ MAIN ============

if __name__ == '__main__':
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    print("Starting WebScraper API on http://localhost:5000")
    print("CORS enabled for frontend development")
    print("\nAvailable endpoints:")
    print("  GET  /api/stats - Dashboard statistics")
    print("  GET  /api/products - List all products")
    print("  POST /api/products - Add product to track")
    print("  GET  /api/deals - Get current deals")
    print("  GET  /api/price-drops - Recent price drops")
    print("  GET  /api/sources - Product sources")
    print("  POST /api/sources - Add product source")
    print("  POST /api/research/start - Start research")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
