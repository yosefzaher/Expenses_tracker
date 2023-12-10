from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
import requests
import json


class Database:
    def __init__(self, data_base_path):
        self.data_base_path = data_base_path
        self.data_base = sqlite3.connect(data_base_path)
        self.curser = self.data_base.cursor()

        self.curser.execute("""CREATE TABLE IF NOT EXISTS Expenses_Tracker(
            Amount INTEGER, 
            Currency STRING,
            Category STRING,
            Date STRING,
            Payment_Method STRING
        )""")

    def add(self, amount, currency, category, date, payment_method):
        self.curser.execute(f"""INSERT INTO Expenses_Tracker(Amount, Currency, Category, Date, Payment_Method)
                VALUES (?, ?, ?, ?, ?)""", (amount, currency, category, date, payment_method))
        self.commit()

    def get_all_expenses(self):
        self.curser.execute("SELECT * FROM Expenses_Tracker")
        return self.curser.fetchall()

    def update(self, old, new):
        self.curser.execute(f"""UPDATE Expenses_Tracker SET Amount=?, Currency=?, Category=?, Date=?, Payment_Method=?
                WHERE Amount=? AND Currency=? AND Category=? AND Date=? AND Payment_Method=?""",
                (new[0], new[1], new[2], new[3], new[4], old[0], old[1], old[2], old[3], old[4]))
        self.commit()

    def delete(self, old):
        self.curser.execute("""DELETE FROM Expenses_Tracker WHERE Amount=? AND Currency=? AND
                Category=? AND Date=? AND Payment_Method=?""", (old[0], old[1], old[2], old[3], old[4]))
        self.commit()

    def delete_all(self):
        self.curser.execute("DELETE FROM Expenses_Tracker")
        self.commit()
        update_treeview()

    def total(self):
        sum = 0
        self.curser.execute("SELECT SUM(Amount) FROM Expenses_Tracker ")
        sum += int(self.curser.fetchone()[0])
        self.commit()
        return sum

    def commit(self):
        self.data_base.commit()

    def close(self):
        self.data_base.close()

def update_treeview():
    for item in app.expenses_data.get_children():
        app.expenses_data.delete(item)

    expenses = data_Base.get_all_expenses()

    for expense in expenses:
        app.expenses_data.insert("", "end", values=expense)

def add_expense():
    amount = app.amount_entry.get()
    currency = app.currency_combo.get()
    category = app.category_combo.get()
    date = app.date_datepicker.get()
    payment_method = app.payment_method_combo.get()

    data_Base.add(amount, currency, category, date, payment_method)
    update_treeview()

def delete_expense():
    selected_item = app.expenses_data.selection()
    if not selected_item:
        messagebox.showinfo("Error", "Please select an expense to delete.")
        return

    values = app.expenses_data.item(selected_item, 'values')
    data_Base.delete(values)
    update_treeview()

def update_expense_window():
    selected_item = app.expenses_data.selection()
    if not selected_item:
        messagebox.showinfo("Error", "Please select an expense to update.")
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


    update_button = Button(update_window, text="Update Expense", command=lambda: update_expense_dataBase(old_values, update_amount, update_currency, update_category, update_date, update_payment_method))


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

def update_expense_dataBase(old_values, update_amount, update_currency, update_category, update_date, update_payment_method):

    new_values = [
        update_amount.get(),
        update_currency.get(),
        update_category.get(),
        update_date.get(),
        update_payment_method.get()
    ]


    data_Base.update(old_values, new_values)


    update_treeview()

import json

def Calculate_all_theAmount_in_USD():
    all_data = data_Base.get_all_expenses()
    payload = {}
    headers = {
        "apikey": "d6orT12AcBBuc0a8nkTNrLgVIIGYxuaQ"
    }
    total = 0
    for i in range(len(all_data)):
        url = f"https://api.apilayer.com/fixer/convert?to=USD&from={all_data[i][1]}&amount={all_data[i][0]}"
        response = requests.request("GET", url, headers=headers, data=payload)
        status_code = response.status_code

    if status_code == 200:
        result = json.loads(response.text)
        total += float(result['result'])
    else:
        messagebox.showerror("Error", f"Request failed with status code {status_code}.")

    messagebox.showinfo("Result", f"The total expenses in USD = {total}$")


def Application_GUI():
    global app
    app = Tk()
    app.iconbitmap(r"D:\Front_end Dibloma\مسار أسس البرمجه\the final project of the path\cost.ico")
    app.title('Expense Tracker')
    app.minsize(width=650, height=600)
    app.maxsize(width=650, height=600)
    app.geometry('650x700')
    app.configure(background='#fafad2')

    app.expenses_data = ttk.Treeview(app, columns=("Amount", "Currency", "Category", "Date", "Payment_Method"))
    update_treeview()

    app.expenses_data.column("#0", width=0, stretch=0)
    app.expenses_data.column("Amount", width=120, minwidth=60, anchor=W)
    app.expenses_data.column("Currency", width=120, minwidth=60, anchor=W)
    app.expenses_data.column("Category", width=120, minwidth=60, anchor=W)
    app.expenses_data.column("Date", width=120, minwidth=80, anchor=W)
    app.expenses_data.column("Payment_Method", width=120, minwidth=60, anchor=W)

    app.expenses_data.heading("Amount", text="Amount", anchor=W)
    app.expenses_data.heading("Currency", text="Currency", anchor=W)
    app.expenses_data.heading("Category", text="Category", anchor=W)
    app.expenses_data.heading("Date", text="Date", anchor=W)
    app.expenses_data.heading("Payment_Method", text="Payment_Method", anchor=W)

    app.expenses_data.pack()

    LabelFrame = Frame(app, bg='#fafad2')

    amount_label = Label(LabelFrame, text="Amount:", bg='#fafad2', font=('Helvetica', 17))
    currency_label = Label(LabelFrame, text="Currency:", bg='#fafad2', font=('Helvetica', 17))
    category_label = Label(LabelFrame, text="Category:", bg='#fafad2', font=('Helvetica', 17))
    date_label = Label(LabelFrame, text="Date:", bg='#fafad2', font=('Helvetica', 17))
    payment_method_label = Label(LabelFrame, text="Payment Method:", bg='#fafad2', font=('Helvetica', 17))

    width_ = 15

    app.amount_entry = Entry(LabelFrame, width=18)
    currencies = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD', 'NOK', 'INR', 'BRL', 'ZAR', 'MXN', 'EGP']
    app.currency_combo = ttk.Combobox(LabelFrame, values=currencies, width=width_)
    expense_categories = ['Life Expenses', 'Electricity Bill', 'Gas Bill', 'Rental', 'Grocery', 'Savings', 'Education', 'Charity']
    app.category_combo = ttk.Combobox(LabelFrame, values=expense_categories, width=width_)
    app.date_datepicker = DateEntry(LabelFrame, width=width_)
    payment_methods = ['Credit Card', 'Debit Card', 'Transfer', 'Paypal', 'Cash']
    app.payment_method_combo = ttk.Combobox(LabelFrame, values=payment_methods, width=width_)

    amount_label.grid(row=0, column=1)
    currency_label.grid(row=1, column=1)
    category_label.grid(row=2, column=1)
    date_label.grid(row=3, column=1)
    payment_method_label.grid(row=4, column=1)
    app.amount_entry.grid(row=0, column=2)
    app.currency_combo.grid(row=1, column=2)
    app.category_combo.grid(row=2, column=2)
    app.date_datepicker.grid(row=3, column=2)
    app.payment_method_combo.grid(row=4, column=2)

    LabelFrame.pack()

    buttonFrame = Frame(app, background='#fafad2')

    add_button = Button(buttonFrame, text="Add Expense", width=15, height=1, command=add_expense)
    delete_button = Button(buttonFrame, text="Delete Expense", width=15, height=1, command=delete_expense)
    update_button = Button(buttonFrame, text="Update an Expense", width=15, height=1, command=update_expense_window)
    deleteAll_button = Button(buttonFrame, text="Delete All Expenses", width=15, height=1, command=data_Base.delete_all)
    all_in_USD_button =  Button(buttonFrame, text="ALL in USD", width=15, height=1, command=Calculate_all_theAmount_in_USD)

    add_button.grid(row=3, column=0, padx=10, pady=10)
    delete_button.grid(row=4, column=0, padx=10, pady=10)
    update_button.grid(row=5, column=0, padx=10, pady=10)
    deleteAll_button.grid(row=6, column=0, padx=10, pady=10)
    all_in_USD_button.grid(row=7, column=0, padx=10, pady=10)

    buttonFrame.pack(side="top")

    app.mainloop()

def main():
    global data_Base
    data_Base = Database(r"""D:\Front_end Dibloma\مسار أسس البرمجه\the final project of the path\Expenses.db""")
    Application_GUI()
    data_Base.close()

if __name__ == "__main__":
    main()