from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., "Size: Large, Color: Red"
    
    # Pricing in cents
    price_cents = Column(Integer, nullable=False)
    compare_at_price_cents = Column(Integer, nullable=True)
    cost_cents = Column(Integer, nullable=True)
    
    # Inventory management
    stock_quantity = Column(Integer, default=0, nullable=False)
    inventory_management = Column(String(50), nullable=True)  # "shopify", "manual", null
    inventory_policy = Column(String(20), default="deny", nullable=False)  # "deny" or "continue"
    track_stock = Column(Boolean, default=True, nullable=False)
    
    # Variant attributes stored as JSON-like strings or separate columns
    # For simplicity, using string columns
    option1_name = Column(String(50), nullable=True)  # e.g., "Size"
    option1_value = Column(String(50), nullable=True)  # e.g., "Large"
    option2_name = Column(String(50), nullable=True)  # e.g., "Color"
    option2_value = Column(String(50), nullable=True)  # e.g., "Red"
    option3_name = Column(String(50), nullable=True)
    option3_value = Column(String(50), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    
    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, name={self.name})>"
