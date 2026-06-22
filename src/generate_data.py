"""Generate synthetic Bali cafe POS data for KopiKita analytics.

Realistic patterns:
- 6 months of transactions (Jan-Jun 2026)
- Indonesian + Western menu items at cafe-realistic prices (IDR)
- Time-of-day patterns (morning rush, lunch, afternoon coffee, dinner)
- Weekly seasonality (weekend bump)
- Weather proxy (occasional rainy days with reduced traffic)
- Customer segments (regulars vs walk-ins)
- Some seasonal variation (es kopi naik pas musim panas)

Output: data/transactions.csv (one row per transaction line item)
        data/customers.csv (customer master)
        data/menu.csv (menu master)
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)  # reproducible

# ============================================================================
# MASTERS
# ============================================================================

# Bali cafe menu — realistic IDR prices
MENU = [
    # Coffee
    {"id": "M001", "name": "Es Kopi Susu", "category": "Coffee", "price": 22000, "cost": 7000},
    {"id": "M002", "name": "Kopi Tubruk", "category": "Coffee", "price": 15000, "cost": 4000},
    {"id": "M003", "name": "Americano", "category": "Coffee", "price": 20000, "cost": 5000},
    {"id": "M004", "name": "Cappuccino", "category": "Coffee", "price": 28000, "cost": 8000},
    {"id": "M005", "name": "Latte", "category": "Coffee", "price": 28000, "cost": 8000},
    {"id": "M006", "name": "Es Kopi Gula Aren", "category": "Coffee", "price": 25000, "cost": 7500},
    # Non-coffee drinks
    {"id": "M010", "name": "Teh Manis Panas/Dingin", "category": "Tea", "price": 10000, "cost": 2000},
    {"id": "M011", "name": "Matcha Latte", "category": "Tea", "price": 28000, "cost": 9000},
    {"id": "M012", "name": "Es Jeruk", "category": "Juice", "price": 18000, "cost": 5000},
    {"id": "M013", "name": "Es Campur", "category": "Juice", "price": 20000, "cost": 6000},
    {"id": "M014", "name": "Coconut Water", "category": "Juice", "price": 15000, "cost": 5000},
    # Indonesian food
    {"id": "M020", "name": "Nasi Goreng", "category": "Food", "price": 35000, "cost": 12000},
    {"id": "M021", "name": "Mie Goreng", "category": "Food", "price": 32000, "cost": 10000},
    {"id": "M022", "name": "Bakso", "category": "Food", "price": 30000, "cost": 11000},
    {"id": "M023", "name": "Soto Ayam", "category": "Food", "price": 28000, "cost": 9000},
    {"id": "M024", "name": "Gado-Gado", "category": "Food", "price": 28000, "cost": 8000},
    {"id": "M025", "name": "Nasi Uduk Komplit", "category": "Food", "price": 30000, "cost": 10000},
    {"id": "M026", "name": "Ayam Geprek", "category": "Food", "price": 38000, "cost": 14000},
    # Snacks / pastry
    {"id": "M030", "name": "Croissant", "category": "Pastry", "price": 22000, "cost": 7000},
    {"id": "M031", "name": "Banana Bread", "category": "Pastry", "price": 25000, "cost": 8000},
    {"id": "M032", "name": "Pisang Goreng", "category": "Pastry", "price": 18000, "cost": 5000},
    {"id": "M033", "name": "Donut", "category": "Pastry", "price": 15000, "cost": 4000},
    {"id": "M034", "name": "Cookies (3 pcs)", "category": "Pastry", "price": 18000, "cost": 5000},
    # Add-on / modifier
    {"id": "M040", "name": "Extra Shot", "category": "AddOn", "price": 8000, "cost": 1500},
]

CATEGORIES = sorted({m["category"] for m in MENU})

# Customer segments
CUSTOMER_TYPES = ["regular", "walk_in", "tourist"]


def gen_customer_pool(n_regulars=120, n_walkins_count=4000):
    """Generate customer master + walk-in pseudo customers."""
    customers = []
    cid = 1
    # Regulars (have IDs, repeat visits)
    for _ in range(n_regulars):
        ctype = "regular"
        reg_date = datetime(2025, 6, 1) + timedelta(days=random.randint(0, 500))
        customers.append({
            "customer_id": f"C{cid:05d}",
            "type": ctype,
            "registered_at": reg_date.strftime("%Y-%m-%d"),
            "name": f"Regular #{cid:03d}",
        })
        cid += 1
    # Walk-ins (just IDs, no profile)
    for _ in range(n_walkins_count):
        customers.append({
            "customer_id": f"W{cid:06d}",
            "type": "walk_in",
            "registered_at": "",
            "name": "",
        })
        cid += 1
    return customers


# ============================================================================
# TRANSACTION GENERATION
# ============================================================================

# Hour-of-day weight (probability multiplier for a transaction in that hour)
HOUR_WEIGHTS = {
    7: 0.6, 8: 0.9, 9: 0.7,           # morning rush
    10: 0.4, 11: 0.5,
    12: 1.0, 13: 0.8,                  # lunch peak
    14: 0.4, 15: 0.5,
    16: 0.7, 17: 0.8,                  # afternoon coffee
    18: 0.9, 19: 0.8, 20: 0.6,         # dinner
    21: 0.3, 22: 0.1,
}

# Day-of-week multiplier (0=Monday ... 6=Sunday)
DOW_MULT = {
    0: 0.85, 1: 0.90, 2: 0.95, 3: 1.00, 4: 1.15,  # Thu rises, Fri biggest weekday
    5: 1.35,  # Saturday
    6: 1.20,  # Sunday
}

# Item probability weights (some items more popular)
ITEM_WEIGHTS = {
    "M001": 2.0, "M002": 1.0, "M003": 0.8, "M004": 1.2, "M005": 1.5, "M006": 1.8,
    "M010": 0.7, "M011": 0.9, "M012": 0.5, "M013": 0.3, "M014": 0.4,
    "M020": 1.5, "M021": 1.0, "M022": 1.2, "M023": 0.8, "M024": 0.5, "M025": 0.6, "M026": 1.3,
    "M030": 0.8, "M031": 0.5, "M032": 0.7, "M033": 0.4, "M034": 0.3,
    "M040": 0.2,
}

# Time-of-day item preferences (morning = more coffee, lunch = more food, etc)
HOUR_CATEGORY_BOOST = {
    "Coffee": {7: 1.8, 8: 2.0, 9: 1.8, 15: 1.5, 16: 1.5, 17: 1.5},
    "Tea": {7: 1.0, 15: 1.3, 16: 1.3},
    "Juice": {11: 1.5, 12: 1.5, 13: 1.5, 14: 1.5, 15: 2.0},
    "Food": {12: 2.0, 13: 2.0, 18: 1.8, 19: 1.8, 20: 1.5},
    "Pastry": {7: 1.5, 8: 1.5, 9: 1.5, 15: 1.3, 16: 1.3},
    "AddOn": {},  # just rare add-on
}


def is_rainy_day(d):
    """Pseudo-random rainfall based on date — Bali dry/wet season mix."""
    # Dry season Apr-Oct, wet Nov-Mar (synthetic)
    if d.month in (11, 12, 1, 2, 3):
        return random.random() < 0.45
    return random.random() < 0.15


def gen_day_txn_count(d):
    """Expected transactions for a day, based on weekday + month + weather."""
    base = 65  # avg weekday base
    mult = DOW_MULT[d.weekday()]
    # Holiday bumps: Indonesian holidays in first half of year
    if (d.month, d.day) in [(1, 1), (3, 7), (4, 10), (5, 1), (5, 14), (6, 1)]:
        mult *= 0.7  # some holidays = closed or low
    # Slight growth trend (cafe gaining popularity)
    months_since = (d.year - 2026) * 12 + d.month - 1
    growth = 1 + (months_since * 0.015)
    # Weather penalty
    if is_rainy_day(d):
        mult *= 0.7
    n = int(base * mult * growth)
    # Add noise
    n += random.randint(-8, 8)
    return max(20, n)


def gen_transactions_for_day(d, customers, regulars_list):
    """Yield (datetime, customer_id, line_items) for one day."""
    n_txns = gen_day_txn_count(d)
    # Pre-compute hour distribution
    hours = list(HOUR_WEIGHTS.keys())
    weights = list(HOUR_WEIGHTS.values())
    for _ in range(n_txns):
        hour = random.choices(hours, weights=weights)[0]
        minute = random.randint(0, 59)
        ts = d.replace(hour=hour, minute=minute, second=random.randint(0, 59))
        # 70% regulars (for the cafe's regulars), 30% walk-ins
        if regulars_list and random.random() < 0.6:
            customer = random.choice(regulars_list)
        else:
            customer = random.choice(customers)
        # Decide number of items (1-4)
        n_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.35, 0.15, 0.05])[0]
        items = []
        for _ in range(n_items):
            # Boost category by hour
            cat_boost = HOUR_CATEGORY_BOOST
            weights_adjusted = []
            for m in MENU:
                w = ITEM_WEIGHTS.get(m["id"], 0.5)
                for hour_match, mult in cat_boost.get(m["category"], {}).items():
                    if hour == hour_match:
                        w *= mult
                weights_adjusted.append(w)
            chosen = random.choices(MENU, weights=weights_adjusted)[0]
            qty = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            items.append({
                "menu_id": chosen["id"],
                "menu_name": chosen["name"],
                "category": chosen["category"],
                "unit_price": chosen["price"],
                "quantity": qty,
                "line_total": chosen["price"] * qty,
            })
        yield ts, customer["customer_id"], items


def main():
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    # Save menu
    with open(out_dir / "menu.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "name", "category", "price", "cost"])
        w.writeheader()
        for m in MENU:
            w.writerow(m)

    # Generate customer pool
    customers = gen_customer_pool(n_regulars=120, n_walkins_count=4000)
    regulars = [c for c in customers if c["type"] == "regular"]

    # Save customers (anonymized — no real PII)
    with open(out_dir / "customers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["customer_id", "type", "registered_at", "name"])
        w.writeheader()
        for c in customers:
            w.writerow(c)

    # Generate 6 months of transactions: Jan 1 - Jun 30, 2026
    start = datetime(2026, 1, 1)
    end = datetime(2026, 6, 30)
    txn_id = 1
    line_id = 1

    with open(out_dir / "transactions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "transaction_id", "timestamp", "customer_id", "customer_type",
            "menu_id", "menu_name", "category", "unit_price", "quantity", "line_total",
        ])
        w.writeheader()
        d = start
        while d <= end:
            # Inject an anomaly: ~3% of days have very low or very high sales
            for ts, cust_id, items in gen_transactions_for_day(d, customers, regulars):
                cust_type = next((c["type"] for c in customers if c["customer_id"] == cust_id), "walk_in")
                for it in items:
                    w.writerow({
                        "transaction_id": f"T{txn_id:06d}",
                        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "customer_id": cust_id,
                        "customer_type": cust_type,
                        "menu_id": it["menu_id"],
                        "menu_name": it["menu_name"],
                        "category": it["category"],
                        "unit_price": it["unit_price"],
                        "quantity": it["quantity"],
                        "line_total": it["line_total"],
                    })
                    line_id += 1
                txn_id += 1
            d += timedelta(days=1)

    print(f"Generated data in {out_dir}/")
    print(f"  menu.csv      — {len(MENU)} items across {len(CATEGORIES)} categories")
    print(f"  customers.csv — {len(customers)} customers ({len(regulars)} regulars, {len(customers)-len(regulars)} walk-ins)")
    print(f"  transactions.csv — {txn_id-1} transactions, {line_id-1} line items")


if __name__ == "__main__":
    main()
