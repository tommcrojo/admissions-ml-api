"""API REST para predicción de admisiones universitarias usando ML.

Este módulo proporciona endpoints para predecir la probabilidad de admisión
de estudiantes basándose en características demográficas y académicas.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import uvicorn
import os

app = FastAPI(
    title="Admissions Scoring API",
    description="ML-powered admission prediction service",
    version="1.0.0"
)

# Load model and mappings at startup
model = joblib.load("models/rf_model.pkl")
programas_mapping = None
try:
    programas_mapping = joblib.load("models/programas.pkl")
except:
    pass

# Pydantic schemas
class ApplicantInput(BaseModel):
    edad: int = Field(..., ge=16, le=80)
    nota_media: float = Field(..., ge=0, le=10)
    pais_nacimiento: str
    programa: str
    solicita_beca: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "edad": 22,
                "nota_media": 8.5,
                "pais_nacimiento": "España",
                "programa": "Ingeniería Informática",
                "solicita_beca": True
            }
        }

class PredictionOutput(BaseModel):
    prediction: str
    probability: float
    confidence: str
    model_version: str = "1.0.0"

# Endpoints
@app.get("/")
def root() -> Dict[str, str]:
    """Endpoint raíz que confirma que la API está activa.

    Returns:
        Dict con mensaje de bienvenida y estado del servicio.
    """
    return {"message": "Admissions Scoring API", "status": "active"}

@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Verifica el estado de salud de la API y del modelo ML.

    Returns:
        Dict con el estado del servicio y confirmación de carga del modelo.
    """
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionOutput)
def predict(applicant: ApplicantInput) -> PredictionOutput:
    """Predice la probabilidad de admisión de un solicitante.

    Args:
        applicant: Datos del solicitante incluyendo edad, nota media,
                  país de nacimiento, programa solicitado y solicitud de beca.

    Returns:
        PredictionOutput con la predicción (admitido/rechazado),
        probabilidad y nivel de confianza.

    Raises:
        HTTPException: Si ocurre un error durante la predicción.
    """
    try:
        # Feature engineering
        nota_normalizada = (applicant.nota_media - 5.0) / 5.0
        es_extranjero = 1 if applicant.pais_nacimiento != "España" else 0

        # Encode país de nacimiento
        paises = {
            "España": 0, "México": 1, "Colombia": 2, "Argentina": 3,
            "Chile": 4, "Perú": 5, "Venezuela": 6, "Ecuador": 7
        }
        pais_idx = paises.get(applicant.pais_nacimiento, -1)

        # Encode programa
        programas = {
            "Ingeniería Informática": 0, "ADE": 1, "Derecho": 2,
            "Medicina": 3, "Arquitectura": 4, "Psicología": 5
        }
        programa_idx = programas.get(applicant.programa, -1)

        # Create feature vector (orden debe coincidir con el entrenamiento)
        features = np.array([[
            applicant.edad,
            nota_normalizada,
            pais_idx,
            programa_idx,
            es_extranjero,
            int(applicant.solicita_beca)
        ]], dtype=np.float64)

        # Get prediction probabilities
        proba = model.predict_proba(features)[0]
        prob_admitido = float(proba[1]) if len(proba) > 1 else float(proba[0])

        # Determine prediction and confidence
        prediction = "admitido" if prob_admitido >= 0.5 else "rechazado"
        confidence = "high" if prob_admitido >= 0.8 or prob_admitido <= 0.2 else \
                    "medium" if prob_admitido >= 0.65 or prob_admitido <= 0.35 else "low"

        return PredictionOutput(
            prediction=prediction,
            probability=round(prob_admitido, 3),
            confidence=confidence
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)