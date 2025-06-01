import tkinter as tk
from tkinter import messagebox, scrolledtext
import asyncio
import tempfile
import os
from datetime import datetime
from utils import SpeechToText, AlfredChatbot, TextToSpeech
from playsound import playsound
import threading
from pydub import AudioSegment
from pydub.playback import play

# Ensure directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs("Outputs", exist_ok=True)

class AlfredApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfred AI Assistant")

        # Components
        self.start_button = tk.Button(root, text="🎙️ Hold to Talk")
        self.start_button.bind("<ButtonPress>", self.on_press)
        self.start_button.bind("<ButtonRelease>", self.on_release)
        self.start_button.pack(pady=10)

        self.response_box = scrolledtext.ScrolledText(root, height=15, width=60, wrap=tk.WORD)
        self.response_box.pack(padx=10, pady=10)

        self.play_button = tk.Button(root, text="🔊 Play Last Response", command=self.play_last_audio)
        self.play_button.pack(pady=5)

        # AI + Voice Modules
        self.stt = SpeechToText()
        self.alfred = AlfredChatbot()
        self.tts = TextToSpeech()
        self.last_audio_path = None
        self.log_path = os.path.join("logs", datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt")

    def start_listening(self):
        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.run_pipeline, daemon=True).start()

    def run_pipeline(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.pipeline())
        loop.close()

    async def pipeline(self):
        try:
            self.update_response_box("🎙️ Listening...")
            text = await self.capture_speech()

            if not text:
                self.update_response_box("🤖 Didn't catch that. Try again.")
                return

            self.update_response_box(f"👤 You: {text}")
            self.log(f"You: {text}")

            response = self.alfred.chat(text)

            if not response:
                self.update_response_box("🤖 Alfred encountered an issue.")
                return

            self.update_response_box(f"🤖 Alfred: {response}")
            self.log(f"Alfred: {response}")

            audio_file = os.path.join("Outputs", datetime.now().strftime("%H-%M-%S") + ".mp3")
            await self.tts.speak(response, audio_file)
            self.last_audio_path = audio_file
            audio = AudioSegment.from_file(audio_file, format="mp3")
            play(audio)

        except Exception as e:
            self.update_response_box(f"⚠️ Error: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL)

    async def capture_speech(self):
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self._blocking_stt)
        return await future

    def _blocking_stt(self):
        with self.stt.mic as source:
            self.stt.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.stt.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                return self.stt.recognizer.recognize_google(audio)
            except Exception:
                return ""

    def update_response_box(self, text):
        self.response_box.insert(tk.END, text + "\n")
        self.response_box.see(tk.END)

    def play_last_audio(self):
        if self.last_audio_path and os.path.exists(self.last_audio_path):
            threading.Thread(target=self._play_audio_file, daemon=True).start()
        else:
            messagebox.showinfo("No Audio", "No audio has been generated yet.")

    def _play_audio_file(self):
        try:
            audio = AudioSegment.from_file(self.last_audio_path, format="mp3")
            play(audio)
        except Exception as e:
            self.update_response_box(f"⚠️ Audio Playback Error: {e}")

    def log(self, text):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def on_press(self, event=None):
        self.update_response_box("🎤 Listening... (hold button)")
        self._listening_thread = threading.Thread(target=self._start_listening, daemon=True)
        self._listening_thread.start()

    def _start_listening(self):
        with self.stt.mic as source:
            self.stt.recognizer.adjust_for_ambient_noise(source)
            try:
                self.audio_data = self.stt.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except Exception:
                self.audio_data = None

    def on_release(self, event=None):
        if hasattr(self, 'audio_data') and self.audio_data:
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
            self.log(f"You: {text}")

            response = self.alfred.chat(text)

            if not response:
                self.update_response_box("🤖 Alfred encountered an issue.")
                return

            self.update_response_box(f"🤖 Alfred: {response}")
            self.log(f"Alfred: {response}")

            audio_file = os.path.join("Outputs", datetime.now().strftime("%H-%M-%S") + ".mp3")
            await self.tts.speak(response, audio_file)
            self.last_audio_path = audio_file

            audio = AudioSegment.from_file(audio_file, format="mp3")
            play(audio)

        except Exception as e:
            self.update_response_box(f"⚠️ Error: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.update_response_box("🎤 Listening stopped.\n") 

if __name__ == "__main__":
    root = tk.Tk()
    app = AlfredApp(root)
    root.mainloop()
