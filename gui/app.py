# Standard library imports
import tkinter as tk  # For building the GUI
from tkinter import messagebox  # To display alert dialogs
import asyncio  # To run asynchronous tasks
import threading  # For running blocking operations without freezing the UI
import os  # File and path management
from datetime import datetime  # Timestamping logs and audio filenames
import tempfile  # For creating temp directories and files
# Local GUI modules
from gui.components import create_button, create_scrolled_text  # Reusable UI components
from gui.helpers import (
    async_play_audio,  # Async wrapper for playing audio
    get_log_path,      # Generates a log file path with timestamp
    log_text           # Appends conversation text to a log file
)
# Core AI + Audio modules
from utils import SpeechToText, AlfredChatbot, TextToSpeech

class AlfredApp:
    # Main application class for the Alfred AI Assistant.
    def __init__(self, root):
        ''' Initialize the main application window and components.
        Args:
            root (tk.Tk): The main application window.
        '''
        # === Core Modules ===
        self.stt = SpeechToText()       # Converts speech → text
        self.alfred = AlfredChatbot()   # Handles chatbot logic
        self.tts = TextToSpeech()       # Converts text → speech
        self.root = root
        self.root.title("Alfred AI Assistant")

        # === GUI Components ===
        # Button: Press to start talking, release to process
        self.start_button = create_button(
            root,
            text="Hold to Talk",
            press_callback=self.on_press,
            release_callback=self.on_release,
        )

        # Scrolled text box: To display the chat between user and Alfred
        self.response_box = create_scrolled_text(root, height=15, width=60)

        # Button: To replay the last audio response
        self.play_button = create_button(
            root,
            text="Play Last Response",
            command=self.play_last_audio,
        )

        # Other instance variables
        self.last_audio_path = None     # Stores last generated audio file path
        self.log_path = get_log_path()  # Generates new log file path
        self.audio_data = None          # Placeholder for recorded audio

    # Called when the user presses the talk button
    def on_press(self, event=None):
        self.audio_data = None  # Reset any previous audio
        self.update_response_box("Listening... (hold button)")
        self.listening_thread = threading.Thread(
            target=self._start_listening, daemon=True
        )
        self.listening_thread.start()


    # Records audio using microphone input
    def _start_listening(self):
        with self.stt.mic as source:
            self.stt.recognizer.adjust_for_ambient_noise(source)  # Noise cancellation
            try:
                # Listen until button is released; no timeout limit
                self.audio_data = self.stt.recognizer.listen(
                    source, timeout=None, phrase_time_limit=None
                )
                print("[DEBUG] New audio recorded.")
            except Exception as e:
                print(f"[ERROR] Failed to record audio: {e}")
                self.audio_data = None

    # Called when the user releases the talk button
    def on_release(self, event=None):
        if self.audio_data:
            # Run audio processing pipeline in a separate thread
            threading.Thread(
                target=self._process_pipeline_from_audio, daemon=True
            ).start()
        else:
            self.update_response_box("⚠️ Didn't catch anything.\n")

    # Wrapper to safely run an async function in a thread
    def _process_pipeline_from_audio(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.pipeline_with_audio())
        loop.close()

    # The full AI pipeline from voice → text → chatbot → voice
    async def pipeline_with_audio(self):
        try:
            text = ""
            try:
                # Convert audio to text using Google STT
                text = self.stt.recognizer.recognize_google(self.audio_data)
            except Exception:
                text = ""

            if not text:
                self.update_response_box("Didn't catch that. Try again.\n")
                return

            # Display and log user input
            self.update_response_box(f"👤 You: {text}")
            log_text(self.log_path, f"You: {text}")

            # Get chatbot response
            response = self.alfred.chat(text)
            if not response:
                self.update_response_box("Alfred encountered an issue.")
                return

            # Display and log AI response
            self.update_response_box(f"Alfred: {response}")
            log_text(self.log_path, f"Alfred: {response}")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                audio_file = temp_audio.name

            await self.tts.speak(response, audio_file)
            self.last_audio_path = audio_file

            # Play the audio in a separate thread and schedule its deletion
            async_play_audio(audio_file)

            # Schedule the file for deletion after a short delay
            threading.Timer(5.0, self.cleanup_audio_file, args=[audio_file]).start()
        except Exception as e:
            self.update_response_box(f"Error: {e}")
        finally:
            self.update_response_box("Listening stopped.\n")

    # Updates the scrollable response box with new messages
    def update_response_box(self, text):
        self.response_box.insert(tk.END, text + "\n")
        self.response_box.see(tk.END)

    # Cleans up temporary audio files after playback
    def cleanup_audio_file(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
                if self.last_audio_path == path:
                    self.last_audio_path = None
                print(f"[INFO] Deleted temp audio file: {path}")
        except Exception as e:
            print(f"[WARN] Could not delete temp file: {e}")

    # Play the last generated response audio if it exists
    def play_last_audio(self):
        if self.last_audio_path and os.path.exists(self.last_audio_path):
            async_play_audio(self.last_audio_path)
            # Optionally delete after playing again
            threading.Timer(3.0, self.cleanup_audio_file, args=[self.last_audio_path]).start()
        else:
            messagebox.showinfo("No Audio", "Audio has already been cleared.")

