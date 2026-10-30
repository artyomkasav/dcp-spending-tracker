# Spending Tracker

## 1. About the Project

Spending Tracker is a Python project made for the Data Centric Programming 2026 assignment.

The program records purchases and helps explore where money is spent. Each row in the dataset is one purchased item.

The project uses a CSV file to keep the purchase records. When the program starts, it reads the CSV file and updates the SQLite database from it. This means the CSV file is the main copy of the data.

The project can:
- Show and search purchases.
- Calculate total and average spending.
- Compare spending between shops and categories.
- Compare Needs and Wants.
- Show spending by payment method.
- Filter purchases by date.
- Add and delete purchases.
- Create charts from the CSV data.

## 2. Project Goals

The goals of this project are to:

- Record purchases with their dates, prices and other details.
- Keep the records in a CSV file.
- Store the records in an SQLite database.
- Check that the data is valid.
- Use SQL to answer questions about spending.
- Use pandas to analyse the data.
- Use Matplotlib to create charts.
- Make it possible to explore the data through a simple terminal menu.

## 3. Tools Used

| Tool | What it is used for |
|---|---|
| Python | Main programming language |
| CSV | Stores the purchase records |
| SQLite | Stores the records in a database |
| SQL | Searches and groups the database records |
| pandas | Reads and analyses the CSV data |
| Matplotlib | Creates charts |
| Git and GitHub | Saves the project and tracks changes |

## 4. Dataset

The dataset is stored in `data/spendings.csv`.

Each row is one purchased item. It is not one full shopping receipt. For example, if a shopping trip contains five different items, it can be recorded as five rows.

### Data Dictionary

| Column | Type | Meaning |
|---|---|---|
| `date` | DATE / TEXT in CSV | Date of the purchase, in `YYYY-MM-DD` format |
| `category` | TEXT | Type of purchase, for example Food or Household |
| `item` | TEXT | Name of the purchased item |
| `amount` | REAL / number | Price of the item in euros |
| `shop` | TEXT | Shop where the item was bought |
| `need_want` | TEXT | Whether the purchase was a Need or a Want |
| `payment_method` | TEXT | How it was paid: Cash, Revolut or PTSB |

### Data Collection

Purchase details should be recorded from real purchases, receipts or transaction records.

Dates, item names, shops, prices and payment methods should be entered as accurately as possible. Missing information should not be guessed or made up.

The dataset used for the final assignment must contain real records collected for this project. Test or example data must not be presented as real purchases.

## 5. Research Questions

This project looks at these questions:

1. Which shops have the highest total spending?
2. How much is spent on Needs compared with Wants?
3. How does spending change from one date to another?

The program also shows:
- Spending by category.
- Spending by payment method.
- The average price of a purchase.
- The most expensive purchases.

## 6. Project Files

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

`spending.db` is the SQLite database created by the program. If it is ignored by Git, it may not appear in the GitHub repository. The program can create it again when it runs.

## 7. How the Program Works

### CSV and Database

The CSV file is the main source of purchase data.

When `main.py` starts, it:
1. Reads the CSV file.
2. Checks that the required columns are present.
3. Checks dates, prices and other required values.
4. Replaces the records in the SQLite database with the current CSV records.

If the CSV contains invalid records, the program stops instead of replacing the CSV with database data.

When a purchase is added or deleted through the menu, the change is saved to the database and written back to the CSV file.

### Database Queries

The program uses SQL queries to:
- Calculate total spending.
- Group spending by shop.
- Group spending by category.
- Compare Needs and Wants.
- Group spending by payment method.
- Calculate the average purchase amount.
- Filter purchases by date.
- Search for purchases.

### Terminal Menu

Run `main.py` to open the menu.

The menu has these options:

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

## 8. Data Analysis and Charts

`analysis.py` reads the data from `data/spendings.csv` using pandas.

It prints:
- Number of purchases.
- Total spending.
- Average purchase price.
- Most expensive and cheapest purchases.
- Date range in the dataset.
- Spending by shop.
- Spending by category.
- Spending on Needs and Wants.
- Spending by payment method.
- Daily spending.
- The ten most expensive purchases.

It also creates five charts using Matplotlib:

1. `spending_by_shop.png` — total spending at each shop.
2. `spending_by_category.png` — total spending in each category.
3. `needs_vs_wants.png` — comparison of Needs and Wants.
4. `daily_spending.png` — spending on each date.
5. `payment_methods.png` — spending by payment method.

The charts are saved in the `charts` folder. They do not open automatically when the script runs. Open the PNG files from that folder to view them.

## 9. How to Run

Python 3 is required.

Install the libraries used for analysis:

```bash
pip install pandas matplotlib
```

SQLite is included with Python, so it does not need to be installed separately.

### Run the spending tracker

```bash
python main.py
```

### Run the analysis and create the charts

```bash
python analysis.py
```

Run both commands from the main project folder.

## 10. Current Project Progress

| Part | Status |
|---|---|
| CSV file with the required columns | Implemented |
| SQLite database | Implemented |
| CSV data validation | Implemented |
| CSV-to-database synchronisation | Implemented |
| SQL queries and summaries | Implemented |
| Terminal menu | Implemented |
| Add and delete purchases | Implemented |
| Search and date filter | Implemented |
| pandas analysis | Implemented |
| Five charts | Implemented |
| Final data collection evidence | Still needs checking |
| Findings based on the final real dataset | To be completed |
| Project reflection | To be completed |
| Final screenshots and demonstration preparation | To be completed |

## 11. Findings

Complete this section after running the analysis on the final collected dataset.

Use the results to answer the research questions:

- Which shop has the highest total spending?
- Is more money spent on Needs or Wants?
- Which dates have the highest spending?

Add the actual results from `analysis.py` here. Do not use example or test data as final findings.

## 12. Limitations

The results depend on the data entered into the CSV file.

The dataset only shows the purchases that were recorded. It may not include every expense, so it cannot show all spending outside the recorded period.

The results may also be affected by missing or incorrect records. The project is a small personal spending tracker, not a full banking or budgeting system.

## 13. Reflection

Complete this section before submission.

Write a few sentences in your own words about:
- What you learned while using Python, SQLite, SQL, pandas and Matplotlib.
- What problems you had while building the program and how you fixed them.
- Which part was the hardest.
- What you would improve if you had more time.
