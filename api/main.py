"""API REST para predicción de admisiones universitarias usando ML.

Este módulo proporciona endpoints para predecir la probabilidad de admisión
de estudiantes basándose en características demográficas y académicas.
"""

from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import uvicorn

app = FastAPI(
    title="Admissions Scoring API",
    description="ML-powered admission prediction service",
    version="1.0.0"
)

# Load model at startup
model = joblib.load("models/rf_model.pkl")

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
        # Preprocess input
        df = pd.DataFrame([applicant.dict()])
        
        # Feature engineering (match training pipeline)
        df["nota_normalizada"] = (df["nota_media"] - 5) / 5
        df["es_extranjero"] = df["pais_nacimiento"] != "España"
        
        # Encode categoricals (simplified - use actual mappings from training)
        pais_mapping = {"España": 0, "México": 1, "Colombia": 2}  # etc
        programa_mapping = {"Ingeniería Informática": 0, "ADE": 1}  # etc
        
        df["pais_idx"] = df["pais_nacimiento"].map(pais_mapping).fillna(-1)
        df["programa_idx"] = df["programa"].map(programa_mapping).fillna(-1)
        
        # Select features
        feature_cols = ["edad", "nota_normalizada", "pais_idx", "programa_idx", 
                       "es_extranjero", "solicita_beca"]
        X = df[feature_cols]
        
        # Predict
        proba = model.predict_proba(X)[0]
        prediction = "admitido" if proba[1] >= 0.5 else "rechazado"
        confidence = "high" if max(proba) >= 0.8 else "medium" if max(proba) >= 0.6 else "low"
        
        return PredictionOutput(
            prediction=prediction,
            probability=round(float(proba[1]), 3),
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)