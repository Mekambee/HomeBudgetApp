import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageTk

class StatsManager:
    def __init__(self, data_manager, limits_manager):
        self.data_manager = data_manager
        self.limits_manager = limits_manager

    def generate_expenses_pie_chart(self):
        """Generates a pie chart showing expenses for each category."""
        expenses = self.data_manager.df[self.data_manager.df["Type"] == "expense"]

        if expenses.empty:
            return None

        expenses_by_category = expenses.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots()
        ax.pie(expenses_by_category, labels=expenses_by_category.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        ax.set_title("Expenses by Categories")

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        img = Image.open(buf)
        return ImageTk.PhotoImage(img)

    def compare_expenses_to_limits(self):
        """Generates a bar chart comparing expenses to limits for each category."""
        expenses = self.data_manager.df[self.data_manager.df["Type"] == "expense"]
        if expenses.empty:
            return None

        expenses_by_category = expenses.groupby("Category")["Amount"].sum()
        categories = self.limits_manager.get_all_categories()
        limits = {cat: self.limits_manager.get_limit(cat) for cat in categories}

        category_names = list(expenses_by_category.index)
        spent_values = [expenses_by_category[cat] for cat in category_names]
        limit_values = [limits.get(cat, 0) for cat in category_names]

        fig, ax = plt.subplots()
        ax.bar(category_names, spent_values, label="Spent", alpha=0.7)
        ax.bar(category_names, limit_values, label="Limit", alpha=0.7)
        ax.set_ylabel("price in PLN")
        ax.set_title("Expenses vs Limits comparision")
        ax.legend()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        img = Image.open(buf)
        tk_image = ImageTk.PhotoImage(img)
        return tk_image
