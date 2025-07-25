# File: api/main.py

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from typing import List
import uvicorn

app = FastAPI(
    title="Admissions Scoring API",
    description="ML-powered admission prediction service",
    version="1.0.0"
)

# Load model at startup
model = joblib.load("models/admission_model.pkl")

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
def root():
    return {"message": "Admissions Scoring API", "status": "active"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionOutput)
def predict(applicant: ApplicantInput):
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