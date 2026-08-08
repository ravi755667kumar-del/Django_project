"""
dataset.py  —  Build / append the recommendation CSV.

Can be used in two ways:
  A) Called from views.py automatically after every order (recommended).
  B) Run standalone from terminal to rebuild the full dataset:
       python shop/recommendations/dataset.py
"""

import os
import sys
import pandas as pd

# ─── Make sure Django is set up when run as a standalone script ───────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django                      # noqa: E402
from django.conf import settings   # noqa: E402
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tea.settings")
    django.setup()

# ─── Imports (after django.setup) ────────────────────────────────────────────
from shop.models import Order_data                    # noqa: E402
from shop.recommendations.weather import get_weather  # noqa: E402

# ─── CSV path ─────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")


# =============================================================================
# Main function — called from views.py after every order
# =============================================================================
def update_dataset():
    """
    Rebuild the full dataset.csv from all Order_data rows + live weather.
    Safe to call from Django views (no django.setup() needed there).
    """

    # ── Fetch live weather ────────────────────────────────────────────────────
    weather_info = get_weather()
    weather      = weather_info.get("weather",     "Unknown")
    category     = weather_info.get("category",    "Normal")
    temperature  = weather_info.get("temperature", 0)
    humidity     = weather_info.get("humidity",    0)
    city         = weather_info.get("city",        "Unknown")

    # ── Fetch all orders from DB ──────────────────────────────────────────────
    orders = Order_data.objects.select_related("customer").all()

    data = []
    for order in orders:

        customer_name = order.customer.name if order.customer_id else "Unknown"

        order_date = order.Order_data_date.date() if order.Order_data_date else None
        order_time = order.Order_data_date.time() if order.Order_data_date else None

        data.append({
            "customer":    customer_name,
            "item_name":   order.item_name,
            "price":       float(order.price),
            "quantity":    order.quantity,
            "mobile":      order.mobile,
            "date":        order_date,
            "time":        order_time,
            # ── Weather columns ──────────────────────────────────────────────
            "city":        city,
            "weather":     weather,
            "category":    category,
            "temperature": temperature,
            "humidity":    humidity,
        })

    # ── Save to CSV ───────────────────────────────────────────────────────────
    df = pd.DataFrame(data)
    df.to_csv(CSV_PATH, index=False)

    print(f"[dataset] Updated -> {CSV_PATH}  ({len(df)} rows)")
    return df


# =============================================================================
# Standalone run — rebuild from scratch
# =============================================================================
if __name__ == "__main__":
    df = update_dataset()
    print(df.head())