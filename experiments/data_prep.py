import pandas as pd
import numpy as np
import os

def generate_synthetic_tourism_data(periods=120):
    np.random.seed(42)
    t = np.arange(periods)
    seasonal = 200 * np.sin(2 * np.pi * t / 12)   # dalam ribuan
    trend = 5 * t                                 # dalam ribuan
    noise = 50 * np.random.randn(periods)         # dalam ribuan
    arrivals = 500 + seasonal + trend + noise     # dalam ribuan (base 500 ribu)
    arrivals = np.clip(arrivals, 100, 2000)       # batasan wajar
    df = pd.DataFrame({'date': pd.date_range('2010-01-01', periods=periods, freq='ME'),
                       'arrivals': arrivals.astype(int)})
    return df

def load_real_data():
    """Try to load real BPS data if available, else generate synthetic."""
    csv_path = os.path.join('data', 'bali_tourism.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=['date'])
        return df
    else:
        print("Real data not found. Generating synthetic data.")
        return generate_synthetic_tourism_data()

def create_sequences(df, window=12, target='arrivals'):
    """Create sequences for LSTM."""
    data = df[target].values.reshape(-1,1)
    X, y = [], []
    for i in range(len(data)-window):
        X.append(data[i:i+window])
        y.append(data[i+window])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)