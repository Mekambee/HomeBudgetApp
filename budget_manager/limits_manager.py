import csv
from pathlib import Path

class LimitsManager:
    def __init__(self, limits_file="categories.csv"):
        self.limits_file = Path(limits_file)
        self.categories = self.load_limits()

        if not self.categories:
            self.create_default_categories()

    def load_limits(self):
        """
        Load categories and limits from a CSV file or creates a default list.
        """
        categories = {}
        if self.limits_file.exists() and self.limits_file.stat().st_size > 0:
            with open(self.limits_file, mode="r", newline="", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)
                for row in csv_reader:
                    if len(row) == 2:
                        category, limit = row
                        categories[category] = float(limit) if limit else 0.0
        return categories

    def save_limits(self):
        """
        Save categories and limits to a CSV file.
        """
        with open(self.limits_file, mode="w", newline="", encoding="utf-8") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(["Category", "Limit"])
            for category, limit in self.categories.items():
                csv_writer.writerow([category, limit])

    def set_limit(self, category, amount):
        """
        Sets or changes limit for a category from parameter.
        """
        self.categories[category] = float(amount)
        self.save_limits()

    def get_limit(self, category):
        """
        Returns limit for a category from parameter.
        """
        return self.categories.get(category, None)

    def is_category_limit_reached(self, category, current_expense_sum):
        """
        Returns True if the sum of expenses for a category exceeds the limit.
        """
        limit = self.get_limit(category)
        if limit is None:
            return True
        return current_expense_sum > limit

    def add_category(self, category, limit=None):
        """
        Adds a new category with an optional limit, if not already exists.
        """
        if category in self.categories:
            raise ValueError(f"Category '{category}' already exists!")
        self.categories[category] = float(limit) if limit is not None else 0.0
        self.save_limits()

    def remove_category(self, category):
        """
        Removes a category from the list.
        """
        if category in self.categories:
            del self.categories[category]
            self.save_limits()
        else:
            raise ValueError(f"Category '{category}' does not exist!")

    def get_all_categories(self):
        """
        Returns a list of all categories.
        """
        return list(self.categories.keys())

    def create_default_categories(self):
        """
        Creates a default list of categories with limits.
        """
        self.categories = {
            "Food": 500.0,
            "Transport": 300.0,
            "Entertainment": 200.0,
            "Other": 200.0
        }
        self.save_limits()
