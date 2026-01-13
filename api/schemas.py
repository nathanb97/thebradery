"""Pydantic schemas for API serialization.

This module defines all Pydantic models used for API request/response
serialization, validation, and documentation generation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema.
    
    Contains all core product fields shared between different
    product representations in the API.
    
    Attributes:
        product_id (int): Unique identifier for the product.
        product_type (Optional[str]): Category or type of the product.
        product_tags (Optional[str]): Comma-separated tags associated with the product.
        images_array (Optional[List[str]]): List of product image URLs.
        vendor (Optional[str]): Name of the product vendor/brand.
        inventory_quantity (Optional[int]): Available stock quantity.
        gross_amount_exc_tax_product (Optional[float]): Product price excluding tax.
        description (Optional[str]): Product description text.
        is_generated_description (Optional[bool]): Whether description was auto-generated.
    """

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
    """Product response schema.
    
    Extends ProductBase for API responses, with configuration
    to handle SQLAlchemy model serialization.
    """

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Search request schema.
    
    Defines all possible search and filter parameters for the
    product search endpoint, including validation rules.
    
    Attributes:
        query (Optional[str]): Text search term for product matching.
        vendors (Optional[List[str]]): List of vendor names to filter by.
        product_types (Optional[List[str]]): List of product types to filter by.
        price_min (Optional[float]): Minimum price threshold.
        price_max (Optional[float]): Maximum price threshold.
        has_description (Optional[bool]): Filter for products with/without descriptions.
        sort_by (str): Field name to sort results by. Default: 'product_id'.
        sort_order (str): Sort direction, 'asc' or 'desc'. Default: 'asc'.
        limit (int): Number of results per page (1-100). Default: 20.
        offset (int): Number of results to skip for pagination. Default: 0.
    """

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
    """Pagination information.
    
    Contains metadata about paginated search results to help
    clients navigate through large result sets.
    
    Attributes:
        total_count (int): Total number of results matching the search.
        limit (int): Maximum number of results per page.
        offset (int): Number of results skipped from the beginning.
        has_next (bool): Whether there are more results after this page.
        has_previous (bool): Whether there are results before this page.
    """

    total_count: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class SearchResponse(BaseModel):
    """Search response schema.
    
    Combines the actual search results with pagination metadata
    for complete search response information.
    
    Attributes:
        products (List[ProductResponse]): List of products matching the search.
        page_info (PageInfo): Pagination and result count information.
    """

    products: List[ProductResponse]
    page_info: PageInfo


class VendorResponse(BaseModel):
    """Vendor response schema.
    
    Represents vendor information with product count for
    metadata endpoints.
    
    Attributes:
        vendor (str): Name of the vendor/brand.
        product_count (int): Number of products from this vendor.
    """

    vendor: str
    product_count: int


class ProductTypeResponse(BaseModel):
    """Product type response schema.
    
    Represents product type information with count for
    metadata endpoints.
    
    Attributes:
        product_type (str): Name of the product type/category.
        product_count (int): Number of products of this type.
    """

    product_type: str
    product_count: int
