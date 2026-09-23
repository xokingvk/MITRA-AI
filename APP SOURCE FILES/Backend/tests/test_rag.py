from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_scheme_summary_endpoint():
    response = client.get("/api/schemes")
    assert response.status_code == 200
    data = response.json()
    assert "total_indexed_chunks" in data
    assert "source_documents" in data

def test_scheme_eligibility_endpoint():
    payload = {
        "age": 65,
        "state": "Tamil Nadu",
        "annual_income": 50000,
        "category": "General",
        "gender": "Female",
        "language": "en"
    }
    response = client.post("/api/schemes/eligibility", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "matching_schemes" in data
    assert "guidance_notes" in data
    assert "disclaimer" in data
