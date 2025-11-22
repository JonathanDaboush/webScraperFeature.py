"""
SQLAlchemy Models for E-commerce Platform
All models are imported here for easy access and to ensure proper relationship resolution
"""

from .User import User, UserRole
from .Address import Address
from .Session import Session
from .APIKey import APIKey
from .Category import Category
from .Product import Product
from .ProductImage import ProductImage
from .ProductVariant import ProductVariant
from .Cart import Cart
from .CartItem import CartItem
from .Order import Order, OrderStatus
from .OrderItem import OrderItem
from .Payment import Payment, PaymentStatus, PaymentMethod
from .Shipment import Shipment, ShipmentStatus
from .ShipmentItem import ShipmentItem
from .Refund import Refund, RefundStatus
from .Return import Return, ReturnStatus
from .Review import Review
from .Wishlist import Wishlist
from .WishlistItem import WishlistItem
from .InventoryTransaction import InventoryTransaction, TransactionType
from .Coupon import Coupon
from .Blob import Blob
from .AuditLog import AuditLog
from .Job import Job, JobStatus
from .ProductFeed import ProductFeed, FeedStatus

__all__ = [
    # User related
    "User",
    "UserRole",
    "Address",
    "Session",
    "APIKey",
    
    # Product related
    "Category",
    "Product",
    "ProductImage",
    "ProductVariant",
    "Review",
    
    # Cart related
    "Cart",
    "CartItem",
    "Wishlist",
    "WishlistItem",
    
    # Order related
    "Order",
    "OrderStatus",
    "OrderItem",
    "Payment",
    "PaymentStatus",
    "PaymentMethod",
    "Shipment",
    "ShipmentStatus",
    "ShipmentItem",
    "Refund",
    "RefundStatus",
    "Return",
    "ReturnStatus",
    
    # Inventory related
    "InventoryTransaction",
    "TransactionType",
    
    # Promotion related
    "Coupon",
    
    # Infrastructure
    "Blob",
    "AuditLog",
    "Job",
    "JobStatus",
    "ProductFeed",
    "FeedStatus",
]
