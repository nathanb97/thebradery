"""Pydantic schemas for API serialization."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema."""

    product_id: int
    product_type: Optional[str] = None
    product_tags: Optional[str] = None
    images_array: Optional[List[str]] = None
    vendor: Optional[str] = None
    inventory_quantity: Optional[int] = None
    gross_amount_exc_tax_product: Optional[float] = None
    description: Optional[str] = None
    is_generated_description: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response schema."""

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Search request schema."""

    query: Optional[str] = Field(None, description="Search term for description, vendor, or product type")
    vendors: Optional[List[str]] = Field(None, description="Filter by specific vendors")
    product_types: Optional[List[str]] = Field(None, description="Filter by specific product types")
    price_min: Optional[float] = Field(None, description="Minimum price filter")
    price_max: Optional[float] = Field(None, description="Maximum price filter")
    has_description: Optional[bool] = Field(None, description="Filter products with/without descriptions")
    sort_by: str = Field(
        "product_id", description="Sort field: product_id, vendor, product_type, gross_amount_exc_tax_product"
    )
    sort_order: str = Field("asc", description="Sort order: asc or desc")
    limit: int = Field(20, ge=1, le=100, description="Number of results to return (1-100)")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class PageInfo(BaseModel):
    """Pagination information."""

    total_count: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class SearchResponse(BaseModel):
    """Search response schema."""

    products: List[ProductResponse]
    page_info: PageInfo


class VendorResponse(BaseModel):
    """Vendor response schema."""

    vendor: str
    product_count: int


class ProductTypeResponse(BaseModel):
    """Product type response schema."""

    product_type: str
    product_count: int
