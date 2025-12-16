# WebScraper - Intelligent Web Research & E-commerce Platform

A full-stack web scraping and research application with advanced keyword extraction, automated web crawling, price tracking, and comprehensive analytics. Features intelligent content analysis using 848+ keywords across tech skills, products, seasonal themes, and demographics.

## 🌟 Key Features

### 🎯 Intelligent Keyword Extraction (NEW)
- **848 Keywords** across 4 categories
  - **Tech Skills** (200+): Programming languages, frameworks, databases, cloud platforms, DevOps tools
  - **Product Categories** (150+): Electronics, fashion, home goods, sports equipment
  - **Seasonal Themes** (50+): Holidays, sales events, seasonal trends
  - **Demographics** (25+): Age groups, professions, interests
- **Automatic Classification**: Detects page types (tech/e-commerce/seasonal)
- **Relevance Scoring**: Calculates content relevance based on keyword density
- **API Integration**: RESTful endpoints for keyword analysis
- **Browser History Analysis**: Extract interests from browsing patterns

### 🕷️ Advanced Web Crawling
- **Research Crawler**: Intelligent web page analysis with keyword extraction
- **Content Extraction**: Main content, headings, metadata, summaries
- **Link Discovery**: Automatic internal/external link detection
- **Subject & Tag Extraction**: Hierarchical content organization
- **Database Persistence**: Saves pages, tags, subjects, links with relationships

### 🛒 E-commerce Price Tracking
- Track products from Amazon, eBay, Walmart
- Automatic price updates and history tracking
- Deal detection and price drop alerts
- Price comparison across platforms

### 📊 Comprehensive Analytics
- **10 Analysis Modules**: Sentiment, topics, NLP, trends, clustering, classification
- **Data Export**: CSV, JSON, Vector DB (ChromaDB/Pinecone), Search Index (Elasticsearch)
- **Visualization**: Interactive charts and dashboards
- **Performance Metrics**: Response times, success rates, coverage stats

### 🔍 Research Tools
- Automated web research for content discovery
- Browser history analysis (Chrome, Firefox, Edge)
- Interest category detection
- URL pattern analysis

### 🧪 Comprehensive Testing
- **90+ Tests**: Unit, integration, and performance tests
- **Mock Infrastructure**: Isolated testing without external dependencies
- **Coverage Reports**: HTML, terminal, and XML formats
- **CI/CD Ready**: Automated testing and verification

## 🏗️ Architecture

### Tech Stack

#### Backend
- **Python 3.9+**
- **Flask** - REST API with CORS support
- **SQLAlchemy** - ORM with PostgreSQL
- **BeautifulSoup4** - HTML parsing and content extraction
- **Selenium** - Dynamic content scraping
- **scikit-learn** - Machine learning analysis
- **ChromaDB/Pinecone** - Vector database integration
- **Elasticsearch** - Full-text search

#### Frontend
- **React 19.2.1** - Modern UI framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icon library

#### Testing
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **unittest.mock** - Mocking framework

#### Database
- **PostgreSQL** - Primary data store
- Complex schema with 20+ tables
- Relationships: domains, pages, tags, subjects, products, jobs

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

1. Install PostgreSQL and create database:
```powershell
# Create database in psql
CREATE DATABASE webscraper;
```

2. Install Python dependencies:
```powershell
cd backend
pip install -r requirements.txt
```

3. Configure database (already set in code):
- Host: localhost
- Port: 5432
- Database: webscraper
- User: postgres
- Password: password

4. Initialize database:
```powershell
python Persistance/createDb.py
```

### Frontend Setup

1. Install Node dependencies:
```powershell
cd frontend
npm install
```

## Running the Application

### Start Backend API
```powershell
cd backend
python api.py
```
API will run on http://localhost:5000

### Start Frontend Dev Server
```powershell
cd frontend
npm start
```
Frontend will run on http://localhost:3000

### Start Product Scraper Worker (Optional)
```powershell
cd backend/crawler
python product_worker.py
```

## Project Structure

```
webScraper/
├── backend/
│   ├── Persistance/
│   │   ├── crawler.py          # Database models
│   │   ├── createDb.py         # DB initialization
│   │   ├── repository.py       # Data access layer
│   │   └── search.py           # Search functionality
│   ├── Crawler/
│   │   ├── keyword_extractor.py # **NEW: 848 keywords extraction**
│   │   ├── research_crawler.py  # **NEW: Intelligent web crawler**
│   │   ├── browser_history.py   # Browser analysis with keywords
│   │   ├── product_scrapers.py  # Site-specific scrapers
│   │   ├── product_normalizer.py # Data normalization
│   │   ├── product_repository.py # Product operations
│   │   ├── product_worker.py    # Scraping orchestration
│   │   ├── worker.py            # Generic worker
│   │   ├── scheduler.py         # Task scheduling
│   │   ├── user_research_agent.py # Research automation
│   │   └── config.py            # Configuration
│   ├── analysis/                # 10 analysis modules
│   ├── export/                  # 4 export modules
│   ├── api.py                   # Flask REST API (1000+ lines)
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.js     # Stats overview
│   │   │   ├── Products.js      # Product list
│   │   │   ├── PriceTracker.js  # Price monitoring
│   │   │   ├── BrowserHistory.js # History analysis
│   │   │   ├── Research.js      # Research interface
│   │   │   ├── Analysis.js      # Data analysis with 10 modules
│   │   │   └── Settings.js      # Configuration
│   │   ├── App.js               # Main component
│   │   └── App.css              # Styling
│   └── package.json             # Node dependencies
├── tests/                       # **NEW: Comprehensive test suite**
│   ├── unit/
│   │   ├── test_keyword_extractor.py # 47 tests
│   │   └── test_research_crawler.py  # 32 tests
│   ├── integration/
│   │   └── test_integration.py       # 11 tests
│   ├── fixtures/
│   │   └── sample_data.py            # Test data
│   ├── conftest.py              # Pytest configuration
│   ├── run_tests.py             # Test runner
│   ├── verify_tests.py          # Structure verification
│   ├── requirements.txt         # Test dependencies
│   ├── README.md                # Test documentation
│   └── TEST_SUMMARY.md          # Test summary
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.9+**
- **Node.js 18+**
- **PostgreSQL 14+**

### 2. Database Setup
```powershell
# In PostgreSQL (psql or pgAdmin)
CREATE DATABASE webscraper;

# Initialize tables
cd backend
python Persistance/createDb.py
```

### 3. Backend Setup
```powershell
cd backend
pip install -r requirements.txt
python api.py
```
✅ API running on http://localhost:5000

### 4. Frontend Setup
```powershell
cd frontend
npm install
npm start
```
✅ UI running on http://localhost:3000

### 5. Run Tests (Optional)
```powershell
cd tests
pip install -r requirements.txt
python run_tests.py
```
✅ 90+ tests validating all functionality

## 📖 Usage Guide

### Adding Products to Track

1. Navigate to **Products** page
2. Click **Add Product** button
3. Paste Amazon/eBay/Walmart product URL
4. System automatically scrapes price, title, image, reviews
5. Product added to tracking list with initial price

### Price Monitoring & Alerts

1. Go to **Price Tracker** page
2. Select a product from your tracked list
3. View interactive price history chart
4. Set target price for notifications
5. Receive alerts when price drops below target

### Browser History Analysis

1. Go to **Browser History** page
2. **Close your browser** (Chrome/Firefox/Edge)
3. Click **Analyze History**
4. System extracts:
   - **Tech interests**: Programming languages, frameworks
   - **Product interests**: Electronics, fashion, home goods
   - **Seasonal interests**: Holiday shopping patterns
   - **Demographics**: Age groups, professions
5. View categorized interests and product URLs

### Intelligent Web Research

1. Go to **Research** page
2. Enter search query (e.g., "best gaming laptops 2025")
3. Configure options:
   - Max depth: How many links to follow
   - Max pages: Total pages to crawl
   - Keywords: Focus terms (optional)
4. Click **Start Research**
5. System crawls pages and extracts:
   - Main content and summaries
   - Subjects and tags (with prefixes: tech:, product:, seasonal:)
   - Relevant keywords from 848-keyword database
   - Internal/external links
6. View results with relevance scores

### Data Analysis

### Data Analysis

1. Go to **Analysis** page
2. Select analysis type from 10 modules:
   - **Text Analysis**: Word frequency, readability scores, text statistics
   - **Sentiment Analysis**: Emotion detection in reviews and content
   - **Topic Modeling**: LDA topic extraction from documents
   - **NLP Features**: Named entities, POS tagging, linguistic features
   - **Time Series**: Trend analysis over time periods
   - **Link Network**: Page connectivity and relationship graphs
   - **Domain Metrics**: Statistical measurements and distributions
   - **Frequency Analysis**: Pattern detection in data
   - **Content Clustering**: K-means grouping of similar content
   - **PageRank**: Page importance scoring algorithm
3. Configure data source:
   - Products (titles, descriptions, reviews)
   - Pages (crawled web content)
   - Browser history (visited URLs)
   - Reviews (customer feedback)
4. Apply filters:
   - Category selection
   - Date range
   - Price range
   - Text search
5. Click **Run Analysis**
6. View interactive charts, graphs, and statistics
7. Export results in multiple formats:
   - **CSV**: Spreadsheet-compatible tabular data
   - **JSON**: Structured data for APIs
   - **Vector DB**: Embeddings for ChromaDB/Pinecone
   - **Search Index**: Full-text search for Elasticsearch

### Keyword Extraction API

Use the keyword extraction system via API:

```python
import requests

# Extract keywords from text
response = requests.post('http://localhost:5000/api/keywords/extract', json={
    'text': 'Python developer with React and AWS experience',
    'title': 'Job Posting'
})

result = response.json()
# {
#   'tech_skills': ['python', 'react', 'aws'],
#   'product_categories': [],
#   'seasonal_themes': [],
#   'demographics': [],
#   'all_keywords': ['python', 'react', 'aws']
# }

# Analyze a web page
response = requests.post('http://localhost:5000/api/keywords/analyze-page', json={
    'url': 'https://example.com/article',
    'keywords': ['python', 'django']
})

result = response.json()
# {
#   'url': 'https://example.com/article',
#   'title': 'Article Title',
#   'tech_skills': ['python', 'django', 'postgresql'],
#   'is_tech_related': True,
#   'is_ecommerce_related': False,
#   'relevance_score': 0.85
# }

# Get available keyword categories
response = requests.get('http://localhost:5000/api/keywords/categories')
categories = response.json()
# {
#   'tech_skills': ['python', 'javascript', ...],
#   'product_categories': ['laptop', 'smartphone', ...],
#   'total_tech_skills': 200,
#   'total_product_categories': 150
# }
```

## 🔌 API Reference

### Products
- `GET /api/products` - List all tracked products
- `POST /api/products` - Add new product to track
  - Body: `{ "url": "https://amazon.com/product/..." }`
- `GET /api/products/:id/price-history` - Get price history for product
- `DELETE /api/products/:id` - Remove product from tracking

### Price Tracking
- `GET /api/deals` - Current deals and discounts
- `GET /api/price-drops` - Recent price drops
- `GET /api/alerts` - Configured price alerts
- `POST /api/alerts` - Create price alert
  - Body: `{ "product_id": 1, "target_price": 99.99 }`

### Browser History
- `POST /api/browser-history/analyze` - Analyze browser history
  - Body: `{ "days_back": 7 }`
- `GET /api/browser-history/categories` - Get interest categories
- `GET /api/browser-history/products` - Extract product URLs

### Research & Crawling
- `POST /api/research/start` - Start automated research
  - Body: `{ "query": "search term", "max_depth": 2, "max_pages": 10, "keywords": ["python"] }`
- `GET /api/research/history` - View research history
- `POST /api/crawler/start` - Start web crawler
- `GET /api/crawler/runs/active` - Active crawl jobs

### Keyword Extraction (NEW)
- `POST /api/keywords/extract` - Extract keywords from text
  - Body: `{ "text": "content...", "title": "optional title" }`
- `POST /api/keywords/analyze-page` - Analyze web page
  - Body: `{ "url": "https://example.com", "keywords": ["optional", "focus", "terms"] }`
- `GET /api/keywords/categories` - Get all keyword categories
- `GET /api/keywords/stats` - Keyword extraction statistics

### Analysis Modules (NEW)
- `POST /api/analysis/text` - Text analysis (word frequency, readability)
  - Body: `{ "data_source": "products", "filters": {...} }`
- `POST /api/analysis/sentiment` - Sentiment analysis
- `POST /api/analysis/topics` - Topic modeling (LDA)
- `POST /api/analysis/nlp` - NLP features (NER, POS)
- `POST /api/analysis/time-series` - Time series trends
- `POST /api/analysis/network` - Link network graph
- `POST /api/analysis/metrics` - Domain metrics
- `POST /api/analysis/frequency` - Frequency analysis
- `POST /api/analysis/clustering` - Content clustering (K-means)
- `POST /api/analysis/ranking` - PageRank scoring

### Export Modules (NEW)
- `POST /api/export/csv` - Export to CSV
  - Body: `{ "data_type": "products", "filters": {...} }`
- `POST /api/export/json` - Export to JSON
- `POST /api/export/vector` - Export to Vector DB (ChromaDB/Pinecone)
  - Body: `{ "data_type": "pages", "target": "chromadb", "collection": "web_pages" }`
- `POST /api/export/search` - Export to Search Index (Elasticsearch)
  - Body: `{ "data_type": "products", "index": "products_index" }`

### Settings & Configuration
- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings
  - Body: `{ "scrape_interval": 3600, "rate_limit": 10 }`
- `GET /api/sources` - List configured sources
- `POST /api/sources` - Add new source
- `DELETE /api/sources/:id` - Remove source
- `POST /api/sources/:id/scrape` - Trigger manual scrape

### Statistics
- `GET /api/stats` - Dashboard statistics
  - Returns: Total products, pages, average prices, active jobs, etc.
- `GET /api/stats/performance` - Performance metrics
  - Returns: Response times, success rates, error rates

## 🗄️ Database Schema

## 🗄️ Database Schema

### Product Tracking Tables
- **ProductSource**: E-commerce sites to scrape (Amazon, eBay, Walmart)
- **Product**: Tracked products with current prices
- **PriceHistory**: Historical price data with timestamps
- **Category**: Product categories and hierarchies
- **ProductReview**: Customer reviews with ratings and sentiment
- **ProductRun**: Scraping job history and statistics

### Web Crawling Tables
- **Domain**: Crawled domains with metadata
- **Page**: Individual web pages with content
  - Fields: url, title, content, summary, status_code
  - Keywords: tech_skills, product_categories, seasonal_themes
  - Flags: is_tech_related, is_ecommerce_related, is_seasonal
- **Request**: HTTP requests with response data
- **CrawlJob**: Crawl tasks and scheduling
- **Subject**: Content subjects extracted from headings
- **Tag**: Content tags with prefixes (tech:, product:, seasonal:, demo:)
- **Link**: Discovered links (internal/external)
- **PageSubject**: Many-to-many relationship (pages ↔ subjects)
- **PageTag**: Many-to-many relationship (pages ↔ tags)

### Job Scraping Tables (Optional)
- **JobSource**: Job boards to scrape
- **RawJobEntry**: Raw job postings
- **JobPosting**: Processed job listings
- **Skill**: Required skills extracted from jobs
- **JobRun**: Job scraping history

## 🧪 Testing

### Test Suite (90+ Tests)

The project includes comprehensive testing:

#### Unit Tests (79 tests)
- **test_keyword_extractor.py** (47 tests)
  - Tech skills extraction validation
  - Product category detection
  - Seasonal theme identification
  - Demographics extraction
  - Page type classification
  - Edge cases and error handling
  
- **test_research_crawler.py** (32 tests)
  - Content extraction from HTML
  - Subject and tag extraction
  - Link discovery and filtering
  - Metadata extraction
  - Relevance scoring
  - Summary generation

#### Integration Tests (11 tests)
- **test_integration.py**
  - Database persistence validation
  - API endpoint testing
  - End-to-end workflows
  - Performance benchmarks
  - Error recovery scenarios

### Running Tests

```powershell
# Navigate to tests directory
cd tests

# Install test dependencies
pip install -r requirements.txt

# Verify test structure
python verify_tests.py

# Run all tests
python run_tests.py

# Run unit tests only
python run_tests.py --unit

# Run integration tests only
python run_tests.py --integration

# Run with coverage report
python run_tests.py --coverage
# Opens htmlcov/index.html

# Using pytest directly
pytest tests/ -v
pytest tests/unit/test_keyword_extractor.py -v
pytest tests/ --cov=backend/Crawler --cov-report=html
```

### Test Documentation

See `tests/README.md` and `tests/TEST_SUMMARY.md` for:
- Detailed test descriptions
- How to write new tests
- Coverage goals and metrics
- CI/CD integration examples

## 🛠️ Development

### Adding New Product Scrapers

1. Create scraper class in `backend/Crawler/product_scrapers.py`:

```python
class NewStoreScraper(BaseScraper):
    """Scraper for NewStore e-commerce site."""
    
    def scrape(self, url):
        """Scrape product from NewStore."""
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return {
            'title': soup.find('h1', class_='product-title').text,
            'price': float(soup.find('span', class_='price').text.replace('$', '')),
            'image': soup.find('img', class_='product-image')['src'],
            'rating': float(soup.find('div', class_='rating')['data-rating']),
            'reviews_count': int(soup.find('span', class_='review-count').text)
        }
```

2. Register in `product_worker.py`:

```python
self.scrapers = {
    'amazon': AmazonScraper(),
    'ebay': EbayScraper(),
    'walmart': WalmartScraper(),
    'newstore': NewStoreScraper()  # Add here
}
```

### Adding New Analysis Modules

1. Create module in `backend/analysis/`:

```python
# new_analysis.py
def analyze_custom_metric(data, params):
    """Perform custom analysis."""
    # Your analysis logic
    results = process_data(data)
    return {
        'metric': results,
        'visualization': chart_data,
        'insights': findings
    }
```

2. Add endpoint in `api.py`:

```python
@app.route('/api/analysis/custom', methods=['POST'])
def custom_analysis():
    data = request.json
    results = analyze_custom_metric(data['source'], data['params'])
    return jsonify(results)
```

3. Add UI component in `frontend/src/pages/Analysis.js`

### Adding Frontend Pages

1. Create component in `frontend/src/pages/NewPage.js`:

```javascript
import React from 'react';

function NewPage() {
  return (
    <div className="new-page">
      <h1>New Feature</h1>
      {/* Your component code */}
    </div>
  );
}

export default NewPage;
```

2. Add route in `frontend/src/App.js`:

```javascript
import NewPage from './pages/NewPage';

// In Routes section:
<Route path="/new-feature" element={<NewPage />} />
```

3. Add navigation link in sidebar

### Database Migrations

When modifying models in `backend/Persistance/crawler.py`:

```powershell
# Recreate database (WARNING: Drops all data)
python backend/Persistance/createDb.py

# For production, use Alembic for migrations:
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

## 🔒 Security & Privacy

### Data Protection
- Browser history analyzed **locally only**
- No personal data transmitted externally
- Scraped data stored in local PostgreSQL
- API keys and credentials in environment variables (not committed)

### Rate Limiting
- Respectful scraping with delays between requests
- User-Agent rotation to avoid blocks
- Configurable rate limits per site

### Privacy
- `.gitignore` configured to exclude:
  - Database credentials
  - Browser history files
  - Personal data exports
  - API keys and tokens

## ⚡ Performance

### Optimization Features
- **Concurrent Scraping**: Multiple products scraped in parallel
- **Database Indexing**: Optimized queries on URLs, domains, tags
- **Caching**: Frequently accessed data cached in memory
- **Batch Operations**: Bulk inserts for price history and tags
- **Efficient Querying**: SQLAlchemy with relationship loading

### Benchmarks
From integration tests (`tests/integration/test_integration.py`):
- Keyword extraction: < 0.5 seconds for 10,000 words
- Single page crawl: < 1 second
- 10 page crawl: < 5 seconds
- Database save: < 0.1 seconds per page

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Error
```
Error: could not connect to server
```
**Solution:**
- Verify PostgreSQL is running: `Get-Service postgresql*`
- Check credentials in code match your PostgreSQL setup
- Ensure database `webscraper` exists: `CREATE DATABASE webscraper;`
- Check firewall allows connection to port 5432

#### Scraping Failures
```
Error: Failed to scrape product
```
**Solution:**
- Check internet connection
- Verify target site is accessible in browser
- Update User-Agent in settings (sites may block old agents)
- Some sites require Selenium for JavaScript rendering
- Check if site has anti-bot measures (CAPTCHA, etc.)

#### Frontend Not Loading
```
Error: Cannot GET /api/products
```
**Solution:**
- Ensure backend API is running on port 5000
- Run `npm install` in `frontend/` directory
- Verify CORS is enabled in `api.py`
- Check browser console for error details
- Clear browser cache and restart dev server

#### Browser History Access Denied
```
Error: Permission denied reading history
```
**Solution:**
- **Close browser completely** before analysis
- Run terminal as administrator (Windows)
- Check browser profile paths in `browser_history.py`
- Ensure browser is supported (Chrome, Firefox, Edge)

#### Import Errors in Tests
```
ModuleNotFoundError: No module named 'crawler'
```
**Solution:**
- Ensure you're in the correct directory
- Install test dependencies: `pip install -r tests/requirements.txt`
- Add backend to Python path (handled automatically in tests)
- Check that all backend dependencies are installed

#### Low Test Coverage
```
Coverage: 65% (Goal: 80%)
```
**Solution:**
- Run tests with coverage: `python run_tests.py --coverage`
- View HTML report in `htmlcov/index.html`
- Identify uncovered lines and add tests
- Focus on critical modules (keyword_extractor, research_crawler)

## 🚀 Future Enhancements

### Planned Features
- [ ] Real-time price alerts via email/SMS
- [ ] Mobile app for iOS and Android
- [ ] Chrome extension for one-click product tracking
- [ ] AI-powered price prediction
- [ ] Multi-user support with authentication
- [ ] Product comparison tool
- [ ] Wishlist and favorites
- [ ] Social sharing of deals
- [ ] Advanced filtering and search
- [ ] Scheduled crawl jobs with cron
- [ ] Webhook notifications for events
- [ ] GraphQL API alternative
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Redis caching layer
- [ ] Elasticsearch for full-text search
- [ ] Machine learning for product recommendations

### Keyword Extraction Improvements
- [ ] Expand to 1000+ keywords
- [ ] Add more categories (healthcare, finance, education)
- [ ] Context-aware extraction (word embeddings)
- [ ] Multi-language support
- [ ] Custom keyword lists per user
- [ ] Automatic keyword discovery from data

### Analysis Enhancements
- [ ] Real-time streaming analysis
- [ ] Predictive analytics and forecasting
- [ ] Anomaly detection
- [ ] Custom report builder
- [ ] Scheduled reports via email
- [ ] Interactive dashboards
- [ ] A/B testing framework

## 📄 License

This project is for educational and personal use. Be respectful when scraping websites:
- Follow `robots.txt` rules
- Implement rate limiting
- Cache responses when possible
- Identify your scraper with accurate User-Agent
- Respect website terms of service

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional product scrapers for new sites
- Enhanced analysis algorithms
- UI/UX improvements
- Test coverage expansion
- Documentation updates
- Bug fixes and optimizations

## 📞 Support

For issues or questions:
1. Check this README and other documentation files
2. Review test files for usage examples
3. Check database schema in `Persistance/crawler.py`
4. Review API endpoints in `api.py`
5. Examine test output for error details

## 📊 Project Statistics

- **Total Lines of Code**: ~15,000+
- **Backend Modules**: 20+
- **API Endpoints**: 50+
- **Database Tables**: 20+
- **Frontend Pages**: 7
- **Tests**: 90+
- **Keywords**: 848
- **Supported Sites**: Amazon, eBay, Walmart
- **Analysis Modules**: 10
- **Export Formats**: 4
- **Browsers Supported**: Chrome, Firefox, Edge

---

**Built with ❤️ for smart shopping and intelligent web research**

- [ ] Real-time notifications (WebSocket)
- [ ] Mobile app
- [ ] More e-commerce sites
- [ ] Machine learning price prediction
- [ ] User authentication
- [ ] Multi-user support
- [ ] Telegram/Discord bot integration
- [ ] Price alert emails

## License

MIT License - Feel free to use and modify

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Support

For issues and questions, please create an issue on GitHub.

---

**Built with ❤️ for deal hunters and data enthusiasts**
