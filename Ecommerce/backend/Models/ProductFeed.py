from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class FeedStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class ProductFeed(Base):
    """
    Bulk import/export facility for catalog data.
    Tracks the processing of CSV/Excel files containing product data.
    
    Design principles:
    - Validate input rows before processing
    - Support idempotent imports by SKU/external_id
    - Provide row-level error reporting for admin review
    - Run as asynchronous Jobs
    - Support transactional batches and rollback options
    """
    __tablename__ = "product_feeds"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # File reference
    blob_id = Column(Integer, ForeignKey("blobs.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)  # Snapshot of original filename
    
    # Feed metadata
    feed_type = Column(String(50), nullable=False)  # "import" or "export"
    format = Column(String(20), nullable=False)  # "csv", "xlsx", "json"
    
    # Processing status
    status = Column(SQLEnum(FeedStatus), default=FeedStatus.PENDING, nullable=False, index=True)
    
    # Statistics
    total_rows = Column(Integer, default=0, nullable=False)
    processed_rows = Column(Integer, default=0, nullable=False)
    success_rows = Column(Integer, default=0, nullable=False)
    error_rows = Column(Integer, default=0, nullable=False)
    
    # Error tracking
    errors = Column(JSON, nullable=True)  # Array of {row: int, error: string, data: dict}
    
    # Job reference (for async processing)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    
    # Actor tracking
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    blob = relationship("Blob")
    job = relationship("Job")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<ProductFeed(id={self.id}, filename={self.filename}, status={self.status}, {self.success_rows}/{self.total_rows} success)>"
    
    # Note: The actual processing logic (start() method) will be in ProductFeedService
    # which coordinates with JobService for async execution
