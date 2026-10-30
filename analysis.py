import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "data" / "spendings.csv"
CHARTS_DIR = PROJECT_DIR / "charts"

REQUIRED_COLUMNS = [
    "date",
    "category",
    "item",
    "amount",
    "shop",
    "need_want",
    "payment_method",
]


def load_data():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing CSV columns: {', '.join(missing_columns)}")

    df = df[REQUIRED_COLUMNS].copy()

    text_columns = ["category", "item", "shop", "need_want", "payment_method"]
    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.replace(r"\\s+", " ", regex=True)
        )

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    invalid_rows = (
        df[REQUIRED_COLUMNS].isna().any(axis=1)
        | (df["amount"] <= 0)
        | (df["category"] == "")
        | (df["item"] == "")
        | (df["shop"] == "")
        | (~df["need_want"].isin(["Need", "Want"]))
        | (~df["payment_method"].isin(["Cash", "Revolut", "PTSB"]))
    )

    if invalid_rows.any():
        print(f"Warning: {invalid_rows.sum()} invalid row(s) were excluded.")

    df = df.loc[~invalid_rows].copy()

    if df.empty:
        raise ValueError("The CSV contains no valid purchase records.")

    shop_names = {
        "ikea": "IKEA",
        "amazon": "Amazon",
        "woodies": "Woodies",
        "zara": "Zara",
        "lidl": "Lidl",
        "aldi": "Aldi",
        "tesco": "Tesco",
        "supervalu": "SuperValu",
        "gino's": "Gino's",
    }

    df["shop"] = df["shop"].apply(
        lambda shop: shop_names.get(shop.casefold(), shop)
    )

    return df


def print_analysis(df):
    print("\n====== SPENDING TRACKER ANALYSIS ======")

    print("\n--- GENERAL STATISTICS ---")
    print(f"Number of purchases: {len(df)}")
    print(f"Total spending: €{df['amount'].sum():.2f}")
    print(f"Average purchase: €{df['amount'].mean():.2f}")
    print(f"Most expensive purchase: €{df['amount'].max():.2f}")
    print(f"Cheapest purchase: €{df['amount'].min():.2f}")
    print(f"First date: {df['date'].min().date()}")
    print(f"Last date: {df['date'].max().date()}")

    print("\n--- SPENDING BY SHOP ---")
    shop_spending = df.groupby("shop")["amount"].agg(["sum", "count"])
    shop_spending = shop_spending.sort_values("sum", ascending=False)
    for shop, row in shop_spending.iterrows():
        print(f"{shop}: €{row['sum']:.2f} ({int(row['count'])} purchases)")

    print("\n--- SPENDING BY CATEGORY ---")
    category_spending = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    for category, total in category_spending.items():
        print(f"{category}: €{total:.2f}")

    print("\n--- NEEDS VS WANTS ---")
    needs_wants = df.groupby("need_want")["amount"].agg(["sum", "count"])
    needs_wants = needs_wants.sort_values("sum", ascending=False)
    for classification, row in needs_wants.iterrows():
        print(f"{classification}: €{row['sum']:.2f} ({int(row['count'])} purchases)")

    print("\n--- SPENDING BY PAYMENT METHOD ---")
    payment_spending = df.groupby("payment_method")["amount"].agg(["sum", "count"])
    payment_spending = payment_spending.sort_values("sum", ascending=False)
    for method, row in payment_spending.iterrows():
        print(f"{method}: €{row['sum']:.2f} ({int(row['count'])} purchases)")

    print("\n--- DAILY SPENDING ---")
    daily_spending = df.groupby(df["date"].dt.date)["amount"].sum().sort_index()
    for purchase_date, total in daily_spending.items():
        print(f"{purchase_date}: €{total:.2f}")

    print("\n--- TOP 10 MOST EXPENSIVE PURCHASES ---")
    top_purchases = df.nlargest(10, "amount")
    print(
        top_purchases[["date", "item", "shop", "amount"]]
        .to_string(index=False, formatters={"amount": lambda value: f"€{value:.2f}"})
    )


def save_charts(df):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    shop_spending = df.groupby("shop")["amount"].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    shop_spending.plot(kind="bar")
    plt.title("Total Spending by Shop")
    plt.xlabel("Shop")
    plt.ylabel("Amount (€)")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "spending_by_shop.png", dpi=150)
    plt.close()

    category_spending = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    category_spending.plot(kind="bar")
    plt.title("Total Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (€)")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "spending_by_category.png", dpi=150)
    plt.close()

    needs_wants = df.groupby("need_want")["amount"].sum()
    plt.figure(figsize=(7, 7))
    needs_wants.plot(kind="pie", autopct="%1.1f%%", startangle=90)
    plt.title("Needs vs Wants")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "needs_vs_wants.png", dpi=150)
    plt.close()

    daily_spending = df.groupby(df["date"].dt.date)["amount"].sum().sort_index()
    plt.figure(figsize=(11, 6))
    daily_spending.plot(kind="line", marker="o")
    plt.title("Daily Spending")
    plt.xlabel("Date")
    plt.ylabel("Amount (€)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "daily_spending.png", dpi=150)
    plt.close()

    payment_spending = df.groupby("payment_method")["amount"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    payment_spending.plot(kind="bar")
    plt.title("Spending by Payment Method")
    plt.xlabel("Payment Method")
    plt.ylabel("Amount (€)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "payment_methods.png", dpi=150)
    plt.close()

    print(f"\nCharts saved in: {CHARTS_DIR}")


def main():
    try:
        df = load_data()
        print_analysis(df)
        save_charts(df)
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        print(f"Analysis could not be completed: {error}")


if __name__ == "__main__":
    main()
