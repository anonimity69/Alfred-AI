import tkinter as tk
from tkinter import scrolledtext

def create_button(root, text, command=None, press_callback=None, release_callback=None):
    button = tk.Button(root, text=text)
    if command:
        button.config(command=command)
    if press_callback:
        button.bind("<ButtonPress>", press_callback)
    if release_callback:
        button.bind("<ButtonRelease>", release_callback)
    button.pack(pady=10)
    return button

def create_scrolled_text(root, height=15, width=60):
    box = scrolledtext.ScrolledText(root, height=height, width=width, wrap=tk.WORD)
    box.pack(padx=10, pady=10)
    return box
