from ..models.models import FinancialMetric
from ..config import logger

class FinancialMetricsCalculator:
    """Calculate financial metrics and ratios from financial statements."""
    
    def __init__(self):
        logger.info("Initialized Financial Metrics Calculator")
    
    def calculate_metrics(self, company_id, income_statement, balance_sheet, prev_income_statement=None):
        """
        Calculate financial metrics based on financial statements.
        
        Args:
            company_id (int): Company ID
            income_statement (dict): Income statement data
            balance_sheet (dict): Balance sheet data
            prev_income_statement (dict, optional): Previous period income statement
            
        Returns:
            dict: Calculated financial metrics
        """
        metrics = {
            "company_id": company_id,
            "fiscal_year": income_statement.get("fiscal_year"),
            "fiscal_quarter": income_statement.get("fiscal_quarter"),
            "version": income_statement.get("version", 1),
        }
        
        # Income statement metrics
        revenue = income_statement["data"].get("revenue")
        net_income = income_statement["data"].get("net_income")
        operating_income = income_statement["data"].get("operating_income")
        gross_profit = income_statement["data"].get("gross_profit")
        
        # Balance sheet metrics
        total_assets = balance_sheet["data"].get("total_assets")
        total_equity = balance_sheet["data"].get("total_equity")
        total_liabilities = balance_sheet["data"].get("total_liabilities")
        current_assets = balance_sheet["data"].get("total_current_assets")
        current_liabilities = balance_sheet["data"].get("total_current_liabilities")
        inventory = balance_sheet["data"].get("inventory")
        
        # Calculate ratios where data is available
        
        # Profitability ratios
        if net_income is not None and revenue is not None and revenue != 0:
            metrics["net_margin"] = (net_income / revenue) * 100
        
        if gross_profit is not None and revenue is not None and revenue != 0:
            metrics["gross_margin"] = (gross_profit / revenue) * 100
            
        if operating_income is not None and revenue is not None and revenue != 0:
            metrics["operating_margin"] = (operating_income / revenue) * 100
        
        # Return on assets and equity
        if net_income is not None and total_assets is not None and total_assets != 0:
            metrics["roa"] = (net_income / total_assets) * 100
            
        if net_income is not None and total_equity is not None and total_equity != 0:
            metrics["roe"] = (net_income / total_equity) * 100
        
        # Liquidity ratios
        if current_assets is not None and current_liabilities is not None and current_liabilities != 0:
            metrics["current_ratio"] = current_assets / current_liabilities
            
        if current_assets is not None and inventory is not None and current_liabilities is not None and current_liabilities != 0:
            metrics["quick_ratio"] = (current_assets - inventory) / current_liabilities
        
        # Solvency ratios
        if total_liabilities is not None and total_equity is not None and total_equity != 0:
            metrics["debt_to_equity"] = total_liabilities / total_equity
        
        # Add market metrics like P/E ratio later when market data is available
        metrics["pe_ratio"] = None
        metrics["pb_ratio"] = None
        metrics["dividend_yield"] = None
        
        return metrics
    
    def save_metrics(self, db_session, metrics):
        """
        Save calculated metrics to the database.
        
        Args:
            db_session: Database session
            metrics (dict): Calculated financial metrics
            
        Returns:
            FinancialMetric: Saved financial metric object
        """
        financial_metric = FinancialMetric(**metrics)
        db_session.add(financial_metric)
        db_session.commit()
        return financial_metric