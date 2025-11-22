from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base


class AuditLog(Base):
    """
    Append-only security and operational trail for auditing, compliance, and debugging.
    Captures who did what, when, and to which resource.
    
    CRITICAL: Never delete or modify audit logs. They're immutable for compliance.
    """
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Who performed the action
    actor_id = Column(Integer, nullable=True, index=True)  # User ID (NULL for system actions)
    actor_type = Column(String(50), nullable=False)  # "user", "api_key", "system"
    actor_email = Column(String(255), nullable=True)  # Snapshot of email at time of action
    
    # What action was performed
    action = Column(String(100), nullable=False, index=True)  # "order.created", "product.updated", "user.deleted"
    
    # What resource was affected
    target_type = Column(String(50), nullable=False, index=True)  # "Order", "Product", "User"
    target_id = Column(String(100), nullable=False, index=True)  # ID of the affected resource
    
    # Additional context
    metadata = Column(JSON, nullable=True)  # Structured data: before/after values, IP address, user agent
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Timestamp (immutable)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, actor_id={self.actor_id}, target={self.target_type}:{self.target_id})>"
    
    # Note: to_dict() method will be in a service/serializer
