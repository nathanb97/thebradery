"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Product


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        'product_id': 123456,
        'product_type': 'T-Shirt',
        'product_tags': 'cotton, casual, summer',
        'images_array': '["https://example.com/image1.jpg", "https://example.com/image2.jpg"]',
        'vendor': 'TestBrand',
        'inventory_quantity': 100,
        'gross_amount_exc_tax_product': 29.99,
        'description': 'A comfortable cotton t-shirt',
        'is_generated_description': False
    }


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing."""
    return pd.DataFrame([
        {
            'product_id': 123456,
            'product_type': 'T-Shirt',
            'product_tags': 'cotton, casual',
            'images_array': '["https://example.com/image1.jpg"]',
            'vendor': 'TestBrand',
            'inventory_quantity': 100,
            'gross_amount_exc_tax_product': 29.99,
            'description': 'Good t-shirt',
            'is_generated_description': False
        },
        {
            'product_id': 123457,
            'product_type': 'Jeans',
            'product_tags': 'denim, casual',
            'images_array': '["https://example.com/jean1.jpg"]',
            'vendor': 'TestBrand',
            'inventory_quantity': 50,
            'gross_amount_exc_tax_product': 79.99,
            'description': None,  # Missing description
            'is_generated_description': False
        }
    ])


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    session = Mock()
    return session


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "response": "Découvrez ce magnifique t-shirt en coton de la marque TestBrand. "
                   "Confortable et élégant, parfait pour un style décontracté. "
                   "Matière 100% coton pour un confort optimal."
    }


@pytest.fixture
def mock_requests():
    """Mock requests for testing API calls."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield mock_get, mock_post