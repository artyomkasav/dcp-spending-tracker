import sqlite3
import csv
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
    errors = []

    for column in REQUIRED_COLUMNS:
        if not row.get(column, "").strip():
            errors.append(f"{column} cannot be empty")

    try:
        date.fromisoformat(row["date"])
    except (ValueError, TypeError, KeyError):
        errors.append("Date must use YYYY-MM-DD format")

    try:
        amount = float(row["amount"])
        if not amount > 0:
            errors.append("Amount must be greater than zero")
    except (ValueError, TypeError, KeyError):
        errors.append("Amount must be a number")

    if row.get("need_want") not in ["Need", "Want"]:
        errors.append("Choose Need or Want")

    if row.get("payment_method") not in ["Cash", "Revolut", "PTSB"]:
        errors.append("Choose Cash, Revolut or PTSB")

    return errors


def create_table():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS spending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                item TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                shop TEXT NOT NULL,
                need_want TEXT NOT NULL,
                payment_method TEXT NOT NULL
            )
        """)


def read_csv_rows():
    if not CSV_PATH.exists():
        print("CSV file was not found.")
        return None

    try:
        with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames != REQUIRED_COLUMNS:
                print("CSV columns are incorrect.")
                return None

            rows = []

            for line_number, row in enumerate(reader, start=2):
                errors = validate_row(row)

                if errors:
                    print(f"Error on CSV line {line_number}:")
                    for error in errors:
                        print(f"- {error}")
                    return None

                row["amount"] = float(row["amount"])
                rows.append(row)

            return rows

    except (OSError, csv.Error) as error:
        print(f"Could not read CSV: {error}")
        return None


def save_database_to_csv():
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT date, category, item, amount, shop, need_want, payment_method
            FROM spending
            ORDER BY date, id
        """).fetchall()

    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(REQUIRED_COLUMNS)
        writer.writerows(rows)


def synchronize_data():
    rows = read_csv_rows()

    if rows is None:
        return False

    try:
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute("DELETE FROM spending")
            connection.executemany("""
                INSERT INTO spending (
                    date, category, item, amount, shop, need_want, payment_method
                )
                VALUES (
                    :date, :category, :item, :amount, :shop, :need_want, :payment_method
                )
            """, rows)

        print(f"Loaded {len(rows)} purchases.")
        return True

    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return False


def show_all_purchases():
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT id, date, item, amount, shop, payment_method
            FROM spending
            ORDER BY date DESC, id DESC
        """).fetchall()

    if not rows:
        print("No purchases found.")
        return

    for purchase in rows:
        print(f"{purchase[0]} | {purchase[1]} | {purchase[2]} | €{purchase[3]:.2f} | {purchase[4]} | {purchase[5]}")


def show_total_spending():
    with sqlite3.connect(DB_PATH) as connection:
        total = connection.execute("SELECT SUM(amount) FROM spending").fetchone()[0]

    print(f"Total spending: €{total or 0:.2f}")


def show_spending_by_shop():
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT shop, SUM(amount), COUNT(*)
            FROM spending
            GROUP BY shop
            ORDER BY SUM(amount) DESC
        """).fetchall()

    for shop, total, count in rows:
        print(f"{shop}: €{total:.2f} ({count} purchases)")


def show_spending_by_category():
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT category, SUM(amount)
            FROM spending
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """).fetchall()

    for category, total in rows:
        print(f"{category}: €{total:.2f}")


def filter_by_date():
    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()

    try:
        date.fromisoformat(start_date)
        date.fromisoformat(end_date)
    except ValueError:
        print("Enter valid dates in YYYY-MM-DD format.")
        return

    if start_date > end_date:
        print("Start date cannot be after end date.")
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

    total = 0

    for purchase_date, item, amount, shop in rows:
        print(f"{purchase_date} | {item} | €{amount:.2f} | {shop}")
        total += amount

    print(f"Period total: €{total:.2f}")


def add_purchase():
    row = {
        "date": input("Date (YYYY-MM-DD): ").strip(),
        "category": input("Category: ").strip(),
        "item": input("Item: ").strip(),
        "amount": input("Amount (€): ").strip(),
        "shop": input("Shop: ").strip(),
        "need_want": input("Need or Want: ").strip().capitalize(),
        "payment_method": input("Payment method (Cash/Revolut/PTSB): ").strip(),
    }

    errors = validate_row(row)

    if errors:
        for error in errors:
            print(error)
        return

    row["amount"] = float(row["amount"])

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            INSERT INTO spending (
                date, category, item, amount, shop, need_want, payment_method
            )
            VALUES (
                :date, :category, :item, :amount, :shop, :need_want, :payment_method
            )
        """, row)

    save_database_to_csv()
    print("Purchase added.")


def show_spending_by_payment():
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT payment_method, SUM(amount), COUNT(*)
            FROM spending
            GROUP BY payment_method
            ORDER BY SUM(amount) DESC
        """).fetchall()

    for method, total, count in rows:
        print(f"{method}: €{total:.2f} ({count} purchases)")


def show_needs_vs_wants():
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT need_want, SUM(amount), COUNT(*)
            FROM spending
            GROUP BY need_want
            ORDER BY SUM(amount) DESC
        """).fetchall()

    for classification, total, count in rows:
        print(f"{classification}: €{total:.2f} ({count} purchases)")


def show_average_purchase():
    with sqlite3.connect(DB_PATH) as connection:
        average, count = connection.execute("""
            SELECT AVG(amount), COUNT(*)
            FROM spending
        """).fetchone()

    print(f"Average purchase: €{(average or 0):.2f}")
    print(f"Number of purchases: {count}")


def search_purchase():
    keyword = input("Enter item name: ").strip()

    if not keyword:
        print("Search cannot be empty.")
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

    for purchase in rows:
        print(f"{purchase[0]} | {purchase[1]} | {purchase[2]} | €{purchase[3]:.2f} | {purchase[4]}")


def delete_purchase():
    try:
        purchase_id = int(input("Enter purchase ID: "))
    except ValueError:
        print("ID must be a number.")
        return

    with sqlite3.connect(DB_PATH) as connection:
        purchase = connection.execute("""
            SELECT item, amount, shop
            FROM spending
            WHERE id = ?
        """, (purchase_id,)).fetchone()

        if purchase is None:
            print("Purchase not found.")
            return

        print(f"Selected: {purchase[0]} | €{purchase[1]:.2f} | {purchase[2]}")
        confirmation = input("Delete this purchase? (yes/no): ").strip().lower()

        if confirmation != "yes":
            print("Deletion cancelled.")
            return

        connection.execute("DELETE FROM spending WHERE id = ?", (purchase_id,))

    save_database_to_csv()
    print("Purchase deleted.")


def main_menu():
    while True:
        print("\n====== SPENDING TRACKER ======")
        print("1. Show all purchases")
        print("2. Show total spending")
        print("3. Spending by shop")
        print("4. Spending by category")
        print("5. Filter by date")
        print("6. Add purchase")
        print("7. Spending by payment method")
        print("8. Needs vs Wants")
        print("9. Average purchase")
        print("10. Search purchases")
        print("11. Delete purchase")
        print("12. Exit")

        choice = input("Choose an option: ").strip()

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
            search_purchase()
        elif choice == "11":
            delete_purchase()
        elif choice == "12":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    create_table()

    if synchronize_data():
        main_menu()
    else:
        print("Application stopped because the CSV file has errors.")
