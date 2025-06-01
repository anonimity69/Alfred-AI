import tkinter as tk
from tkinter import scrolledtext

def create_push_to_talk_button(root, on_press, on_release):
    button = tk.Button(root, text="🎙️ Hold to Talk")
    button.bind("<ButtonPress>", on_press)
    button.bind("<ButtonRelease>", on_release)
    button.pack(pady=10)
    return button

def create_response_box(root):
    box = scrolledtext.ScrolledText(root, height=15, width=60, wrap=tk.WORD)
    box.pack(padx=10, pady=10)
    return box

def create_play_button(root, command):
    button = tk.Button(root, text="🔊 Play Last Response", command=command)
    button.pack(pady=5)
    return button
