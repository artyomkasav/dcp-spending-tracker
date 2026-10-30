
import sqlite3, csv, math
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


def validate_row(row: dict) -> list[str]:
    errors = []

    for column in REQUIRED_COLUMNS:
        value = str(row.get(column) or "").strip()
        if not value:
            errors.append(f"{column} cannot be empty")

    try:
        purchase_date = date.fromisoformat(str(row["date"]))
        if purchase_date.isoformat() != row["date"]:
            errors.append("Date must use YYYY-MM-DD format")
    except (ValueError, TypeError, KeyError):
        errors.append("Invalid date. Use YYYY-MM-DD")

    try:
        amount = float(row["amount"])
        if not math.isfinite(amount) or amount <= 0:
            errors.append("Amount must be a positive finite number")
    except (ValueError, TypeError, KeyError):
        errors.append("Amount must be numeric")

    if row.get("need_want") not in {"Need", "Want"}:
        errors.append("need_want must be Need or Want")

    if row.get("payment_method") not in {"Cash", "Revolut", "PTSB"}:
        errors.append("Payment method must be Cash, Revolut or PTSB")

    return errors


def create_table() -> None:
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


def read_csv_rows() -> list[dict] | None:
    if not CSV_PATH.exists():
        print(f"CSV file not found: {CSV_PATH}")
        return None

    try:
        with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames != REQUIRED_COLUMNS:
                print("CSV columns do not match the required format.")
                return None

            rows = []
            has_errors = False

            for line_number, row in enumerate(reader, start=2):
                errors = validate_row(row)

                if errors:
                    has_errors = True
                    for error in errors:
                        print(f"CSV line {line_number}: {error}")
                else:
                    row["amount"] = float(row["amount"])
                    rows.append(row)

            if has_errors:
                print("CSV contains invalid records. Correct the file before continuing.")
                return None

            return rows

    except (OSError, csv.Error) as error:
        print(f"Could not read CSV file: {error}")
        return None


def get_database_rows() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as connection:
        return connection.execute("""
            SELECT date, category, item, amount, shop, need_want, payment_method
            FROM spending
            ORDER BY date, id
        """).fetchall()


def rows_match(csv_rows: list[dict], database_rows: list[tuple]) -> bool:
    if len(csv_rows) != len(database_rows):
        return False

    for csv_row, db_row in zip(csv_rows, database_rows):
        csv_values = (
            csv_row["date"],
            csv_row["category"],
            csv_row["item"],
            round(float(csv_row["amount"]), 2),
            csv_row["shop"],
            csv_row["need_want"],
            csv_row["payment_method"],
        )
        db_values = (
            db_row[0],
            db_row[1],
            db_row[2],
            round(float(db_row[3]), 2),
            db_row[4],
            db_row[5],
            db_row[6],
        )

        if csv_values != db_values:
            return False

    return True


def save_database_to_csv() -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = CSV_PATH.with_suffix(".tmp")

    with temporary_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(REQUIRED_COLUMNS)
        writer.writerows(get_database_rows())

    temporary_path.replace(CSV_PATH)


def synchronize_data() -> bool:
    csv_rows = read_csv_rows()

    if csv_rows is None:
        print("Application stopped. The CSV was not changed.")
        return False

    # The CSV file is the source of truth.
    # Replace the database contents with the current CSV records.
    try:
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute("DELETE FROM spending")

            if csv_rows:
                connection.executemany("""
                    INSERT INTO spending (
                        date, category, item, amount,
                        shop, need_want, payment_method
                    )
                    VALUES (
                        :date, :category, :item, :amount,
                        :shop, :need_want, :payment_method
                    )
                """, csv_rows)

        print(f"Loaded {len(csv_rows)} purchases from CSV into the database.")
        print("CSV is the source of truth. Database synchronised from CSV.")
        return True

    except sqlite3.Error as error:
        print(f"Could not synchronise the database: {error}")
        return False


def show_all_purchases() -> None:
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


def show_total_spending() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        total = connection.execute(
            "SELECT SUM(amount) FROM spending"
        ).fetchone()[0]

    print(f"\nTotal spending: €{total or 0:.2f}")


def show_spending_by_shop() -> None:
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


def show_spending_by_category() -> None:
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


def filter_by_date() -> None:
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
            ORDER BY date, id
        """, (start_date, end_date)).fetchall()

    if not rows:
        print("No purchases found for this period.")
        return

    print("\n--- PURCHASES IN SELECTED PERIOD ---")
    period_total = 0

    for purchase_date, item, amount, shop in rows:
        print(f"{purchase_date} | {item} | €{amount:.2f} | {shop}")
        period_total += amount

    print(f"Period total: €{period_total:.2f}")


def add_purchase() -> None:
    print("\n--- ADD NEW PURCHASE ---")

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
        print("\nPurchase was not added:")
        for error in errors:
            print(f"- {error}")
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
    print("Purchase added successfully.")


def show_spending_by_payment() -> None:
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


def show_needs_vs_wants() -> None:
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


def show_average_purchase() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        average, count = connection.execute("""
            SELECT AVG(amount), COUNT(*)
            FROM spending
        """).fetchone()

    print(f"\nAverage purchase: €{(average or 0):.2f}")
    print(f"Total number of purchases: {count}")


def search_purchase() -> None:
    keyword = input("Enter item name to search: ").strip()

    if not keyword:
        print("Search term cannot be empty.")
        return

    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT id, date, item, amount, shop
            FROM spending
            WHERE item LIKE ?
            ORDER BY date DESC, id DESC
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


def delete_purchase() -> None:
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

        cursor = connection.execute(
            "DELETE FROM spending WHERE id = ?",
            (purchase_id,)
        )

        if cursor.rowcount == 0:
            print("Purchase was not deleted.")
            return

    save_database_to_csv()
    print("Purchase deleted successfully.")


def main_menu() -> None:
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
        print("10. Search purchases")
        print("11. Delete purchase")
        print("12. Exit")

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
            search_purchase()
        elif choice == "11":
            delete_purchase()
        elif choice == "12":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-12.")


if __name__ == "__main__":
    create_table()

    if synchronize_data():
        main_menu()
    else:
        print("Application stopped because the CSV file could not be validated.")
