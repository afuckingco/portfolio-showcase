import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def compute_metrics(y_true, y_pred):
    mse = np.mean((y_true - y_pred)**2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))
    return {'MSE': mse, 'RMSE': rmse, 'MAE': mae}

def paired_ttest(baseline_errors, proposed_errors):
    t_stat, p_val = stats.ttest_rel(baseline_errors, proposed_errors)
    return t_stat, p_val

def plot_comparison(y_test, pred_base, pred_prop, save_path='../results/air_comparison.png'):
    plt.figure(figsize=(12,5))
    plt.plot(y_test, label='Actual', color='black', linewidth=2)
    plt.plot(pred_base, label='Baseline (no reset)', linestyle='--')
    plt.plot(pred_prop, label='Proposed (periodic reset)', linestyle=':')
    plt.legend()
    plt.title('Air Quality (PM2.5) Prediction')
    plt.xlabel('Time step')
    plt.ylabel('PM2.5 (µg/m³)')
    plt.grid(alpha=0.3)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()