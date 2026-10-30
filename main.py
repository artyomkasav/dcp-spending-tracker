
import csv, math, sqlite3
from datetime import date
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "data" / "spendings.csv"
DB_PATH = PROJECT_DIR / "spending.db"

REQUIRED_COLUMNS = [
    "date",
    "category",
    "item",
    "amount",
    "shop",
    "need_want",
    "payment_method",
]


def validate_row(row):
    """Validate the fields of one purchase."""
    errors = []

    for column in REQUIRED_COLUMNS:
        value = str(row.get(column) or "").strip()
        if not value:
            errors.append(f"{column} cannot be empty")

    # Validate date
    try:
        purchase_date = date.fromisoformat(row["date"])
        if purchase_date.isoformat() != row["date"]:
            errors.append("Date must use YYYY-MM-DD format")
    except (ValueError, TypeError, KeyError):
        errors.append("Invalid date. Use YYYY-MM-DD")

    # Validate amount
    try:
        amount = float(row["amount"])
        if not math.isfinite(amount) or amount <= 0:
            errors.append("Amount must be a positive finite number")
    except (ValueError, TypeError, KeyError):
        errors.append("Amount must be numeric")

    if row.get("need_want") not in {"Need", "Want"}:
        errors.append("need_want must be Need or Want")

    if row.get("payment_method") not in {
        "Cash", "Revolut", "PTSB"
    }:
        errors.append("Payment method must be Cash, Revolut or PTSB")

    return errors


def create_table():
    """Create the spending table if it does not exist."""
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

def save_database_to_csv():
    """Export all purchases from SQLite to the CSV file."""
    columns = [
        "date",
        "category",
        "item",
        "amount",
        "shop",
        "need_want",
        "payment_method"
    ]

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT date, category, item, amount, shop, need_want, payment_method
            FROM spending
            ORDER BY date, id
        """)
        rows = cursor.fetchall()

    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)

def load_csv_if_database_empty():
    """Import CSV records only when the database is empty."""
    if not CSV_PATH.exists():
        print("CSV file was not found.")
        return

    with sqlite3.connect(DB_PATH) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM spending"
        ).fetchone()[0]

        if count > 0:
            print(f"Database already contains {count} records.")
            return

        with CSV_PATH.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            if reader.fieldnames != REQUIRED_COLUMNS:
                print("CSV columns do not match the required format.")
                return

            valid_rows = []
            errors_found = False

            for line_number, row in enumerate(reader, start=2):
                errors = validate_row(row)

                if errors:
                    errors_found = True
                    for error in errors:
                        print(f"CSV line {line_number}: {error}")
                else:
                    valid_rows.append(row)

            if errors_found:
                print("Fix the CSV errors before importing.")
                return

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

        print(f"Imported {len(valid_rows)} purchases from CSV.")


def show_all_purchases():
    """Display all purchases stored in the database."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT id, date, item, amount, shop, payment_method
            FROM spending
            ORDER BY date DESC, id DESC
        """).fetchall()

    if not rows:
        print("No purchases found.")
        return

    print("\n--- ALL PURCHASES ---")

    for purchase_id, purchase_date, item, amount, shop, payment in rows:
        print(
            f"ID: {purchase_id} | {purchase_date} | "
            f"{item} | €{amount:.2f} | {shop} | {payment}"
        )

def show_total_spending():
    """Display the total amount spent."""
    with sqlite3.connect(DB_PATH) as connection:
        total = connection.execute("""
            SELECT SUM(amount) FROM spending
        """).fetchone()[0]

    print(f"\nTotal spending: €{total or 0:.2f}")


def show_spending_by_shop():
    """Display total spending grouped by shop."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT shop, SUM(amount), COUNT(*)
            FROM spending
            GROUP BY shop
            ORDER BY SUM(amount) DESC
        """).fetchall()

    print("\n--- SPENDING BY SHOP ---")
    for shop, total, count in rows:
        print(f"{shop}: €{total:.2f} ({count} items)")


def show_spending_by_category():
    """Display total spending grouped by category."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT category, SUM(amount)
            FROM spending
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """).fetchall()

    print("\n--- SPENDING BY CATEGORY ---")
    for category, total in rows:
        print(f"{category}: €{total:.2f}")


def filter_by_date():
    """Show purchases between two dates."""
    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()

    try:
        date.fromisoformat(start_date)
        date.fromisoformat(end_date)

        if start_date > end_date:
            print("Start date cannot be after end date.")
            return

    except ValueError:
        print("Invalid date format.")
        return

    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT date, item, amount, shop
            FROM spending
            WHERE date BETWEEN ? AND ?
            ORDER BY date
        """, (start_date, end_date)).fetchall()

    if not rows:
        print("No purchases found for this period.")
        return

    print("\n--- PURCHASES IN SELECTED PERIOD ---")
    period_total = 0

    for purchase_date, item, amount, shop in rows:
        print(
            f"{purchase_date} | {item} | "
            f"€{amount:.2f} | {shop}"
        )
        period_total += amount

    print(f"Period total: €{period_total:.2f}")


def add_purchase():
    """Add a new purchase to SQLite and the CSV file."""
    print("\n--- ADD NEW PURCHASE ---")

    row = {
        "date": input("Date (YYYY-MM-DD): ").strip(),
        "category": input("Category: ").strip(),
        "item": input("Item: ").strip(),
        "amount": input("Amount (€): ").strip(),
        "shop": input("Shop: ").strip(),
        "need_want": input("Need or Want: ").strip().capitalize(),
        "payment_method": input(
            "Payment method (Cash/Revolut/PTSB): "
        ).strip(),
    }

    errors = validate_row(row)

    if errors:
        print("\nPurchase was not added:")
        for error in errors:
            print("-", error)
        return

    row["amount"] = float(row["amount"])

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            INSERT INTO spending (
                date, category, item, amount,
                shop, need_want, payment_method
            )
            VALUES (
                :date, :category, :item, :amount,
                :shop, :need_want, :payment_method
            )
        """, row)

    save_database_to_csv()

    print("Purchase added successfully!")


def show_spending_by_payment():
    """Display spending grouped by payment method."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT payment_method, SUM(amount), COUNT(*)
            FROM spending
            GROUP BY payment_method
            ORDER BY SUM(amount) DESC
        """).fetchall()

    print("\n--- SPENDING BY PAYMENT METHOD ---")
    for method, total, count in rows:
        print(f"{method}: €{total:.2f} ({count} purchases)")


def show_needs_vs_wants():
    """Compare spending on needs and wants."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT need_want, SUM(amount), COUNT(*)
            FROM spending
            GROUP BY need_want
            ORDER BY SUM(amount) DESC
        """).fetchall()

    print("\n--- NEEDS VS WANTS ---")
    for classification, total, count in rows:
        print(f"{classification}: €{total:.2f} ({count} items)")


def show_average_purchase():
    """Calculate the average purchase amount."""
    with sqlite3.connect(DB_PATH) as connection:
        result = connection.execute("""
            SELECT AVG(amount), COUNT(*)
            FROM spending
        """).fetchone()

    average, count = result

    print(f"\nAverage purchase: €{average:.2f}")
    print(f"Total number of purchases: {count}")

def search_purchase():
    """Search purchases by item name."""
    keyword = input("Enter item name to search: ").strip()

    if not keyword:
        print("Search term cannot be empty.")
        return

    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT id, date, item, amount, shop
            FROM spending
            WHERE item LIKE ?
            ORDER BY date DESC
        """, (f"%{keyword}%",)).fetchall()

    if not rows:
        print("No matching purchases found.")
        return

    print("\n--- SEARCH RESULTS ---")

    for purchase_id, purchase_date, item, amount, shop in rows:
        print(
            f"ID: {purchase_id} | {purchase_date} | "
            f"{item} | €{amount:.2f} | {shop}"
        )

def main_menu():
    """Display the main menu and handle user choices."""
    while True:
        print("\n====== SPENDING TRACKER ======")
        print("1. Show all purchases")
        print("2. Show total spending")
        print("3. Spending by shop")
        print("4. Spending by category")
        print("5. Filter purchases by date")
        print("6. Add a new purchase")
        print("7. Spending by payment method")
        print("8. Needs vs Wants")
        print("9. Average purchase")
        print("10. Exit")
        print("11. Search purchases")
        print("12. Delete purchase")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            show_all_purchases()
        elif choice == "2":
            show_total_spending()
        elif choice == "3":
            show_spending_by_shop()
        elif choice == "4":
            show_spending_by_category()
        elif choice == "5":
            filter_by_date()
        elif choice == "6":
            add_purchase()
        elif choice == "7":
            show_spending_by_payment()
        elif choice == "8":
            show_needs_vs_wants()
        elif choice == "9":
            show_average_purchase()
        elif choice == "10":
            print("Goodbye!")
        elif choice == "11":
            search_purchase()
        elif choice == "12":
            delete_purchase()
            break
        else:
            print("Invalid option. Please choose 1-10.")

def delete_purchase():
    """Delete a purchase using its database ID."""
    try:
        purchase_id = int(input("Enter purchase ID to delete: "))
    except ValueError:
        print("ID must be a number.")
        return

    with sqlite3.connect(DB_PATH) as connection:
        row = connection.execute("""
            SELECT item, amount, shop
            FROM spending
            WHERE id = ?
        """, (purchase_id,)).fetchone()

        if row is None:
            print("Purchase not found.")
            return

        item, amount, shop = row

        print(f"\nSelected: {item} | €{amount:.2f} | {shop}")
        confirmation = input("Delete this purchase? (yes/no): ").strip().lower()

        if confirmation != "yes":
            print("Deletion cancelled.")
            return

        connection.execute(
            "DELETE FROM spending WHERE id = ?",
            (purchase_id,)
        )
    save_database_to_csv()
    print("Purchase deleted from database.")
    print("Note: the CSV file has not been changed.")

if __name__ == "__main__":
    create_table()
    load_csv_if_database_empty()
    main_menu()
