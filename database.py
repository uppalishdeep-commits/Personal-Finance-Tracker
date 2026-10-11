
import sqlite3
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "finance_tracker.db"

CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills", "Entertainment",
    "Education", "Health", "Salary", "Gift", "Other"
]


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    with connect() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_pence INTEGER NOT NULL CHECK (amount_pence > 0),
                transaction_type TEXT NOT NULL
                    CHECK (transaction_type IN ('income', 'expense')),
                transaction_date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT ''
            )
        """)


def add_transaction(amount_pence, transaction_type, transaction_date,
                    category, description=""):
    with connect() as connection:
        connection.execute("""
            INSERT INTO transactions
                (amount_pence, transaction_type, transaction_date,
                 category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            amount_pence, transaction_type, transaction_date,
            category, description
        ))


def update_transaction(transaction_id, amount_pence, transaction_type,
                       transaction_date, category, description=""):
    with connect() as connection:
        connection.execute("""
            UPDATE transactions
            SET amount_pence = ?, transaction_type = ?,
                transaction_date = ?, category = ?, description = ?
            WHERE id = ?
        """, (
            amount_pence, transaction_type, transaction_date,
            category, description, transaction_id
        ))


def delete_transaction(transaction_id):
    with connect() as connection:
        connection.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )


def get_transactions(search="", transaction_type="All",
                     category="All"):
    query = """
        SELECT id, amount_pence, transaction_type,
               transaction_date, category, description
        FROM transactions
        WHERE (category LIKE ? OR description LIKE ?)
    """
    parameters = [f"%{search}%", f"%{search}%"]

    if transaction_type != "All":
        query += " AND transaction_type = ?"
        parameters.append(transaction_type.lower())

    if category != "All":
        query += " AND category = ?"
        parameters.append(category)

    query += " ORDER BY transaction_date DESC, id DESC"

    with connect() as connection:
        return connection.execute(query, parameters).fetchall()


def get_summary():
    with connect() as connection:
        income = connection.execute("""
            SELECT COALESCE(SUM(amount_pence), 0)
            FROM transactions WHERE transaction_type = 'income'
        """).fetchone()[0]

        expenses = connection.execute("""
            SELECT COALESCE(SUM(amount_pence), 0)
            FROM transactions WHERE transaction_type = 'expense'
        """).fetchone()[0]

        count = connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        return {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "count": count
        }


def get_category_summary():
    with connect() as connection:
        return connection.execute("""
            SELECT category, SUM(amount_pence)
            FROM transactions
            WHERE transaction_type = 'expense'
            GROUP BY category
            ORDER BY SUM(amount_pence) DESC
        """).fetchall()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
    print("Saved transactions:", len(get_transactions()))


