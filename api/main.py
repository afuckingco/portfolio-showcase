from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import torch
import joblib
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.model import SimpleLSTM

app = FastAPI(title="Bali Tourism Forecast API")

model_path = "models/bali_lstm_reset.pth"
scaler_path = "models/scaler.pkl"

if not os.path.exists(model_path):
    raise RuntimeError("Model not found. Train first using experiments/train.py")

model = SimpleLSTM(input_size=1, hidden_size=32)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()
scaler = joblib.load(scaler_path)

class InputData(BaseModel):
    history: list  # list of 12 monthly arrivals

@app.get("/")
def root():
    return {"message": "Bali Tourism Forecast API - Use /predict endpoint with POST"}

@app.post("/predict")
def predict(data: InputData):
    if len(data.history) != 12:
        raise HTTPException(status_code=400, detail="History must contain exactly 12 values")
    
    input_array = np.array(data.history).reshape(-1, 1)
    input_scaled = scaler.transform(input_array).reshape(1, 12, 1)
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32)
    
    with torch.no_grad():
        prediction_scaled = model(input_tensor).numpy().squeeze()
    
    pred_array = np.array([[prediction_scaled]])
    prediction = scaler.inverse_transform(pred_array).squeeze()
    
    return {"prediction": float(prediction)}