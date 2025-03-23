import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, Company
from src.api.main import app
from src.api.database import get_db

# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Create testing db session fixture
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency
@pytest.fixture
def override_get_db():
    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    return _override_get_db  # Return the function, not the session

@pytest.fixture
def client(override_get_db):
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def sample_company(db_session):  # Use db_session directly, not override_get_db
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

class TestCompaniesAPI:
    
    def test_get_companies(self, client, sample_company):
        response = client.get("/companies/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(company["ticker"] == sample_company.ticker for company in data)
    
    def test_get_company(self, client, sample_company):
        response = client.get(f"/companies/{sample_company.ticker}")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == sample_company.ticker
        assert data["name"] == sample_company.name
    
    def test_create_company(self, client, db_session):
        # First ensure the company doesn't already exist
        existing = db_session.query(Company).filter(Company.ticker == "NEW").first()
        if existing:
            db_session.delete(existing)
            db_session.commit()
        
        company_data = {
            "ticker": "NEW",
            "name": "New Test Company",
            "sector": "Finance",
            "industry": "Banking"
        }
        response = client.post("/companies/", json=company_data)
        
        # Print the error response for debugging
        if response.status_code >= 400:
            print(f"Error creating company: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "NEW"
        assert data["name"] == "New Test Company"