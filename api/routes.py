"""API routes for product search endpoints.

This module contains all FastAPI routes for the product search API,
including endpoints for searching products, retrieving metadata,
and health checks.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .dependencies import get_db
from .schemas import (ProductResponse, SearchRequest, SearchResponse, VendorResponse, ProductTypeResponse,
                     EnrichedProductsRequest, EnrichedProductsResponse, EnrichedProductResponse)
from .services import (search_products, get_product_by_id, get_vendors, get_product_types, 
                      get_catalog_stats, get_enriched_products)

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint.

    Verifies that the API and database are operational.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: Health status and database connection status.

    Raises:
        HTTPException: 503 if database connection fails.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@router.get("/api/v1/stats", tags=["Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """Get catalog statistics.

    Retrieves overall statistics about the product catalog,
    including counts of products, vendors, and types.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: Catalog statistics including product counts and metadata.

    Raises:
        HTTPException: 500 if error occurs while retrieving statistics.
    """
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
    """Search products with filters and pagination.

    Performs a comprehensive search across the product catalog with
    support for text search, filtering by vendors and product types,
    price range filtering, and pagination.

    Args:
        query (Optional[str]): Text search term to match against product names.
        vendors (Optional[List[str]]): List of vendor names to filter by.
        product_types (Optional[List[str]]): List of product types to filter by.
        price_min (Optional[float]): Minimum price filter.
        price_max (Optional[float]): Maximum price filter.
        has_description (Optional[bool]): Filter for products with/without descriptions.
        sort_by (str): Field to sort results by. Default: 'product_id'.
        sort_order (str): Sort order, either 'asc' or 'desc'. Default: 'asc'.
        limit (int): Number of results per page (1-100). Default: 20.
        offset (int): Number of results to skip for pagination. Default: 0.
        db (Session): Database session dependency.

    Returns:
        SearchResponse: Search results with products and pagination info.

    Raises:
        HTTPException: 500 if search operation fails.
    """
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


@router.get("/api/v1/products/bonus", response_model=EnrichedProductsResponse, tags=["Products"])
async def get_enriched_products_bonus(
    has_photos: Optional[bool] = Query(None, description="Filter products with/without photos"),
    min_quality_score: Optional[float] = Query(None, ge=0, le=1, description="Minimum quality score"),
    vendors: Optional[List[str]] = Query(None, description="Filter by vendor names"),
    product_types: Optional[List[str]] = Query(None, description="Filter by product types"),
    enrichment_model: Optional[str] = Query(None, description="Filter by AI model used"),
    sort_by: str = Query("product_id", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Results to skip"),
    db: Session = Depends(get_db),
):
    """Get enriched products with photos and quality comparison.

    Retrieves products that have been enriched with AI-generated descriptions,
    including their parsed image URLs for photo comparison with descriptions.
    This endpoint is perfect for quality assessment and visual validation.

    Args:
        has_photos (Optional[bool]): Filter for products with/without photos.
        min_quality_score (Optional[float]): Minimum quality score filter (0-1).
        vendors (Optional[List[str]]): List of vendor names to filter by.
        product_types (Optional[List[str]]): List of product types to filter by.
        enrichment_model (Optional[str]): Filter by AI model used for enrichment.
        sort_by (str): Field to sort results by. Default: 'product_id'.
        sort_order (str): Sort order, either 'asc' or 'desc'. Default: 'desc'.
        limit (int): Number of results per page (1-100). Default: 20.
        offset (int): Number of results to skip for pagination. Default: 0.
        db (Session): Database session dependency.

    Returns:
        EnrichedProductsResponse: Enriched products with photos, pagination, and stats.

    Raises:
        HTTPException: 500 if error occurs while retrieving enriched products.
    """
    try:
        # Create request object
        request = EnrichedProductsRequest(
            has_photos=has_photos,
            min_quality_score=min_quality_score,
            vendors=vendors,
            product_types=product_types,
            enrichment_model=enrichment_model,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

        # Execute search
        products, page_info, enrichment_stats = get_enriched_products(db, request)

        # Convert to response format
        product_responses = [EnrichedProductResponse.model_validate(product) for product in products]

        return EnrichedProductsResponse(
            products=product_responses,
            page_info=page_info,
            enrichment_stats=enrichment_stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enriched products: {str(e)}")


@router.get("/api/v1/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID.

    Retrieves detailed information for a specific product.

    Args:
        product_id (int): Unique identifier of the product to retrieve.
        db (Session): Database session dependency.

    Returns:
        ProductResponse: Detailed product information.

    Raises:
        HTTPException: 404 if product not found, 500 for other errors.
    """
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
    """Get all vendors with product counts.

    Retrieves a list of all vendors in the catalog along with
    the number of products each vendor has.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[VendorResponse]: List of vendors with their product counts.

    Raises:
        HTTPException: 500 if error occurs while retrieving vendors.
    """
    try:
        vendors = get_vendors(db)
        return [VendorResponse(**vendor) for vendor in vendors]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving vendors: {str(e)}")


@router.get("/api/v1/product-types", response_model=List[ProductTypeResponse], tags=["Metadata"])
async def get_product_types_endpoint(db: Session = Depends(get_db)):
    """Get all product types with product counts.

    Retrieves a list of all product types in the catalog along with
    the number of products for each type.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[ProductTypeResponse]: List of product types with their product counts.

    Raises:
        HTTPException: 500 if error occurs while retrieving product types.
    """
    try:
        types = get_product_types(db)
        return [ProductTypeResponse(**product_type) for product_type in types]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product types: {str(e)}")


@router.get("/api/v1/products/enriched", response_model=EnrichedProductsResponse, tags=["Products"])
async def get_enriched_products_endpoint(
    has_photos: Optional[bool] = Query(None, description="Filter products with/without photos"),
    min_quality_score: Optional[float] = Query(None, ge=0, le=1, description="Minimum quality score"),
    vendors: Optional[List[str]] = Query(None, description="Filter by vendor names"),
    product_types: Optional[List[str]] = Query(None, description="Filter by product types"),
    enrichment_model: Optional[str] = Query(None, description="Filter by AI model used"),
    sort_by: str = Query("product_id", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Results to skip"),
    db: Session = Depends(get_db),
):
    """Get enriched products with photos and quality comparison.

    Retrieves products that have been enriched with AI-generated descriptions,
    including their parsed image URLs for photo comparison with descriptions.
    This endpoint is perfect for quality assessment and visual validation.

    Args:
        has_photos (Optional[bool]): Filter for products with/without photos.
        min_quality_score (Optional[float]): Minimum quality score filter (0-1).
        vendors (Optional[List[str]]): List of vendor names to filter by.
        product_types (Optional[List[str]]): List of product types to filter by.
        enrichment_model (Optional[str]): Filter by AI model used for enrichment.
        sort_by (str): Field to sort results by. Default: 'product_id'.
        sort_order (str): Sort order, either 'asc' or 'desc'. Default: 'desc'.
        limit (int): Number of results per page (1-100). Default: 20.
        offset (int): Number of results to skip for pagination. Default: 0.
        db (Session): Database session dependency.

    Returns:
        EnrichedProductsResponse: Enriched products with photos, pagination, and stats.

    Raises:
        HTTPException: 500 if error occurs while retrieving enriched products.
    """
    try:
        # Create request object
        request = EnrichedProductsRequest(
            has_photos=has_photos,
            min_quality_score=min_quality_score,
            vendors=vendors,
            product_types=product_types,
            enrichment_model=enrichment_model,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

        # Execute search
        products, page_info, enrichment_stats = get_enriched_products(db, request)

        # Convert to response format
        product_responses = [EnrichedProductResponse.model_validate(product) for product in products]

        return EnrichedProductsResponse(
            products=product_responses,
            page_info=page_info,
            enrichment_stats=enrichment_stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enriched products: {str(e)}")


@router.get("/api/v1/examples/search", tags=["Examples"])
async def search_examples():
    """Examples of search queries.

    Provides example API calls demonstrating various search features
    and filtering options available in the product search endpoint.

    Returns:
        dict: Dictionary containing example search queries with descriptions.
    """
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
                "url": "/api/v1/products/search?query=luxury&vendors=CHANEL&price_min=200&"
                       "has_description=true&sort_by=gross_amount_exc_tax_product&sort_order=desc&limit=10",
            },
            {
                "description": "Enriched products with photos",
                "url": "/api/v1/products/enriched?has_photos=true&limit=10",
            },
            {
                "description": "High quality enriched products",
                "url": "/api/v1/products/enriched?min_quality_score=0.8&vendors=CHANEL",
            },
        ]
    }
