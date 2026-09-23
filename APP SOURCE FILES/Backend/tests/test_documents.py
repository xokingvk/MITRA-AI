import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_temporary_document_upload():
    file_content = b"Sample Income Certificate Content. Annual Income: 45000 INR."
    files = {
        "file": ("income_cert.txt", io.BytesIO(file_content), "text/plain")
    }
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["is_temporary"] is True
    assert "document_id" in data
    assert data["filename"] == "income_cert.txt"
