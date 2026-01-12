"""Unit tests for database_utils.py."""

import pytest
import pandas as pd
import json
from unittest.mock import Mock, patch, MagicMock
from front_streamlit.database_utils import to_list, load_csv_to_database, get_database_stats, check_database_connection


class TestToList:
    """Test the to_list function."""

    def test_to_list_with_none(self):
        """Test to_list with None value."""
        assert to_list(None) is None
        assert to_list(pd.NA) is None

    def test_to_list_with_existing_list(self):
        """Test to_list with already a list."""
        test_list = ["url1", "url2"]
        assert to_list(test_list) == test_list

    def test_to_list_with_json_string(self):
        """Test to_list with valid JSON string."""
        json_string = '["url1", "url2", "url3"]'
        expected = ["url1", "url2", "url3"]
        assert to_list(json_string) == expected

    def test_to_list_with_python_string(self):
        """Test to_list with Python-like string."""
        python_string = "['url1', 'url2']"
        expected = ["url1", "url2"]
        assert to_list(python_string) == expected

    def test_to_list_with_bracket_format(self):
        """Test to_list with bracket format without quotes."""
        bracket_string = "[url1, url2, url3]"
        expected = ["url1", "url2", "url3"]
        assert to_list(bracket_string) == expected

    def test_to_list_with_empty_brackets(self):
        """Test to_list with empty brackets."""
        assert to_list("[]") == []
        assert to_list("[ ]") == []

    def test_to_list_with_single_url(self):
        """Test to_list with single URL."""
        single_url = "https://example.com/image.jpg"
        expected = ["https://example.com/image.jpg"]
        assert to_list(single_url) == expected


class TestLoadCsvToDatabase:
    """Test the load_csv_to_database function."""

    @patch('front_streamlit.database_utils.pd.read_csv')
    @patch('front_streamlit.database_utils.create_tables')
    @patch('front_streamlit.database_utils.get_db')
    def test_load_csv_success(self, mock_get_db, mock_create_tables, mock_read_csv, sample_dataframe):
        """Test successful CSV loading."""
        # Setup mocks
        mock_read_csv.return_value = sample_dataframe
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Execute
        success, message = load_csv_to_database("test.csv")
        
        # Assertions
        assert success is True
        assert "Successfully loaded" in message
        mock_create_tables.assert_called_once()
        mock_db.query.assert_called()
        mock_db.bulk_save_objects.assert_called()
        mock_db.commit.assert_called()

    @patch('front_streamlit.database_utils.pd.read_csv')
    def test_load_csv_file_error(self, mock_read_csv):
        """Test CSV loading with file error."""
        mock_read_csv.side_effect = FileNotFoundError("File not found")
        
        success, message = load_csv_to_database("nonexistent.csv")
        
        assert success is False
        assert "CSV loading error" in message

    @patch('front_streamlit.database_utils.pd.read_csv')
    @patch('front_streamlit.database_utils.create_tables')
    @patch('front_streamlit.database_utils.get_db')
    def test_load_csv_database_error(self, mock_get_db, mock_create_tables, mock_read_csv, sample_dataframe):
        """Test CSV loading with database error."""
        mock_read_csv.return_value = sample_dataframe
        mock_db = Mock()
        mock_db.bulk_save_objects.side_effect = Exception("Database error")
        mock_get_db.return_value = iter([mock_db])
        
        success, message = load_csv_to_database("test.csv")
        
        assert success is False
        assert "Database error" in message
        mock_db.rollback.assert_called_once()


class TestGetDatabaseStats:
    """Test the get_database_stats function."""

    @patch('front_streamlit.database_utils.get_db')
    def test_get_database_stats_success(self, mock_get_db):
        """Test successful database stats retrieval."""
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Setup query results
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.count.return_value = 100
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        
        # Different counts for different queries
        mock_query.count.side_effect = [100, 10, 5, 80, 20]  # total, vendors, types, with_desc, generated
        
        stats = get_database_stats()
        
        expected = {
            "total_products": 100,
            "vendors_count": 10,
            "types_count": 5,
            "with_description": 80,
            "without_description": 20,
            "generated_descriptions": 20
        }
        assert stats == expected

    @patch('front_streamlit.database_utils.get_db')
    def test_get_database_stats_error(self, mock_get_db):
        """Test database stats with connection error."""
        mock_get_db.side_effect = Exception("Connection failed")
        
        stats = get_database_stats()
        
        expected = {
            "total_products": 0,
            "vendors_count": 0,
            "types_count": 0,
            "with_description": 0,
            "without_description": 0,
            "generated_descriptions": 0
        }
        assert stats == expected


class TestCheckDatabaseConnection:
    """Test the check_database_connection function."""

    @patch('front_streamlit.database_utils.get_db')
    def test_check_database_connection_success(self, mock_get_db):
        """Test successful database connection check."""
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        mock_db.execute.return_value = None
        
        result = check_database_connection()
        
        assert result is True
        mock_db.execute.assert_called_once()

    @patch('front_streamlit.database_utils.get_db')
    def test_check_database_connection_failure(self, mock_get_db):
        """Test failed database connection check."""
        mock_get_db.side_effect = Exception("Connection failed")
        
        result = check_database_connection()
        
        assert result is False