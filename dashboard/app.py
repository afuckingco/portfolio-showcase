import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🌴 Bali Tourism Arrival Forecast")

st.markdown("""
Enter the last 12 months of tourist arrivals **in thousands** (e.g., 450 = 450,000).
""")

default_history = [450, 480, 520, 600, 650, 700, 680, 720, 800, 850, 900, 950]
history = st.text_input("Enter 12 comma-separated values (in thousands):", 
                        value=",".join(map(str, default_history)))

if st.button("Predict"):
    try:
        values = [float(x.strip()) for x in history.split(",")]
        if len(values) != 12:
            st.error("Please enter exactly 12 numbers.")
        else:
            # Kirim langsung ke API (model sekarang pakai ribuan)
            api_url = "http://localhost:8000/predict"
            response = requests.post(api_url, json={"history": values})
            if response.status_code == 200:
                pred = response.json()["prediction"]
                st.success(f"Predicted arrivals for next month: **{pred:.0f} thousand** ({pred*1000:,.0f} persons)")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(range(1,13)), y=values, mode='lines+markers', name='Actual (last 12 months)'))
                fig.add_trace(go.Scatter(x=[13], y=[pred], mode='markers', marker=dict(size=15, color='red'), name='Prediction'))
                fig.update_layout(title='Tourist Arrivals (thousands)', xaxis_title='Month', yaxis_title='Arrivals (thousands)')
                st.plotly_chart(fig)
            else:
                st.error(f"API error: {response.text}")
    except Exception as e:
        st.error(f"Error: {e}")