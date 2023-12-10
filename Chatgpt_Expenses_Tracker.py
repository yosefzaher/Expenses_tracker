from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
import requests
import json

class Database:
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Expenses_Tracker(
            Amount INTEGER, 
            Currency STRING,
            Category STRING,
            Date STRING,
            Payment_Method STRING
        )""")

    def execute_query(self, query, *args):
        self.cursor.execute(query, args)
        self.connection.commit()

    def add(self, amount, currency, category, date, payment_method):
        self.execute_query(
            "INSERT INTO Expenses_Tracker(Amount, Currency, Category, Date, Payment_Method) VALUES (?, ?, ?, ?, ?)",
            amount, currency, category, date, payment_method
        )

    def get_all_expenses(self):
        self.cursor.execute("SELECT * FROM Expenses_Tracker")
        return self.cursor.fetchall()

    def update(self, old, new):
        self.execute_query(
            "UPDATE Expenses_Tracker SET Amount=?, Currency=?, Category=?, Date=?, Payment_Method=? "
            "WHERE Amount=? AND Currency=? AND Category=? AND Date=? AND Payment_Method=?",
            *new, *old
        )

    def delete(self, old):
        self.execute_query(
            "DELETE FROM Expenses_Tracker WHERE Amount=? AND Currency=? AND Category=? AND Date=? AND Payment_Method=?",
            *old
        )

    def delete_all(self):
        self.execute_query("DELETE FROM Expenses_Tracker")
        update_treeview()

    def total(self):
        self.cursor.execute("SELECT SUM(Amount) FROM Expenses_Tracker")
        return int(self.cursor.fetchone()[0])

    def close(self):
        self.connection.close()

def update_treeview():
    for item in app.expenses_data.get_children():
        app.expenses_data.delete(item)

    expenses = data_Base.get_all_expenses()

    for expense in expenses:
        app.expenses_data.insert("", "end", values=expense)

def handle_error(message):
    messagebox.showerror("Error", message)

def add_expense():
    try:
        data_Base.add(
            app.amount_entry.get(),
            app.currency_combo.get(),
            app.category_combo.get(),
            app.date_datepicker.get(),
            app.payment_method_combo.get()
        )
        update_treeview()
    except Exception as e:
        handle_error(str(e))

def delete_expense():
    selected_item = app.expenses_data.selection()
    if not selected_item:
        handle_error("Please select an expense to delete.")
        return

    values = app.expenses_data.item(selected_item, 'values')
    try:
        data_Base.delete(values)
        update_treeview()
    except Exception as e:
        handle_error(str(e))

def update_expense_window():
    selected_item = app.expenses_data.selection()
    if not selected_item:
        handle_error("Please select an expense to update.")
        return

    old_values = app.expenses_data.item(selected_item, 'values')

    update_window = Toplevel(app)
    update_window.title("Update Expense")

    update_amount = Entry(update_window)
    update_currency = ttk.Combobox(update_window, values=['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD', 'NOK', 'INR', 'BRL', 'ZAR', 'MXN', 'EGP'])
    update_category = ttk.Combobox(update_window, values=['Life Expenses', 'Electricity Bill', 'Gas Bill', 'Rental', 'Grocery', 'Savings', 'Education', 'Charity'])
    update_date = DateEntry(update_window)
    update_payment_method = ttk.Combobox(update_window, values=['Credit Card', 'Debit Card', 'Transfer', 'Paypal', 'Cash'])

    update_amount.insert(0, old_values[0])
    update_currency.set(old_values[1])
    update_category.set(old_values[2])
    update_date.set_date(old_values[3])
    update_payment_method.set(old_values[4])

    label_amount = Label(update_window, text="Amount:")
    label_currency = Label(update_window, text="Currency:")
    label_category = Label(update_window, text="Category:")
    label_date = Label(update_window, text="Date:")
    label_payment_method = Label(update_window, text="Payment Method:")

    update_button = Button(update_window, text="Update Expense", command=lambda: update_expense_database(old_values, update_amount, update_currency, update_category, update_date, update_payment_method))

    label_amount.grid(row=0, column=0)
    update_amount.grid(row=0, column=1)
    label_currency.grid(row=1, column=0)
    update_currency.grid(row=1, column=1)
    label_category.grid(row=2, column=0)
    update_category.grid(row=2, column=1)
    label_date.grid(row=3, column=0)
    update_date.grid(row=3, column=1)
    label_payment_method.grid(row=4, column=0)
    update_payment_method.grid(row=4, column=1)
    update_button.grid(row=5, columnspan=2)

def update_expense_database(old_values, update_amount, update_currency, update_category, update_date, update_payment_method):
    new_values = [
        update_amount.get(),
        update_currency.get(),
        update_category.get(),
        update_date.get(),
        update_payment_method.get()
    ]

    try:
        data_Base.update(old_values, new_values)
        update_treeview()
    except Exception as e:
        handle_error(str(e))

def calculate_all_the_amount_in_usd():
    all_data = data_Base.get_all_expenses()
    payload = {}
    headers = {
        "apikey": "d6orT12AcBBuc0a8nkTNrLgVIIGYxuaQ"
    }
    total = 0
    for i in range(len(all_data)):
        url = f"https://api.apilayer.com/fixer/convert?to=USD&from={all_data[i][1]}&amount={all_data[i][0]}"
        response = requests.get(url, headers=headers, data=payload)
        status_code = response.status_code

        if status_code == 200:
            result = json.loads(response.text)
            total += float(result['result'])
        else:
            handle_error(f"Request failed with status code {status_code}.")

    messagebox.showinfo("Result", f"The total expenses in USD = {total}$")

def application_gui():
    global app
    app = Tk()
    app.iconbitmap(r"D:\Front_end Dibloma\مسار أسس البرمجه\the final project of the path\cost.ico")
    app.title('Expense Tracker')
    app.geometry('650x700')
    app.configure(background='#fafad2')

    app.expenses_data = ttk.Treeview(app, columns=("Amount", "Currency", "Category", "Date", "Payment_Method"))
    update_treeview()

    column_data = [("Amount", 120), ("Currency", 120), ("Category", 120), ("Date", 120), ("Payment_Method", 120)]

    for col, width in column_data:
        app.expenses_data.column("#0", width=0, stretch=0)
        app.expenses_data.column(col, width=width, minwidth=60, anchor=W)
        app.expenses_data.heading(col, text=col, anchor=W)

    app.expenses_data.pack()

    label_frame = Frame(app, bg='#fafad2')

    labels = ["Amount", "Currency", "Category", "Date", "Payment Method"]
    width_ = 15

    entries = [
        Entry(label_frame, width=18),
        ttk.Combobox(label_frame, values=['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD', 'NOK', 'INR', 'BRL', 'ZAR', 'MXN', 'EGP'], width=width_),
        ttk.Combobox(label_frame, values=['Life Expenses', 'Electricity Bill', 'Gas Bill', 'Rental', 'Grocery', 'Savings', 'Education', 'Charity'], width=width_),
        DateEntry(label_frame, width=width_),
        ttk.Combobox(label_frame, values=['Credit Card', 'Debit Card', 'Transfer', 'Paypal', 'Cash'], width=width_)
    ]

    for i, label in enumerate(labels):
        Label(label_frame, text=f"{label}:", bg='#fafad2', font=('Helvetica', 17)).grid(row=i, column=0)
        entries[i].grid(row=i, column=1)

    label_frame.pack()

    button_frame = Frame(app, background='#fafad2')

    button_data = [
        ("Add Expense", add_expense),
        ("Delete Expense", delete_expense),
        ("Update an Expense", update_expense_window),
        ("Delete All Expenses", data_Base.delete_all),
        ("ALL in USD", calculate_all_the_amount_in_usd)
    ]

    for text, command in button_data:
        Button(button_frame, text=text, width=15, height=1, command=command).pack(padx=10, pady=10)

    button_frame.pack(side="top")

    app.mainloop()

def main():
    global data_Base
    data_Base = Database(r"""D:\Front_end Dibloma\مسار أسس البرمجه\the final project of the path\Expenses.db""")
    application_gui()
    data_Base.close()

if __name__ == "__main__":
    main()

