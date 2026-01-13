"""Unit tests for ai_enrichment.py."""

import pytest
import pandas as pd
import requests
from unittest.mock import Mock, patch, MagicMock
from front_streamlit.ai_enrichment import ProductEnricher


class TestProductEnricher:
    """Test the ProductEnricher class."""

    def test_init_default_config(self):
        """Test ProductEnricher initialization with default config."""
        with patch('front_streamlit.ai_enrichment.config.OLLAMA_BASE_URL', 'http://localhost:11434'), \
             patch('front_streamlit.ai_enrichment.config.OLLAMA_MODEL', 'mistral'):
            enricher = ProductEnricher()
            assert enricher.base_url == 'http://localhost:11434'
            assert enricher.model == 'mistral'

    def test_init_custom_config(self):
        """Test ProductEnricher initialization with custom config."""
        custom_url = 'http://custom:11434'
        enricher = ProductEnricher(base_url=custom_url)
        assert enricher.base_url == custom_url

    @patch('requests.get')
    def test_is_ollama_available_success(self, mock_get):
        """Test successful Ollama availability check."""
        mock_get.return_value.status_code = 200
        enricher = ProductEnricher()
        
        assert enricher.is_ollama_available() is True
        mock_get.assert_called_with(f"{enricher.base_url}/api/tags", timeout=5)

    @patch('requests.get')
    def test_is_ollama_available_failure(self, mock_get):
        """Test failed Ollama availability check."""
        mock_get.side_effect = requests.RequestException("Connection failed")
        enricher = ProductEnricher()
        
        assert enricher.is_ollama_available() is False

    @patch('requests.get')
    def test_get_available_models_success(self, mock_get):
        """Test successful model retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "mistral:7b"},
                {"name": "llama2:7b"}
            ]
        }
        mock_get.return_value = mock_response
        enricher = ProductEnricher()
        
        models = enricher.get_available_models()
        
        assert models == ["mistral:7b", "llama2:7b"]

    @patch('requests.get')
    def test_get_available_models_failure(self, mock_get):
        """Test failed model retrieval."""
        mock_get.side_effect = requests.RequestException("Connection failed")
        enricher = ProductEnricher()
        
        models = enricher.get_available_models()
        
        assert models == []

    def test_create_enrichment_prompt(self, sample_product_data):
        """Test enrichment prompt creation."""
        enricher = ProductEnricher()
        prompt = enricher._create_enrichment_prompt(sample_product_data)
        
        assert "TestBrand" in prompt
        assert "T-Shirt" in prompt
        assert "29.99" in prompt
        assert "cotton, casual, summer" in prompt
        assert "Description:" in prompt

    def test_create_improvement_prompt(self):
        """Test improvement prompt creation."""
        enricher = ProductEnricher()
        description = "T-shirt avec référence X0P123 très bien"
        prompt = enricher._create_improvement_prompt(description)
        
        assert description in prompt
        assert "X0P" in prompt
        assert "Description améliorée:" in prompt

    @patch('front_streamlit.ai_enrichment.ProductEnricher.is_ollama_available')
    @patch('requests.post')
    def test_call_ollama_api_success(self, mock_post, mock_is_available, mock_ollama_response):
        """Test successful Ollama API call."""
        mock_is_available.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ollama_response
        mock_post.return_value = mock_response
        
        enricher = ProductEnricher()
        result = enricher._call_ollama_api("Test prompt")
        
        expected = mock_ollama_response["response"]
        assert result == expected

    @patch('front_streamlit.ai_enrichment.ProductEnricher.is_ollama_available')
    def test_call_ollama_api_not_available(self, mock_is_available):
        """Test Ollama API call when service not available."""
        mock_is_available.return_value = False
        
        enricher = ProductEnricher()
        result = enricher._call_ollama_api("Test prompt")
        
        assert result is None

    @patch('front_streamlit.ai_enrichment.ProductEnricher.is_ollama_available')
    @patch('requests.post')
    def test_call_ollama_api_short_response(self, mock_post, mock_is_available):
        """Test Ollama API call with too short response."""
        mock_is_available.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Short"}  # Too short
        mock_post.return_value = mock_response
        
        enricher = ProductEnricher()
        result = enricher._call_ollama_api("Test prompt")
        
        assert result is None

    @patch('front_streamlit.ai_enrichment.ProductEnricher._call_ollama_api')
    def test_enrich_single_description(self, mock_call_api, sample_product_data):
        """Test single product description enrichment."""
        mock_call_api.return_value = "Enriched description"
        
        enricher = ProductEnricher()
        result = enricher.enrich_single_description(sample_product_data)
        
        assert result == "Enriched description"
        mock_call_api.assert_called_once()

    @patch('front_streamlit.ai_enrichment.ProductEnricher._call_ollama_api')
    def test_improve_description_success(self, mock_call_api):
        """Test successful description improvement."""
        mock_call_api.return_value = "Improved description"
        
        enricher = ProductEnricher()
        result = enricher.improve_description("Original description")
        
        assert result == "Improved description"

    def test_improve_description_empty(self):
        """Test description improvement with empty input."""
        enricher = ProductEnricher()
        result = enricher.improve_description("")
        
        assert result is None

    def test_improve_description_too_short(self):
        """Test description improvement with too short input."""
        enricher = ProductEnricher()
        result = enricher.improve_description("Short")
        
        assert result is None

    def test_identify_missing_descriptions(self, sample_dataframe):
        """Test identification of missing descriptions."""
        enricher = ProductEnricher()
        missing = enricher.identify_missing_descriptions(sample_dataframe)
        
        # Should identify the row with None description
        assert len(missing) == 1
        assert missing.iloc[0]['product_id'] == 123457

    def test_identify_missing_descriptions_empty_string(self):
        """Test identification of empty string descriptions."""
        df = pd.DataFrame([{
            'product_id': 123,
            'description': '',  # Empty string
            'vendor': 'Test'
        }])
        
        enricher = ProductEnricher()
        missing = enricher.identify_missing_descriptions(df)
        
        assert len(missing) == 1

    def test_identify_missing_descriptions_very_short(self):
        """Test identification of very short descriptions."""
        df = pd.DataFrame([{
            'product_id': 123,
            'description': 'Short',  # Too short (< 10 chars)
            'vendor': 'Test'
        }])
        
        enricher = ProductEnricher()
        missing = enricher.identify_missing_descriptions(df)
        
        assert len(missing) == 1

    @patch('front_streamlit.ai_enrichment.st')
    @patch('front_streamlit.ai_enrichment.ProductEnricher.enrich_single_description')
    @patch('front_streamlit.ai_enrichment.ProductEnricher.improve_description')
    @patch('front_streamlit.ai_enrichment.time.sleep')
    def test_enrich_missing_descriptions_success(self, mock_sleep, mock_improve, 
                                                mock_enrich, mock_st, sample_dataframe):
        """Test successful enrichment of missing descriptions."""
        # Setup mocks
        mock_enrich.return_value = "Generated description"
        mock_improve.return_value = "Improved description"
        mock_st.progress.return_value = Mock()
        mock_st.empty.return_value = Mock()
        mock_st.container.return_value = Mock()
        mock_st.info = Mock()
        mock_st.success = Mock()
        mock_st.expander.return_value.__enter__ = Mock()
        mock_st.expander.return_value.__exit__ = Mock()
        
        enricher = ProductEnricher()
        result_df = enricher.enrich_missing_descriptions(sample_dataframe)
        
        # Should have enriched the missing description
        enriched_row = result_df[result_df['product_id'] == 123457].iloc[0]
        assert enriched_row['description'] == "Improved description"
        assert enriched_row['is_generated_description'] is True

    def test_get_enrichment_stats(self, sample_dataframe):
        """Test enrichment statistics calculation."""
        enricher = ProductEnricher()
        
        # Create enriched version
        enriched_df = sample_dataframe.copy()
        enriched_df.loc[enriched_df['product_id'] == 123457, 'description'] = "New description"
        
        stats = enricher.get_enrichment_stats(sample_dataframe, enriched_df)
        
        assert stats['total_products'] == 2
        assert stats['originally_missing'] == 1
        assert stats['still_missing'] == 0
        assert stats['enriched_count'] == 1
        assert stats['enrichment_rate'] == 100.0