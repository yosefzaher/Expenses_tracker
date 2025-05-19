from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
import requests
import json
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation


class Database:
    def __init__(self, data_base_path):
        self.data_base_path = data_base_path
        self.data_base = sqlite3.connect(data_base_path)
        self.curser = self.data_base.cursor()

        self.curser.execute("""CREATE TABLE IF NOT EXISTS Expenses_Tracker(
            Amount DECIMAL(10,2), 
            Currency STRING,
            Category STRING,
            Date STRING,
            Payment_Method STRING
        )""")

    def add(self, amount, currency, category, date, payment_method):
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            self.curser.execute(f"""INSERT INTO Expenses_Tracker(Amount, Currency, Category, Date, Payment_Method)
                    VALUES (?, ?, ?, ?, ?)""", (str(amount), currency, category, date, payment_method))
            self.commit()
            return True, None
        except (InvalidOperation, ValueError) as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error adding expense: {str(e)}"

    def get_all_expenses(self):
        self.curser.execute("SELECT * FROM Expenses_Tracker")
        return self.curser.fetchall()

    def update(self, old, new):
        try:
            amount = Decimal(new[0])
            if amount <= 0:
                raise ValueError("Amount must be positive")
            self.curser.execute(f"""UPDATE Expenses_Tracker SET Amount=?, Currency=?, Category=?, Date=?, Payment_Method=?
                    WHERE Amount=? AND Currency=? AND Category=? AND Date=? AND Payment_Method=?""",
                    (str(amount), new[1], new[2], new[3], new[4], old[0], old[1], old[2], old[3], old[4]))
            self.commit()
            return True, None
        except (InvalidOperation, ValueError) as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error updating expense: {str(e)}"

    def delete(self, old):
        try:
            self.curser.execute("""DELETE FROM Expenses_Tracker WHERE Amount=? AND Currency=? AND
                    Category=? AND Date=? AND Payment_Method=?""", (old[0], old[1], old[2], old[3], old[4]))
            self.commit()
            return True, None
        except Exception as e:
            return False, f"Error deleting expense: {str(e)}"

    def delete_all(self):
        try:
            self.curser.execute("DELETE FROM Expenses_Tracker")
            self.commit()
            return True, None
        except Exception as e:
            return False, f"Error deleting all expenses: {str(e)}"

    def total(self):
        try:
            self.curser.execute("SELECT SUM(CAST(Amount AS DECIMAL(10,2))) FROM Expenses_Tracker")
            result = self.curser.fetchone()[0]
            return Decimal(result if result else 0)
        except Exception:
            return Decimal(0)

    def commit(self):
        self.data_base.commit()

    def close(self):
        self.data_base.close()

def validate_amount(amount_str):
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            return False, "Amount must be positive"
        return True, None
    except InvalidOperation:
        return False, "Invalid amount format"

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%m/%d/%y')
        return True, None
    except ValueError:
        return False, "Invalid date format"

def update_treeview():
    for item in app.expenses_data.get_children():
        app.expenses_data.delete(item)

    expenses = data_Base.get_all_expenses()
    for expense in expenses:
        app.expenses_data.insert("", "end", values=expense)
    
    # Update total label
    total = data_Base.total()
    app.total_label.config(text=f"Total Expenses: {total:.2f}")

def add_expense():
    amount = app.amount_entry.get().strip()
    currency = app.currency_combo.get()
    category = app.category_combo.get()
    date = app.date_datepicker.get()
    payment_method = app.payment_method_combo.get()

    # Validate inputs
    if not all([amount, currency, category, date, payment_method]):
        messagebox.showerror("Error", "All fields are required")
        return

    valid, error = validate_amount(amount)
    if not valid:
        messagebox.showerror("Error", error)
        return

    valid, error = validate_date(date)
    if not valid:
        messagebox.showerror("Error", error)
        return

    success, error = data_Base.add(amount, currency, category, date, payment_method)
    if success:
        update_treeview()
        # Clear inputs
        app.amount_entry.delete(0, END)
        app.currency_combo.set('')
        app.category_combo.set('')
        app.payment_method_combo.set('')
    else:
        messagebox.showerror("Error", error)

def delete_expense():
    selected_item = app.expenses_data.selection()
    if not selected_item:
        messagebox.showinfo("Error", "Please select an expense to delete.")
        return

    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
        values = app.expenses_data.item(selected_item, 'values')
        success, error = data_Base.delete(values)
        if success:
            update_treeview()
        else:
            messagebox.showerror("Error", error)

def update_expense_window():
    selected_item = app.expenses_data.selection()
    if not selected_item:
        messagebox.showinfo("Error", "Please select an expense to update.")
        return

    old_values = app.expenses_data.item(selected_item, 'values')

    update_window = Toplevel(app)
    update_window.title("Update Expense")
    update_window.geometry("400x300")
    update_window.configure(background='#fafad2')

    # Center the window
    update_window.transient(app)
    update_window.grab_set()
    
    # Create and pack widgets with proper spacing
    frame = Frame(update_window, bg='#fafad2', padx=20, pady=20)
    frame.pack(fill=BOTH, expand=True)

    labels = ["Amount:", "Currency:", "Category:", "Date:", "Payment Method:"]
    entries = []
    
    for i, label_text in enumerate(labels):
        Label(frame, text=label_text, bg='#fafad2').grid(row=i, column=0, pady=5, sticky=W)
    
    update_amount = Entry(frame)
    update_currency = ttk.Combobox(frame, values=['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD', 'NOK', 'INR', 'BRL', 'ZAR', 'MXN', 'EGP'])
    update_category = ttk.Combobox(frame, values=['Life Expenses', 'Electricity Bill', 'Gas Bill', 'Rental', 'Grocery', 'Savings', 'Education', 'Charity'])
    update_date = DateEntry(frame)
    update_payment_method = ttk.Combobox(frame, values=['Credit Card', 'Debit Card', 'Transfer', 'Paypal', 'Cash'])

    entries = [update_amount, update_currency, update_category, update_date, update_payment_method]
    
    for i, entry in enumerate(entries):
        entry.grid(row=i, column=1, pady=5, padx=5, sticky=EW)

    update_amount.insert(0, old_values[0])
    update_currency.set(old_values[1])
    update_category.set(old_values[2])
    update_date.set_date(old_values[3])
    update_payment_method.set(old_values[4])

    Button(frame, text="Update Expense", 
           command=lambda: update_expense_dataBase(old_values, update_amount, update_currency, 
                                                 update_category, update_date, update_payment_method, update_window),
           bg='#4CAF50', fg='white', pady=10).grid(row=5, columnspan=2, pady=20)

def update_expense_dataBase(old_values, update_amount, update_currency, update_category, update_date, update_payment_method, window):
    new_values = [
        update_amount.get().strip(),
        update_currency.get(),
        update_category.get(),
        update_date.get(),
        update_payment_method.get()
    ]

    # Validate inputs
    if not all(new_values):
        messagebox.showerror("Error", "All fields are required")
        return

    valid, error = validate_amount(new_values[0])
    if not valid:
        messagebox.showerror("Error", error)
        return

    valid, error = validate_date(new_values[3])
    if not valid:
        messagebox.showerror("Error", error)
        return

    success, error = data_Base.update(old_values, new_values)
    if success:
        update_treeview()
        window.destroy()
    else:
        messagebox.showerror("Error", error)

def Calculate_all_theAmount_in_USD():
    all_data = data_Base.get_all_expenses()
    if not all_data:
        messagebox.showinfo("Info", "No expenses to convert")
        return

    API_KEY = "d6orT12AcBBuc0a8nkTNrLgVIIGYxuaQ"  # In production, this should be in environment variables
    headers = {"apikey": API_KEY}
    total = Decimal(0)
    
    try:
        for expense in all_data:
            if expense[1] == 'USD':
                total += Decimal(expense[0])
                continue
                
            url = f"https://api.apilayer.com/fixer/convert?to=USD&from={expense[1]}&amount={expense[0]}"
            response = requests.request("GET", url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                total += Decimal(str(result['result']))
            else:
                messagebox.showerror("Error", f"Failed to convert {expense[1]} to USD")
                return
        
        messagebox.showinfo("Result", f"Total expenses in USD: ${total:.2f}")
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed: {str(e)}")

def export_to_csv():
    try:
        import csv
        from datetime import datetime
        
        filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Amount", "Currency", "Category", "Date", "Payment Method"])
            writer.writerows(data_Base.get_all_expenses())
        
        messagebox.showinfo("Success", f"Data exported to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {str(e)}")

def delete_all_expenses():
    if not data_Base.get_all_expenses():
        messagebox.showinfo("Info", "No expenses to delete")
        return
        
    if messagebox.askyesno("Confirm Delete All", "Are you sure you want to delete all expenses? This action cannot be undone."):
        success, error = data_Base.delete_all()
        if success:
            update_treeview()
            messagebox.showinfo("Success", "All expenses have been deleted")
        else:
            messagebox.showerror("Error", error)

def Application_GUI():
    global app
    app = Tk()
    app.title('Expense Tracker')
    app.minsize(width=800, height=700)
    app.maxsize(width=800, height=700)
    app.geometry('800x700')
    app.configure(background='#fafad2')

    # Try to set icon, fallback gracefully if not found
    try:
        icon_path = "cost.ico"
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)
    except:
        pass  # Ignore icon errors

    # Main frame for input fields
    input_frame = Frame(app, bg='#fafad2', padx=20, pady=20)
    input_frame.pack(fill=X)

    # Input fields
    Label(input_frame, text="Amount:", bg='#fafad2').grid(row=0, column=0, pady=5, sticky=W)
    app.amount_entry = Entry(input_frame)
    app.amount_entry.grid(row=0, column=1, pady=5, padx=5)

    Label(input_frame, text="Currency:", bg='#fafad2').grid(row=0, column=2, pady=5, sticky=W)
    app.currency_combo = ttk.Combobox(input_frame, values=['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD', 'NOK', 'INR', 'BRL', 'ZAR', 'MXN', 'EGP'])
    app.currency_combo.grid(row=0, column=3, pady=5, padx=5)

    Label(input_frame, text="Category:", bg='#fafad2').grid(row=1, column=0, pady=5, sticky=W)
    app.category_combo = ttk.Combobox(input_frame, values=['Life Expenses', 'Electricity Bill', 'Gas Bill', 'Rental', 'Grocery', 'Savings', 'Education', 'Charity'])
    app.category_combo.grid(row=1, column=1, pady=5, padx=5)

    Label(input_frame, text="Date:", bg='#fafad2').grid(row=1, column=2, pady=5, sticky=W)
    app.date_datepicker = DateEntry(input_frame, date_pattern='mm/dd/yy')
    app.date_datepicker.grid(row=1, column=3, pady=5, padx=5)

    Label(input_frame, text="Payment Method:", bg='#fafad2').grid(row=2, column=0, pady=5, sticky=W)
    app.payment_method_combo = ttk.Combobox(input_frame, values=['Credit Card', 'Debit Card', 'Transfer', 'Paypal', 'Cash'])
    app.payment_method_combo.grid(row=2, column=1, pady=5, padx=5)

    # Buttons frame
    button_frame = Frame(app, bg='#fafad2', padx=20, pady=10)
    button_frame.pack(fill=X)

    Button(button_frame, text="Add Expense", command=add_expense, bg='#4CAF50', fg='white', pady=5).pack(side=LEFT, padx=5)
    Button(button_frame, text="Delete Expense", command=delete_expense, bg='#f44336', fg='white', pady=5).pack(side=LEFT, padx=5)
    Button(button_frame, text="Update Expense", command=update_expense_window, bg='#2196F3', fg='white', pady=5).pack(side=LEFT, padx=5)
    Button(button_frame, text="Delete All", command=delete_all_expenses, bg='#d32f2f', fg='white', pady=5).pack(side=LEFT, padx=5)
    Button(button_frame, text="Convert to USD", command=Calculate_all_theAmount_in_USD, bg='#FF9800', fg='white', pady=5).pack(side=LEFT, padx=5)
    Button(button_frame, text="Export to CSV", command=export_to_csv, bg='#9C27B0', fg='white', pady=5).pack(side=LEFT, padx=5)

    # Total expenses label
    app.total_label = Label(app, text="Total Expenses: 0.00", bg='#fafad2', font=('Arial', 12, 'bold'))
    app.total_label.pack(pady=10)

    # Treeview
    app.expenses_data = ttk.Treeview(app, columns=("Amount", "Currency", "Category", "Date", "Payment_Method"), height=15)
    app.expenses_data.pack(padx=20, pady=10, fill=BOTH, expand=True)

    # Configure treeview
    app.expenses_data.column("#0", width=0, stretch=NO)
    for col in ("Amount", "Currency", "Category", "Date", "Payment_Method"):
        app.expenses_data.column(col, width=150, minwidth=150)
        app.expenses_data.heading(col, text=col.replace("_", " "), anchor=W)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(app, orient=VERTICAL, command=app.expenses_data.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    app.expenses_data.configure(yscrollcommand=scrollbar.set)

    update_treeview()

def main():
    global data_Base
    data_Base = Database("Expenses.db")
    Application_GUI()
    app.mainloop()
    data_Base.close()

if __name__ == "__main__":
    main()