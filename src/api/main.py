from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from ..models.models import Base
from ..pipeline.etl_pipeline import ETLPipeline
from .routes import companies, statements, metrics, data_quality
from ..config import logger, DATABASE_URL
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# Create the FastAPI application
app = FastAPI(
    title="Financial Data API",
    description="API for accessing normalized financial data and metrics",
    version="1.0.0"
)

# Database setup
engine = sa.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(statements.router, prefix="/companies", tags=["statements"])
app.include_router(metrics.router, prefix="/companies", tags=["metrics"])
app.include_router(data_quality.router, prefix="/companies", tags=["data-quality"])

# ETL process endpoint
@app.post("/process-company/")
def run_etl_process(
    ticker: str,
    form_type: str = Query("10-K,10-Q", description="SEC form types to extract"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    limit: int = Query(4, description="Maximum number of filings to process"),
    db: Session = Depends(get_db)
):
    """Run the ETL process for a company."""
    etl = ETLPipeline(db)
    results = etl.process_company(
        ticker=ticker,
        form_type=form_type,
        start_date=start_date,
        limit=limit
    )
    
    return results

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    logger.info("API initialized and database tables created")