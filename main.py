import tkinter as tk
from gui.app import SimpleAlfredApp

def main():
    root = tk.Tk()
    app = SimpleAlfredApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
