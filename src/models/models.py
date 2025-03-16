import os
import logging
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    cik = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    statement_type = Column(String)  # "income_statement", "balance_sheet", "cash_flow"
    fiscal_year = Column(Integer)
    fiscal_quarter = Column(Integer)
    filing_date = Column(DateTime)
    report_date = Column(DateTime)
    source = Column(String)  # "sec_filing", "earnings_report"
    source_url = Column(String)
    version = Column(Integer)  # For tracking changes/updates
    data = Column(JSON)  # Normalized financial data
    raw_data = Column(JSON)  # Original data before normalization
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    __table_args__ = (
        sa.UniqueConstraint('company_id', 'statement_type', 'fiscal_year', 
                          'fiscal_quarter', 'version', name='uix_financial_statement'),
    )


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    fiscal_year = Column(Integer)
    fiscal_quarter = Column(Integer)
    calculation_date = Column(DateTime, default=datetime.datetime.utcnow)
    version = Column(Integer)  # Linked to the financial statement version
    
    # Common financial ratios
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    roe = Column(Float)  # Return on Equity
    roa = Column(Float)  # Return on Assets
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)
    dividend_yield = Column(Float)
    
    # Additional metrics can be added as needed
    
    __table_args__ = (
        sa.UniqueConstraint('company_id', 'fiscal_year', 'fiscal_quarter', 'version', 
                           name='uix_financial_metric'),
    )


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    statement_id = Column(Integer, ForeignKey("financial_statements.id"), nullable=True)
    issue_type = Column(String)  # "missing_data", "inconsistent_data", "outlier", etc.
    description = Column(Text)
    severity = Column(String)  # "low", "medium", "high", "critical"
    status = Column(String)  # "open", "resolved", "ignored"
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)