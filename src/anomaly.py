"""Anomaly detection on daily sales.

Two methods:
1. Statistical: z-score on rolling 14-day mean (>2σ flagged)
2. ML: Isolation Forest (multivariate — revenue + transactions + items)

Outputs:
- outputs/anomalies.csv — flagged days with scores
- outputs/charts/11_anomalies.png — overlay of anomalies on revenue line
"""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.ensemble import IsolationForest
from pathlib import Path

OUT = Path("outputs/charts")
OUT.mkdir(parents=True, exist_ok=True)


def load_daily():
    df = pd.read_csv("data/transactions.csv", parse_dates=["timestamp"])
    daily = df.groupby(df["timestamp"].dt.date).agg(
        revenue=("line_total", "sum"),
        transactions=("transaction_id", "nunique"),
        items=("quantity", "sum"),
    ).reset_index()
    daily.columns = ["date", "revenue", "transactions", "items"]
    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values("date").reset_index(drop=True)


def zscore_anomalies(daily, window=14, threshold=2.0):
    daily["rolling_mean"] = daily["revenue"].rolling(window=window, min_periods=7).mean()
    daily["rolling_std"] = daily["revenue"].rolling(window=window, min_periods=7).std()
    daily["zscore"] = (daily["revenue"] - daily["rolling_mean"]) / (daily["rolling_std"] + 1e-9)
    daily["z_anomaly"] = daily["zscore"].abs() > threshold
    return daily


def isolation_forest_anomalies(daily, contamination=0.05):
    features = daily[["revenue", "transactions", "items"]].values
    iso = IsolationForest(contamination=contamination, random_state=42)
    daily["if_label"] = iso.fit_predict(features)
    daily["if_score"] = iso.decision_function(features)
    daily["if_anomaly"] = daily["if_label"] == -1
    return daily


def plot_anomalies(daily):
    anomalies = daily[daily["z_anomaly"] | daily["if_anomaly"]]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(daily["date"], daily["revenue"], color="#2c5e3f", linewidth=1.5, label="Daily revenue")
    ax.plot(daily["date"], daily["rolling_mean"], color="#8a5a44", linewidth=1.2,
            linestyle="--", alpha=0.7, label="14-day rolling mean")

    # Highlight anomalies with red dots, label by which method caught it
    z_only = daily[daily["z_anomaly"] & ~daily["if_anomaly"]]
    if_only = daily[~daily["z_anomaly"] & daily["if_anomaly"]]
    both = daily[daily["z_anomaly"] & daily["if_anomaly"]]
    ax.scatter(z_only["date"], z_only["revenue"], color="#e8a838", s=70, zorder=5,
               label=f"Z-score only ({len(z_only)})", edgecolors="black", linewidth=0.5)
    ax.scatter(if_only["date"], if_only["revenue"], color="#c54b3c", s=70, zorder=5,
               label=f"Isolation Forest only ({len(if_only)})", edgecolors="black", linewidth=0.5)
    ax.scatter(both["date"], both["revenue"], color="#7d1538", s=100, zorder=6, marker="X",
               label=f"Both methods ({len(both)})", edgecolors="black", linewidth=0.5)

    ax.set_title("Anomaly Detection — Daily Revenue (Jan–Jun 2026)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Revenue (IDR)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(OUT / "11_anomalies.png")
    plt.close()
    print("✓ 11_anomalies.png")


def main():
    print("Loading daily data...")
    daily = load_daily()
    print(f"  {len(daily)} days\n")

    print("Z-score method (|z| > 2 on 14-day rolling)...")
    daily = zscore_anomalies(daily, window=14, threshold=2.0)
    n_z = daily["z_anomaly"].sum()
    print(f"  Flagged: {n_z} days ({n_z/len(daily)*100:.1f}%)")

    print("\nIsolation Forest (multivariate, contamination=5%)...")
    daily = isolation_forest_anomalies(daily, contamination=0.05)
    n_if = daily["if_anomaly"].sum()
    print(f"  Flagged: {n_if} days ({n_if/len(daily)*100:.1f}%)")

    n_both = (daily["z_anomaly"] & daily["if_anomaly"]).sum()
    n_either = (daily["z_anomaly"] | daily["if_anomaly"]).sum()
    print(f"  Overlap (both methods): {n_both} days")
    print(f"  Union (either method): {n_either} days")

    # Save
    export_cols = ["date", "revenue", "transactions", "items", "rolling_mean",
                   "zscore", "z_anomaly", "if_score", "if_anomaly"]
    daily[export_cols].to_csv("outputs/anomalies.csv", index=False)
    print("\nSaved → outputs/anomalies.csv")

    plot_anomalies(daily)

    # Top anomalies (most extreme)
    print("\nTop 5 most anomalous days (by Isolation Forest score):")
    top = daily.nsmallest(5, "if_score")[["date", "revenue", "transactions", "items", "if_score", "zscore"]]
    for _, row in top.iterrows():
        print(f"  {row['date'].date()}  Rp {row['revenue']:>10,.0f}  "
              f"txns={int(row['transactions'])}  if_score={row['if_score']:.2f}  z={row['zscore']:+.2f}")


if __name__ == "__main__":
    main()
