# Personal Finance Tracker

A desktop program made with Python, Tkinter and SQLite that lets people keep track of and manage their money.

## Features

- Dashboard that shows income, expenses and the current balance.

- Add new income and expense transactions.

- View and search transaction history.

- Filter transactions by type and category.

- Edit and delete existing transactions.

- Spending summaries by category.

- Input validation for amounts and dates.

- Persistent storage using an SQLite database.

## Technologies Used

- **Python**. Application logic and validation.

- **Tkinter**. Graphical user interface.

- **SQLite**. Database storage.

- **. Github**. Version. Project hosting.

## How to Run

1. Install Python 3.

2.. Clone this repository.

3. Open a terminal in the project folder.

4. Run:

```bash

python main.py

```

The Personal Finance Tracker creates its database and tables automatically when first launched.

## Project Structure

```text

Personal-Finance-Tracker/

├── main.py

├── database.py

├── README.md

└── data/

└── finance_tracker.db

```

## Testing

The Personal Finance Tracker has been tested for:

- Adding income and expenses.

- Rejecting zero and negative amounts.

- Rejecting dates.

- Searching and filtering transactions.

- Editing and deleting transactions.

- Updating totals correctly.

## Future Improvements

- charts and visual reports.

- Exporting transactions to CSV.

- Monthly budgets and savings goals.

- Improved interface design.

## Learning Outcomes

This project has helped me develop skills, in Python programming, GUI development, relational databases SQL queries, input validation and software testing.