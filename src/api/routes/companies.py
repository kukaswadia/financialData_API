from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...models.models import Company
from ..schemas import CompanyCreate, CompanyResponse
from ...config import logger
from ..database import get_db


router = APIRouter()

@router.get("/", response_model=List[CompanyResponse])
def get_companies(
    skip: int = Query(0, description="Skip N companies"),
    limit: int = Query(100, description="Limit to N companies"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db)
):
    """Get a list of companies."""
    query = db.query(Company)
    
    if sector:
        query = query.filter(Company.sector == sector)
        
    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/{ticker}", response_model=CompanyResponse)
def get_company(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get company details by ticker symbol."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")
    return company


@router.post("/", response_model=CompanyResponse)
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    """Create a new company."""
    db_company = db.query(Company).filter(Company.ticker == company.ticker).first()
    if db_company:
        raise HTTPException(status_code=400, detail=f"Company with ticker {company.ticker} already exists")
    
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


# Define the get_db dependency function (should be imported from a common location)
def get_db():
    # This function should be defined in a common location and imported
    # It's included here for completeness
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from ...config import DATABASE_URL
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()