import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.stats import ttest_rel
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_loader import download_beijing_pm25, add_synthetic_drift, create_sequences
from src.model import SimpleGRU, train_model, predict
from src.utils import compute_metrics

WINDOW = 24
EPOCHS = 20
BATCH = 32
LR = 0.001
RESET_RATIO = 0.03
RESET_FREQ = 15
N_ITER = 30

print("Loading Beijing PM2.5 data...")
df_raw = download_beijing_pm25()
print(f"Data shape: {df_raw.shape}")

all_base_mse = []
all_prop_mse = []

for seed in tqdm(range(N_ITER)):
    np.random.seed(seed)
    df = add_synthetic_drift(df_raw.copy(), drift_point=0.7, drift_factor=1.3)
    X, y = create_sequences(df, window=WINDOW)
    if len(X) < 100:
        continue
    split = int(0.7 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train.reshape(-1,1)).reshape(X_train.shape)
    X_test_scaled = scaler.transform(X_test.reshape(-1,1)).reshape(X_test.shape)
    
    # Baseline
    model_base = SimpleGRU(input_size=1)
    train_model(model_base, X_train_scaled, y_train, epochs=EPOCHS, batch_size=BATCH, lr=LR)
    pred_base = predict(model_base, X_test_scaled)
    mse_base = compute_metrics(y_test, pred_base)['MSE']
    
    # Proposed
    model_prop = SimpleGRU(input_size=1)
    train_model(model_prop, X_train_scaled, y_train, epochs=EPOCHS, batch_size=BATCH, lr=LR,
                reset_every=RESET_FREQ, reset_ratio=RESET_RATIO)
    pred_prop = predict(model_prop, X_test_scaled)
    mse_prop = compute_metrics(y_test, pred_prop)['MSE']
    
    all_base_mse.append(mse_base)
    all_prop_mse.append(mse_prop)

base_mean = np.mean(all_base_mse)
base_std = np.std(all_base_mse)
prop_mean = np.mean(all_prop_mse)
prop_std = np.std(all_prop_mse)
t_stat, p_val = ttest_rel(all_base_mse, all_prop_mse)
improvement = (base_mean - prop_mean) / base_mean * 100

print("\n" + "="*60)
print("AIR QUALITY (PM2.5) PREDICTION WITH PERIODIC RESET (GRU)")
print(f"Iterations: {len(all_base_mse)}")
print(f"Baseline MSE: {base_mean:.6f} ± {base_std:.6f}")
print(f"Proposed MSE: {prop_mean:.6f} ± {prop_std:.6f}")
print(f"Improvement: {improvement:.2f}%")
print(f"Paired t-test: t={t_stat:.3f}, p={p_val:.4e}")

os.makedirs('../results', exist_ok=True)
df_res = pd.DataFrame({'mse_base': all_base_mse, 'mse_prop': all_prop_mse})
df_res.to_csv('../results/air_results.csv', index=False)

plt.figure(figsize=(6,5))
sns.boxplot(data=df_res[['mse_base', 'mse_prop']])
plt.xticks([0,1], ['Baseline', 'Proposed'])
plt.ylabel('MSE')
plt.title('Air Quality Prediction MSE Comparison (GRU)')
plt.savefig('../results/boxplot_air.png', dpi=300)
plt.show()