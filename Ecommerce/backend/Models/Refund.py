from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"


class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    amount_cents = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(SQLEnum(RefundStatus), default=RefundStatus.PENDING, nullable=False)
    admin_notes = Column(Text, nullable=True)
    
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="refunds")
    payment = relationship("Payment")
    
    def __repr__(self):
        return f"<Refund(id={self.id}, order_id={self.order_id}, status={self.status}, amount_cents={self.amount_cents})>"
