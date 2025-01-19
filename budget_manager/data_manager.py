from pathlib import Path
import pandas as pd

class DataManager:
    def __init__(self, limits_manager, csv_file_path="budget_data.csv"):
        self.csv_file_path = Path(csv_file_path)
        self.limits_manager = limits_manager
        self.df = self.load_or_init_data()

    def load_or_init_data(self):
        """
        Try to load the data from the CSV file.
        If the file does not exist or is empty, create a new DataFrame.
        """
        if not self.csv_file_path.exists() or self.csv_file_path.stat().st_size == 0:
            print(f"File '{self.csv_file_path}' not found or is empty. Creating new DataFrame...")
            df = self.create_default_df()
            self.save_df_to_csv(df)
            return df
        else:
            try:
                print(f"Data successfully loaded from '{self.csv_file_path}'")
                df = pd.read_csv(self.csv_file_path)
                return df
            except pd.errors.EmptyDataError:
                print(f"File '{self.csv_file_path}' is empty or corrupted. Creating new DataFrame...")
                df = self.create_default_df()
                self.save_df_to_csv(df)
                return df

    def create_default_df(self):
        """
        Create a new empty default DataFrame with columns only:
        """
        df = pd.DataFrame(columns=["Type", "Category", "Amount", "Date", "Description"])

        return df

    def save_df_to_csv(self, df):
        """
        Save the DataFrame to a CSV file.
        """
        df.to_csv(self.csv_file_path, index=False)

    def add_record(self, record_type, category, amount, date, description=""):
        """
        Adding new row to the DataFrame function.
        Parameters:

        record_type: 'income' or 'expense'
        category: for example: 'Food', 'Transit', 'Entertainment'
        amount: expense amount (float type)
        date: for example: '2025-01-01'
        description: additional information (optional)
        """
        if category not in self.limits_manager.get_all_categories():
            raise ValueError(f"Category '{category}' does not exist! You have to add it first!")
        new_row = {
            "Type": record_type,
            "Category": category,
            "Amount": amount,
            "Date": date,
            "Description": description
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.save_to_csv()

    def save_to_csv(self):
        """
        Save the DataFrame to a CSV file.
        """
        self.df.to_csv(self.csv_file_path, index=False)

    def get_total_expenses(self):
        """
        Return the sum of all expenses.
        """
        expenses = self.df[self.df["Type"] == "expense"]
        return expenses["Amount"].sum()

    def get_total_incomes(self):
        """
        Return the sum of all incomes.
        """
        incomes = self.df[self.df["Type"] == "income"]
        return incomes["Amount"].sum()

    def get_balance(self):
        """
        Return the difference between total income and total expenses.
        """
        return self.get_total_incomes() - self.get_total_expenses()
