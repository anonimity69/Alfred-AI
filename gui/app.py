import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import speech_recognition as sr
from utils import AlfredChatbot  # your chatbot logic

class SimpleAlfredApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfred AI Assistant")

        # Chatbot engine
        self.alfred = AlfredChatbot()

        # Buttons frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.listen_button = tk.Button(button_frame, text="Start Listening", command=self.start_listening)
        self.listen_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Listening", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Text box to display conversation
        self.response_box = scrolledtext.ScrolledText(root, height=20, width=70)
        self.response_box.pack(padx=10, pady=10)

        # Speech recognizer
        self.recognizer = sr.Recognizer()

        # Control flags and variables
        self.is_listening = False
        self.stop_listening_flag = False
        self.audio_chunks = []

    def start_listening(self):
        if self.is_listening:
            messagebox.showinfo("Info", "Already listening...")
            return
        self.is_listening = True
        self.stop_listening_flag = False
        self.audio_chunks = []
        self.update_text("Start speaking after a few seconds\n")
        self.listen_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.listen_and_process, daemon=True).start()

    def stop_listening(self):
        if not self.is_listening:
            return
        self.stop_listening_flag = True
        self.update_text("Stopping listening early...\n")
        self.stop_button.config(state=tk.DISABLED)

    def listen_and_process(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            silence_limit = 10  # seconds of silence to stop recording
            silence_timer = 0

            while silence_timer < silence_limit:
                if self.stop_listening_flag:
                    break
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_chunks.append(audio)
                    silence_timer = 0  # reset silence timer on audio
                except sr.WaitTimeoutError:
                    silence_timer += 1  # increment silence timer for each second of silence

        if not self.audio_chunks:
            self.update_text("No speech detected.\n")
            self.finish_listening()
            return

        full_text = ""
        for chunk in self.audio_chunks:
            try:
                text = self.recognizer.recognize_google(chunk)
                full_text += text + " "
            except Exception:
                pass  # ignore chunks that fail to recognize

        full_text = full_text.strip()
        if not full_text:
            self.update_text("Could not understand any audio.\n")
            self.finish_listening()
            return

        self.update_text(f"You said: {full_text}\n")

        # Get chatbot response
        response = self.alfred.chat(full_text)
        self.update_text(f"Alfred: {response}\n")

        self.finish_listening()

    def finish_listening(self):
        self.is_listening = False
        self.stop_listening_flag = False
        self.listen_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_text(self, message):
        self.response_box.insert(tk.END, message)
        self.response_box.see(tk.END)