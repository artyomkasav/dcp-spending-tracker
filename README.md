# Spending Tracker

## 1. About the Project

Spending Tracker is a Python application I made for the Data Centric Programming 2026 assignment.

The idea of the project is simple: record purchases and use the data to understand where the money goes. Each row in the CSV file represents one purchased item. The program can display the records, search them, calculate totals and compare spending in different shops and categories.

I used Python, CSV, SQLite, SQL, pandas and Matplotlib to build the project.

## 2. Project Goals

The main goals were to:

- Record purchases with their date, item, price, shop and payment method.
- Store the records in a CSV file.
- Use an SQLite database to work with the records.
- Check the data before adding it to the database.
- Write SQL queries to calculate and group spending.
- Use pandas to analyse the dataset.
- Create charts to make the results easier to understand.
- Build a simple menu so the user can work with the data.

## 3. Tools Used

| Tool | How I used it |
|---|---|
| Python | To write the application and connect all parts of the project |
| CSV | To store the purchase records |
| SQLite | To store and query the purchase data |
| SQL | To search, filter and group records and calculate totals |
| pandas | To load, organise and analyse the data |
| Matplotlib | To create charts |
| Git and GitHub | To save my work and keep track of changes |

## 4. Dataset

The dataset is stored in `data/spendings.csv`.

Each row represents one purchased item, not one complete shopping receipt. For example, if a shopping trip contains several different items, each item is recorded on a separate row.

### Data Dictionary

| Column | Data type | Description |
|---|---|---|
| `date` | DATE / TEXT | Date of the purchase in `YYYY-MM-DD` format |
| `category` | TEXT | Category of the purchase, for example Food or Household |
| `item` | TEXT | Name of the purchased item |
| `amount` | REAL | Price of the item in euros |
| `shop` | TEXT | Shop where the item was purchased |
| `need_want` | TEXT | Shows whether the purchase is a Need or a Want |
| `payment_method` | TEXT | Payment method: Cash, Revolut or PTSB |

### Data Collection

The purchase records are entered into the CSV file. The information for each record includes the date, item, price, shop, category, whether it was a Need or a Want, and the payment method.

The values need to be checked against the original purchase information, such as receipts or transaction records. Missing prices or other details should not be guessed.

## 5. Research Questions

I chose these questions for the project:

1. Which shops account for the highest total spending?
2. How much is spent on Needs compared with Wants?
3. How does spending change between different dates?

The program also makes it possible to look at spending by category and payment method, as well as the average price of a purchase.

## 6. Project Structure

```text
dcp-spending-tracker/
│
├── data/
│   └── spendings.csv
│
├── charts/
│   ├── spending_by_shop.png
│   ├── spending_by_category.png
│   ├── needs_vs_wants.png
│   ├── daily_spending.png
│   └── payment_methods.png
│
├── main.py
├── analysis.py
├── spending.db
├── README.md
└── .gitignore
```

The `data` folder contains the CSV file. The `charts` folder contains the graphs created by the analysis script. The SQLite database is created by the application when it runs.

## 7. Application Features

### Data Validation

Before records are added to the database, the program checks that:

- All required fields have a value.
- Dates use the `YYYY-MM-DD` format.
- Amounts are numeric and greater than zero.
- The `need_want` value is either `Need` or `Want`.
- The payment method is `Cash`, `Revolut` or `PTSB`.

If the CSV contains invalid records, the program displays an error and stops the import.

### CSV and SQLite

The CSV file is the main source of the purchase data.

When `main.py` starts, it reads the CSV file, checks the records and updates the SQLite database using the current CSV contents. This means that changes made directly to the CSV are loaded into the database the next time the program starts.

When a purchase is added or deleted through the menu, the database is updated and the CSV file is saved as well.

### SQL Queries

I used SQL queries to:

- Display all purchases.
- Calculate total spending.
- Group spending by shop.
- Group spending by category.
- Compare Needs and Wants.
- Calculate spending by payment method.
- Calculate the average purchase amount.
- Filter purchases by date.
- Search for an item.
- Delete a selected purchase.

### Terminal Menu

The program has an interactive menu with these options:

1. Show all purchases.
2. Show total spending.
3. Show spending by shop.
4. Show spending by category.
5. Filter purchases by date.
6. Add a new purchase.
7. Show spending by payment method.
8. Compare Needs and Wants.
9. Show the average purchase.
10. Search purchases.
11. Delete a purchase.
12. Exit.

The menu allows the user to explore the records without having to write SQL queries manually.

## 8. Data Analysis and Visualisation

The `analysis.py` file reads the CSV data using pandas. It prepares the dates and amounts, checks for invalid records and groups the data to calculate different statistics.

The analysis displays:

- Number of purchases.
- Total spending.
- Average purchase amount.
- Most expensive and cheapest purchase.
- Date range of the dataset.
- Spending by shop.
- Spending by category.
- Spending on Needs and Wants.
- Spending by payment method.
- Total spending for each date.
- The ten most expensive purchases.

Matplotlib is used to create five charts:

| Chart | What it shows |
|---|---|
| `spending_by_shop.png` | Total spending in each shop |
| `spending_by_category.png` | Total spending in each category |
| `needs_vs_wants.png` | How spending is split between Needs and Wants |
| `daily_spending.png` | Total spending on each date |
| `payment_methods.png` | Total spending for each payment method |

The charts are saved in the `charts` folder. They are not opened automatically when the script runs. I can open the PNG files from that folder or use them during the project demonstration.

## 9. How to Run the Project

Python 3 is required.

Install the libraries for the analysis:

```bash
pip install pandas matplotlib
```

SQLite is included with Python, so there is no separate installation needed for it.

Open a terminal in the main project folder.

### Run the Spending Tracker

```bash
python main.py
```

### Run the Analysis

```bash
python analysis.py
```

The first command opens the terminal menu. The second command prints the analysis results and creates the charts in the `charts` folder.

## 10. Findings

While working on this project, I learned how Python can be used together with an SQLite database. One of the main things I learned was how to write SQL queries inside a Python program and use the results in the application. I also got more practice with commands such as `SELECT`, `WHERE`, `GROUP BY` and `ORDER BY`.

I learned how to organise data in a DataFrame with pandas and use functions such as `groupby()`, `sum()`, `mean()` and `nlargest()` to get useful information from the dataset.

The charts make the spending information easier to understand. For example, the shop and category charts make it easier to compare totals, while the daily spending chart shows how the totals change over time. The Needs vs Wants chart gives a quick comparison between the two types of purchases.

The project also showed me why data needs to be consistent. If shop names or categories are entered in different ways, the results can be split into separate groups. Cleaning text values before grouping helps avoid this problem.

## 11. Reflection

The project helped me improve my Python skills and understand how different tools can work together in one application.

Working with SQLite was useful because I had to learn how to connect Python to a database, execute SQL queries and use the returned data. At the beginning, implementing SQL in Python was new to me, but after working on the different menu options I became more comfortable with it.

Matplotlib was a small challenge for me. I had to spend extra time watching YouTube tutorials and learning how to create different chart types, add titles and labels, adjust the layout and save the charts as image files. After some practice, I managed to create the five charts used in this project.

Another important part was keeping the CSV file and the database synchronised. I learned that it is important to decide which file is the main source of data and make sure that changes are handled consistently.

If I had more time, I would improve the menu further and add more ways to filter and compare purchases. I would also like to make the charts interactive in a future version.

Overall, this project gave me practical experience with Python, SQL, SQLite, pandas, Matplotlib and GitHub. It also helped me understand more clearly how data can be collected, stored, checked, analysed and presented.

## 12. Limitations

The results depend on the records included in the CSV file. The project only analyses purchases that have been recorded, so it may not show every expense.

Incorrect or missing information can affect the results. The program checks several common input problems, but it cannot independently confirm that every purchase detail is correct.

This is a small personal spending tracker. It is designed for this assignment and is not a full banking or budgeting application.
