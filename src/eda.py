"""Exploratory Data Analysis for KopiKita synthetic cafe data.

Generates visualizations:
- Daily sales trend (line chart)
- Hourly heatmap of transactions
- Category breakdown (pie + bar)
- Top 10 menu items (horizontal bar)
- Day-of-week pattern
- Sales distribution histogram

Outputs to outputs/charts/
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["savefig.bbox"] = "tight"

DATA = Path("data")
OUT = Path("outputs/charts")
OUT.mkdir(parents=True, exist_ok=True)


def load():
    txns = pd.read_csv(DATA / "transactions.csv", parse_dates=["timestamp"])
    menu = pd.read_csv(DATA / "menu.csv")
    customers = pd.read_csv(DATA / "customers.csv")
    txns["date"] = txns["timestamp"].dt.date
    txns["hour"] = txns["timestamp"].dt.hour
    txns["dow"] = txns["timestamp"].dt.day_name()
    txns["month"] = txns["timestamp"].dt.to_period("M")
    return txns, menu, customers


def daily_sales(txns):
    daily = txns.groupby("date").agg(
        transactions=("transaction_id", "nunique"),
        revenue=("line_total", "sum"),
        items=("quantity", "sum"),
    ).reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["avg_basket"] = daily["revenue"] / daily["transactions"]

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    axes[0].plot(daily["date"], daily["revenue"], color="#2c5e3f", linewidth=1.5)
    axes[0].set_title("Daily Revenue — KopiKita (Jan–Jun 2026)", fontsize=14, fontweight="bold")
    axes[0].set_ylabel("Revenue (IDR)")
    axes[0].xaxis.set_major_locator(mdates.MonthLocator())
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    axes[1].bar(daily["date"], daily["transactions"], color="#8a5a44", width=1.0, alpha=0.7)
    axes[1].set_title("Daily Transaction Count", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("Transactions")
    axes[1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    plt.tight_layout()
    plt.savefig(OUT / "01_daily_sales.png")
    plt.close()
    print("✓ 01_daily_sales.png")
    return daily


def hourly_heatmap(txns):
    pivot = txns.groupby(["dow", "hour"]).size().unstack(fill_value=0)
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex(dow_order)
    fig, ax = plt.subplots(figsize=(14, 5))
    sns.heatmap(pivot, cmap="YlGnBu", ax=ax, cbar_kws={"label": "Transaction Count"})
    ax.set_title("Transaction Volume by Hour × Day-of-Week", fontsize=14, fontweight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(OUT / "02_hourly_heatmap.png")
    plt.close()
    print("✓ 02_hourly_heatmap.png")


def category_breakdown(txns):
    by_cat = txns.groupby("category").agg(
        items=("quantity", "sum"),
        revenue=("line_total", "sum"),
    ).reset_index().sort_values("revenue", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].pie(by_cat["revenue"], labels=by_cat["category"], autopct="%1.1f%%",
                colors=sns.color_palette("muted"), startangle=90)
    axes[0].set_title("Revenue Share by Category", fontsize=13, fontweight="bold")

    sns.barplot(data=by_cat, x="revenue", y="category", ax=axes[1], palette="muted", hue="category", legend=False)
    axes[1].set_title("Revenue by Category (IDR)", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("Revenue (IDR)")
    axes[1].set_ylabel("")
    plt.tight_layout()
    plt.savefig(OUT / "03_categories.png")
    plt.close()
    print("✓ 03_categories.png")


def top_items(txns, n=10):
    top = txns.groupby(["menu_id", "menu_name", "category"]).agg(
        qty=("quantity", "sum"),
        revenue=("line_total", "sum"),
    ).reset_index().sort_values("revenue", ascending=False).head(n)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top, x="revenue", y="menu_name", palette="viridis", hue="category", dodge=False, legend=True)
    ax.set_title(f"Top {n} Items by Revenue", fontsize=14, fontweight="bold")
    ax.set_xlabel("Revenue (IDR)")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(OUT / "04_top_items.png")
    plt.close()
    print("✓ 04_top_items.png")
    return top


def basket_distribution(txns):
    basket = txns.groupby("transaction_id")["line_total"].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(basket, bins=40, color="#5b8a72", edgecolor="white", alpha=0.85)
    ax.axvline(basket.median(), color="#c54b3c", linestyle="--", linewidth=2,
               label=f"Median: Rp {basket.median():,.0f}")
    ax.set_title("Distribution of Basket Size (per Transaction)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Basket Total (IDR)")
    ax.set_ylabel("Number of Transactions")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT / "05_basket_distribution.png")
    plt.close()
    print("✓ 05_basket_distribution.png")
    print(f"  Stats: median Rp {basket.median():,.0f}, mean Rp {basket.mean():,.0f}, p90 Rp {basket.quantile(0.9):,.0f}")


def customer_type_mix(txns):
    by_type = txns.groupby("customer_type").agg(
        txns=("transaction_id", "nunique"),
        revenue=("line_total", "sum"),
    ).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].pie(by_type["txns"], labels=by_type["customer_type"], autopct="%1.1f%%",
                colors=["#2c5e3f", "#c89666", "#8a5a44"], startangle=90)
    axes[0].set_title("Transaction Share", fontsize=12, fontweight="bold")
    axes[1].pie(by_type["revenue"], labels=by_type["customer_type"], autopct="%1.1f%%",
                colors=["#2c5e3f", "#c89666", "#8a5a44"], startangle=90)
    axes[1].set_title("Revenue Share", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(OUT / "06_customer_mix.png")
    plt.close()
    print("✓ 06_customer_mix.png")


def main():
    print("Loading data...")
    txns, menu, customers = load()
    print(f"  {len(txns):,} line items, {txns['transaction_id'].nunique():,} transactions\n")

    print("Generating charts...")
    daily = daily_sales(txns)
    hourly_heatmap(txns)
    category_breakdown(txns)
    top = top_items(txns)
    basket_distribution(txns)
    customer_type_mix(txns)

    # Save daily summary for downstream use
    daily.to_csv("outputs/daily_summary.csv", index=False)
    print(f"\nDaily summary saved → outputs/daily_summary.csv")

    # Quick text report
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)
    print(f"Date range:        {daily['date'].min().date()} to {daily['date'].max().date()}")
    print(f"Days covered:      {len(daily)}")
    print(f"Total revenue:     Rp {daily['revenue'].sum():,.0f}")
    print(f"Avg daily revenue: Rp {daily['revenue'].mean():,.0f}")
    print(f"Total transactions:{daily['transactions'].sum():,}")
    print(f"Avg daily txns:    {daily['transactions'].mean():.0f}")
    print(f"Avg basket:        Rp {daily['avg_basket'].mean():,.0f}")
    print(f"\nTop 5 items by revenue:")
    for _, row in top.head(5).iterrows():
        print(f"  {row['menu_name']:<25} Rp {row['revenue']:>10,.0f}  ({row['qty']:,} sold)")


if __name__ == "__main__":
    main()
