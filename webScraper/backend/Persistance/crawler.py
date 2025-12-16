from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Import shared Base and engine
from Persistance.createDb import Base, engine

# ────────────────────────────────
# ENUMS
# ────────────────────────────────

class RequestType(enum.Enum):
    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"
    SUBREQUEST = "SUBREQUEST"


class JobStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EmploymentType(enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERNSHIP = "INTERNSHIP"


# ────────────────────────────────
# MAIN TABLES
# ────────────────────────────────

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True, nullable=False)
    
    pages = relationship("Page", back_populates="domain")
    requests = relationship("Request", back_populates="domain")


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(Integer, primary_key=True)
    search_query = Column(String, nullable=True)  # What you searched for
    started = Column(DateTime, default=datetime.utcnow)
    description = Column(String)

    requests = relationship("Request", back_populates="crawl_job")


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    request_type = Column(Enum(RequestType), default=RequestType.GET)
    parent_request_id = Column(Integer, ForeignKey("requests.id"))
    domain_id = Column(Integer, ForeignKey("domains.id"))
    crawl_job_id = Column(Integer, ForeignKey("crawl_jobs.id"))

    date_requested = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)
    
    # Relations
    parent = relationship("Request", remote_side=[id])
    domain = relationship("Domain", back_populates="requests")
    crawl_job = relationship("CrawlJob", back_populates="requests")
    page = relationship("Page", uselist=False, back_populates="request")


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    request_id = Column(Integer, ForeignKey("requests.id"))

    title = Column(String)
    html = Column(Text)
    date_found = Column(DateTime, default=datetime.utcnow)
    crawled = Column(Boolean, default=False)

    domain = relationship("Domain", back_populates="pages")
    request = relationship("Request", back_populates="page")

    subjects = relationship("PageSubject", back_populates="page")
    tags = relationship("PageTag", back_populates="page")


# ────────────────────────────────
# SUBJECTS AND TAGGING
# ────────────────────────────────

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    pages = relationship("PageSubject", back_populates="subject")


class PageSubject(Base):
    __tablename__ = "page_subjects"

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("pages.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    page = relationship("Page", back_populates="subjects")
    subject = relationship("Subject", back_populates="pages")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    tag = Column(String, unique=True)

    pages = relationship("PageTag", back_populates="tag_obj")


class PageTag(Base):
    __tablename__ = "page_tags"

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("pages.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    page = relationship("Page", back_populates="tags")
    tag_obj = relationship("Tag", back_populates="pages")


# ────────────────────────────────
# JOB SCRAPING TABLES
# ────────────────────────────────

class JobSource(Base):
    """Job board sources to scrape from"""
    __tablename__ = "job_sources"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    base_url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    scrape_interval_minutes = Column(Integer, default=60)
    last_successful_scrape = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)
    
    raw_entries = relationship("RawJobEntry", back_populates="job_source")
    postings = relationship("JobPosting", back_populates="job_source")


class RawJobEntry(Base):
    """Raw scraped data before normalization"""
    __tablename__ = "raw_job_entries"
    
    id = Column(Integer, primary_key=True)
    job_source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=False)
    external_id = Column(String, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    raw_payload = Column(Text, nullable=False)  # JSON string
    query = Column(String, nullable=True)
    location = Column(String, nullable=True)
    http_status = Column(Integer, nullable=True)
    fetch_duration_ms = Column(Integer, nullable=True)
    
    job_source = relationship("JobSource", back_populates="raw_entries")


class JobPosting(Base):
    """Normalized and deduplicated job postings"""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True)
    job_source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=False)
    external_id = Column(String, nullable=True)
    
    # Core fields
    title = Column(String, nullable=False)
    normalized_title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    is_remote = Column(Boolean, nullable=True)
    description = Column(Text, nullable=False)
    
    # Dates
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Employment details
    employment_type = Column(Enum(EmploymentType), nullable=True)
    salary_min_cents = Column(Integer, nullable=True)  # Annualized in cents
    salary_max_cents = Column(Integer, nullable=True)
    currency = Column(String(3), nullable=True)  # ISO 4217
    
    # Skills as JSON array
    skills = Column(Text, nullable=True)  # JSON array string
    
    # URL and fingerprint
    url = Column(String, nullable=True)
    fingerprint = Column(String(64), unique=True, nullable=False)  # SHA256 hash
    
    # Versioning and provenance
    ingest_version = Column(String, nullable=False)
    source_references = Column(Text, nullable=True)  # JSON array of source refs
    
    job_source = relationship("JobSource", back_populates="postings")
    skills_rel = relationship("JobPostingSkill", back_populates="posting")


class Skill(Base):
    """Canonical skill names"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=True)
    
    postings = relationship("JobPostingSkill", back_populates="skill")


class JobPostingSkill(Base):
    """Many-to-many relationship between postings and skills"""
    __tablename__ = "job_posting_skills"
    
    id = Column(Integer, primary_key=True)
    posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    posting = relationship("JobPosting", back_populates="skills_rel")
    skill = relationship("Skill", back_populates="postings")


class PostingMerge(Base):
    """Audit log for deduplication merges"""
    __tablename__ = "posting_merges"
    
    id = Column(Integer, primary_key=True)
    canonical_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    duplicate_fingerprint = Column(String(64), nullable=False)
    merge_reason = Column(String, nullable=False)
    merge_score = Column(Integer, nullable=True)  # Score * 100
    merged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class JobRun(Base):
    """Track scraper job execution"""
    __tablename__ = "job_runs"
    
    id = Column(Integer, primary_key=True)
    job_source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=False)
    idempotency_key = Column(String, unique=True, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    query = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Statistics
    processed_count = Column(Integer, default=0)
    inserted_count = Column(Integer, default=0)
    merged_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    errors = Column(Text, nullable=True)  # JSON array of error messages


# E-Commerce Product Models
class ProductSource(Base):
    """E-commerce sites to scrape for products."""
    __tablename__ = 'product_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)  # 'Amazon', 'eBay', etc.
    source_type = Column(String(64), nullable=False)  # 'amazon', 'ebay', 'walmart', 'generic'
    base_url = Column(String(512), nullable=False)
    config = Column(Text)  # JSON: selectors, pagination, categories
    scrape_interval_minutes = Column(Integer, default=60)
    last_scraped_at = Column(DateTime)
    failure_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship('Product', back_populates='source')
    runs = relationship('ProductRun', back_populates='source')


class RawProductEntry(Base):
    """Raw scraped product data before normalization."""
    __tablename__ = 'raw_product_entries'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('product_sources.id'), nullable=False)
    external_id = Column(String(128))  # Site's product ID/SKU
    raw_payload = Column(Text, nullable=False)  # Full HTML/JSON
    fetch_metadata = Column(Text)  # JSON: status_code, headers, etc.
    run_key = Column(String(255))  # Link to scrape run
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    source = relationship('ProductSource')


class Category(Base):
    """Product categories (hierarchical)."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    slug = Column(String(128))
    
    # Relationships
    parent = relationship('Category', remote_side=[id], backref='children')
    products = relationship('ProductCategory', back_populates='category')


class Product(Base):
    """Normalized product data with price tracking."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('product_sources.id'), nullable=False)
    raw_product_entry_id = Column(Integer, ForeignKey('raw_product_entries.id'))
    
    # Core fields
    name = Column(String(500), nullable=False)
    brand = Column(String(200))
    model = Column(String(200))
    sku = Column(String(128))  # Site-specific SKU
    upc = Column(String(128))  # Universal Product Code
    external_id = Column(String(128))  # Site's product ID
    url = Column(String(512))
    image_url = Column(String(512))
    
    # Pricing (in cents to avoid floating point issues)
    current_price_cents = Column(Integer)
    original_price_cents = Column(Integer)  # Before discount
    currency = Column(String(3), default='USD')
    
    # Discount info
    discount_percent = Column(Integer)  # 0-100
    is_on_sale = Column(Boolean, default=False)
    
    # Availability
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer)
    availability_text = Column(String(128))  # "In Stock", "Ships in 3-5 days", etc.
    
    # Details
    description = Column(Text)
    specifications = Column(Text)  # JSON: key-value pairs
    features = Column(Text)  # JSON array of feature strings
    
    # Reviews & Ratings
    rating = Column(Float)  # Average rating (e.g., 4.5)
    review_count = Column(Integer, default=0)
    
    # Shipping
    shipping_cost_cents = Column(Integer)
    free_shipping = Column(Boolean, default=False)
    prime_eligible = Column(Boolean, default=False)  # Amazon specific
    
    # Seller info
    seller_name = Column(String(200))
    seller_rating = Column(Float)
    
    # Metadata
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)
    ingest_version = Column(String(32))
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship('ProductSource', back_populates='products')
    raw_entry = relationship('RawProductEntry')
    price_history = relationship('PriceHistory', back_populates='product')
    categories = relationship('ProductCategory', back_populates='product')
    reviews = relationship('ProductReview', back_populates='product')
    merges = relationship('ProductMerge', back_populates='product')


class PriceHistory(Base):
    """Track price changes over time for deal detection."""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    price_cents = Column(Integer, nullable=False)
    original_price_cents = Column(Integer)
    discount_percent = Column(Integer)
    currency = Column(String(3), default='USD')
    in_stock = Column(Boolean, default=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    product = relationship('Product', back_populates='price_history')


class ProductCategory(Base):
    """Many-to-many: Product categories."""
    __tablename__ = 'product_categories'
    
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    is_primary = Column(Boolean, default=False)  # Primary category
    
    # Relationships
    product = relationship('Product', back_populates='categories')
    category = relationship('Category', back_populates='products')


class ProductReview(Base):
    """Product reviews and ratings."""
    __tablename__ = 'product_reviews'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    external_review_id = Column(String(128))
    
    # Review content
    author = Column(String(200))
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(500))
    content = Column(Text)
    
    # Metadata
    verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    review_date = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    product = relationship('Product', back_populates='reviews')


class ProductMerge(Base):
    """Track when duplicate products are merged."""
    __tablename__ = 'product_merges'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    duplicate_fingerprint = Column(String(64), nullable=False)
    similarity_score = Column(Float)
    merged_at = Column(DateTime, default=datetime.utcnow)
    merge_metadata = Column(Text)  # JSON: source info
    
    # Relationship
    product = relationship('Product', back_populates='merges')


class ProductRun(Base):
    """Track product scraping runs."""
    __tablename__ = 'product_runs'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('product_sources.id'), nullable=False)
    run_key = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    raw_count = Column(Integer, default=0)
    new_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    price_changes = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Relationship
    source = relationship('ProductSource', back_populates='runs')


# Create all tables
# Note: Commented out for testing - use createDb.py to create tables
# Base.metadata.create_all(engine)
