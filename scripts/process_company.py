import sys
import os
import argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.config import DATABASE_URL
from src.pipeline.etl_pipeline import ETLPipeline

def main():
    parser = argparse.ArgumentParser(description="Financial Data ETL Pipeline")
    parser.add_argument("--ticker", required=True, help="Company ticker symbol")
    parser.add_argument("--cik", help="Company CIK number")
    parser.add_argument("--form-type", default="10-K,10-Q", help="SEC form types to extract")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=4, help="Maximum number of filings to process")
    
    args = parser.parse_args()
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    etl = ETLPipeline(db)
    
    try:
        results = etl.process_company(
            ticker=args.ticker,
            cik=args.cik,
            form_type=args.form_type,
            start_date=args.start_date,
            end_date=args.end_date,
            limit=args.limit
        )
        
        print(f"ETL Process Results for {args.ticker}:")
        print(f"Filings processed: {results['filings_processed']}")
        print(f"Statements processed: {results['statements_processed']}")
        print(f"Quality issues found: {results['quality_issues']}")
        print(f"Metrics calculated: {results['metrics_calculated']}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()