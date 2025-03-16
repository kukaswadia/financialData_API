import logging
import requests
from sec_api import QueryApi, RenderApi
from ..config import SEC_API_KEY, logger

class SECExtractor:
    """Extract financial data from SEC filings using the SEC API."""
    
    def __init__(self, api_key=SEC_API_KEY):
        self.api_key = api_key
        self.query_api = QueryApi(api_key=api_key)
        self.render_api = RenderApi(api_key=api_key)
        logger.info("Initialized SEC Extractor")
    
    def get_company_filings(self, ticker=None, cik=None, form_type="10-K,10-Q", 
                          start_date=None, end_date=None, limit=10):
        """
        Query the SEC API for company filings.
        
        Args:
            ticker (str): Company ticker symbol
            cik (str): Company CIK number
            form_type (str): SEC form types (comma-separated)
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            limit (int): Maximum number of filings to return
            
        Returns:
            List of filing metadata
        """
        query = ""
        
        if ticker:
            query += f"ticker:{ticker} "
        if cik:
            query += f"cik:{cik} "
        
        query += f"formType:({form_type}) "
        
        if start_date:
            query += f"filedAt:>{start_date} "
        if end_date:
            query += f"filedAt:<{end_date} "
        
        logger.info(f"Querying SEC API with query: {query}")
        
        try:
            response = self.query_api.get_filings(
                query=query.strip(),
                limit=limit,
                sort="filedAt:desc"
            )
            return response.get("filings", [])
        except Exception as e:
            logger.error(f"Error querying SEC API: {str(e)}")
            return []
    
    def extract_financial_data(self, accession_number):
        """
        Extract financial data from a specific SEC filing.
        
        Args:
            accession_number (str): SEC filing accession number
            
        Returns:
            dict: Extracted financial data
        """
        try:
            # Get the XBRL data from the filing
            xbrl_json = self.render_api.xbrl_to_json(accession_number)
            
            # Extract relevant financial statement data
            income_statement = xbrl_json.get("IncomeStatement", {})
            balance_sheet = xbrl_json.get("BalanceSheet", {})
            cash_flow = xbrl_json.get("CashFlow", {})
            
            financial_data = {
                "income_statement": income_statement,
                "balance_sheet": balance_sheet,
                "cash_flow": cash_flow,
                "metadata": xbrl_json.get("DocumentAndEntityInformation", {})
            }
            
            return financial_data
        except Exception as e:
            logger.error(f"Error extracting financial data from {accession_number}: {str(e)}")
            return {}