from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class ShipmentItem(Base):
    __tablename__ = "shipment_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)  # Quantity being shipped
    
    # Relationships
    shipment = relationship("Shipment", back_populates="items")
    order_item = relationship("OrderItem", back_populates="shipment_items")
    
    def __repr__(self):
        return f"<ShipmentItem(id={self.id}, shipment_id={self.shipment_id}, quantity={self.quantity})>"
