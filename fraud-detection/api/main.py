from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os

app = FastAPI(title="Fraud Detection API")

model_path = "models/fraud_model.pkl"
scaler_path = "models/scaler.pkl"

if not os.path.exists(model_path):
    raise RuntimeError("Model not found. Run train.py first.")

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

class Transaction(BaseModel):
    features: list  # 30 fitur (semua kolom kecuali Class)

@app.get("/")
def root():
    return {"message": "Fraud Detection API - use /predict endpoint with POST"}

@app.post("/predict")
def predict(transaction: Transaction):
    try:
        if len(transaction.features) != 30:
            raise HTTPException(status_code=400, detail="Exactly 30 features required")
        X = np.array(transaction.features).reshape(1, -1)
        X_scaled = scaler.transform(X)
        pred = int(model.predict(X_scaled)[0])
        proba = float(model.predict_proba(X_scaled)[0][1])
        return {"fraud": pred, "probability": proba}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))