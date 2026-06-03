import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
import joblib

from src.model import SimpleLSTM, train_model
from experiments.data_prep import load_real_data, create_sequences

WINDOW = 12
EPOCHS = 50
BATCH = 32
LR = 0.001
RESET_RATIO = 0.03
RESET_FREQ = 15

def main():
    df = load_real_data()
    print(f"Data shape: {df.shape}")
    
    X, y = create_sequences(df, window=WINDOW)
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train.reshape(-1, 1)).reshape(X_train.shape)
    X_test_scaled = scaler.transform(X_test.reshape(-1, 1)).reshape(X_test.shape)
    
    model = SimpleLSTM(input_size=1, hidden_size=32)
    model = train_model(model, X_train_scaled, y_train,
                        epochs=EPOCHS, batch_size=BATCH, lr=LR,
                        reset_every=RESET_FREQ, reset_ratio=RESET_RATIO)
    
    os.makedirs('../models', exist_ok=True)
    torch.save(model.state_dict(), '../models/bali_lstm_reset.pth')
    joblib.dump(scaler, '../models/scaler.pkl')
    print("Model saved to models/bali_lstm_reset.pth")
    
    model.eval()
    with torch.no_grad():
        X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
        pred = model(X_test_t).numpy().squeeze()
        mse = np.mean((pred - y_test)**2)
        print(f"Test MSE: {mse:.4f}")

if __name__ == '__main__':
    main()