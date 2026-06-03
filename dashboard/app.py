import streamlit as st
import numpy as np
import torch
import plotly.graph_objects as go
import joblib
import sys
import os

# Tambahkan path ke folder src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.model import SimpleLSTM

# Load model dan scaler (cached)
@st.cache_resource
def load_model_and_scaler():
    model_path = "models/bali_lstm_reset.pth"
    scaler_path = "models/scaler.pkl"
    model = SimpleLSTM(input_size=1, hidden_size=32)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    scaler = joblib.load(scaler_path)
    return model, scaler

model, scaler = load_model_and_scaler()

def predict(history):
    """history: list of 12 values in thousands"""
    if len(history) != 12:
        raise ValueError("Exactly 12 values required")
    input_array = np.array(history).reshape(-1, 1)
    input_scaled = scaler.transform(input_array).reshape(1, 12, 1)
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32)
    with torch.no_grad():
        pred_scaled = model(input_tensor).numpy().squeeze()
    pred = scaler.inverse_transform([[pred_scaled]]).squeeze()
    return pred

st.set_page_config(layout="wide")
st.title("🌴 Bali Tourism Arrival Forecast")

st.markdown("Enter the last 12 months of tourist arrivals **in thousands** (e.g., `450` = 450,000).")

default = [450, 480, 520, 600, 650, 700, 680, 720, 800, 850, 900, 950]
history_input = st.text_input("Enter 12 comma-separated values (in thousands):",
                              value=",".join(map(str, default)))

if st.button("Predict"):
    try:
        values = [float(x.strip()) for x in history_input.split(",")]
        if len(values) != 12:
            st.error("Please enter exactly 12 numbers.")
        else:
            pred = predict(values)
            st.success(f"Predicted arrivals for next month: **{pred:.0f} thousand** ({pred*1000:,.0f} persons)")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(range(1,13)), y=values,
                                     mode='lines+markers', name='Actual (last 12 months)'))
            fig.add_trace(go.Scatter(x=[13], y=[pred], mode='markers',
                                     marker=dict(size=15, color='red'), name='Prediction'))
            fig.update_layout(title='Tourist Arrivals (thousands)',
                              xaxis_title='Month', yaxis_title='Arrivals (thousands)')
            st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error: {e}")