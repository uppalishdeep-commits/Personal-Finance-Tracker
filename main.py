
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from database import (
    create_tables,
    add_transaction,
    update_transaction,
    delete_transaction,
    get_transactions,
    get_summary,
    get_category_summary,
    CATEGORIES
)


class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1100x720")
        self.root.minsize(850, 600)

        self.selected_id = None
        self.search_var = tk.StringVar()
        self.type_filter = tk.StringVar(value="All")
        self.category_filter = tk.StringVar(value="All")

        self.setup_style()
        self.build_interface()
        self.refresh()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Title.TLabel", font=("Arial", 22, "bold"))
        style.configure("CardTitle.TLabel", font=("Arial", 10))
        style.configure("CardValue.TLabel", font=("Arial", 17, "bold"))
        style.configure("TButton", padding=7)

    def build_interface(self):
        header = ttk.Frame(self.root, padding=(20, 18))
        header.pack(fill="x")

        ttk.Label(
            header, text="Personal Finance Tracker",
            style="Title.TLabel"
        ).pack(side="left")

        ttk.Button(
            header, text="+ Add Transaction",
            command=self.add_new
        ).pack(side="right")

        self.cards = ttk.Frame(self.root, padding=(20, 0, 20, 15))
        self.cards.pack(fill="x")

        self.income_value = self.create_card(
            "Total Income", self.cards, 0
        )
        self.expense_value = self.create_card(
            "Total Expenses", self.cards, 1
        )
        self.balance_value = self.create_card(
            "Current Balance", self.cards, 2
        )
        self.count_value = self.create_card(
            "Transactions", self.cards, 3
        )

        filters = ttk.LabelFrame(
            self.root, text="Search and filter", padding=12
        )
        filters.pack(fill="x", padx=20, pady=(0, 12))

        ttk.Label(filters, text="Search").grid(
            row=0, column=0, padx=5, sticky="w"
        )
        search_entry = ttk.Entry(
            filters, textvariable=self.search_var, width=25
        )
        search_entry.grid(row=1, column=0, padx=5, sticky="ew")
        search_entry.bind("<KeyRelease>", lambda event: self.refresh_table())

        ttk.Label(filters, text="Type").grid(
            row=0, column=1, padx=5, sticky="w"
        )
        type_box = ttk.Combobox(
            filters, textvariable=self.type_filter,
            values=["All", "Income", "Expense"],
            state="readonly", width=13
        )
        type_box.grid(row=1, column=1, padx=5, sticky="ew")
        type_box.bind("<<ComboboxSelected>>", lambda event: self.refresh_table())

        ttk.Label(filters, text="Category").grid(
            row=0, column=2, padx=5, sticky="w"
        )
        category_box = ttk.Combobox(
            filters, textvariable=self.category_filter,
            values=["All"] + CATEGORIES,
            state="readonly", width=17
        )
        category_box.grid(row=1, column=2, padx=5, sticky="ew")
        category_box.bind(
            "<<ComboboxSelected>>", lambda event: self.refresh_table()
        )

        ttk.Button(
            filters, text="Clear filters", command=self.clear_filters
        ).grid(row=1, column=3, padx=8)

        filters.columnconfigure(0, weight=2)
        filters.columnconfigure(1, weight=1)
        filters.columnconfigure(2, weight=1)

        history = ttk.LabelFrame(
            self.root, text="Transaction history", padding=10
        )
        history.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        columns = (
            "id", "date", "type", "category", "description", "amount"
        )
        self.table = ttk.Treeview(
            history, columns=columns, show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "date": "Date",
            "type": "Type",
            "category": "Category",
            "description": "Description",
            "amount": "Amount"
        }
        widths = {
            "id": 50, "date": 110, "type": 90,
            "category": 130, "description": 300, "amount": 110
        }

        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(
                column, width=widths[column],
                anchor="w" if column == "description" else "center"
            )

        scrollbar = ttk.Scrollbar(
            history, orient="vertical", command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.table.bind("<Double-1>", lambda event: self.edit_selected())

        actions = ttk.Frame(self.root, padding=(20, 0, 20, 10))
        actions.pack(fill="x")

        ttk.Button(
            actions, text="Edit selected", command=self.edit_selected
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            actions, text="Delete selected", command=self.delete_selected
        ).pack(side="left")
        ttk.Button(
            actions, text="Refresh", command=self.refresh
        ).pack(side="right")

        self.summary_text = tk.StringVar()
        ttk.Label(
            self.root, textvariable=self.summary_text,
            padding=(20, 0, 20, 12)
        ).pack(anchor="w")

    def create_card(self, title, parent, column):
        card = ttk.LabelFrame(parent, text=title, padding=12)
        card.grid(row=0, column=column, padx=5, sticky="nsew")
        parent.columnconfigure(column, weight=1)

        value = ttk.Label(card, text="£0.00", style="CardValue.TLabel")
        value.pack(anchor="w")
        return value

    def money(self, pence):
        return f"£{pence / 100:,.2f}"

    def refresh(self):
        summary = get_summary()
        self.income_value.config(text=self.money(summary["income"]))
        self.expense_value.config(text=self.money(summary["expenses"]))
        self.balance_value.config(text=self.money(summary["balance"]))
        self.count_value.config(text=str(summary["count"]))

        if summary["balance"] < 0:
            self.balance_value.config(foreground="red")
        else:
            self.balance_value.config(foreground="green")

        self.refresh_table()

        categories = get_category_summary()
        if categories:
            category_text = "   |   ".join(
                f"{name}: {self.money(amount)}"
                for name, amount in categories
            )
            self.summary_text.set("Spending by category: " + category_text)
        else:
            self.summary_text.set(
                "Spending by category: No expenses recorded yet."
            )

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        selected_type = self.type_filter.get()
        if selected_type == "All":
            selected_type = "All"

        rows = get_transactions(
            search=self.search_var.get().strip(),
            transaction_type=selected_type,
            category=self.category_filter.get()
        )

        for transaction in rows:
            transaction_id, amount, kind, trans_date, category, description = transaction
            display_amount = self.money(amount)

            if kind == "expense":
                display_amount = "-" + display_amount
            else:
                display_amount = "+" + display_amount

            self.table.insert("", "end", values=(
                transaction_id,
                trans_date,
                kind.title(),
                category,
                description,
                display_amount
            ))

    def clear_filters(self):
        self.search_var.set("")
        self.type_filter.set("All")
        self.category_filter.set("All")
        self.refresh_table()

    def add_new(self):
        self.open_transaction_form()

    def get_selected_transaction(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning(
                "No selection", "Select a transaction first."
            )
            return None

        transaction_id = int(
            self.table.item(selection[0], "values")[0]
        )

        for transaction in get_transactions():
            if transaction[0] == transaction_id:
                return transaction

        messagebox.showerror(
            "Not found", "That transaction could not be found."
        )
        return None

    def edit_selected(self):
        transaction = self.get_selected_transaction()
        if transaction:
            self.open_transaction_form(transaction)

    def delete_selected(self):
        transaction = self.get_selected_transaction()
        if not transaction:
            return

        transaction_id = transaction[0]
        confirmed = messagebox.askyesno(
            "Confirm deletion",
            f"Delete transaction #{transaction_id}? This cannot be undone."
        )

        if confirmed:
            delete_transaction(transaction_id)
            self.refresh()
            messagebox.showinfo("Deleted", "Transaction deleted successfully.")

    def open_transaction_form(self, transaction=None):
        editing = transaction is not None

        window = tk.Toplevel(self.root)
        window.title("Edit transaction" if editing else "Add transaction")
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()

        form = ttk.Frame(window, padding=20)
        form.pack(fill="both", expand=True)

        default_amount = ""
        default_type = "Expense"
        default_date = date.today().isoformat()
        default_category = "Food"
        default_description = ""

        if editing:
            _, amount, kind, default_date, default_category, default_description = transaction
            default_amount = f"{amount / 100:.2f}"
            default_type = kind.title()

        amount_var = tk.StringVar(value=default_amount)
        type_var = tk.StringVar(value=default_type)
        date_var = tk.StringVar(value=default_date)
        category_var = tk.StringVar(value=default_category)
        description_var = tk.StringVar(value=default_description)

        fields = [
            ("Amount (£)", amount_var),
            ("Date (YYYY-MM-DD)", date_var),
            ("Description", description_var)
        ]

        ttk.Label(form, text="Amount (£)").grid(
            row=0, column=0, sticky="w", pady=6
        )
        amount_entry = ttk.Entry(form, textvariable=amount_var, width=30)
        amount_entry.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="Type").grid(
            row=1, column=0, sticky="w", pady=6
        )
        ttk.Combobox(
            form, textvariable=type_var,
            values=["Income", "Expense"],
            state="readonly", width=27
        ).grid(row=1, column=1, pady=6)

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(
            row=2, column=0, sticky="w", pady=6
        )
        ttk.Entry(
            form, textvariable=date_var, width=30
        ).grid(row=2, column=1, pady=6)

        ttk.Label(form, text="Category").grid(
            row=3, column=0, sticky="w", pady=6
        )
        ttk.Combobox(
            form, textvariable=category_var,
            values=CATEGORIES, state="readonly", width=27
        ).grid(row=3, column=1, pady=6)

        ttk.Label(form, text="Description").grid(
            row=4, column=0, sticky="w", pady=6
        )
        ttk.Entry(
            form, textvariable=description_var, width=30
        ).grid(row=4, column=1, pady=6)

        def save():
            raw_amount = amount_var.get().strip()
            raw_date = date_var.get().strip()
            kind = type_var.get().lower()
            category = category_var.get()
            description = description_var.get().strip()

            try:
                amount = float(raw_amount)
                if amount <= 0:
                    raise ValueError
                amount_pence = round(amount * 100)
                if amount_pence <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid amount",
                    "Enter an amount greater than £0.00.",
                    parent=window
                )
                return

            try:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                if parsed_date.isoformat() != raw_date:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid date",
                    "Enter a real date in YYYY-MM-DD format.",
                    parent=window
                )
                return

            if not category:
                messagebox.showerror(
                    "Missing category", "Choose a category.", parent=window
                )
                return

            if editing:
                update_transaction(
                    transaction[0], amount_pence, kind, raw_date,
                    category, description
                )
            else:
                add_transaction(
                    amount_pence, kind, raw_date, category, description
                )

            window.destroy()
            self.refresh()

        buttons = ttk.Frame(form)
        buttons.grid(row=5, column=0, columnspan=2, pady=(15, 0), sticky="e")

        ttk.Button(
            buttons, text="Cancel", command=window.destroy
        ).pack(side="left", padx=5)
        ttk.Button(
            buttons, text="Save transaction", command=save
        ).pack(side="left", padx=5)

        amount_entry.focus_set()


def main():
    create_tables()
    root = tk.Tk()
    FinanceTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()



