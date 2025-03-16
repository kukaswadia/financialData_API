import pytest
from src.transformers.normalizer import FinancialDataNormalizer

class TestFinancialDataNormalizer:
    
    def test_normalize_income_statement(self, mock_financial_data):
        normalizer = FinancialDataNormalizer()
        income_statement = mock_financial_data["income_statement"]
        
        # Normalize income statement
        normalized = normalizer.normalize_income_statement(income_statement, "sec_filing")
        
        # Assert the results
        assert normalized["revenue"] == 1000000.0
        assert normalized["cost_of_revenue"] == 600000.0
        assert normalized["gross_profit"] == 400000.0
        assert normalized["operating_expenses"] == 250000.0
        assert normalized["operating_income"] == 150000.0
        assert normalized["net_income"] == 100000.0
        assert normalized["eps_basic"] == 1.5
        assert normalized["eps_diluted"] == 1.45
    
    def test_normalize_balance_sheet(self, mock_financial_data):
        normalizer = FinancialDataNormalizer()
        balance_sheet = mock_financial_data["balance_sheet"]
        
        # Normalize balance sheet
        normalized = normalizer.normalize_balance_sheet(balance_sheet, "sec_filing")
        
        # Assert the results
        assert normalized["cash_and_equivalents"] == 200000.0
        assert normalized["accounts_receivable"] == 150000.0
        assert normalized["inventory"] == 100000.0
        assert normalized["total_current_assets"] == 450000.0
        assert normalized["property_plant_equipment"] == 300000.0
        assert normalized["total_assets"] == 750000.0
        assert normalized["accounts_payable"] == 80000.0
        assert normalized["total_current_liabilities"] == 150000.0
        assert normalized["long_term_debt"] == 200000.0
        assert normalized["total_liabilities"] == 350000.0
        assert normalized["total_equity"] == 400000.0
    
    def test_normalize_cash_flow(self, mock_financial_data):
        normalizer = FinancialDataNormalizer()
        cash_flow = mock_financial_data["cash_flow"]
        
        # Normalize cash flow
        normalized = normalizer.normalize_cash_flow(cash_flow, "sec_filing")
        
        # Assert the results
        assert normalized["operating_cash_flow"] == 120000.0
        assert normalized["capital_expenditures"] == 50000.0
        assert normalized["free_cash_flow"] == 70000.0  # Calculated field
        assert normalized["net_investing_cash_flow"] == -50000.0
        assert normalized["net_financing_cash_flow"] == -30000.0
        assert normalized["net_change_in_cash"] == 40000.0