from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...models.models import Company, DataQualityIssue
from ...config import logger
from .companies import get_db
from ..database import get_db

router = APIRouter()

@router.get("/{ticker}/data-quality-issues/", response_model=List[dict])
def get_data_quality_issues(
    ticker: str,
    status: Optional[str] = Query(None, description="Filter by status (open, resolved, ignored)"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    db: Session = Depends(get_db)
):
    """Get data quality issues for a company."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")
    
    query = db.query(DataQualityIssue).filter(DataQualityIssue.company_id == company.id)
    
    if status:
        query = query.filter(DataQualityIssue.status == status)
    if severity:
        query = query.filter(DataQualityIssue.severity == severity)
    
    issues = query.order_by(DataQualityIssue.detected_at.desc()).all()
    
    # Convert to dictionaries for response
    issues_list = []
    for issue in issues:
        issues_list.append({
            "id": issue.id,
            "company_id": issue.company_id,
            "statement_id": issue.statement_id,
            "issue_type": issue.issue_type,
            "description": issue.description,
            "severity": issue.severity,
            "status": issue.status,
            "detected_at": issue.detected_at,
            "resolved_at": issue.resolved_at
        })
    
    return issues_list