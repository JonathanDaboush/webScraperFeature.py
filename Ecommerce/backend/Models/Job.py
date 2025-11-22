from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import enum


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    """
    Durable descriptor for background work: email sends, shipping label generation,
    feed processing, reconciliation, etc.
    
    Design principles:
    - Jobs are single-purpose and retryable
    - Use idempotency_key to prevent duplicate execution
    - Support exponential backoff for retries
    - Long-running jobs should implement checkpointing
    """
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Job identification
    job_type = Column(String(100), nullable=False, index=True)  # "send_email", "generate_label", "import_products"
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)  # Prevents duplicate jobs
    
    # Job payload and result
    payload = Column(JSON, nullable=False)  # Input data for the job
    result = Column(JSON, nullable=True)  # Output data after completion
    
    # Status tracking
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED, nullable=False, index=True)
    
    # Worker tracking
    worker_id = Column(String(100), nullable=True)  # Which worker is processing this
    
    # Retry logic
    attempts = Column(Integer, default=0, nullable=False)  # How many times we've tried
    max_attempts = Column(Integer, default=3, nullable=False)  # Maximum retry attempts
    
    # Error tracking
    error = Column(JSON, nullable=True)  # Error details if job failed
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Next retry time (for exponential backoff)
    retry_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status}, attempts={self.attempts})>"
    
    # Note: Methods like enqueue(), start(), complete(), fail() will be in JobService
    # These methods need to interact with a job queue (Redis, Celery, etc.)
