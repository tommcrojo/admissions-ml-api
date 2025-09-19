"""Tests unitarios para la API de inferencia de admisiones."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Verifica que el endpoint /health devuelve estado correcto."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_success() -> None:
    """Verifica que una predicción válida devuelve los campos esperados."""
    payload = {
        "nota_normalizada": 0.7,
        "edad": 22,
        "creditos_ratio": 1.0,
        "rama_ciencias": 1,
        "rama_sociales": 0,
        "rama_ingenieria": 0,
        "es_murcia": 1,
        "es_extranjero": 0,
        "es_online": 0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "probability" in response.json()


def test_predict_invalid_nota() -> None:
    """Verifica que una nota normalizada inválida genera error de validación."""
    payload = {
        "nota_normalizada": 1.5,  # Invalid (> 1.0)
        "edad": 22,
        "creditos_ratio": 1.0,
        "rama_ciencias": 1,
        "rama_sociales": 0,
        "rama_ingenieria": 0,
        "es_murcia": 1,
        "es_extranjero": 0,
        "es_online": 0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error


def test_predict_invalid_encoding() -> None:
    """Verifica que encoding binario inválido genera error."""
    payload = {
        "nota_normalizada": 0.7,
        "edad": 22,
        "creditos_ratio": 1.0,
        "rama_ciencias": 2,  # Invalid (> 1)
        "rama_sociales": 0,
        "rama_ingenieria": 0,
        "es_murcia": 1,
        "es_extranjero": 0,
        "es_online": 0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error
