# ######################################                    #
# File: alfred_tts_gui.py                                   #
# Author: Shrayanendra Nath Mandal, Preetish Majumdar       #
# Date: 06/01/2025                                          #
# Description: Gemini AI Alfred with Speech + TTS           #
# ######################################                    #

import os
import threading
import tkinter as tk
from dotenv import load_dotenv
from RealtimeSTT import AudioToTextRecorder
import pyttsx3
from google import genai
from google.genai import types

# Load API key
env_path = os.path.join("Assets", "Gemini.env")
load_dotenv(dotenv_path=env_path)

# Setup TTS Engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 160)  # Adjust voice rate if needed

# Alfred Chatbot
class AlfredChatbot:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.0-flash"
        self.system_instruction = [
            types.Part.from_text(text=
        """
        You are Alfred, a hyper-intelligent AI assistant modeled after Alfred Pennyworth...
        [truncated: use the full original persona block here for brevity]
        """)
        ]
        self.chat_history = []

    def add_user_message(self, message: str):
        self.chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))

    def add_model_message(self, message: str):
        self.chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=message)]))

    def chat(self, user_input: str):
        self.add_user_message(user_input)
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            response_mime_type="text/plain",
            system_instruction=self.system_instruction
        )
        contents = self.chat_history.copy()

        response_text = ""
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config
        ):
            response_text += chunk.text
        self.add_model_message(response_text)
        return response_text

# GUI App
class SpeechApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Alfred - Push to Talk")

        self.label = tk.Label(master, text="Press and hold to talk", font=("Arial", 14))
        self.label.pack(pady=20)

        self.output = tk.Text(master, height=12, width=60, state='disabled', wrap='word')
        self.output.pack(padx=20, pady=10)

        self.button = tk.Button(master, text="🎙 Push to Talk", font=("Arial", 16), width=20)
        self.button.pack(pady=20)

        self.button.bind('<ButtonPress>', self.start_listening)
        self.button.bind('<ButtonRelease>', self.stop_listening)

        self.recorder = AudioToTextRecorder()
        self.listening = False
        self.bot = AlfredChatbot()

    def display_message(self, message, speaker="System"):
        self.output.config(state='normal')
        self.output.insert(tk.END, f"{speaker}: {message}\n")
        self.output.see(tk.END)
        self.output.config(state='disabled')

    def speak(self, text):
        tts_engine.say(text)
        tts_engine.runAndWait()

    def process_text(self, text):
        self.display_message(text, speaker="🗣 You")
        response = self.bot.chat(text)
        self.display_message(response.strip(), speaker="🤖 Alfred")
        threading.Thread(target=self.speak, args=(response.strip(),), daemon=True).start()

    def start_listening(self, event=None):
        if not self.listening:
            self.listening = True
            self.display_message("🟢 Listening...", speaker="System")
            threading.Thread(target=self.recorder.text, args=(self.process_text,), daemon=True).start()

    def stop_listening(self, event=None):
        if self.listening:
            self.recorder.stop()
            self.display_message("🛑 Stopped.", speaker="System")
            self.listening = False

def main():
    root = tk.Tk()
    app = SpeechApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
