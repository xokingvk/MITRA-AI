from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_greeting_intent():
    payload = {
        "message": "Hello",
        "language": "en"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "greeting"
    assert "MITRA AI" in data["answer"]
    assert "conversation_id" in data

def test_chat_multilingual_hindi():
    payload = {
        "message": "नमस्ते",
        "language": "hi"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "hi"

def test_chat_medical_safety_guardrail():
    payload = {
        "message": "What dosage of medicine should I take for fever?",
        "language": "en"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "medical_safety"
    assert "cannot diagnose" in data["answer"].lower() or "prescribe" in data["answer"].lower()

def test_chat_empty_message_validation():
    payload = {
        "message": "   ",
        "language": "en"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 422
