import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestCompaniesAPI:
    
    def test_get_companies(self, sample_company):
        response = client.get("/companies/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(company["ticker"] == sample_company.ticker for company in data)
    
    def test_get_company(self, sample_company):
        response = client.get(f"/companies/{sample_company.ticker}")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == sample_company.ticker
        assert data["name"] == sample_company.name
    
    def test_get_nonexistent_company(self):
        response = client.get("/companies/NONEXISTENT")
        assert response.status_code == 404
    
    def test_create_company(self):
        company_data = {
            "ticker": "NEW",
            "name": "New Test Company",
            "sector": "Finance",
            "industry": "Banking"
        }
        response = client.post("/companies/", json=company_data)
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "NEW"
        assert data["name"] == "New Test Company"