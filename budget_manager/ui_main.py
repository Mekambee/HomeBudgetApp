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
        self.limits_manager = LimitsManager()
        self.data_manager = DataManager(self.limits_manager)
        self.stats_manager = StatsManager(self.data_manager, self.limits_manager)

        self.categories = self.limits_manager.get_all_categories()

        self.entry_frame = tk.Frame(root, padx=10, pady=10)
        self.entry_frame.pack(side=tk.TOP, fill=tk.X)

        self.record_type_var = tk.StringVar(value="expense")
        self.record_type_dropdown = tk.OptionMenu(self.entry_frame, self.record_type_var, "expense", "income")
        self.record_type_dropdown.grid(row=0, column=0)

        self.category_var = tk.StringVar(value=self.categories[0] if self.categories else "")
        self.category_dropdown = tk.OptionMenu(self.entry_frame, self.category_var, *self.categories)
        self.category_dropdown.grid(row=0, column=1)

        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(self.entry_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=0, column=2)

        self.add_button = tk.Button(self.entry_frame, text="Add new expense", command=self.add_record)
        self.add_button.grid(row=0, column=3, padx=5)

        self.add_category_button = tk.Button(self.entry_frame, text="Add category", command=self.add_category)
        self.add_category_button.grid(row=0, column=4, padx=5)

        self.summary_label = tk.Label(root, text="", font=("Arial", 12), padx=10, pady=10)
        self.summary_label.pack()
        self.update_summary()

        self.chart_frame = tk.Frame(root)
        self.chart_frame.pack()

        self.pie_chart_button = tk.Button(root, text="Show expenses pie chart", command=self.show_pie_chart)
        self.pie_chart_button.pack()

        self.bar_chart_button = tk.Button(root, text="Expenses and limits comparision", command=self.show_bar_chart)
        self.bar_chart_button.pack()

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

        date = datetime.date.today().strftime("%Y-%m-%d")

        try:
            self.data_manager.add_record(record_type, category, amount, date)
            self.update_summary()
            if record_type == "expense":
                self.refresh_charts()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def add_category(self):
        """Adds a new category to the limits manager and updates the category dropdown."""
        new_category = simpledialog.askstring("Add new category", "Enter new category name:")
        if new_category:
            if not re.match(r'^[A-Za-z]+$', new_category):
                messagebox.showerror("Error", "Category name must contain only letters (A-Za-z)!")
                return
            try:
                self.limits_manager.add_category(new_category)
                self.categories = self.limits_manager.get_all_categories()
                self.update_category_dropdown()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

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
            text=f"Income: {total_income:.2f} zł | Expenses: {total_expenses:.2f} zł | Balance: {balance:.2f} zł"
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
        self.show_pie_chart()
