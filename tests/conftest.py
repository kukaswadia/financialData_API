
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, Company
from src.api.main import app
from src.api.database import get_db
from fastapi.testclient import TestClient



# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Optional: Drop tables after all tests
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(override_get_db):
    # Override the dependency
    app.dependency_overrides[get_db] = lambda: override_get_db
    return TestClient(app)

@pytest.fixture
def sample_company(db_session):
    company = db_session.query(Company).filter(Company.ticker == "TEST").first()
    if not company:
        company = Company(
            ticker="TEST",
            name="Test Company",
            sector="Technology",
            industry="Software",
            cik="0001234567"
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
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