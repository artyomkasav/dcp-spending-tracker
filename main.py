
import csv
import sqlite3
from datetime import date
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "data" / "spendings.csv"
DB_PATH = PROJECT_DIR / "spending.db"

REQUIRED_COLUMNS = {
    "date",
    "category",
    "item",
    "amount",
    "shop",
    "need_want",
    "payment_method",
}


def validate_row(row, line_number):
    """Check required fields, date format and purchase amount."""
    errors = []

    # Required fields
    for column in REQUIRED_COLUMNS:
        if not row.get(column, "").strip():
            errors.append(f"Line {line_number}: {column} is empty")

    # Validate date
    try:
        date.fromisoformat(row["date"])
    except (ValueError, TypeError):
        errors.append(
            f"Line {line_number}: date must use YYYY-MM-DD"
        )

    # Validate amount
    try:
        amount = float(row["amount"])
        if amount <= 0:
            errors.append(
                f"Line {line_number}: amount must be greater than 0"
            )
    except (ValueError, TypeError):
        errors.append(
            f"Line {line_number}: amount must be numeric"
        )

    # Validate category classification
    if row.get("need_want", "").strip() not in {"Need", "Want"}:
        errors.append(
            f"Line {line_number}: need_want must be Need or Want"
        )

    return errors


def load_data():
    """Validate CSV data and load valid records into SQLite."""
    if not CSV_PATH.exists():
        print(f"CSV file not found: {CSV_PATH}")
        return

    with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            print("The CSV file has no header.")
            return

        if set(reader.fieldnames) != REQUIRED_COLUMNS:
            print("CSV columns do not match the data dictionary.")
            print("Expected:", sorted(REQUIRED_COLUMNS))
            print("Found:", sorted(reader.fieldnames))
            return

        valid_rows = []
        all_errors = []

        for line_number, row in enumerate(reader, start=2):
            errors = validate_row(row, line_number)

            if errors:
                all_errors.extend(errors)
            else:
                valid_rows.append(row)

    if all_errors:
        print("Please correct these problems before loading:")
        for error in all_errors:
            print("-", error)
        return

    if not valid_rows:
        print("No purchase records to load yet.")
        print("Add your own recorded purchases to the CSV first.")
        return

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS spending (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                item TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                shop TEXT NOT NULL,
                need_want TEXT NOT NULL
                    CHECK (need_want IN ('Need', 'Want')),
                payment_method TEXT NOT NULL
            )
        """)

        # Replace the table contents to avoid duplicate imports
        # when the program is run again.
        connection.execute("DELETE FROM spending")

        connection.executemany("""
            INSERT INTO spending (
                date, category, item, amount,
                shop, need_want, payment_method
            )
            VALUES (
                :date, :category, :item, :amount,
                :shop, :need_want, :payment_method
            )
        """, valid_rows)

    print(f"Loaded {len(valid_rows)} purchase records.")
    print(f"Database saved at: {DB_PATH}")

def show_summary():
    """Display a summary of spending by shop."""
    with sqlite3.connect(DB_PATH) as connection:
        results = connection.execute("""
            SELECT shop, SUM(amount), COUNT(*)
            FROM spending
            GROUP BY shop
            ORDER BY SUM(amount) DESC
        """).fetchall()

    print("\nSpending by shop:")
    for shop, total, item_count in results:
        print(f"{shop}: €{total:.2f} ({item_count} items)")

if __name__ == "__main__":
    load_data()
    show_summary()
