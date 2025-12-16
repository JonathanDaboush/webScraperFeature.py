"""
Flask API for Web Crawler

Provides a simple REST API to trigger crawling from the frontend.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Crawler.research_crawler import ResearchCrawler
from Crawler.http_client import HttpClient
from Persistance.repository import Repository
from Persistance.createDb import SessionLocal

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


@app.route('/api/crawl', methods=['POST'])
def crawl_url():
    """
    Crawl a single URL and return results.
    
    POST /api/crawl
    Body: {
        "url": "https://example.com",
        "keywords": ["python", "programming"]  # optional
    }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        keywords = data.get('keywords', [])
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Initialize crawler
        client = HttpClient()
        session = SessionLocal()
        repo = Repository(session)
        crawler = ResearchCrawler(client, repo)
        
        # Crawl the page
        result = crawler.crawl_page(url, keywords)
        
        session.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get crawler statistics."""
    try:
        session = SessionLocal()
        
        from Persistance.crawler import Domain, Page
        
        stats = {
            'total_domains': session.query(Domain).count(),
            'total_pages': session.query(Page).count(),
            'crawled_pages': session.query(Page).filter(Page.crawled == True).count()
        }
        
        session.close()
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_data():
    """
    Export crawled data.
    
    GET /api/export?format=json&limit=100
    """
    try:
        format_type = request.args.get('format', 'json')
        limit = int(request.args.get('limit', 100))
        
        session = SessionLocal()
        from Persistance.crawler import Page
        
        pages = session.query(Page).limit(limit).all()
        
        data = []
        for page in pages:
            data.append({
                'url': page.url,
                'title': page.title,
                'date_found': page.date_found.isoformat() if page.date_found else None,
                'crawled': page.crawled
            })
        
        session.close()
        
        if format_type == 'json':
            return jsonify(data), 200
        else:
            # CSV format
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=['url', 'title', 'date_found', 'crawled'])
            writer.writeheader()
            writer.writerows(data)
            
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=export.csv'
            }
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Crawler API is running'}), 200


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Crawler API Server Starting")
    print("=" * 60)
    print()
    print("API Endpoints:")
    print("  POST   /api/crawl   - Crawl a URL")
    print("  GET    /api/stats   - Get statistics")
    print("  GET    /api/export  - Export data")
    print("  GET    /api/health  - Health check")
    print()
    print("Server running at: http://localhost:5000")
    print("=" * 60)
    print()
    
    app.run(debug=True, port=5000)
