"""Daily revenue forecasting using Prophet.

Trains on first 5 months, predicts next month. Compares to actual (last month held-out)
and computes MAPE.

Outputs:
- outputs/charts/07_forecast.png — actual vs predicted with uncertainty interval
- outputs/predictions/forecast.csv — daily predictions with yhat, yhat_lower, yhat_upper
"""
import warnings
warnings.filterwarnings("ignore")  # Prophet + sklearn chatter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error
from pathlib import Path

OUT = Path("outputs/charts")
PRED = Path("outputs/predictions")
OUT.mkdir(parents=True, exist_ok=True)
PRED.mkdir(parents=True, exist_ok=True)


def load_daily():
    df = pd.read_csv("data/transactions.csv", parse_dates=["timestamp"])
    daily = df.groupby(df["timestamp"].dt.date).agg(
        revenue=("line_total", "sum"),
        transactions=("transaction_id", "nunique"),
    ).reset_index()
    daily.columns = ["ds", "y", "transactions"]
    daily["ds"] = pd.to_datetime(daily["ds"])
    return daily.sort_values("ds").reset_index(drop=True)


def train_test_split(daily, test_days=30):
    train = daily.iloc[:-test_days].copy()
    test = daily.iloc[-test_days:].copy()
    return train, test


def fit_prophet(train):
    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,  # only 6 months of data
        changepoint_prior_scale=0.05,
        seasonality_mode="multiplicative",  # cafe sales scale with day-of-week
        interval_width=0.80,
    )
    m.fit(train[["ds", "y"]])
    return m


def evaluate(model, train, test):
    future = model.make_future_dataframe(periods=len(test), freq="D")
    forecast = model.predict(future)
    # Use the test portion
    pred_test = forecast.set_index("ds").loc[test["ds"].values][["yhat", "yhat_lower", "yhat_upper"]].reset_index()
    pred_test = pred_test.rename(columns={"index": "ds"})
    y_true = test["y"].values
    y_pred = pred_test["yhat"].values

    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    mae = mean_absolute_error(y_true, y_pred)
    # Avg % error relative to mean
    pct_error = mae / y_true.mean() * 100
    return pred_test, mape, mae, pct_error


def plot_forecast(train, test, pred_test, model):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(train["ds"], train["y"], label="Train (Jan–May)", color="#2c5e3f", linewidth=1.5)
    ax.plot(test["ds"], test["y"], label="Actual (Jun)", color="#2c5e3f", linewidth=2, alpha=0.5, linestyle="--")
    ax.plot(pred_test["ds"], pred_test["yhat"], label="Prophet forecast", color="#c54b3c", linewidth=2)
    ax.fill_between(pred_test["ds"], pred_test["yhat_lower"], pred_test["yhat_upper"],
                    color="#c54b3c", alpha=0.2, label="80% confidence interval")
    ax.set_title("KopiKita Daily Revenue — Prophet Forecast vs Actual", fontsize=14, fontweight="bold")
    ax.set_ylabel("Revenue (IDR)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(OUT / "07_forecast.png")
    plt.close()
    print("✓ 07_forecast.png")


def main():
    print("Loading daily revenue...")
    daily = load_daily()
    print(f"  {len(daily)} days, Rp {daily['y'].sum():,.0f} total revenue\n")

    print("Train/test split (5 months train, last month test)...")
    train, test = train_test_split(daily, test_days=30)
    print(f"  Train: {len(train)} days ({train['ds'].min().date()} to {train['ds'].max().date()})")
    print(f"  Test:  {len(test)} days ({test['ds'].min().date()} to {test['ds'].max().date()})\n")

    print("Fitting Prophet model...")
    model = fit_prophet(train)

    print("Evaluating on test set...")
    pred_test, mape, mae, pct_error = evaluate(model, train, test)
    print(f"  MAPE: {mape:.2f}%")
    print(f"  MAE:  Rp {mae:,.0f}")
    print(f"  Avg error: {pct_error:.2f}% of mean revenue\n")

    # Save predictions
    pred_test.to_csv(PRED / "forecast.csv", index=False)
    print(f"Predictions saved → {PRED / 'forecast.csv'}")

    # Plot
    plot_forecast(train, test, pred_test, model)

    # Forecast future (next 30 days beyond data)
    print("\nForecasting next 30 days (Jul 2026 projection)...")
    future = model.make_future_dataframe(periods=len(test) + 30, freq="D")
    full_fc = model.predict(future)
    future_only = full_fc[full_fc["ds"] > daily["ds"].max()][["ds", "yhat", "yhat_lower", "yhat_upper"]]
    future_only.to_csv(PRED / "future_forecast.csv", index=False)
    print(f"  Next 30 days projection saved → {PRED / 'future_forecast.csv'}")
    print(f"  Projected avg daily revenue: Rp {future_only['yhat'].mean():,.0f}")

    # Component plot (weekly + yearly seasonality)
    fig2 = model.plot_components(model.predict(future))
    plt.tight_layout()
    plt.savefig(OUT / "08_forecast_components.png")
    plt.close("all")
    print("✓ 08_forecast_components.png")


if __name__ == "__main__":
    main()
