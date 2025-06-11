import time
import threading
import tkinter as tk
from tkinter import messagebox
from utils.alfredai_engine import AlfredChatbot
from utils.speechtotext import SpeechToText
from utils.texttospeech import TextToSpeech

class AlfredGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfred AI Assistant")
        self.root.geometry("400x250")
        self.root.configure(bg="#1e1e1e")

        self.bot = AlfredChatbot()
        self.stt = SpeechToText()
        self.tts = TextToSpeech(voice="en-GB-RyanNeural")

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Alfred AI", font=("Segoe UI", 18), fg="white", bg="#1e1e1e")
        self.label.pack(pady=20)

        self.listen_button = tk.Button(
            self.root,
            text="🎙️ Listen",
            command=self.run_assistant,
            bg="#2d2d2d",
            fg="white",
            font=("Segoe UI", 14),
            relief="flat",
            padx=20,
            pady=10
        )
        self.listen_button.pack(pady=10)

        self.response_label = tk.Label(self.root, text="", fg="white", bg="#1e1e1e", wraplength=350, justify="center")
        self.response_label.pack(pady=20)

    def run_assistant(self):
        threading.Thread(target=self.assistant_logic).start()

    def assistant_logic(self):
        self.response_label.config(text="Listening... Speak now.")
        self.stt.start()
        time.sleep(5)
        self.stt.stop()

        user_input = self.stt.get_last_text()
        self.stt.last_text = None

        if not user_input:
            self.response_label.config(text="I beg your pardon, sir. I didn't quite catch that.")
            return

        if user_input.lower() in ["exit", "quit"]:
            self.response_label.config(text="Very well, sir. Until next time.")
            self.root.after(2000, self.root.quit)
            return

        self.response_label.config(text=f"You said: {user_input}")

        response = self.bot.chat(user_input)

        self.response_label.config(text=f"Alfred: {response}")

        self.tts.speak(response)

def main():
    root = tk.Tk()
    app = AlfredGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
