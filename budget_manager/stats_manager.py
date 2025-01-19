from io import BytesIO
from PIL import Image, ImageTk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
matplotlib.use('Agg')

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
        fig, ax = plt.subplots(figsize=(9, 6))
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

        fig, ax = plt.subplots(figsize=(9, 6))

        bars_spent = ax.bar(category_names, spent_values, label="Over limit", color="red", alpha=0.9, width=0.7)
        ax.bar(category_names, limit_values, label="Limit", color="orange", alpha=0.6, width=0.7)

        ax.set_ylabel("Price in PLN")
        ax.set_title("Expenses vs Limits Comparison")

        ax.set_facecolor("#f0f0f0")

        legend_patches = [
            mpatches.Patch(color="red", label="Over limit"),
            mpatches.Patch(color="#fa6f05", label="Spent"),
            mpatches.Patch(color="#f2d268", label="Limit"),
        ]
        ax.legend(handles=legend_patches, loc="upper left", bbox_to_anchor=(0.80, 1.15), borderaxespad=0.)

        for bar, spent, limit in zip(bars_spent, spent_values, limit_values):
            color = "black" if spent <= limit else "red"
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                    f"{spent:.2f}zł / {limit:.2f}zł", ha='center', va='bottom',
                    fontsize=10, fontweight='bold', color=color)

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        img = Image.open(buf)
        tk_image = ImageTk.PhotoImage(img)
        return tk_image
