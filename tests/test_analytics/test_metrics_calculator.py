import pytest
from src.analytics.metrics_calculator import FinancialMetricsCalculator

class TestFinancialMetricsCalculator:
    
    def test_calculate_metrics(self, sample_company):
        # Create calculator
        calculator = FinancialMetricsCalculator()
        
        # Create test data
        income_statement = {
            "fiscal_year": 2020,
            "fiscal_quarter": 4,
            "version": 1,
            "data": {
                "revenue": 1000000.0,
                "cost_of_revenue": 600000.0,
                "gross_profit": 400000.0,
                "operating_income": 150000.0,
                "net_income": 100000.0
            }
        }
        
        balance_sheet = {
            "fiscal_year": 2020,
            "fiscal_quarter": 4,
            "version": 1,
            "data": {
                "total_assets": 750000.0,
                "total_equity": 400000.0,
                "total_liabilities": 350000.0,
                "total_current_assets": 450000.0,
                "total_current_liabilities": 150000.0,
                "inventory": 100000.0
            }
        }
        
        # Calculate metrics
        metrics = calculator.calculate_metrics(
            sample_company.id,
            income_statement,
            balance_sheet
        )
        
        # Assert the results
        assert metrics["company_id"] == sample_company.id
        assert metrics["fiscal_year"] == 2020
        assert metrics["fiscal_quarter"] == 4
        assert metrics["net_margin"] == 10.0  # (100k / 1M) * 100
        assert metrics["gross_margin"] == 40.0  # (400k / 1M) * 100
        assert metrics["operating_margin"] == 15.0  # (150k / 1M) * 100
        assert metrics["roa"] == (100000.0 / 750000.0) * 100  # (100k / 750k) * 100
        assert metrics["roe"] == (100000.0 / 400000.0) * 100  # (100k / 400k) * 100
        assert metrics["current_ratio"] == 450000.0 / 150000.0  # 450k / 150k
        assert metrics["quick_ratio"] == (450000.0 - 100000.0) / 150000.0  # (450k - 100k) / 150k
        assert metrics["debt_to_equity"] == 350000.0 / 400000.0  # 350k / 400k