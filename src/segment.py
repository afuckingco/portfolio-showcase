"""Customer segmentation using RFM (Recency, Frequency, Monetary) + KMeans.

RFM framework:
- Recency:   days since last purchase
- Frequency: number of transactions in window
- Monetary:  total spend

Workflow:
1. Compute RFM per customer (regulars only — walk-ins have no identity)
2. Standardize features
3. KMeans clustering (k=4)
4. Profile clusters with descriptive labels

Outputs:
- outputs/customer_segments.csv — RFM + cluster per customer
- outputs/charts/09_rfm_clusters.png — 3D scatter of RFM
- outputs/charts/10_segment_profiles.png — radar chart per cluster
"""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pathlib import Path

OUT = Path("outputs/charts")
OUT.mkdir(parents=True, exist_ok=True)


def compute_rfm():
    df = pd.read_csv("data/transactions.csv", parse_dates=["timestamp"])
    customers = pd.read_csv("data/customers.csv")

    # Filter to regulars (have identity, repeat visits)
    regular_ids = customers.loc[customers["type"] == "regular", "customer_id"].tolist()
    rfm = df[df["customer_id"].isin(regular_ids)].copy()

    snapshot_date = df["timestamp"].max() + pd.Timedelta(days=1)

    rfm_agg = rfm.groupby("customer_id").agg(
        last_purchase=("timestamp", "max"),
        frequency=("transaction_id", "nunique"),
        monetary=("line_total", "sum"),
    ).reset_index()
    rfm_agg["recency_days"] = (snapshot_date - rfm_agg["last_purchase"]).dt.days
    rfm_agg = rfm_agg[["customer_id", "recency_days", "frequency", "monetary"]]
    return rfm_agg


def find_optimal_k(rfm_scaled, k_range=range(2, 8)):
    inertias = []
    silhouettes = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(rfm_scaled)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(rfm_scaled, labels))
    return inertias, silhouettes


def cluster_and_label(rfm, k=4):
    scaler = StandardScaler()
    X = rfm[["recency_days", "frequency", "monetary"]].values
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    rfm_out = rfm.copy()
    rfm_out["cluster"] = labels

    # Profile clusters
    profile = rfm_out.groupby("cluster").agg(
        n_customers=("customer_id", "count"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
    ).reset_index()

    # Compute percentile ranks for each metric to label reliably
    medians = profile[["avg_recency", "avg_frequency", "avg_monetary"]].median()

    def label(row, medians):
        high_freq = row["avg_frequency"] > medians["avg_frequency"]
        high_mon = row["avg_monetary"] > medians["avg_monetary"]
        low_rec = row["avg_recency"] < medians["avg_recency"]
        # 4-bin classification
        if high_freq and high_mon and low_rec:
            return "Champions"
        if low_rec and not high_freq:
            return "New / Occasional"
        if not low_rec and high_freq and high_mon:
            return "At Risk (was valuable)"
        if not low_rec and not high_freq:
            return "Dormant"
        # Fallback to monetary-based
        if high_mon:
            return "High Spenders"
        return "Average"

    profile["segment_name"] = profile.apply(lambda r: label(r, medians), axis=1)
    return rfm_out, profile, scaler


def plot_3d(rfm):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    segments = rfm["segment_name"].unique()
    colors = plt.cm.Set2(np.linspace(0, 1, len(segments)))
    for seg, color in zip(segments, colors):
        sub = rfm[rfm["segment_name"] == seg]
        ax.scatter(sub["recency_days"], sub["frequency"], sub["monetary"],
                   label=seg, color=color, s=40, alpha=0.7, edgecolors="white")
    ax.set_xlabel("Recency (days)")
    ax.set_ylabel("Frequency")
    ax.set_zlabel("Monetary (Rp)")
    ax.set_title("RFM Customer Segments — 3D View", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", bbox_to_anchor=(1.1, 1.0))
    plt.tight_layout()
    plt.savefig(OUT / "09_rfm_clusters.png")
    plt.close()
    print("✓ 09_rfm_clusters.png")


def plot_profiles(profile):
    metrics = ["avg_recency", "avg_frequency", "avg_monetary"]
    # Normalize each metric to 0-1 for radar comparability
    norm = profile[metrics].copy()
    for m in metrics:
        norm[m] = (norm[m] - norm[m].min()) / (norm[m].max() - norm[m].min() + 1e-9)
    norm["segment_name"] = profile["segment_name"]

    fig, ax = plt.subplots(figsize=(9, 7), subplot_kw=dict(polar=True))
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    colors = plt.cm.Set2(np.linspace(0, 1, len(profile)))
    for i, (_, row) in enumerate(norm.iterrows()):
        values = row[metrics].tolist()
        values += values[:1]
        ax.plot(angles, values, label=row["segment_name"], color=colors[i], linewidth=2)
        ax.fill(angles, values, color=colors[i], alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(["Recency (inv)", "Frequency", "Monetary"])
    ax.set_ylim(0, 1.1)
    ax.set_title("Segment Profiles (normalized)", fontsize=14, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
    plt.tight_layout()
    plt.savefig(OUT / "10_segment_profiles.png")
    plt.close()
    print("✓ 10_segment_profiles.png")


def main():
    print("Computing RFM features...")
    rfm = compute_rfm()
    print(f"  {len(rfm)} regular customers")

    scaler = StandardScaler()
    X = scaler.fit_transform(rfm[["recency_days", "frequency", "monetary"]].values)

    print("Finding optimal k (silhouette analysis)...")
    inertias, silhouettes = find_optimal_k(X)
    best_k = np.argmax(silhouettes) + 2
    print(f"  Best k by silhouette: {best_k} (silhouette = {max(silhouettes):.3f})")

    print("Clustering with k=4...")
    rfm_out, profile, _ = cluster_and_label(rfm, k=4)

    # Save
    rfm_out.to_csv("outputs/customer_segments.csv", index=False)
    profile.to_csv("outputs/segment_profiles.csv", index=False)
    print("Saved → outputs/customer_segments.csv, outputs/segment_profiles.csv")

    # Plots
    plot_3d(rfm_out.merge(profile[["cluster", "segment_name"]], on="cluster"))
    plot_profiles(profile)

    # Report
    print("\n" + "=" * 70)
    print("SEGMENT PROFILES")
    print("=" * 70)
    for _, row in profile.iterrows():
        print(f"\n  {row['segment_name']}  (cluster {int(row['cluster'])})")
        print(f"    Customers:  {int(row['n_customers'])}")
        print(f"    Avg recency: {row['avg_recency']:.0f} days since last visit")
        print(f"    Avg frequency: {row['avg_frequency']:.1f} transactions / 6 months")
        print(f"    Avg monetary: Rp {row['avg_monetary']:,.0f}")
        print(f"    Total revenue contribution: Rp {row['total_monetary']:,.0f}")


if __name__ == "__main__":
    main()
