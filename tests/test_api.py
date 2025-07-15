# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_success():
    payload = {
        "edad": 22,
        "nota_media": 8.5,
        "pais_nacimiento": "España",
        "programa": "Ingeniería Informática",
        "solicita_beca": True
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "probability" in response.json()

def test_predict_invalid_edad():
    payload = {
        "edad": 150,  # Invalid
        "nota_media": 8.5,
        "pais_nacimiento": "España",
        "programa": "Ingeniería Informática"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error