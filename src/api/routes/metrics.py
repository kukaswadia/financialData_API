from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from ...models.models import Company, FinancialMetric
from ..schemas import FinancialMetricResponse
from ...config import logger
from .companies import get_db
from ..database import get_db


router = APIRouter()

@router.get("/{ticker}/financial-metrics/", response_model=List[FinancialMetricResponse])
def get_financial_metrics(
    ticker: str,
    year: Optional[int] = Query(None, description="Filter by fiscal year"),
    quarter: Optional[int] = Query(None, description="Filter by fiscal quarter"),
    version: Optional[int] = Query(None, description="Get specific version"),
    latest_only: bool = Query(True, description="Get only the latest version"),
    db: Session = Depends(get_db)
):
    """Get financial metrics for a company."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")
    
    query = db.query(FinancialMetric).filter(FinancialMetric.company_id == company.id)
    
    if year:
        query = query.filter(FinancialMetric.fiscal_year == year)
    if quarter:
        query = query.filter(FinancialMetric.fiscal_quarter == quarter)
    if version:
        query = query.filter(FinancialMetric.version == version)
    
    # Handle latest version only
    if latest_only:
        if year and quarter:
            latest = query.order_by(FinancialMetric.version.desc()).first()
            return [latest] if latest else []
        else:
            # Group by year and quarter and get the latest version of each
            metrics = query.all()
            grouped = {}
            for metric in metrics:
                key = (metric.fiscal_year, metric.fiscal_quarter)
                if key not in grouped or grouped[key].version < metric.version:
                    grouped[key] = metric
            return list(grouped.values())
    
    metrics = query.order_by(
        FinancialMetric.fiscal_year.desc(),
        FinancialMetric.fiscal_quarter.desc(),
        FinancialMetric.version.desc()
    ).all()
    
    return metrics

@router.get("/compare/", response_model=List[dict])
def compare_companies(
    tickers: str = Query(..., description="Comma-separated list of ticker symbols"),
    metrics: str = Query("pe_ratio,roe,net_margin", description="Comma-separated list of metrics to compare"),
    year: Optional[int] = Query(None, description="Fiscal year"),
    quarter: Optional[int] = Query(None, description="Fiscal quarter"),
    db: Session = Depends(get_db)
):
    """Compare financial metrics across multiple companies."""
    ticker_list = [t.strip() for t in tickers.split(",")]
    metric_list = [m.strip() for m in metrics.split(",")]
    
    companies = db.query(Company).filter(Company.ticker.in_(ticker_list)).all()
    company_ids = {company.id: company.ticker for company in companies}
    
    query = db.query(FinancialMetric).filter(FinancialMetric.company_id.in_(company_ids.keys()))
    
    if year:
        query = query.filter(FinancialMetric.fiscal_year == year)
    if quarter:
        query = query.filter(FinancialMetric.fiscal_quarter == quarter)
    
    # Get the latest version for each company
    metrics_data = query.order_by(
        FinancialMetric.company_id,
        FinancialMetric.fiscal_year.desc(),
        FinancialMetric.fiscal_quarter.desc(),
        FinancialMetric.version.desc()
    ).all()
    
    # Group by company and get the latest metrics for each
    latest_metrics = {}
    for metric in metrics_data:
        company_id = metric.company_id
        period = (metric.fiscal_year, metric.fiscal_quarter)
        
        if company_id not in latest_metrics:
            latest_metrics[company_id] = {}
        
        if period not in latest_metrics[company_id]:
            latest_metrics[company_id][period] = metric
    
    # Format the comparison data
    comparison = []
    for company_id, periods in latest_metrics.items():
        ticker = company_ids[company_id]
        for period, metric in periods.items():
            fiscal_year, fiscal_quarter = period
            
            # Extract the requested metrics
            metric_values = {}
            for m in metric_list:
                if hasattr(metric, m):
                    metric_values[m] = getattr(metric, m)
            
            comparison.append({
                "ticker": ticker,
                "fiscal_year": fiscal_year,
                "fiscal_quarter": fiscal_quarter,
                "metrics": metric_values
            })
    
    return comparison