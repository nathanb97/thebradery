"""Search services for product catalog."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from database.models import Product
from .schemas import SearchRequest, PageInfo, EnrichedProductsRequest
import json
from datetime import datetime


def search_products(db: Session, search_request: SearchRequest) -> Tuple[List[Product], PageInfo]:
    """Search products with filters and pagination.

    Args:
        db: Database session
        search_request: Search criteria

    Returns:
        Tuple of (products list, page info)
    """
    # Start with base query
    query = db.query(Product)

    # Text search across multiple fields
    if search_request.query:
        search_term = f"%{search_request.query}%"
        query = query.filter(
            or_(
                Product.description.ilike(search_term),
                Product.vendor.ilike(search_term),
                Product.product_type.ilike(search_term),
                Product.product_tags.ilike(search_term),
            )
        )

    # Vendor filter
    if search_request.vendors:
        query = query.filter(Product.vendor.in_(search_request.vendors))

    # Product type filter
    if search_request.product_types:
        query = query.filter(Product.product_type.in_(search_request.product_types))

    # Price range filter
    if search_request.price_min is not None:
        query = query.filter(Product.gross_amount_exc_tax_product >= search_request.price_min)

    if search_request.price_max is not None:
        query = query.filter(Product.gross_amount_exc_tax_product <= search_request.price_max)

    # Description filter
    if search_request.has_description is not None:
        if search_request.has_description:
            query = query.filter(
                and_(Product.description.isnot(None), Product.description != "", func.length(Product.description) > 10)
            )
        else:
            query = query.filter(
                or_(Product.description.is_(None), Product.description == "", func.length(Product.description) <= 10)
            )

    # Get total count before pagination
    total_count = query.count()

    # Sorting
    sort_column = getattr(Product, search_request.sort_by, Product.product_id)
    if search_request.sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Pagination
    query = query.offset(search_request.offset).limit(search_request.limit)

    # Execute query
    products = query.all()

    # Create page info
    page_info = PageInfo(
        total_count=total_count,
        limit=search_request.limit,
        offset=search_request.offset,
        has_next=(search_request.offset + search_request.limit) < total_count,
        has_previous=search_request.offset > 0,
    )

    return products, page_info


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """Get a product by its ID.

    Args:
        db: Database session
        product_id: Product ID

    Returns:
        Product or None if not found
    """
    return db.query(Product).filter(Product.product_id == product_id).first()


def get_vendors(db: Session) -> List[dict]:
    """Get all vendors with product count.

    Args:
        db: Database session

    Returns:
        List of vendor dictionaries
    """
    vendors = (
        db.query(Product.vendor, func.count(Product.product_id).label("product_count"))
        .filter(Product.vendor.isnot(None))
        .group_by(Product.vendor)
        .order_by(Product.vendor)
        .all()
    )

    return [{"vendor": vendor, "product_count": count} for vendor, count in vendors]


def get_product_types(db: Session) -> List[dict]:
    """Get all product types with product count.

    Args:
        db: Database session

    Returns:
        List of product type dictionaries
    """
    types = (
        db.query(Product.product_type, func.count(Product.product_id).label("product_count"))
        .filter(Product.product_type.isnot(None))
        .group_by(Product.product_type)
        .order_by(Product.product_type)
        .all()
    )

    return [{"product_type": product_type, "product_count": count} for product_type, count in types]


def get_catalog_stats(db: Session) -> dict:
    """Get catalog statistics.

    Args:
        db: Database session

    Returns:
        Dictionary with catalog statistics
    """
    total_products = db.query(Product).count()
    total_vendors = db.query(Product.vendor).distinct().count()
    total_types = db.query(Product.product_type).distinct().count()

    with_description = (
        db.query(Product)
        .filter(and_(Product.description.isnot(None), Product.description != "", func.length(Product.description) > 10))
        .count()
    )

    avg_price = db.query(func.avg(Product.gross_amount_exc_tax_product)).scalar() or 0
    min_price = db.query(func.min(Product.gross_amount_exc_tax_product)).scalar() or 0
    max_price = db.query(func.max(Product.gross_amount_exc_tax_product)).scalar() or 0

    return {
        "total_products": total_products,
        "total_vendors": total_vendors,
        "total_types": total_types,
        "with_description": with_description,
        "without_description": total_products - with_description,
        "avg_price": round(float(avg_price), 2),
        "min_price": float(min_price),
        "max_price": float(max_price),
    }


def parse_images_array(images_data) -> List[str]:
    """Parse images_array field into a list of image URLs.
    
    Args:
        images_data: Images data (can be list, string, or None)
        
    Returns:
        List of image URLs
    """
    # If already a list (SQLAlchemy auto-deserialized JSON)
    if isinstance(images_data, list):
        return [url for url in images_data if url and isinstance(url, str)]
    
    # If it's a string, parse as JSON
    if isinstance(images_data, str):
        if not images_data or images_data.strip() == "":
            return []
        
        try:
            # Try to parse as JSON array
            parsed = json.loads(images_data)
            if isinstance(parsed, list):
                return [url for url in parsed if url and isinstance(url, str)]
            elif isinstance(parsed, str):
                return [parsed]
            else:
                return []
        except (json.JSONDecodeError, TypeError):
            # If not valid JSON, treat as single URL or comma-separated
            if "," in images_data:
                return [url.strip() for url in images_data.split(",") if url.strip()]
            else:
                return [images_data.strip()]
    
    # If None or other type
    return []
from datetime import datetime
from typing import List, Tuple

from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.orm import Session

def get_enriched_products(
    db: Session,
    request: EnrichedProductsRequest
) -> Tuple[List[dict], PageInfo, dict]:
    """Get enriched products with photos and comparison data."""

    print(f"DEBUG: Starting get_enriched_products with request: {request}")

    try:
        # Base query: products with AI-generated descriptions
        query = db.query(Product).filter(Product.is_generated_description.is_(True))
        print("DEBUG: Base query created")

        # Apply filters
        print(f"DEBUG: request.has_photos = {request.has_photos}")
        if request.has_photos is not None:
            if request.has_photos:
                print("DEBUG: Filtering for products WITH photos")
                query = query.filter(
                    func.json_array_length(Product.images_array) > 0
                )
                print("DEBUG: Photos filter applied")
            else:
                print("DEBUG: Filtering for products WITHOUT photos")
                query = query.filter(
                    or_(
                        Product.images_array.is_(None),
                        func.json_array_length(Product.images_array) == 0
                    )
                )
                print("DEBUG: No photos filter applied")

        if request.vendors:
            query = query.filter(Product.vendor.in_(request.vendors))

        if request.product_types:
            query = query.filter(Product.product_type.in_(request.product_types))

        # Total count before pagination
        print("DEBUG: About to count query")
        total_count = query.count()
        print(f"DEBUG: Total count: {total_count}")

        # Sorting (fallback to product_id)
        print(f"DEBUG: About to sort by {request.sort_by}")
        sort_column = getattr(Product, request.sort_by, Product.product_id)
        print(f"DEBUG: Sort column: {sort_column}")

        if (request.sort_order or "desc").lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        print("DEBUG: About to execute query.all()")
        products = query.all()
        print(f"DEBUG: Retrieved {len(products)} products")

        # Process products
        print("DEBUG: About to process products")
        enriched_products: List[dict] = []

        for i, product in enumerate(products):
            print(f"DEBUG: Processing product {i+1}/{len(products)}: {product.product_id}")

            images_parsed = parse_images_array(product.images_array)
            has_photos = len(images_parsed) > 0
            print(f"DEBUG: Images parsed: {len(images_parsed)} images, has_photos={has_photos}")

            enriched_products.append(
                {
                    # Base product fields
                    "product_id": product.product_id,
                    "product_type": product.product_type,
                    "product_tags": product.product_tags,
                    "images_array": product.images_array,
                    "vendor": product.vendor,
                    "inventory_quantity": product.inventory_quantity,
                    "gross_amount_exc_tax_product": product.gross_amount_exc_tax_product,
                    "description": product.description,
                    "is_generated_description": product.is_generated_description,

                    # Enriched fields
                    "original_description": None,  # Would need to be stored separately
                    "enriched_description": product.description if product.is_generated_description else None,
                    "images_parsed": images_parsed,
                    "enrichment_date": None,       # Would need enrichment timestamp field
                    "enrichment_model": "ollama",  # Could be stored in a separate field
                    "quality_score": None,         # Would need quality assessment
                    "has_photos": has_photos,
                }
            )
            print(f"DEBUG: Product {product.product_id} processed successfully")

        # Page info
        page_info = PageInfo(
            total_count=total_count,
            limit=request.limit,
            offset=request.offset,
            has_next=(request.offset + request.limit) < total_count,
            has_previous=request.offset > 0,
        )

        # Enrichment statistics
        total_enriched = db.query(Product).filter(
            Product.is_generated_description.is_(True)
        ).count()

        total_products = db.query(Product).count()

        enriched_with_photos = db.query(Product).filter(
            and_(
                Product.is_generated_description.is_(True),
                func.json_array_length(Product.images_array) > 0
            )
        ).count()

        enrichment_stats = {
            "total_enriched": total_enriched,
            "total_products": total_products,
            "enrichment_percentage": round((total_enriched / total_products * 100), 2)
            if total_products > 0
            else 0,
            "with_photos": enriched_with_photos,
            "without_photos": total_enriched - enriched_with_photos,
            "avg_quality_score": None,          # Future implementation
            "models_used": ["ollama"],          # Future: track different models used
            "last_enrichment": datetime.now().isoformat(),  # Future: track actual dates
        }

        return enriched_products, page_info, enrichment_stats

    except Exception as e:
        print(f"DEBUG: ERROR in get_enriched_products: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
