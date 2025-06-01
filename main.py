import tkinter as tk
from gui.app import AlfredApp

def main():
    root = tk.Tk()
    app = AlfredApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
