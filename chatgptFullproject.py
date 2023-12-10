from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests

class ExpenseTrackerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Expense Tracker")

        # Database setup (replace with your database logic)
        self.expenses = []

        # GUI components
        self.amount_label = Label(self.master, text="Amount:")
        self.amount_entry = Entry(self.master)

        self.category_label = Label(self.master, text="Category:")
        self.category_combobox = ttk.Combobox(self.master, values=['Life Expenses', 'Electricity', 'Gas', 'Rental', 'Grocery', 'Savings', 'Education', 'Charity'])

        self.date_label = Label(self.master, text="Date:")
        self.date_entry = DateEntry(self.master, width=12)

        self.payment_label = Label(self.master, text="Payment Method:")
        self.payment_combobox = ttk.Combobox(self.master, values=['Cash', 'Credit Card', 'Paypal'])

        self.add_button = Button(self.master, text="Add Expense", command=self.add_expense)

        self.total_label = Label(self.master, text="Total Expenses in USD:")
        self.total_value_label = Label(self.master, text="0")

        # Grid layout
        self.amount_label.grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        self.category_label.grid(row=1, column=0, padx=5, pady=5)
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.date_label.grid(row=2, column=0, padx=5, pady=5)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        self.payment_label.grid(row=3, column=0, padx=5, pady=5)
        self.payment_combobox.grid(row=3, column=1, padx=5, pady=5)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)
        self.total_label.grid(row=5, column=0, padx=5, pady=5)
        self.total_value_label.grid(row=5, column=1, padx=5, pady=5)

        # Update total value
        self.update_total_value()

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_combobox.get()
            date = self.date_entry.get()
            payment_method = self.payment_combobox.get()

            # Convert to USD using an API (replace with your own API logic)
            usd_amount = self.convert_to_usd(amount, 'YOUR_BASE_CURRENCY')

            self.expenses.append({'amount': amount, 'usd_amount': usd_amount, 'category': category, 'date': date, 'payment_method': payment_method})
            self.update_total_value()

            # You can add database logic to store the expense data here

            messagebox.showinfo("Success", "Expense added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

    def convert_to_usd(self, amount, base_currency):
        # You can replace this with your own API logic for currency conversion
        api_key = 'd6orT12AcBBuc0a8nkTNrLgVIIGYxuaQ'
        url = f'https://api.apilayer.com/fixer/convert?to=USD&from={base_currency}&amount={amount}'
        headers = {"apikey": api_key}
        response = requests.get(url, headers=headers)
        result = response.json()
        return result.get('result', 0)

    def update_total_value(self):
        total_usd = sum(expense['usd_amount'] for expense in self.expenses)
        self.total_value_label.config(text=f"{total_usd:.2f} USD")

def main():
    root = Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
