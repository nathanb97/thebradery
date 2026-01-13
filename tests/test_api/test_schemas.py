"""Unit tests for API schemas validation."""

import pytest
from pydantic import ValidationError
from api.schemas import (
    ProductBase,
    ProductResponse,
    SearchRequest,
    PageInfo,
    SearchResponse,
    VendorResponse,
    ProductTypeResponse
)


class TestProductBase:
    """Test ProductBase schema validation."""

    def test_product_base_valid(self):
        """Test valid product base data."""
        data = {
            "product_id": 123456,
            "product_type": "T-Shirt",
            "product_tags": "cotton, casual, summer",
            "images_array": ["https://example.com/image1.jpg"],
            "vendor": "TestBrand",
            "inventory_quantity": 100,
            "gross_amount_exc_tax_product": 29.99,
            "description": "A comfortable cotton t-shirt",
            "is_generated_description": False
        }
        
        product = ProductBase(**data)
        
        assert product.product_id == 123456
        assert product.product_type == "T-Shirt"
        assert product.vendor == "TestBrand"
        assert product.gross_amount_exc_tax_product == 29.99

    def test_product_base_minimal(self):
        """Test product base with minimal required data."""
        data = {
            "product_id": 123456
        }
        
        product = ProductBase(**data)
        
        assert product.product_id == 123456
        assert product.product_type is None
        assert product.vendor is None
        assert product.description is None

    def test_product_base_invalid_product_id(self):
        """Test invalid product ID type."""
        data = {
            "product_id": "invalid"  # Should be int
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProductBase(**data)
        
        assert "product_id" in str(exc_info.value)

    def test_product_base_negative_quantity(self):
        """Test negative inventory quantity (should be valid as it's Optional[int])."""
        data = {
            "product_id": 123456,
            "inventory_quantity": -5
        }
        
        product = ProductBase(**data)
        assert product.inventory_quantity == -5

    def test_product_base_invalid_price_type(self):
        """Test invalid price type."""
        data = {
            "product_id": 123456,
            "gross_amount_exc_tax_product": "not_a_number"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProductBase(**data)
        
        assert "gross_amount_exc_tax_product" in str(exc_info.value)


class TestProductResponse:
    """Test ProductResponse schema validation."""

    def test_product_response_inherits_from_base(self):
        """Test that ProductResponse inherits ProductBase functionality."""
        data = {
            "product_id": 123456,
            "vendor": "TestBrand",
            "description": "Test description"
        }
        
        product = ProductResponse(**data)
        
        assert product.product_id == 123456
        assert product.vendor == "TestBrand"
        assert product.description == "Test description"

    def test_product_response_config(self):
        """Test that ProductResponse has correct config."""
        # Config should allow attribute access for SQLAlchemy models
        assert hasattr(ProductResponse.model_config, 'from_attributes')
        assert ProductResponse.model_config['from_attributes'] is True


class TestSearchRequest:
    """Test SearchRequest schema validation."""

    def test_search_request_defaults(self):
        """Test search request with default values."""
        search = SearchRequest()
        
        assert search.query is None
        assert search.vendors is None
        assert search.product_types is None
        assert search.price_min is None
        assert search.price_max is None
        assert search.has_description is None
        assert search.sort_by == "product_id"
        assert search.sort_order == "asc"
        assert search.limit == 20
        assert search.offset == 0

    def test_search_request_all_fields(self):
        """Test search request with all fields specified."""
        data = {
            "query": "test query",
            "vendors": ["CHANEL", "DIOR"],
            "product_types": ["Dress", "T-Shirt"],
            "price_min": 50.0,
            "price_max": 200.0,
            "has_description": True,
            "sort_by": "vendor",
            "sort_order": "desc",
            "limit": 50,
            "offset": 100
        }
        
        search = SearchRequest(**data)
        
        assert search.query == "test query"
        assert search.vendors == ["CHANEL", "DIOR"]
        assert search.product_types == ["Dress", "T-Shirt"]
        assert search.price_min == 50.0
        assert search.price_max == 200.0
        assert search.has_description is True
        assert search.sort_by == "vendor"
        assert search.sort_order == "desc"
        assert search.limit == 50
        assert search.offset == 100

    def test_search_request_limit_validation(self):
        """Test limit field validation."""
        # Valid limits
        SearchRequest(limit=1)  # Minimum
        SearchRequest(limit=100)  # Maximum
        SearchRequest(limit=50)  # Middle
        
        # Invalid limits should raise ValidationError
        with pytest.raises(ValidationError):
            SearchRequest(limit=0)  # Below minimum
        
        with pytest.raises(ValidationError):
            SearchRequest(limit=101)  # Above maximum

    def test_search_request_offset_validation(self):
        """Test offset field validation."""
        # Valid offsets
        SearchRequest(offset=0)  # Minimum
        SearchRequest(offset=1000)  # Large value
        
        # Invalid offset should raise ValidationError
        with pytest.raises(ValidationError):
            SearchRequest(offset=-1)  # Negative

    def test_search_request_invalid_price_range(self):
        """Test price validation (business logic handled elsewhere)."""
        # Schema should accept any valid float values
        search = SearchRequest(price_min=100.0, price_max=50.0)  # Min > Max
        
        # Schema validates types but not business logic
        assert search.price_min == 100.0
        assert search.price_max == 50.0


class TestPageInfo:
    """Test PageInfo schema validation."""

    def test_page_info_valid(self):
        """Test valid page info data."""
        data = {
            "total_count": 100,
            "limit": 20,
            "offset": 40,
            "has_next": True,
            "has_previous": True
        }
        
        page_info = PageInfo(**data)
        
        assert page_info.total_count == 100
        assert page_info.limit == 20
        assert page_info.offset == 40
        assert page_info.has_next is True
        assert page_info.has_previous is True

    def test_page_info_missing_fields(self):
        """Test page info with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            PageInfo(total_count=100)  # Missing other required fields
        
        error_str = str(exc_info.value)
        assert "limit" in error_str
        assert "offset" in error_str
        assert "has_next" in error_str
        assert "has_previous" in error_str

    def test_page_info_invalid_types(self):
        """Test page info with invalid field types."""
        with pytest.raises(ValidationError):
            PageInfo(
                total_count="not_int",
                limit=20,
                offset=0,
                has_next=True,
                has_previous=False
            )


class TestSearchResponse:
    """Test SearchResponse schema validation."""

    def test_search_response_valid(self):
        """Test valid search response."""
        products_data = [
            {
                "product_id": 123456,
                "vendor": "TestBrand"
            }
        ]
        products = [ProductResponse(**product) for product in products_data]
        
        page_info = PageInfo(
            total_count=1,
            limit=20,
            offset=0,
            has_next=False,
            has_previous=False
        )
        
        response = SearchResponse(
            products=products,
            page_info=page_info
        )
        
        assert len(response.products) == 1
        assert response.products[0].product_id == 123456
        assert response.page_info.total_count == 1

    def test_search_response_empty_products(self):
        """Test search response with empty products list."""
        page_info = PageInfo(
            total_count=0,
            limit=20,
            offset=0,
            has_next=False,
            has_previous=False
        )
        
        response = SearchResponse(
            products=[],
            page_info=page_info
        )
        
        assert len(response.products) == 0
        assert response.page_info.total_count == 0

    def test_search_response_missing_fields(self):
        """Test search response with missing required fields."""
        with pytest.raises(ValidationError):
            SearchResponse(products=[])  # Missing page_info


class TestVendorResponse:
    """Test VendorResponse schema validation."""

    def test_vendor_response_valid(self):
        """Test valid vendor response."""
        data = {
            "vendor": "CHANEL",
            "product_count": 150
        }
        
        vendor = VendorResponse(**data)
        
        assert vendor.vendor == "CHANEL"
        assert vendor.product_count == 150

    def test_vendor_response_missing_fields(self):
        """Test vendor response with missing fields."""
        with pytest.raises(ValidationError):
            VendorResponse(vendor="CHANEL")  # Missing product_count

    def test_vendor_response_invalid_count(self):
        """Test vendor response with invalid product count."""
        with pytest.raises(ValidationError):
            VendorResponse(
                vendor="CHANEL",
                product_count="not_int"
            )


class TestProductTypeResponse:
    """Test ProductTypeResponse schema validation."""

    def test_product_type_response_valid(self):
        """Test valid product type response."""
        data = {
            "product_type": "Dress",
            "product_count": 200
        }
        
        product_type = ProductTypeResponse(**data)
        
        assert product_type.product_type == "Dress"
        assert product_type.product_count == 200

    def test_product_type_response_missing_fields(self):
        """Test product type response with missing fields."""
        with pytest.raises(ValidationError):
            ProductTypeResponse(product_type="Dress")  # Missing product_count

    def test_product_type_response_invalid_count(self):
        """Test product type response with invalid count."""
        with pytest.raises(ValidationError):
            ProductTypeResponse(
                product_type="Dress",
                product_count="not_int"
            )

    def test_product_type_response_zero_count(self):
        """Test product type response with zero count."""
        data = {
            "product_type": "Dress",
            "product_count": 0
        }
        
        product_type = ProductTypeResponse(**data)
        
        assert product_type.product_count == 0


class TestSchemaIntegration:
    """Test schema integration scenarios."""

    def test_product_response_to_search_response(self):
        """Test converting ProductResponse to SearchResponse."""
        # Create multiple products
        products_data = [
            {"product_id": 1, "vendor": "Brand A"},
            {"product_id": 2, "vendor": "Brand B"},
        ]
        
        products = [ProductResponse(**data) for data in products_data]
        
        page_info = PageInfo(
            total_count=2,
            limit=20,
            offset=0,
            has_next=False,
            has_previous=False
        )
        
        search_response = SearchResponse(
            products=products,
            page_info=page_info
        )
        
        assert len(search_response.products) == 2
        assert search_response.products[0].vendor == "Brand A"
        assert search_response.products[1].vendor == "Brand B"

    def test_schema_serialization(self):
        """Test schema serialization to dict."""
        search_request = SearchRequest(
            query="test",
            vendors=["CHANEL"],
            limit=10
        )
        
        # Should be able to convert to dict
        data = search_request.model_dump()
        
        assert data["query"] == "test"
        assert data["vendors"] == ["CHANEL"]
        assert data["limit"] == 10
        assert data["sort_by"] == "product_id"  # Default value