from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"  # Stock decreased due to sale
    RESTOCK = "restock"  # Stock increased
    RETURN = "return"  # Stock increased due to return
    ADJUSTMENT = "adjustment"  # Manual adjustment


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    quantity_change = Column(Integer, nullable=False)  # Positive for increase, negative for decrease
    quantity_after = Column(Integer, nullable=False)  # Stock quantity after this transaction
    reference_id = Column(String(100), nullable=True)  # Order ID, PO number, etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="inventory_transactions")
    
    def __repr__(self):
        return f"<InventoryTransaction(id={self.id}, product_id={self.product_id}, type={self.transaction_type})>"
