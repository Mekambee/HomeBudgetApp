import tkinter as tk
from tkinter import messagebox, simpledialog
from budget_manager.data_manager import DataManager
from budget_manager.limits_manager import LimitsManager
from budget_manager.stats_manager import StatsManager
import datetime
import re

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Budget Manager")

        self.limits_manager = LimitsManager()
        self.data_manager = DataManager(self.limits_manager)
        self.stats_manager = StatsManager(self.data_manager, self.limits_manager)

        self.categories = self.limits_manager.get_all_categories()

        self.entry_frame = tk.Frame(root, padx=10, pady=10)
        self.entry_frame.pack(side=tk.TOP, fill=tk.X)

        self.record_type_label = tk.Label(self.entry_frame, text="Record Type:")
        self.record_type_label.grid(row=0, column=0, padx=5, pady=(0, 5))

        self.category_label = tk.Label(self.entry_frame, text="Category:")
        self.category_label.grid(row=0, column=1, padx=5, pady=(0, 5))

        self.amount_label = tk.Label(self.entry_frame, text="Amount (PLN):")
        self.amount_label.grid(row=0, column=2, padx=5, pady=(0, 5))

        self.record_type_var = tk.StringVar(value="expense")
        self.record_type_dropdown = tk.OptionMenu(self.entry_frame, self.record_type_var, "expense", "income")
        self.record_type_dropdown.grid(row=1, column=0, padx=5)

        self.category_var = tk.StringVar(value=self.categories[0] if self.categories else "")
        self.category_dropdown = tk.OptionMenu(self.entry_frame, self.category_var, *self.categories)
        self.category_dropdown.grid(row=1, column=1, padx=5)

        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(self.entry_frame, textvariable=self.amount_var, width=10)
        self.amount_entry.grid(row=1, column=2, padx=5)

        self.add_button = tk.Button(self.entry_frame, text="Add Entry", command=self.add_record)
        self.add_button.grid(row=1, column=3, padx=5)

        self.add_category_button = tk.Button(self.entry_frame, text="Add Category", command=self.add_category)
        self.add_category_button.grid(row=1, column=4, padx=5)

        self.summary_label = tk.Label(root, text="", font=("Arial", 15), padx=10, pady=10)
        self.summary_label.pack()
        self.update_summary()

        self.chart_frame = tk.Frame(root)
        self.chart_frame.pack()

        self.pie_chart_button = tk.Button(root, text="Show expenses categories pie chart", command=self.show_pie_chart)
        self.pie_chart_button.pack()

        self.bar_chart_button = tk.Button(root, text="Show expenses and limits bar chart", command=self.show_bar_chart)
        self.bar_chart_button.pack()

        self.line_chart_button = tk.Button(root, text="Show balance evolution chart",
                                           command=self.show_balance_evolution_chart)
        self.line_chart_button.pack()

        self.show_records_button = tk.Button(root, text="Show all records", command=self.show_all_records)
        self.show_records_button.pack()

        self.show_categories_button = tk.Button(root, text="Show categories and their limits", command=self.show_all_categories)
        self.show_categories_button.pack()

        self.chart_label = tk.Label(root)
        self.chart_label.pack()

        self.update_summary()

    def add_record(self):
        """Adds a new record to the data manager and updates the summary."""
        record_type = self.record_type_var.get()
        category = self.category_var.get()

        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Balance you entered is probably not a number.")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be a positive number!")
            return

        if record_type == "expense":
            current_balance = self.data_manager.get_balance()
            if amount > current_balance:
                messagebox.showerror("Insufficient funds",
                                     f"You only have {current_balance:.2f} zł. Expense of {amount:.2f} zł cannot be done!")
                return

        date = datetime.date.today().strftime("%Y-%m-%d")

        desc = simpledialog.askstring(
            "Description (optional)",
            "Add a description for this record (leave blank if none):"
        )
        if desc is None:
            return
        if not desc:
            desc = "No description"

        try:
            self.data_manager.add_record(record_type, category, amount, date, description=desc)
            self.update_summary()
            if record_type == "expense":
                self.check_limit_info(category)
                self.refresh_charts()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.amount_var.set("")

    def add_category(self):
        """Adds a new category to the limits manager and updates the category dropdown."""
        new_category = simpledialog.askstring("Add new category", "Enter new category name:")
        if new_category:
            if not re.match(r'^[A-Za-z]+$', new_category):
                messagebox.showerror("Error", "Category name must contain only letters (A-Za-z)!")
                return

            new_limit = simpledialog.askfloat("Add new category", f"Enter limit for '{new_category}' category \n(No value means limit = 0.0)")
            if new_limit is None:
                new_limit = 0.0
            try:
                self.limits_manager.add_category(new_category, new_limit)
                self.categories = self.limits_manager.get_all_categories()
                self.update_category_dropdown()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        else:
            return

    def update_category_dropdown(self):
        """Updates the category dropdown with the current list of categories"""
        menu = self.category_dropdown["menu"]
        menu.delete(0, "end")
        for cat in self.categories:
            menu.add_command(label=cat, command=lambda value=cat: self.category_var.set(value))

    def update_summary(self):
        """Updates the summary label with the current total income, expenses, and balance."""
        total_income = self.data_manager.get_total_incomes()
        total_expenses = self.data_manager.get_total_expenses()
        balance = self.data_manager.get_balance()
        self.summary_label.config(
            text=f"Total Income: {total_income:.2f} zł | Total Expenses: {total_expenses:.2f} zł | Your Balance: {balance:.2f} zł"
        )

    def show_pie_chart(self):
        """Generates a pie chart showing expenses by category."""
        chart_img = self.stats_manager.generate_expenses_pie_chart()
        if chart_img:
            self.chart_label.config(image=chart_img)
            self.chart_label.image = chart_img
        else:
            messagebox.showinfo("Warning", "There is no data you could show on the chart.")
    def show_bar_chart(self):
        """Generates a bar chart comparing expenses to limits."""
        chart_img = self.stats_manager.compare_expenses_to_limits()
        if chart_img:
            self.chart_label.config(image=chart_img)
            self.chart_label.image = chart_img
        else:
            messagebox.showinfo("Warning", "There is no data you could compare on the chart.")

    def refresh_charts(self):
        """Refreshes both charts."""

        self.chart_label.config(image="")
        self.chart_label.image = None

        self.show_bar_chart()
        self.show_balance_evolution_chart()
        self.show_pie_chart()

    def check_limit_info(self, category):
        """Shows how much is left or how much over the limit in the given category."""
        expenses = self.data_manager.df
        expenses_by_cat = expenses[expenses["Type"] == "expense"].groupby("Category")["Amount"].sum()
        current_expenses = expenses_by_cat.get(category, 0)

        limit = self.limits_manager.get_limit(category)
        if limit is None:
            return

        if limit <= 0:
            return

        if current_expenses > limit:
            over = current_expenses - limit
            messagebox.showwarning(
                "Limit exceeded",
                f"Expense successfully added! You have exceeded the limit for '{category}' by {over:.2f} zł!"
            )
        else:
            left = limit - current_expenses
            messagebox.showinfo(
                "Limit status",
                f"Expense successfully added! You have {left:.2f} zł left to reach the limit for '{category}'."
            )

    def show_balance_evolution_chart(self):
        """Generates a line chart showing balance evolution by transaction index."""
        chart_img = self.stats_manager.generate_balance_evolution_chart()
        if chart_img:
            self.chart_label.config(image=chart_img)
            self.chart_label.image = chart_img
        else:
            messagebox.showinfo("Warning", "No data to display balance evolution.")

    def show_all_records(self):
        """
        Calls the StatsManager method to display all records in a new Toplevel window.
        """
        self.stats_manager.show_all_records()

    def show_all_categories(self):
        """
        Calls the StatsManager method to display all categories & limits in a new Toplevel window.
        """
        self.stats_manager.show_all_categories()



