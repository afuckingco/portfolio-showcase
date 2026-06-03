import pandas as pd
import numpy as np
import os
import requests
from zipfile import ZipFile

def generate_synthetic_pm25(periods=5000):
    """Generate synthetic PM2.5 data with daily and weekly patterns."""
    np.random.seed(42)
    t = np.arange(periods)
    daily = 30 * np.sin(2 * np.pi * t / 24)
    weekly = 15 * np.sin(2 * np.pi * t / (24 * 7))
    trend = 0.01 * t
    noise = 10 * np.random.randn(periods)
    pm25 = 50 + daily + weekly + trend + noise
    pm25 = np.clip(pm25, 0, 300)
    return pd.DataFrame({'pm25': pm25})

def download_beijing_pm25():
    os.makedirs("data", exist_ok=True)
    csv_path = "data/PRSA_data_2010.1.1-2014.12.31.csv"
    
    if not os.path.exists(csv_path):
        try:
            print("Downloading Beijing PM2.5 dataset...")
            url = "https://archive.ics.uci.edu/static/public/381/beijing+pm2+5+data.zip"
            zip_path = "data/beijing_pm25.zip"
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("data")
            print("Download complete.")
        except Exception as e:
            print(f"Download failed: {e}")
            print("Generating synthetic PM2.5 data instead.")
            return generate_synthetic_pm25()
    
    try:
        df = pd.read_csv(csv_path)
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
        df = df.set_index('datetime')
        df = df[['pm2.5']].copy()
        df.columns = ['pm25']
        df = df.resample('H').mean().dropna()
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return generate_synthetic_pm25()

def add_synthetic_drift(df, drift_point=0.7, drift_factor=1.3):
    df = df.copy()
    idx = int(len(df) * drift_point)
    df.iloc[idx:, 0] = df.iloc[idx:, 0] * drift_factor
    return df

def create_sequences(df, window=24):
    X, y = [], []
    data = df.values
    for i in range(len(data) - window):
        X.append(data[i:i+window])
        y.append(data[i+window])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)