"""
#############################################################
# File        : main_tkinter.py                             #
# Authors     : Shrayanendra Nath Mandal, Preetish Majumdar #
# Date        : 2025-06-06                                  #
# Description : Alfred AI Assistant - Tkinter GUI version   #
#############################################################
"""

import os
import sys
import uuid
import time
import threading
import platform
import subprocess
from tkinter import Tk, Button, Text, Scrollbar, END, DISABLED, NORMAL, Frame, Label
sys.path.append('../')
from utils.alfredai_engine import AlfredChatbot
from utils.speechtotext import SpeechToText
from utils.texttospeech import TextToSpeech


AUDIO_OUTPUT_DIR = "AudioOutput"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

class AlfredGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfred AI Assistant")
        self.root.geometry("600x500")

        self.bot = AlfredChatbot()
        self.stt = SpeechToText()
        self.tts = TextToSpeech(voice="en-GB-RyanNeural")

        self.latest_audio_file = None

        # Speak Button
        self.speak_button = Button(root, text="Speak (or press Enter)", command=self.on_speak)
        self.speak_button.pack(pady=10)

        # Chat display frame with scrollbar
        self.chat_frame = Frame(root)
        self.chat_frame.pack(expand=True, fill='both', padx=10)

        self.scrollbar = Scrollbar(self.chat_frame)
        self.scrollbar.pack(side='right', fill='y')

        self.chat_display = Text(self.chat_frame, wrap='word', state=DISABLED, yscrollcommand=self.scrollbar.set)
        self.chat_display.pack(expand=True, fill='both')
        self.scrollbar.config(command=self.chat_display.yview)

        # Audio controls frame
        self.audio_frame = Frame(root)
        self.audio_frame.pack(pady=10)

        self.play_button = Button(self.audio_frame, text="Play Last Reply Audio", command=self.play_audio, state=DISABLED)
        self.play_button.pack(side='left', padx=5)

        self.audio_label = Label(self.audio_frame, text="Audio: None")
        self.audio_label.pack(side='left')

        # Bind Enter key to speak button
        root.bind('<Return>', lambda event: self.on_speak())

    def append_chat(self, speaker, text):
        self.chat_display.config(state=NORMAL)
        self.chat_display.insert(END, f"{speaker}: {text}\n\n")
        self.chat_display.config(state=DISABLED)
        self.chat_display.see(END)  # Scroll to end

    def on_speak(self):
        # Run in a thread to avoid freezing the GUI
        thread = threading.Thread(target=self.listen_and_respond)
        thread.start()

    def listen_and_respond(self):
        self.speak_button.config(state=DISABLED)
        self.append_chat("System", "Listening... Please speak clearly.")

        try:
            self.stt.start()
            time.sleep(5)  # Listen duration
            self.stt.stop()

            user_input = self.stt.get_last_text()
            if not user_input:
                self.append_chat("Alfred", "I beg your pardon, sir. I didn't quite catch that.")
                self.speak_button.config(state=NORMAL)
                return

            self.append_chat("You", user_input)

            alfred_response = self.bot.chat(user_input)
            self.append_chat("Alfred", alfred_response)

            audio_file = os.path.join(AUDIO_OUTPUT_DIR, f"alfred_reply_{uuid.uuid4()}.mp3")
            self.tts.generate(alfred_response, audio_file)

            self.latest_audio_file = audio_file
            self.audio_label.config(text=f"Audio: {os.path.basename(audio_file)}")
            self.play_button.config(state=NORMAL)

        except Exception as e:
            self.append_chat("System", f"Error: {str(e)}")

        self.speak_button.config(state=NORMAL)

    def play_audio(self):
        if self.latest_audio_file and os.path.exists(self.latest_audio_file):
            # Cross-platform audio play
            if platform.system() == "Windows":
                # Windows
                os.startfile(self.latest_audio_file)
            elif platform.system() == "Darwin":
                # macOS
                subprocess.call(["afplay", self.latest_audio_file])
            else:
                # Linux and others (requires mpg123 or aplay)
                try:
                    subprocess.call(["mpg123", self.latest_audio_file])
                except FileNotFoundError:
                    self.append_chat("System", "mpg123 not found. Install it or play audio manually.")
        else:
            self.append_chat("System", "No audio file found to play.")


def main():
    root = Tk()
    app = AlfredGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
