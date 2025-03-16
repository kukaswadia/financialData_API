import datetime
from ..models.models import Company, FinancialStatement
from ..extractors.sec_extractor import SECExtractor
from ..extractors.earnings_extractor import EarningsReportExtractor
from ..transformers.normalizer import FinancialDataNormalizer
from ..validators.quality_validator import DataQualityValidator
from ..analytics.metrics_calculator import FinancialMetricsCalculator
from ..config import logger

class ETLPipeline:
    """Orchestrate the ETL process for financial data."""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.sec_extractor = SECExtractor()
        self.earnings_extractor = EarningsReportExtractor()
        self.normalizer = FinancialDataNormalizer()
        self.validator = DataQualityValidator(db_session)
        self.metrics_calculator = FinancialMetricsCalculator()
        logger.info("Initialized ETL Pipeline")
    
    def process_company(self, ticker, cik=None, form_type="10-Q,10-K", 
                       start_date=None, end_date=None, limit=4):
        """
        Process financial data for a company.
        
        Args:
            ticker (str): Company ticker symbol
            cik (str, optional): Company CIK number
            form_type (str): SEC form types to extract
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            limit (int): Maximum number of filings to process
            
        Returns:
            dict: Processing results
        """
        results = {
            "ticker": ticker,
            "filings_processed": 0,
            "statements_processed": 0,
            "quality_issues": 0,
            "metrics_calculated": 0
        }
        
        # Get or create company record
        company = self._get_or_create_company(ticker, cik)
        
        # Extract SEC filings
        filings = self.sec_extractor.get_company_filings(
            ticker=ticker, 
            cik=cik, 
            form_type=form_type, 
            start_date=start_date, 
            end_date=end_date, 
            limit=limit
        )
        
        for filing in filings:
            try:
                # Extract and normalize data from SEC filing
                financial_data = self.sec_extractor.extract_financial_data(filing["accessionNumber"])
                
                if not financial_data:
                    logger.warning(f"No financial data found for {ticker} filing {filing['accessionNumber']}")
                    continue
                
                # Process each statement type
                statement_types = ["income_statement", "balance_sheet", "cash_flow"]
                statements = {}
                
                for statement_type in statement_types:
                    if statement_type in financial_data and financial_data[statement_type]:
                        # Normalize the statement data
                        normalized_data = self._normalize_statement(
                            statement_type, financial_data[statement_type], "sec_filing"
                        )
                        
                        # Determine fiscal period
                        fiscal_info = self._extract_fiscal_info(filing, financial_data.get("metadata", {}))
                        
                        # Save the statement
                        statement = self._save_statement(
                            company.id,
                            statement_type,
                            normalized_data,
                            financial_data[statement_type],
                            fiscal_info,
                            "sec_filing",
                            filing["accessionNumber"]
                        )
                        
                        statements[statement_type] = statement
                        results["statements_processed"] += 1
                
                # Validate statements
                all_issues = []
                for statement_type, statement in statements.items():
                    issues = self.validator.validate_financial_statement(company.id, statement)
                    all_issues.extend(issues)
                
                if all_issues:
                    self.validator.save_issues(all_issues)
                    results["quality_issues"] += len(all_issues)
                
                # Calculate financial metrics if we have both income statement and balance sheet
                if "income_statement" in statements and "balance_sheet" in statements:
                    metrics = self.metrics_calculator.calculate_metrics(
                        company.id,
                        statements["income_statement"],
                        statements["balance_sheet"]
                    )
                    
                    self.metrics_calculator.save_metrics(self.db_session, metrics)
                    results["metrics_calculated"] += 1
                
                results["filings_processed"] += 1
                
            except Exception as e:
                logger.error(f"Error processing {ticker} filing {filing['accessionNumber']}: {str(e)}")
        
        # Extract and process earnings reports data if needed
        # This would follow a similar pattern to the SEC filing processing
        
        return results
    
    def _get_or_create_company(self, ticker, cik=None):
        """
        Get or create a company record.
        
        Args:
            ticker (str): Company ticker symbol
            cik (str, optional): Company CIK number
            
        Returns:
            Company: Company object
        """
        company = self.db_session.query(Company).filter(Company.ticker == ticker).first()
        
        if not company:
            # Get company info (could be enhanced to fetch from an API)
            company = Company(ticker=ticker, cik=cik, name=ticker)
            self.db_session.add(company)
            self.db_session.commit()
            
        return company
    
    def _normalize_statement(self, statement_type, data, source):
        """
        Normalize a financial statement.
        
        Args:
            statement_type (str): Statement type
            data (dict): Raw statement data
            source (str): Data source
            
        Returns:
            dict: Normalized statement data
        """
        if statement_type == "income_statement":
            return self.normalizer.normalize_income_statement(data, source)
        elif statement_type == "balance_sheet":
            return self.normalizer.normalize_balance_sheet(data, source)
        elif statement_type == "cash_flow":
            return self.normalizer.normalize_cash_flow(data, source)
        else:
            return {}
    
    def _extract_fiscal_info(self, filing, metadata):
        """
        Extract fiscal year and quarter information.
        
        Args:
            filing (dict): Filing metadata
            metadata (dict): Document metadata
            
        Returns:
            dict: Fiscal information
        """
        fiscal_info = {
            "fiscal_year": None,
            "fiscal_quarter": None,
            "filing_date": None,
            "report_date": None
        }
        
        # Extract filing date
        if "filedAt" in filing:
            try:
                fiscal_info["filing_date"] = datetime.datetime.fromisoformat(filing["filedAt"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                fiscal_info["filing_date"] = datetime.datetime.utcnow()
        
        # Extract report date
        if "periodOfReport" in filing:
            try:
                fiscal_info["report_date"] = datetime.datetime.strptime(filing["periodOfReport"], "%Y-%m-%d")
            except (ValueError, TypeError):
                pass
        
        # Extract fiscal year and quarter from form type and dates
        form_type = filing.get("formType", "")
        
        if "10-K" in form_type:
            # Annual report
            fiscal_info["fiscal_quarter"] = 4
            if fiscal_info["report_date"]:
                fiscal_info["fiscal_year"] = fiscal_info["report_date"].year
        elif "10-Q" in form_type:
            # Quarterly report
            if fiscal_info["report_date"]:
                fiscal_info["fiscal_year"] = fiscal_info["report_date"].year
                # Approximate the quarter based on the month
                month = fiscal_info["report_date"].month
                if month <= 3:
                    fiscal_info["fiscal_quarter"] = 1
                elif month <= 6:
                    fiscal_info["fiscal_quarter"] = 2
                elif month <= 9:
                    fiscal_info["fiscal_quarter"] = 3
                else:
                    fiscal_info["fiscal_quarter"] = 4
        
        return fiscal_info
    
    def _save_statement(self, company_id, statement_type, normalized_data, raw_data, 
                       fiscal_info, source, source_url):
        """
        Save a financial statement to the database.
        
        Args:
            company_id (int): Company ID
            statement_type (str): Statement type
            normalized_data (dict): Normalized statement data
            raw_data (dict): Raw statement data
            fiscal_info (dict): Fiscal period information
            source (str): Data source
            source_url (str): Source URL or identifier
            
        Returns:
            dict: Saved statement information
        """
        # Check if this statement already exists (for versioning)
        existing_statement = self.db_session.query(FinancialStatement).filter(
            FinancialStatement.company_id == company_id,
            FinancialStatement.statement_type == statement_type,
            FinancialStatement.fiscal_year == fiscal_info["fiscal_year"],
            FinancialStatement.fiscal_quarter == fiscal_info["fiscal_quarter"]
        ).order_by(FinancialStatement.version.desc()).first()
        
        version = 1
        if existing_statement:
            version = existing_statement.version + 1
        
        # Create new statement record
        statement = FinancialStatement(
            company_id=company_id,
            statement_type=statement_type,
            fiscal_year=fiscal_info["fiscal_year"],
            fiscal_quarter=fiscal_info["fiscal_quarter"],
            filing_date=fiscal_info["filing_date"],
            report_date=fiscal_info["report_date"],
            source=source,
            source_url=source_url,
            version=version,
            data=normalized_data,
            raw_data=raw_data
        )
        
        self.db_session.add(statement)
        self.db_session.commit()
        
        return {
            "id": statement.id,
            "company_id": company_id,
            "statement_type": statement_type,
            "fiscal_year": fiscal_info["fiscal_year"],
            "fiscal_quarter": fiscal_info["fiscal_quarter"],
            "version": version,
            "data": normalized_data
        }