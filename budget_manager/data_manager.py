from budget_manager.limits_manager import LimitsManager
import pandas as pd
from pathlib import Path

class DataManager:
    def __init__(self, csv_file_path="budget_data.csv"):
        self.csv_file_path = Path(csv_file_path)
        self.limits_manager = LimitsManager()

        if self.csv_file_path.exists():
            self.df = pd.read_csv(self.csv_file_path)
            print(f"Data successfully loaded from '{csv_file_path}'")
        else:
            print(f"File {csv_file_path} not found, creating new DataFrame ...")
            self.df = pd.DataFrame(columns=["Type", "Category", "Amount", "Date", "Description"])

    def add_record(self, record_type, category, amount, date, description=""):
        """
        Adding new row to the DataFrame function.
        Parameters:

        record_type: 'income' lub 'expense'
        category: for example: 'Food', 'Transit', 'Entartainment'
        amount: expense amount (float type)
        date: for example: '2025-01-01'
        description: additional information (optional)
        """

        if category not in self.limits_manager.get_all_categories():
            raise ValueError(f"Kategoria {category} nie istnieje! Najpierw należy ją dodać")
        new_row = {
            "Type": record_type,
            "Category": category,
            "Amount": amount,
            "Date": date,
            "Description": description
        }
        self.df = self.df.append(new_row, ignore_index=True)
        self.save_to_csv()

    def save_to_csv(self):
        """Save the DataFrame to a CSV file."""
        self.df.to_csv(self.csv_file_path, index=False)

    def get_total_expenses(self):
        """Return the sum of all expenses."""
        expenses = self.df[self.df["type"] == "expense"]
        return expenses["amount"].sum()

    def get_total_incomes(self):
        """Return the sum of all incomes."""
        incomes = self.df[self.df["type"] == "income"]
        return incomes["amount"].sum()

    def get_balance(self):
        """Return the difference between total income and total expenses."""
        return self.get_total_incomes() - self.get_total_expenses()

