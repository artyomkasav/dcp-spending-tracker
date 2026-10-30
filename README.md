# Spending Tracker



## 1. Project Overview



Spending Tracker is a Python application developed as part of the Data Centric Programming 2026 assignment.



The purpose of this project is to record, store and analyse personal spending. Each purchase is stored as an individual record, allowing spending patterns to be explored across different dates, shops, categories and payment methods.



The application uses CSV files for data collection, SQLite for database storage, SQL for querying data, and pandas and Matplotlib for data analysis and visualisation.



## 2. Project Objectives



The main objectives are:



- Record individual purchases and their costs.

- Store purchase records in an SQLite database.

- Validate data before importing it into the database.

- Analyse spending using SQL and pandas.

- Visualise spending patterns using charts.

- Provide an interactive terminal menu for exploring and adding purchases.



## 3. Technologies Used



| Technology     | Purpose                                   |

| -------------- | ----------------------------------------- |

| Python         | Main programming language                 |

| CSV            | Initial data storage                      |

| SQLite         | Relational database                       |

| SQL            | Querying and aggregating purchase records |

| pandas         | Data analysis                             |

| Matplotlib     | Data visualisation                        |

| Git and GitHub | Version control and project hosting       |



## 4. Dataset Description



The dataset contains individual purchase records.



Each row represents one purchased item, rather than an entire shopping receipt.



The dataset is stored in:



`data/spendings.csv`



### Data Dictionary



| Column         | Data type | Description                                   |

| -------------- | --------- | --------------------------------------------- |

| date           | DATE      | Date when the purchase was made (YYYY-MM-DD)  |

| category       | TEXT      | Purchase category, such as Food or Household  |

| item           | TEXT      | Name and description of the purchased item    |

| amount         | REAL      | Price paid for the individual item, in EUR    |

| shop           | TEXT      | Shop or retailer where the item was purchased |

| need_want      | TEXT      | Classification of the purchase: Need or Want  |

| payment_method | TEXT      | Payment method: Cash, Revolut or PTSB         |



### Data Collection Method



Purchase information is intended to be collected manually from personal shopping records, receipts and transaction information.



Dates, prices, shops and payment methods should be recorded as accurately as possible.



Missing information should not be invented or estimated.



## 5. Research Questions



The project aims to investigate the following questions:



1. Which shops account for the largest proportion of total spending?

2. How much money is spent on Needs compared with Wants?

3. How does spending vary across different dates?



Additional questions may include:



- Which payment method accounts for the most spending?

- What is the average amount spent per purchased item?

- Which spending categories account for the highest costs?



## 6. Project Structure



```text

dcp-spending-tracker/

│

├── data/

│   └── spendings.csv

│

├── charts/

│   ├── spending_by_shop.png

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



## 7. Application Features



### Data Validation and Database



The application validates purchase records and checks required fields, date formats, numeric amounts and classification values.



Valid records are imported into an SQLite database.



### SQL Analysis



SQL queries are used to:



- Calculate total spending.

- Group spending by shop.

- Group spending by category.

- Compare Needs and Wants.

- Analyse spending by payment method.

- Calculate the average purchase amount.

- Filter purchases by date.



### Interactive Terminal Menu



The application provides a terminal-based interface that allows users to:



- View all purchases.

- View total spending.

- Explore spending by shop.

- Explore spending by category.

- Filter purchases by date.

- Add new purchases.

- Analyse payment methods.

- Compare Needs and Wants.

- Calculate average purchase amounts.



### Data Analysis and Visualisation



Pandas is used to load and analyse the dataset.



Matplotlib is used to generate the following visualisations:



1. Total Spending by Shop.

2. Needs vs Wants.

3. Daily Spending.

4. Spending by Payment Method.



The charts are saved in the `charts/` directory.



## 8. How to Run the Project



### Requirements



Python 3 and the following libraries are required:



```bash

pip install pandas matplotlib

```



### Run the application



```bash

python main.py

```



### Run the analysis



```bash

python analysis.py

```



## 9. Project Progress



The following components have been implemented:



- [x] Initial CSV dataset structure.

- [x] SQLite database creation.

- [x] Data validation.

- [x] CSV-to-SQLite import.

- [x] SQL queries and spending summaries.

- [x] Interactive terminal menu.

- [x] Adding new purchases.

- [x] Pandas data analysis.

- [x] Four spending visualisations.



Further work:



- [ ] Expand the dataset with additional spending categories.

- [ ] Continue collecting and validating actual purchase records.

- [ ] Improve data validation and error handling.

- [ ] Add further analysis and visualisations.

- [ ] Complete project reflection and findings.

- [ ] Prepare the final project demonstration.



## 10. Limitations



The quality of the analysis depends on the accuracy and completeness of the collected data.



The dataset represents only the purchases recorded during the selected collection period. It may not represent all spending over a longer period.



Any missing or incomplete purchase information can affect the results.



## 11. Findings



This section will be completed after analysing the final collected dataset.



It will summarise the main spending patterns, answer the research questions and discuss any limitations discovered during the analysis.



## 12. Reflection



This section will describe the development process, challenges encountered, skills learned and possible improvements to the application.
