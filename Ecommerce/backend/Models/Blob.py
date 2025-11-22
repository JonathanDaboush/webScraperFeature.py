from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from database import Base


class Blob(Base):
    """
    Provider-agnostic pointer to binary assets (images, shipping labels, documents).
    Stores storage keys and metadata (checksum) for file integrity.
    """
    __tablename__ = "blobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Storage reference - where the file lives (e.g., "s3://bucket/path/to/file.jpg")
    storage_key = Column(String(500), nullable=False, unique=True, index=True)
    
    # File metadata
    filename = Column(String(255), nullable=False)  # Original filename
    content_type = Column(String(100), nullable=False)  # MIME type (image/jpeg, application/pdf)
    size_bytes = Column(BigInteger, nullable=False)  # File size in bytes
    checksum = Column(String(64), nullable=False)  # SHA-256 hash for integrity verification
    
    # Storage provider (s3, gcs, local, etc.)
    storage_provider = Column(String(50), default="s3", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Blob(id={self.id}, filename={self.filename}, size={self.size_bytes})>"
    
    # Note: Methods like get_signed_url() and open_stream() will be implemented
    # in a BlobService class, not here. Models should be data-focused.
