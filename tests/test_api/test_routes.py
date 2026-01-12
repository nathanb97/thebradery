"""Unit tests for API routes."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from api.main import app
from api.schemas import SearchRequest, PageInfo, ProductResponse
from database.models import Product


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_success(self):
        """Test successful health check."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.execute.return_value = True
            mock_get_db.return_value = mock_db
            
            response = client.get("/health")
            
            assert response.status_code == 200
            assert response.json() == {"status": "healthy", "database": "connected"}
            mock_db.execute.assert_called_once_with("SELECT 1")

    def test_health_check_database_failure(self):
        """Test health check with database failure."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.execute.side_effect = Exception("Connection failed")
            mock_get_db.return_value = mock_db
            
            response = client.get("/health")
            
            assert response.status_code == 503
            assert "Database connection failed" in response.json()["detail"]


class TestStatsEndpoint:
    """Test statistics endpoint."""

    def test_get_stats_success(self):
        """Test successful stats retrieval."""
        client = TestClient(app)
        mock_stats = {
            "total_products": 1000,
            "total_vendors": 50,
            "total_types": 20,
            "with_description": 750,
            "without_description": 250,
            "avg_price": 45.99,
            "min_price": 9.99,
            "max_price": 299.99
        }
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_catalog_stats') as mock_stats_service:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_stats_service.return_value = mock_stats
            
            response = client.get("/api/v1/stats")
            
            assert response.status_code == 200
            assert response.json() == mock_stats
            mock_stats_service.assert_called_once_with(mock_db)

    def test_get_stats_error(self):
        """Test stats endpoint error handling."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_catalog_stats') as mock_stats_service:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_stats_service.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/stats")
            
            assert response.status_code == 500
            assert "Error retrieving stats" in response.json()["detail"]


class TestProductSearchEndpoint:
    """Test product search endpoint."""

    def test_search_products_basic_query(self):
        """Test basic product search."""
        client = TestClient(app)
        
        # Mock products
        mock_product = Product(
            product_id=123,
            product_type="T-Shirt",
            vendor="TestBrand",
            description="Test description",
            gross_amount_exc_tax_product=29.99
        )
        
        mock_page_info = PageInfo(
            total_count=1,
            limit=20,
            offset=0,
            has_next=False,
            has_previous=False
        )
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.search_products') as mock_search:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_search.return_value = ([mock_product], mock_page_info)
            
            response = client.get("/api/v1/products/search?query=test")
            
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
            assert "page_info" in data
            assert data["page_info"]["total_count"] == 1

    def test_search_products_with_filters(self):
        """Test product search with multiple filters."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.search_products') as mock_search:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_search.return_value = ([], PageInfo(
                total_count=0, limit=20, offset=0, has_next=False, has_previous=False
            ))
            
            response = client.get(
                "/api/v1/products/search?"
                "vendors=CHANEL&vendors=DIOR&"
                "product_types=Dress&"
                "price_min=100&price_max=500&"
                "has_description=true&"
                "sort_by=vendor&sort_order=desc&"
                "limit=10&offset=20"
            )
            
            assert response.status_code == 200
            
            # Verify search was called with correct parameters
            call_args = mock_search.call_args[0]
            search_request = call_args[1]
            assert search_request.vendors == ["CHANEL", "DIOR"]
            assert search_request.product_types == ["Dress"]
            assert search_request.price_min == 100
            assert search_request.price_max == 500
            assert search_request.has_description is True
            assert search_request.sort_by == "vendor"
            assert search_request.sort_order == "desc"
            assert search_request.limit == 10
            assert search_request.offset == 20

    def test_search_products_validation_error(self):
        """Test search with invalid parameters."""
        client = TestClient(app)
        
        response = client.get("/api/v1/products/search?limit=150")  # Exceeds max limit
        
        assert response.status_code == 422

    def test_search_products_service_error(self):
        """Test search endpoint error handling."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.search_products') as mock_search:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_search.side_effect = Exception("Search failed")
            
            response = client.get("/api/v1/products/search")
            
            assert response.status_code == 500
            assert "Search error" in response.json()["detail"]


class TestProductDetailEndpoint:
    """Test product detail endpoint."""

    def test_get_product_success(self):
        """Test successful product retrieval."""
        client = TestClient(app)
        
        mock_product = Product(
            product_id=123,
            product_type="T-Shirt",
            vendor="TestBrand",
            description="Test description",
            gross_amount_exc_tax_product=29.99
        )
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_product_by_id') as mock_get_product:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_get_product.return_value = mock_product
            
            response = client.get("/api/v1/products/123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["product_id"] == 123
            assert data["vendor"] == "TestBrand"
            mock_get_product.assert_called_once_with(mock_db, 123)

    def test_get_product_not_found(self):
        """Test product not found."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_product_by_id') as mock_get_product:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_get_product.return_value = None
            
            response = client.get("/api/v1/products/999")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Product not found"

    def test_get_product_service_error(self):
        """Test product endpoint error handling."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_product_by_id') as mock_get_product:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_get_product.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/products/123")
            
            assert response.status_code == 500
            assert "Error retrieving product" in response.json()["detail"]


class TestVendorsEndpoint:
    """Test vendors endpoint."""

    def test_get_vendors_success(self):
        """Test successful vendors retrieval."""
        client = TestClient(app)
        
        mock_vendors = [
            {"vendor": "CHANEL", "product_count": 150},
            {"vendor": "DIOR", "product_count": 120}
        ]
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_vendors') as mock_get_vendors:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_get_vendors.return_value = mock_vendors
            
            response = client.get("/api/v1/vendors")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["vendor"] == "CHANEL"
            assert data[0]["product_count"] == 150
            mock_get_vendors.assert_called_once_with(mock_db)

    def test_get_vendors_error(self):
        """Test vendors endpoint error handling."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_vendors') as mock_get_vendors:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_get_vendors.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/vendors")
            
            assert response.status_code == 500
            assert "Error retrieving vendors" in response.json()["detail"]


class TestProductTypesEndpoint:
    """Test product types endpoint."""

    def test_get_product_types_success(self):
        """Test successful product types retrieval."""
        client = TestClient(app)
        
        mock_types = [
            {"product_type": "Dress", "product_count": 200},
            {"product_type": "T-Shirt", "product_count": 150}
        ]
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_product_types') as mock_get_types:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_get_types.return_value = mock_types
            
            response = client.get("/api/v1/product-types")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["product_type"] == "Dress"
            assert data[0]["product_count"] == 200
            mock_get_types.assert_called_once_with(mock_db)

    def test_get_product_types_error(self):
        """Test product types endpoint error handling."""
        client = TestClient(app)
        
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.services.get_product_types') as mock_get_types:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_get_types.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/product-types")
            
            assert response.status_code == 500
            assert "Error retrieving product types" in response.json()["detail"]


class TestSearchExamplesEndpoint:
    """Test search examples endpoint."""

    def test_get_search_examples(self):
        """Test search examples endpoint."""
        client = TestClient(app)
        
        response = client.get("/api/v1/examples/search")
        
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert len(data["examples"]) > 0
        
        # Check that examples have required structure
        for example in data["examples"]:
            assert "description" in example
            assert "url" in example
            assert example["url"].startswith("/api/v1/products/search")