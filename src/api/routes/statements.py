from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...models.models import Company, FinancialStatement
from ..schemas import FinancialStatementResponse
from ...config import logger
from .companies import get_db
from ..database import get_db


router = APIRouter()

@router.get("/{ticker}/financial-statements/", response_model=List[FinancialStatementResponse])
def get_financial_statements(
    ticker: str,
    statement_type: Optional[str] = Query(None, description="Filter by statement type"),
    year: Optional[int] = Query(None, description="Filter by fiscal year"),
    quarter: Optional[int] = Query(None, description="Filter by fiscal quarter"),
    version: Optional[int] = Query(None, description="Get specific version"),
    latest_only: bool = Query(False, description="Get only the latest version"),
    db: Session = Depends(get_db)
):
    """Get financial statements for a company."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")
    
    query = db.query(FinancialStatement).filter(FinancialStatement.company_id == company.id)
    
    if statement_type:
        query = query.filter(FinancialStatement.statement_type == statement_type)
    if year:
        query = query.filter(FinancialStatement.fiscal_year == year)
    if quarter:
        query = query.filter(FinancialStatement.fiscal_quarter == quarter)
    if version:
        query = query.filter(FinancialStatement.version == version)
    
    # Handle latest version only
    if latest_only:
        # This is a simplification - a more efficient query would use window functions
        # to get the latest version of each statement
        if statement_type and year and quarter:
            latest = query.order_by(FinancialStatement.version.desc()).first()
            return [latest] if latest else []
        else:
            # Group by statement type, year, quarter and get the latest version of each
            # This is inefficient - in a production system, use window functions or a more optimized query
            statements = query.all()
            grouped = {}
            for stmt in statements:
                key = (stmt.statement_type, stmt.fiscal_year, stmt.fiscal_quarter)
                if key not in grouped or grouped[key].version < stmt.version:
                    grouped[key] = stmt
            return list(grouped.values())
    
    statements = query.order_by(
        FinancialStatement.fiscal_year.desc(),
        FinancialStatement.fiscal_quarter.desc(),
        FinancialStatement.version.desc()
    ).all()
    
    return statements