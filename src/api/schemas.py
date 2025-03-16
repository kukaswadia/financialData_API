from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Any
import datetime

class CompanyCreate(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    cik: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    ticker: str
    name: str
    sector: Optional[str]
    industry: Optional[str]
    cik: Optional[str]
    
    class Config:
        orm_mode = True


class FinancialStatementResponse(BaseModel):
    id: int
    company_id: int
    statement_type: str
    fiscal_year: int
    fiscal_quarter: int
    filing_date: datetime.datetime
    report_date: datetime.datetime
    source: str
    version: int
    data: Dict[str, Any]
    
    class Config:
        orm_mode = True


class FinancialMetricResponse(BaseModel):
    id: int
    company_id: int
    fiscal_year: int
    fiscal_quarter: int
    calculation_date: datetime.datetime
    version: int
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    roe: Optional[float]
    roa: Optional[float]
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    dividend_yield: Optional[float]
    
    class Config:
        orm_mode = True