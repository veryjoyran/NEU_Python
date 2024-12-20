from WebScraper_HouseData import WebScraper_HouseData as WSD
from WebScraperGUI import WebScraperGUI as WSGUI
import tkinter as tk
from tkinter import messagebox, ttk

def main():
    root = tk.Tk()
    app = WSGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()