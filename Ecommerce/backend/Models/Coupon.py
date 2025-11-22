from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from database import Base


class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    discount_type = Column(String(20), nullable=False)  # "percentage", "fixed", "free_shipping"
    discount_value_cents = Column(Integer, nullable=False)  # Amount in cents or percentage (e.g., 1500 = $15 or 15%)
    
    min_purchase_amount_cents = Column(Integer, nullable=True)
    max_discount_amount_cents = Column(Integer, nullable=True)
    
    # Applicability constraints
    applicable_product_ids = Column(JSON, nullable=True)  # Array of product IDs
    applicable_category_ids = Column(JSON, nullable=True)  # Array of category IDs
    
    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # Global usage limit (NULL for unlimited)
    usage_count = Column(Integer, default=0, nullable=False)
    per_user_limit = Column(Integer, nullable=True)  # Per-user usage limit
    
    is_active = Column(Boolean, default=True, nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Coupon(id={self.id}, code={self.code}, discount_value_cents={self.discount_value_cents})>"
