import sqlalchemy as sa
from ..models.models import DataQualityIssue, FinancialStatement
from ..config import logger

class DataQualityValidator:
    """Validate financial data quality."""
    
    def __init__(self, db_session):
        self.db_session = db_session
        logger.info("Initialized Data Quality Validator")
    
    def validate_financial_statement(self, company_id, statement):
        """
        Validate a financial statement for data quality issues.
        
        Args:
            company_id (int): Company ID
            statement (dict): Financial statement data
            
        Returns:
            list: List of data quality issues
        """
        issues = []
        
        # Check for missing key metrics
        if statement["statement_type"] == "income_statement":
            key_metrics = ["revenue", "net_income"]
            for metric in key_metrics:
                if statement["data"].get(metric) is None:
                    issue = DataQualityIssue(
                        company_id=company_id,
                        statement_id=statement["id"] if "id" in statement else None,
                        issue_type="missing_data",
                        description=f"Missing {metric} in income statement",
                        severity="high",
                        status="open"
                    )
                    issues.append(issue)
        
        elif statement["statement_type"] == "balance_sheet":
            # Check if balance sheet balances (assets = liabilities + equity)
            total_assets = statement["data"].get("total_assets")
            total_liabilities = statement["data"].get("total_liabilities")
            total_equity = statement["data"].get("total_equity")
            
            if total_assets is not None and total_liabilities is not None and total_equity is not None:
                # Allow for small rounding differences (0.1% tolerance)
                if abs(total_assets - (total_liabilities + total_equity)) > (total_assets * 0.001):
                    issue = DataQualityIssue(
                        company_id=company_id,
                        statement_id=statement["id"] if "id" in statement else None,
                        issue_type="inconsistent_data",
                        description="Balance sheet doesn't balance (Assets ≠ Liabilities + Equity)",
                        severity="critical",
                        status="open"
                    )
                    issues.append(issue)
        
        # Check for extreme outliers by comparing with historical data
        # (This is a simplified example; in a real system, more sophisticated outlier detection would be used)
        if "id" in statement:
            historical_data = self.get_historical_data(company_id, statement["statement_type"], 
                                                      statement["fiscal_year"], statement["fiscal_quarter"])
            
            for key, value in statement["data"].items():
                if value is not None and historical_data.get(key) is not None:
                    # Check if current value is more than 200% different from historical average
                    historical_avg = historical_data[key].get("avg")
                    if historical_avg and historical_avg != 0:
                        percent_diff = abs((value - historical_avg) / historical_avg)
                        if percent_diff > 2.0:  # More than 200% difference
                            issue = DataQualityIssue(
                                company_id=company_id,
                                statement_id=statement["id"],
                                issue_type="outlier",
                                description=f"Outlier detected for {key}: current value {value} is {percent_diff:.1f}x different from historical average {historical_avg}",
                                severity="medium",
                                status="open"
                            )
                            issues.append(issue)
        
        return issues
    
    def get_historical_data(self, company_id, statement_type, current_year, current_quarter):
        """
        Get historical financial data for comparison.
        
        Args:
            company_id (int): Company ID
            statement_type (str): Statement type
            current_year (int): Current fiscal year
            current_quarter (int): Current fiscal quarter
            
        Returns:
            dict: Historical data statistics by metric
        """
        # Query for historical statements (excluding current period)
        statements = self.db_session.query(FinancialStatement).filter(
            FinancialStatement.company_id == company_id,
            FinancialStatement.statement_type == statement_type,
            sa.or_(
                FinancialStatement.fiscal_year < current_year,
                sa.and_(
                    FinancialStatement.fiscal_year == current_year,
                    FinancialStatement.fiscal_quarter < current_quarter
                )
            )
        ).order_by(
            FinancialStatement.fiscal_year.desc(),
            FinancialStatement.fiscal_quarter.desc()
        ).limit(8).all()  # Last 8 quarters
        
        if not statements:
            return {}
        
        # Extract data points for each metric and calculate statistics
        metrics = {}
        for statement in statements:
            for key, value in statement.data.items():
                if value is not None and isinstance(value, (int, float)):
                    if key not in metrics:
                        metrics[key] = {"values": [], "avg": None, "min": None, "max": None}
                    metrics[key]["values"].append(value)
        
        # Calculate statistics
        for key in metrics:
            values = metrics[key]["values"]
            if values:
                metrics[key]["avg"] = sum(values) / len(values)
                metrics[key]["min"] = min(values)
                metrics[key]["max"] = max(values)
                
        return metrics
    
    def save_issues(self, issues):
        """
        Save data quality issues to the database.
        
        Args:
            issues (list): List of DataQualityIssue objects
            
        Returns:
            list: List of saved issues
        """
        for issue in issues:
            self.db_session.add(issue)
        self.db_session.commit()
        return issues