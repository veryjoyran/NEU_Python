# main.py
import tkinter as tk
from WebScraperGUI import WebScraperGUI

def main():
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
