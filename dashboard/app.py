import streamlit as st
import pandas as pd
import joblib
import numpy as np

st.set_page_config(page_title="Fraud Detection", layout="wide")
st.title("💳 Credit Card Fraud Detection")

@st.cache_resource
def load_model():
    model = joblib.load('models/fraud_model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    return model, scaler

model, scaler = load_model()

st.markdown("""
Upload a CSV file containing the **30 features** (same as the dataset without the 'Class' column).  
If your file includes the 'Class' column, it will be automatically removed.
""")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Jika kolom 'Class' ada, hapus (karena ini target, bukan fitur)
    if 'Class' in df.columns:
        df = df.drop('Class', axis=1)
        st.info("Removed 'Class' column (target) from the uploaded file.")
    
    if df.shape[1] != 30:
        st.error(f"File has {df.shape[1]} columns after processing. Expected exactly 30 features.")
    else:
        with st.spinner("Predicting..."):
            X = scaler.transform(df.values)
            preds = model.predict(X)
            probas = model.predict_proba(X)[:,1]
        
        df_result = df.copy()
        df_result['fraud_prediction'] = preds
        df_result['fraud_probability'] = probas
        
        fraud_count = preds.sum()
        fraud_percent = fraud_count / len(preds) * 100
        
        col1, col2 = st.columns(2)
        col1.metric("Total Transactions", len(preds))
        col2.metric("Fraud Detected", f"{fraud_count} ({fraud_percent:.2f}%)")
        
        st.subheader("Fraudulent Transactions")
        st.dataframe(df_result[df_result['fraud_prediction'] == 1])
        
        st.subheader("All Predictions (first 100)")
        st.dataframe(df_result.head(100))