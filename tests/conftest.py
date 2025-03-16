import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.models import Base, Company, FinancialStatement
from src.extractors.sec_extractor import SECExtractor
from src.extractors.earnings_extractor import EarningsReportExtractor
from src.transformers.normalizer import FinancialDataNormalizer
from src.validators.quality_validator import DataQualityValidator
from src.analytics.metrics_calculator import FinancialMetricsCalculator
from src.pipeline.etl_pipeline import ETLPipeline

@pytest.fixture
def db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(db_engine):
    """Create a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_company(db_session):
    """Create a sample company for testing."""
    company = Company(
        ticker="TEST",
        name="Test Company",
        sector="Technology",
        industry="Software",
        cik="0001234567"
    )
    db_session.add(company)
    db_session.commit()
    return company

@pytest.fixture
def mock_sec_response():
    """Return a mock SEC API response."""
    return {
        "filings": [
            {
                "accessionNumber": "0001234567-21-000001",
                "filedAt": "2021-03-15T16:30:00Z",
                "formType": "10-K",
                "periodOfReport": "2020-12-31"
            },
            {
                "accessionNumber": "0001234567-20-000004",
                "filedAt": "2020-11-05T16:30:00Z",
                "formType": "10-Q",
                "periodOfReport": "2020-09-30"
            }
        ]
    }

@pytest.fixture
def mock_financial_data():
    """Return mock financial data from SEC filing."""
    return {
        "income_statement": {
            "Revenues": "1000000",
            "CostOfGoodsAndServicesSold": "600000",
            "GrossProfit": "400000",
            "OperatingExpenses": "250000",
            "OperatingIncomeLoss": "150000",
            "NetIncomeLoss": "100000",
            "EarningsPerShareBasic": "1.50",
            "EarningsPerShareDiluted": "1.45"
        },
        "balance_sheet": {
            "CashAndCashEquivalentsAtCarryingValue": "200000",
            "AccountsReceivableNetCurrent": "150000",
            "InventoryNet": "100000",
            "AssetsCurrent": "450000",
            "PropertyPlantAndEquipmentNet": "300000",
            "Assets": "750000",
            "AccountsPayableCurrent": "80000",
            "LiabilitiesCurrent": "150000",
            "LongTermDebtNoncurrent": "200000",
            "Liabilities": "350000",
            "StockholdersEquity": "400000"
        },
        "cash_flow": {
            "NetCashProvidedByUsedInOperatingActivities": "120000",
            "PaymentsToAcquirePropertyPlantAndEquipment": "50000",
            "NetCashProvidedByUsedInInvestingActivities": "-50000",
            "NetCashProvidedByUsedInFinancingActivities": "-30000",
            "CashAndCashEquivalentsPeriodIncreaseDecrease": "40000"
        },
        "metadata": {
            "EntityRegistrantName": "Test Company",
            "DocumentPeriodEndDate": "2020-12-31"
        }
    }