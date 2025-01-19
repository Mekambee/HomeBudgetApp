import tkinter as tk
from budget_manager.ui_main import App

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()