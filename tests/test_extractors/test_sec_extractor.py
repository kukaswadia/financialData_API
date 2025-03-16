import pytest
from unittest.mock import patch, MagicMock
from src.extractors.sec_extractor import SECExtractor

class TestSECExtractor:
    
    @patch('src.extractors.sec_extractor.QueryApi')
    def test_get_company_filings(self, mock_query_api, mock_sec_response):
        # Create a mock instance of QueryApi
        mock_query_instance = MagicMock()
        mock_query_instance.get_filings.return_value = mock_sec_response
        mock_query_api.return_value = mock_query_instance
        
        # Initialize the extractor
        extractor = SECExtractor(api_key="test_key")
        
        # Call the method to test
        filings = extractor.get_company_filings(ticker="TEST", limit=2)
        
        # Assert the results
        assert len(filings) == 2
        assert filings[0]["accessionNumber"] == "0001234567-21-000001"
        assert filings[0]["formType"] == "10-K"
        
        # Verify the API was called with correct parameters
        mock_query_instance.get_filings.assert_called_once()
        call_args = mock_query_instance.get_filings.call_args[1]
        assert "ticker:TEST" in call_args["query"]
        assert call_args["limit"] == 2
    
    @patch('src.extractors.sec_extractor.RenderApi')
    def test_extract_financial_data(self, mock_render_api, mock_financial_data):
        # Create a mock instance of RenderApi
        mock_render_instance = MagicMock()
        mock_render_instance.xbrl_to_json.return_value = {
            "IncomeStatement": mock_financial_data["income_statement"],
            "BalanceSheet": mock_financial_data["balance_sheet"],
            "CashFlow": mock_financial_data["cash_flow"],
            "DocumentAndEntityInformation": mock_financial_data["metadata"]
        }
        mock_render_api.return_value = mock_render_instance
        
        # Initialize the extractor
        extractor = SECExtractor(api_key="test_key")
        
        # Call the method to test
        data = extractor.extract_financial_data("0001234567-21-000001")
        
        # Assert the results
        assert "income_statement" in data
        assert "balance_sheet" in data
        assert "cash_flow" in data
        assert "metadata" in data
        assert data["income_statement"]["Revenues"] == "1000000"
        
        # Verify the API was called with correct parameters
        mock_render_instance.xbrl_to_json.assert_called_once_with("0001234567-21-000001")