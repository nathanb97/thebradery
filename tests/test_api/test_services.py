"""Unit tests for API services."""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from api.services import (
    search_products, 
    get_product_by_id, 
    get_vendors, 
    get_product_types, 
    get_catalog_stats
)
from api.schemas import SearchRequest
from database.models import Product


class TestSearchProducts:
    """Test product search service."""

    def test_search_products_no_filters(self):
        """Test search without filters."""
        # Mock database session and query
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        # Chain mock methods
        mock_query.count.return_value = 10
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest()
        
        products, page_info = search_products(mock_db, search_request)
        
        assert products == []
        assert page_info.total_count == 10
        assert page_info.limit == 20
        assert page_info.offset == 0
        assert not page_info.has_previous
        mock_db.query.assert_called_once_with(Product)

    def test_search_products_with_text_query(self):
        """Test search with text query."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        # Mock filter chain
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest(query="test")
        
        products, page_info = search_products(mock_db, search_request)
        
        assert page_info.total_count == 5
        # Verify filter was called for text search
        mock_query.filter.assert_called()

    def test_search_products_with_vendor_filter(self):
        """Test search with vendor filter."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest(vendors=["CHANEL", "DIOR"])
        
        products, page_info = search_products(mock_db, search_request)
        
        assert page_info.total_count == 3
        mock_query.filter.assert_called()

    def test_search_products_with_price_filters(self):
        """Test search with price range filters."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 8
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest(price_min=50.0, price_max=200.0)
        
        products, page_info = search_products(mock_db, search_request)
        
        assert page_info.total_count == 8
        # Should be called twice for min and max price
        assert mock_query.filter.call_count == 2

    def test_search_products_with_description_filter_true(self):
        """Test search filtering for products with descriptions."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 6
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest(has_description=True)
        
        products, page_info = search_products(mock_db, search_request)
        
        assert page_info.total_count == 6
        mock_query.filter.assert_called()

    def test_search_products_with_description_filter_false(self):
        """Test search filtering for products without descriptions."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 4
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest(has_description=False)
        
        products, page_info = search_products(mock_db, search_request)
        
        assert page_info.total_count == 4
        mock_query.filter.assert_called()

    def test_search_products_with_sorting_desc(self):
        """Test search with descending sort order."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        mock_query.count.return_value = 5
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest(sort_by="vendor", sort_order="desc")
        
        products, page_info = search_products(mock_db, search_request)
        
        mock_query.order_by.assert_called_once()

    def test_search_products_pagination(self):
        """Test search pagination calculation."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        mock_query.count.return_value = 100
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        search_request = SearchRequest(limit=10, offset=20)
        
        products, page_info = search_products(mock_db, search_request)
        
        assert page_info.total_count == 100
        assert page_info.limit == 10
        assert page_info.offset == 20
        assert page_info.has_previous is True  # offset > 0
        assert page_info.has_next is True  # 20 + 10 < 100
        
        mock_query.offset.assert_called_once_with(20)
        mock_query.limit.assert_called_once_with(10)


class TestGetProductById:
    """Test get product by ID service."""

    def test_get_product_by_id_found(self):
        """Test successful product retrieval."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_product = Mock(spec=Product)
        mock_product.product_id = 123
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_product
        
        result = get_product_by_id(mock_db, 123)
        
        assert result == mock_product
        mock_db.query.assert_called_once_with(Product)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_product_by_id_not_found(self):
        """Test product not found."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        result = get_product_by_id(mock_db, 999)
        
        assert result is None


class TestGetVendors:
    """Test get vendors service."""

    def test_get_vendors_success(self):
        """Test successful vendors retrieval."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        
        # Mock query chain
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [("CHANEL", 150), ("DIOR", 120)]
        
        result = get_vendors(mock_db)
        
        expected = [
            {"vendor": "CHANEL", "product_count": 150},
            {"vendor": "DIOR", "product_count": 120}
        ]
        assert result == expected
        mock_db.query.assert_called_once()

    def test_get_vendors_empty(self):
        """Test vendors retrieval when no vendors exist."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        result = get_vendors(mock_db)
        
        assert result == []


class TestGetProductTypes:
    """Test get product types service."""

    def test_get_product_types_success(self):
        """Test successful product types retrieval."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [("Dress", 200), ("T-Shirt", 150)]
        
        result = get_product_types(mock_db)
        
        expected = [
            {"product_type": "Dress", "product_count": 200},
            {"product_type": "T-Shirt", "product_count": 150}
        ]
        assert result == expected

    def test_get_product_types_empty(self):
        """Test product types retrieval when no types exist."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        result = get_product_types(mock_db)
        
        assert result == []


class TestGetCatalogStats:
    """Test catalog statistics service."""

    def test_get_catalog_stats_success(self):
        """Test successful catalog statistics retrieval."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        
        # Mock different query chains for different statistics
        mock_db.query.return_value = mock_query
        
        # Mock count calls
        count_calls = [1000, 50, 20, 750]  # total, vendors, types, with_description
        mock_query.count.side_effect = count_calls
        
        # Mock distinct calls
        mock_query.distinct.return_value = mock_query
        
        # Mock filter calls
        mock_query.filter.return_value = mock_query
        
        # Mock scalar calls for price statistics
        scalar_calls = [45.99, 9.99, 299.99]  # avg, min, max
        mock_query.scalar.side_effect = scalar_calls
        
        result = get_catalog_stats(mock_db)
        
        expected = {
            "total_products": 1000,
            "total_vendors": 50,
            "total_types": 20,
            "with_description": 750,
            "without_description": 250,  # 1000 - 750
            "avg_price": 45.99,
            "min_price": 9.99,
            "max_price": 299.99
        }
        
        assert result == expected

    def test_get_catalog_stats_with_none_values(self):
        """Test catalog statistics when some values are None."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        
        mock_db.query.return_value = mock_query
        
        # Mock count calls
        count_calls = [100, 5, 3, 60]
        mock_query.count.side_effect = count_calls
        
        mock_query.distinct.return_value = mock_query
        mock_query.filter.return_value = mock_query
        
        # Mock scalar calls returning None (no products with prices)
        scalar_calls = [None, None, None]
        mock_query.scalar.side_effect = scalar_calls
        
        result = get_catalog_stats(mock_db)
        
        assert result["avg_price"] == 0
        assert result["min_price"] == 0
        assert result["max_price"] == 0
        assert result["total_products"] == 100
        assert result["without_description"] == 40  # 100 - 60