"""SQLAlchemy models for the products database."""

from sqlalchemy import Column, Integer, String, Float, Text, Index, JSON, BigInteger, Boolean
from . import Base


class Product(Base):
    """Product model matching the CSV structure."""
    
    __tablename__ = "products"
    
    # Primary key
    product_id = Column(BigInteger, primary_key=True, index=True)
    
    # Product information
    product_type = Column(String(255), index=True)
    product_tags = Column(Text)
    images_array = Column(JSON)  # JSON array for image URLs
    vendor = Column(String(255), index=True)
    inventory_quantity = Column(Integer)
    gross_amount_exc_tax_product = Column(Float, index=True)
    description = Column(Text)
    is_generated_description = Column(Boolean, default=False, nullable=False)
    
    # Add composite indexes for common search patterns
    __table_args__ = (
        Index('idx_vendor_type', 'vendor', 'product_type'),
        Index('idx_type_price', 'product_type', 'gross_amount_exc_tax_product'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.product_id}, vendor='{self.vendor}', type='{self.product_type}')>"