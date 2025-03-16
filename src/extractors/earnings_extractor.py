import logging
import requests
from ..config import ALPHA_VANTAGE_API_KEY, logger

class EarningsReportExtractor:
    """Extract earnings report data from financial APIs."""
    
    def __init__(self, api_key=ALPHA_VANTAGE_API_KEY):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        logger.info("Initialized Earnings Report Extractor")
    
    def get_earnings(self, ticker):
        """
        Get earnings data for a company.
        
        Args:
            ticker (str): Company ticker symbol
            
        Returns:
            dict: Earnings data
        """
        params = {
            "function": "EARNINGS",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "annual_earnings": data.get("annualEarnings", []),
                "quarterly_earnings": data.get("quarterlyEarnings", [])
            }
        except Exception as e:
            logger.error(f"Error getting earnings data for {ticker}: {str(e)}")
            return {"annual_earnings": [], "quarterly_earnings": []}
    
    def get_income_statement(self, ticker):
        """
        Get income statement data for a company.
        
        Args:
            ticker (str): Company ticker symbol
            
        Returns:
            dict: Income statement data
        """
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting income statement for {ticker}: {str(e)}")
            return {}
    
    def get_balance_sheet(self, ticker):
        """
        Get balance sheet data for a company.
        
        Args:
            ticker (str): Company ticker symbol
            
        Returns:
            dict: Balance sheet data
        """
        params = {
            "function": "BALANCE_SHEET",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting balance sheet for {ticker}: {str(e)}")
            return {}
    
    def get_cash_flow(self, ticker):
        """
        Get cash flow data for a company.
        
        Args:
            ticker (str): Company ticker symbol
            
        Returns:
            dict: Cash flow data
        """
        params = {
            "function": "CASH_FLOW",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting cash flow for {ticker}: {str(e)}")
            return {}