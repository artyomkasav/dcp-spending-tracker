
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "data" / "spendings.csv"
CHARTS_DIR = PROJECT_DIR / "charts"

CHARTS_DIR.mkdir(exist_ok=True)

# Load and prepare data
df = pd.read_csv(CSV_PATH)
df["date"] = pd.to_datetime(df["date"])
df["amount"] = pd.to_numeric(df["amount"])

print("====== SPENDING TRACKER ANALYSIS ======")

# General statistics
print(f"\nNumber of purchases: {len(df)}")
print(f"Total spending: €{df['amount'].sum():.2f}")
print(f"Average purchase: €{df['amount'].mean():.2f}")
print(f"Most expensive purchase: €{df['amount'].max():.2f}")

# Spending by shop
shop_spending = df.groupby("shop")["amount"].sum()
shop_spending = shop_spending.sort_values(ascending=False)

print("\n--- SPENDING BY SHOP ---")
print(shop_spending.round(2))

# Spending by category
category_spending = df.groupby("category")["amount"].sum()
category_spending = category_spending.sort_values(ascending=False)

print("\n--- SPENDING BY CATEGORY ---")
print(category_spending.round(2))

# Needs vs Wants
need_want_spending = df.groupby("need_want")["amount"].sum()

print("\n--- NEEDS VS WANTS ---")
print(need_want_spending.round(2))

# Spending by payment method
payment_spending = df.groupby("payment_method")["amount"].sum()

print("\n--- PAYMENT METHODS ---")
print(payment_spending.round(2))

# Spending by date
daily_spending = df.groupby("date")["amount"].sum()

print("\n--- DAILY SPENDING ---")
print(daily_spending.round(2))

# Top 10 most expensive individual purchases
top_purchases = df.nlargest(10, "amount")

print("\n--- TOP 10 MOST EXPENSIVE PURCHASES ---")
print(top_purchases[["date", "item", "shop", "amount"]].to_string(index=False))


# Chart 1: Spending by shop
plt.figure(figsize=(9, 5))
shop_spending.plot(kind="bar")
plt.title("Total Spending by Shop")
plt.xlabel("Shop")
plt.ylabel("Amount (€)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "spending_by_shop.png")
plt.show()
plt.close()

# Chart 2: Spending by category
plt.figure(figsize=(9, 5))
category_spending.plot(kind="bar")
plt.title("Total Spending by Category")
plt.xlabel("Category")
plt.ylabel("Amount (€)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "spending_by_category.png")
plt.show()
plt.close()

# Chart 3: Needs vs Wants
plt.figure(figsize=(7, 7))
need_want_spending.plot(kind="pie", autopct="%1.1f%%")
plt.title("Needs vs Wants")
plt.ylabel("")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "needs_vs_wants.png")
plt.show()
plt.close()

# Chart 4: Daily spending
plt.figure(figsize=(10, 5))
daily_spending.plot(kind="line", marker="o")
plt.title("Daily Spending")
plt.xlabel("Date")
plt.ylabel("Amount (€)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "daily_spending.png")
plt.show()
plt.close()

# Chart 5: Spending by payment method
plt.figure(figsize=(8, 5))
payment_spending.plot(kind="bar")
plt.title("Spending by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Amount (€)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "payment_methods.png")
plt.show()
plt.close()

print("\nCharts saved in the charts folder.")
