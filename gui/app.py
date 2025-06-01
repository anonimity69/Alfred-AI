import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
import os
from datetime import datetime
from components import create_button, create_scrolled_text
from utils import SpeechToText, AlfredChatbot, TextToSpeech
from helpers import (
    async_play_audio,
    get_log_path,
    log_text,
)

class AlfredApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfred AI Assistant")

        # GUI Components
        self.start_button = create_button(
            root,
            text="🎙️ Hold to Talk",
            press_callback=self.on_press,
            release_callback=self.on_release,
        )
        self.start_button.pack(pady=10)

        self.response_box = create_scrolled_text(root, height=15, width=60)
        self.response_box.pack(padx=10, pady=10)

        self.play_button = create_button(
            root,
            text="🔊 Play Last Response",
            command=self.play_last_audio,
        )
        self.play_button.pack(pady=5)

        # AI and Speech modules
        self.stt = SpeechToText()
        self.alfred = AlfredChatbot()
        self.tts = TextToSpeech()

        self.last_audio_path = None
        self.log_path = get_log_path()
        self.audio_data = None

    def on_press(self, event=None):
        self.update_response_box("🎤 Listening... (hold button)")
        self.listening_thread = threading.Thread(target=self._start_listening, daemon=True)
        self.listening_thread.start()

    def _start_listening(self):
        with self.stt.mic as source:
            self.stt.recognizer.adjust_for_ambient_noise(source)
            try:
                self.audio_data = self.stt.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except Exception:
                self.audio_data = None

    def on_release(self, event=None):
        if self.audio_data:
            threading.Thread(target=self._process_pipeline_from_audio, daemon=True).start()
        else:
            self.update_response_box("⚠️ Didn't catch anything.\n")

    def _process_pipeline_from_audio(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.pipeline_with_audio())
        loop.close()

    async def pipeline_with_audio(self):
        try:
            text = ""
            try:
                text = self.stt.recognizer.recognize_google(self.audio_data)
            except Exception:
                text = ""

            if not text:
                self.update_response_box("🤖 Didn't catch that. Try again.\n")
                return

            self.update_response_box(f"👤 You: {text}")
            log_text(self.log_path, f"You: {text}")

            response = self.alfred.chat(text)
            if not response:
                self.update_response_box("🤖 Alfred encountered an issue.")
                return

            self.update_response_box(f"🤖 Alfred: {response}")
            log_text(self.log_path, f"Alfred: {response}")

            audio_file = os.path.join("Outputs", datetime.now().strftime("%H-%M-%S") + ".mp3")
            await self.tts.speak(response, audio_file)
            self.last_audio_path = audio_file

            # Play audio asynchronously
            await async_play_audio(audio_file)

        except Exception as e:
            self.update_response_box(f"⚠️ Error: {e}")
        finally:
            self.update_response_box("🎤 Listening stopped.\n")

    def update_response_box(self, text):
        self.response_box.insert(tk.END, text + "\n")
        self.response_box.see(tk.END)

    def play_last_audio(self):
        if self.last_audio_path and os.path.exists(self.last_audio_path):
            # Run async playback in thread-safe way
            asyncio.run(async_play_audio(self.last_audio_path))
        else:
            messagebox.showinfo("No Audio", "No audio has been generated yet.")
