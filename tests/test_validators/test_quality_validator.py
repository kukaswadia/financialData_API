import pytest
from src.validators.quality_validator import DataQualityValidator
from src.models.models import FinancialStatement

class TestDataQualityValidator:
    
    def test_validate_income_statement_missing_data(self, db_session, sample_company):
        # Create validator
        validator = DataQualityValidator(db_session)
        
        # Create a statement with missing key metrics
        statement = {
            "id": 1,
            "company_id": sample_company.id,
            "statement_type": "income_statement",
            "fiscal_year": 2020,
            "fiscal_quarter": 4,
            "version": 1,
            "data": {
                # Missing "revenue" and "net_income"
                "operating_expenses": 250000.0
            }
        }
        
        # Validate the statement
        issues = validator.validate_financial_statement(sample_company.id, statement)
        
        # Assert the results
        assert len(issues) == 2
        assert any(issue.issue_type == "missing_data" and "revenue" in issue.description for issue in issues)
        assert any(issue.issue_type == "missing_data" and "net_income" in issue.description for issue in issues)
    
    def test_validate_balance_sheet_not_balanced(self, db_session, sample_company):
        # Create validator
        validator = DataQualityValidator(db_session)
        
        # Create a statement with unbalanced sheet
        statement = {
            "id": 2,
            "company_id": sample_company.id,
            "statement_type": "balance_sheet",
            "fiscal_year": 2020,
            "fiscal_quarter": 4,
            "version": 1,
            "data": {
                "total_assets": 750000.0,
                "total_liabilities": 300000.0,
                "total_equity": 400000.0  # Assets = 750k, Liabilities + Equity = 700k
            }
        }
        
        # Validate the statement
        issues = validator.validate_financial_statement(sample_company.id, statement)
        
        # Assert the results
        assert len(issues) == 1
        assert issues[0].issue_type == "inconsistent_data"
        assert "balance" in issues[0].description.lower()