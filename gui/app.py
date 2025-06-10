import os
import sys
import time
import uuid
import tkinter as tk
from tkinter import messagebox
from threading import Thread
sys.path.append('../')
from utils.alfredai_engine import AlfredChatbot
from utils.speechtotext import SpeechToText
from utils.texttospeech import TextToSpeech

# Create audio output directory if it doesn't exist
AUDIO_OUTPUT_DIR = "AudioOutput"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Initialize Alfred components
bot = AlfredChatbot()
stt = SpeechToText()
tts = TextToSpeech(voice="en-GB-RyanNeural")

# GUI application
def start_conversation():
    def run():
        try:
            stt.start()
            update_status("Listening... Please speak clearly.")
            time.sleep(5)
            stt.stop()

            user_input = stt.get_last_text()
            if not user_input:
                update_status("Alfred: I beg your pardon, sir. I didn't quite catch that.")
                return

            update_status(f"You said: {user_input}")
            alfred_response = bot.chat(user_input)

            audio_file = os.path.join(AUDIO_OUTPUT_DIR, f"alfred_reply_{uuid.uuid4()}.mp3")
            tts.generate(alfred_response, audio_file)
            update_status("Alfred has responded. Audio has been generated.")
        except Exception as e:
            update_status(f"Error: {str(e)}")
        finally:
            stt.stop()

    Thread(target=run).start()

def update_status(message):
    status_label.config(text=message)

def on_exit():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

# Set up the main window
root = tk.Tk()
root.title("Alfred AI Assistant")

tk.Label(root, text="Press the button and speak to Alfred").pack(pady=10)
tk.Button(root, text="Talk to Alfred", command=start_conversation).pack(pady=5)
status_label = tk.Label(root, text="", wraplength=400, justify="left")
status_label.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()