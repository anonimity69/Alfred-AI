import tkinter as tk
import threading
import asyncio
import io

import simpleaudio as sa  # For in-memory WAV audio playback
from pydub import AudioSegment  # For MP3-to-WAV conversion
import edge_tts  # For direct TTS streaming (matches your utils.texttospeech dependency)

from utils import SpeechToText, TextToSpeech, AlfredChatbot

class AlfredGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfred AI Assistant")
        self.root.geometry("700x420")

        # --- UI Elements ---
        self.label = tk.Label(root, text="Press 'Start Listening' and speak...", font=("Helvetica", 14))
        self.label.pack(pady=10)

        self.text_box = tk.Text(root, height=10, font=("Courier", 12), wrap=tk.WORD)
        self.text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Core AI & Audio Classes ---
        self.alfred = AlfredChatbot()
        self.tts = TextToSpeech()
        # The callback will append messages to the transcript box
        self.stt = SpeechToText(callback=self.on_speech_event)

        # --- Controls ---
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        self.start_button = tk.Button(button_frame, text="Start Listening", command=self.start_listening, width=18, bg="lightgreen")
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_listening, width=10, bg="lightcoral")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = tk.Button(button_frame, text="Clear Transcript", command=self.clear_transcript, width=15)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Speech result for flow control
        self.last_transcribed = None

    def on_speech_event(self, message):
        """Callback for STT events/messages, and capture the most recent transcription."""
        self.text_box.insert(tk.END, f"{message}\n")
        self.text_box.see(tk.END)
        if message.startswith("You said: "):
            self.last_transcribed = message[len("You said: "):]
            # Launch Alfred workflow in a new thread so GUI doesn't freeze
            threading.Thread(target=self.handle_alfred_response, daemon=True).start()

    def start_listening(self):
        """Start the speech-to-text process."""
        self.last_transcribed = None
        self.stt.start()
        self.label.config(text="Listening...")

    def stop_listening(self):
        """Stop the speech-to-text process."""
        self.stt.stop()
        self.label.config(text="Recognition stopped.")

    def clear_transcript(self):
        """Clear the transcript text box."""
        self.text_box.delete("1.0", tk.END)
        self.label.config(text="Transcript cleared.")

    def handle_alfred_response(self):
        """Handles the full pipeline: user speech -> Alfred reply -> TTS playback."""
        if not self.last_transcribed:
            return

        self.label.config(text="Alfred is thinking...")
        response = self.get_alfred_response(self.last_transcribed)
        self.text_box.insert(tk.END, f"Alfred: {response}\n")
        self.text_box.see(tk.END)

        self.label.config(text="Speaking...")
        asyncio.run(self.speak_and_play(response))
        self.label.config(text="Ready.")

    def get_alfred_response(self, prompt):
        """Runs AlfredChatbot.chat() and captures the full streamed response as a string."""
        old_print = print
        response_accum = []

        def fake_print(*args, **kwargs):
            end = kwargs.get('end', '\n')
            response_accum.append(' '.join(str(a) for a in args) + end)

        try:
            globals()['print'] = fake_print
            self.alfred.chat(prompt)
        finally:
            globals()['print'] = old_print

        return ''.join(response_accum).strip()

    async def speak_and_play(self, text):
        """Streams TTS audio to memory, converts to WAV, and plays it (no saving to disk)."""
        communicate = edge_tts.Communicate(text=text, voice=self.tts.voice)
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        audio_stream.seek(0)

        # Convert MP3 bytes to WAV in memory for playback
        seg = AudioSegment.from_file(audio_stream, format="mp3")
        wav_io = io.BytesIO()
        seg.export(wav_io, format="wav")
        wav_io.seek(0)
        wave_obj = sa.WaveObject.from_wave_file(wav_io)
        play_obj = wave_obj.play()
        play_obj.wait_done()

if __name__ == "__main__":
    root = tk.Tk()
    app = AlfredGUI(root)
    root.mainloop()