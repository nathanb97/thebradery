"""API routes for product search endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .dependencies import get_db
from database.models import Product
from .schemas import ProductResponse, SearchRequest, SearchResponse, VendorResponse, ProductTypeResponse
from .services import search_products, get_product_by_id, get_vendors, get_product_types, get_catalog_stats

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@router.get("/api/v1/stats", tags=["Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """Get catalog statistics."""
    try:
        stats = get_catalog_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.get("/api/v1/products/search", response_model=SearchResponse, tags=["Products"])
async def search_products_endpoint(
    query: Optional[str] = Query(None, description="Search term"),
    vendors: Optional[List[str]] = Query(None, description="Filter by vendors"),
    product_types: Optional[List[str]] = Query(None, description="Filter by product types"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    has_description: Optional[bool] = Query(None, description="Filter by description presence"),
    sort_by: str = Query("product_id", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Results to skip"),
    db: Session = Depends(get_db),
):
    """Search products with filters and pagination."""
    try:
        # Create search request
        search_request = SearchRequest(
            query=query,
            vendors=vendors,
            product_types=product_types,
            price_min=price_min,
            price_max=price_max,
            has_description=has_description,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

        # Execute search
        products, page_info = search_products(db, search_request)

        # Convert to response format
        product_responses = [ProductResponse.model_validate(product) for product in products]

        return SearchResponse(products=product_responses, page_info=page_info)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/api/v1/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID."""
    try:
        product = get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return ProductResponse.model_validate(product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")


@router.get("/api/v1/vendors", response_model=List[VendorResponse], tags=["Metadata"])
async def get_vendors_endpoint(db: Session = Depends(get_db)):
    """Get all vendors with product counts."""
    try:
        vendors = get_vendors(db)
        return [VendorResponse(**vendor) for vendor in vendors]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving vendors: {str(e)}")


@router.get("/api/v1/product-types", response_model=List[ProductTypeResponse], tags=["Metadata"])
async def get_product_types_endpoint(db: Session = Depends(get_db)):
    """Get all product types with product counts."""
    try:
        types = get_product_types(db)
        return [ProductTypeResponse(**product_type) for product_type in types]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product types: {str(e)}")


@router.get("/api/v1/examples/search", tags=["Examples"])
async def search_examples():
    """Examples of search queries."""
    return {
        "examples": [
            {"description": "Search for 'dress' products", "url": "/api/v1/products/search?query=dress"},
            {"description": "Filter by specific vendor", "url": "/api/v1/products/search?vendors=CHANEL&vendors=DIOR"},
            {"description": "Price range filter", "url": "/api/v1/products/search?price_min=100&price_max=500"},
            {"description": "Products with descriptions only", "url": "/api/v1/products/search?has_description=true"},
            {
                "description": "Sorted by price descending",
                "url": "/api/v1/products/search?sort_by=gross_amount_exc_tax_product&sort_order=desc",
            },
            {"description": "Pagination", "url": "/api/v1/products/search?limit=50&offset=100"},
            {
                "description": "Complex search",
                "url": "/api/v1/products/search?query=luxury&vendors=CHANEL&price_min=200&has_description=true&sort_by=gross_amount_exc_tax_product&sort_order=desc&limit=10",
            },
        ]
    }
