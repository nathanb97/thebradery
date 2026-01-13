"""Search services for product catalog."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from database.models import Product
from .schemas import SearchRequest, PageInfo


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
