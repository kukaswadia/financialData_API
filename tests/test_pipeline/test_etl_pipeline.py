from unittest.mock import patch, MagicMock
import pytest
from src.pipeline.etl_pipeline import ETLPipeline
from src.models.models import FinancialStatement, FinancialMetric

class TestETLPipeline:
    
    @patch('src.extractors.sec_extractor.SECExtractor.get_company_filings')
    @patch('src.extractors.sec_extractor.SECExtractor.extract_financial_data')
    def test_process_company(self, mock_extract_data, mock_get_filings, 
                         db_session, sample_company, mock_sec_response, mock_financial_data):
        # Mock extractor responses
        mock_get_filings.return_value = mock_sec_response["filings"]
        mock_extract_data.return_value = mock_financial_data
        
        # Create pipeline
        pipeline = ETLPipeline(db_session)
        
        # Process company
        results = pipeline.process_company(sample_company.ticker, limit=2)
        
        # Assert the results
        assert results["ticker"] == sample_company.ticker
        assert results["filings_processed"] > 0
        assert results["statements_processed"] > 0
        
        # Fix: Correctly query the FinancialStatement model
        statements = db_session.query(FinancialStatement).all()
        assert len(statements) > 0
        
        # Verify financial metrics were calculated
        metrics = db_session.query(FinancialMetric).all()
        assert len(metrics) > 0