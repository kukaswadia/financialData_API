from ..config import logger

class FinancialDataNormalizer:
    """Normalize financial data from different sources into a standard format."""
    
    def __init__(self):
        logger.info("Initialized Financial Data Normalizer")
    
    def normalize_income_statement(self, data, source):
        """
        Normalize income statement data.
        
        Args:
            data (dict): Raw income statement data
            source (str): Data source
            
        Returns:
            dict: Normalized income statement data
        """
        normalized = {
            "revenue": None,
            "cost_of_revenue": None,
            "gross_profit": None,
            "operating_expenses": None,
            "operating_income": None,
            "net_income": None,
            "eps_basic": None,
            "eps_diluted": None,
        }
        
        if source == "sec_filing":
            # Map SEC XBRL tags to normalized format
            normalized["revenue"] = data.get("Revenues") or data.get("SalesRevenueNet") or data.get("RevenueFromContractWithCustomerExcludingAssessedTax")
            normalized["cost_of_revenue"] = data.get("CostOfGoodsAndServicesSold") or data.get("CostOfRevenue")
            normalized["gross_profit"] = data.get("GrossProfit")
            normalized["operating_expenses"] = data.get("OperatingExpenses")
            normalized["operating_income"] = data.get("OperatingIncomeLoss")
            normalized["net_income"] = data.get("NetIncomeLoss")
            normalized["eps_basic"] = data.get("EarningsPerShareBasic")
            normalized["eps_diluted"] = data.get("EarningsPerShareDiluted")
            
        elif source == "earnings_report":
            if "annualReports" in data:
                report = data["annualReports"][0] if data["annualReports"] else {}
            elif "quarterlyReports" in data:
                report = data["quarterlyReports"][0] if data["quarterlyReports"] else {}
            else:
                report = {}
                
            normalized["revenue"] = report.get("totalRevenue")
            normalized["cost_of_revenue"] = report.get("costOfRevenue")
            normalized["gross_profit"] = report.get("grossProfit")
            normalized["operating_expenses"] = report.get("operatingExpenses")
            normalized["operating_income"] = report.get("operatingIncome")
            normalized["net_income"] = report.get("netIncome")
            normalized["eps_basic"] = report.get("reportedEPS")
            
        # Convert string values to float where applicable
        for key, value in normalized.items():
            if isinstance(value, str):
                try:
                    normalized[key] = float(value)
                except (ValueError, TypeError):
                    pass
            
        return normalized
    
    def normalize_balance_sheet(self, data, source):
        """
        Normalize balance sheet data.
        
        Args:
            data (dict): Raw balance sheet data
            source (str): Data source
            
        Returns:
            dict: Normalized balance sheet data
        """
        normalized = {
            "cash_and_equivalents": None,
            "short_term_investments": None,
            "accounts_receivable": None,
            "inventory": None,
            "total_current_assets": None,
            "property_plant_equipment": None,
            "goodwill": None,
            "total_assets": None,
            "accounts_payable": None,
            "short_term_debt": None,
            "total_current_liabilities": None,
            "long_term_debt": None,
            "total_liabilities": None,
            "common_stock": None,
            "retained_earnings": None,
            "total_equity": None,
        }
        
        if source == "sec_filing":
            # Map SEC XBRL tags to normalized format
            normalized["cash_and_equivalents"] = data.get("CashAndCashEquivalentsAtCarryingValue")
            normalized["short_term_investments"] = data.get("MarketableSecurities") or data.get("ShortTermInvestments")
            normalized["accounts_receivable"] = data.get("AccountsReceivableNetCurrent")
            normalized["inventory"] = data.get("InventoryNet")
            normalized["total_current_assets"] = data.get("AssetsCurrent")
            normalized["property_plant_equipment"] = data.get("PropertyPlantAndEquipmentNet")
            normalized["goodwill"] = data.get("Goodwill")
            normalized["total_assets"] = data.get("Assets")
            normalized["accounts_payable"] = data.get("AccountsPayableCurrent")
            normalized["short_term_debt"] = data.get("LongTermDebtCurrent")
            normalized["total_current_liabilities"] = data.get("LiabilitiesCurrent")
            normalized["long_term_debt"] = data.get("LongTermDebtNoncurrent")
            normalized["total_liabilities"] = data.get("Liabilities")
            normalized["common_stock"] = data.get("CommonStockValue")
            normalized["retained_earnings"] = data.get("RetainedEarningsAccumulatedDeficit")
            normalized["total_equity"] = data.get("StockholdersEquity")
            
        elif source == "earnings_report":
            if "annualReports" in data:
                report = data["annualReports"][0] if data["annualReports"] else {}
            elif "quarterlyReports" in data:
                report = data["quarterlyReports"][0] if data["quarterlyReports"] else {}
            else:
                report = {}
                
            normalized["cash_and_equivalents"] = report.get("cashAndCashEquivalentsAtCarryingValue")
            normalized["short_term_investments"] = report.get("shortTermInvestments")
            normalized["accounts_receivable"] = report.get("currentNetReceivables")
            normalized["inventory"] = report.get("inventory")
            normalized["total_current_assets"] = report.get("totalCurrentAssets")
            normalized["property_plant_equipment"] = report.get("propertyPlantEquipment")
            normalized["total_assets"] = report.get("totalAssets")
            normalized["accounts_payable"] = report.get("currentAccountsPayable")
            normalized["short_term_debt"] = report.get("shortTermDebt")
            normalized["total_current_liabilities"] = report.get("totalCurrentLiabilities")
            normalized["long_term_debt"] = report.get("longTermDebt")
            normalized["total_liabilities"] = report.get("totalLiabilities")
            normalized["common_stock"] = report.get("commonStock")
            normalized["retained_earnings"] = report.get("retainedEarnings")
            normalized["total_equity"] = report.get("totalShareholderEquity")
            
        # Convert string values to float where applicable
        for key, value in normalized.items():
            if isinstance(value, str):
                try:
                    normalized[key] = float(value)
                except (ValueError, TypeError):
                    pass
            
        return normalized
    
    def normalize_cash_flow(self, data, source):
        """
        Normalize cash flow data.
        
        Args:
            data (dict): Raw cash flow data
            source (str): Data source
            
        Returns:
            dict: Normalized cash flow data
        """
        normalized = {
            "operating_cash_flow": None,
            "capital_expenditures": None,
            "free_cash_flow": None,
            "dividends_paid": None,
            "net_borrowings": None,
            "net_investing_cash_flow": None,
            "net_financing_cash_flow": None,
            "net_change_in_cash": None,
        }
        
        if source == "sec_filing":
            # Map SEC XBRL tags to normalized format
            normalized["operating_cash_flow"] = data.get("NetCashProvidedByUsedInOperatingActivities")
            normalized["capital_expenditures"] = data.get("PaymentsToAcquirePropertyPlantAndEquipment")
            normalized["free_cash_flow"] = None  # Calculated field
            normalized["dividends_paid"] = data.get("PaymentsOfDividends")
            normalized["net_borrowings"] = data.get("ProceedsFromIssuanceOfLongTermDebt") and data.get("RepaymentsOfLongTermDebt")
            normalized["net_investing_cash_flow"] = data.get("NetCashProvidedByUsedInInvestingActivities")
            normalized["net_financing_cash_flow"] = data.get("NetCashProvidedByUsedInFinancingActivities")
            normalized["net_change_in_cash"] = data.get("CashAndCashEquivalentsPeriodIncreaseDecrease")
            
        elif source == "earnings_report":
            if "annualReports" in data:
                report = data["annualReports"][0] if data["annualReports"] else {}
            elif "quarterlyReports" in data:
                report = data["quarterlyReports"][0] if data["quarterlyReports"] else {}
            else:
                report = {}
                
            normalized["operating_cash_flow"] = report.get("operatingCashflow")
            normalized["capital_expenditures"] = report.get("capitalExpenditures")
            normalized["dividends_paid"] = report.get("dividendPayout")
            normalized["net_investing_cash_flow"] = report.get("cashflowFromInvestment")
            normalized["net_financing_cash_flow"] = report.get("cashflowFromFinancing")
            
        # Calculate free cash flow if possible
        if normalized["operating_cash_flow"] is not None and normalized["capital_expenditures"] is not None:
            try:
                normalized["free_cash_flow"] = float(normalized["operating_cash_flow"]) - float(normalized["capital_expenditures"])
            except (ValueError, TypeError):
                normalized["free_cash_flow"] = None
                
        # Convert string values to float where applicable
        for key, value in normalized.items():
            if isinstance(value, str):
                try:
                    normalized[key] = float(value)
                except (ValueError, TypeError):
                    pass
            
        return normalized