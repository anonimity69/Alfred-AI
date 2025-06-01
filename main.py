import tkinter as tk
import threading
import asyncio
import io
import simpleaudio as sa  # For audio playback (WAV)
from pydub import AudioSegment  # For MP3 to WAV conversion
import edge_tts  # For text-to-speech synthesis
from utils.speechtotext import SpeechToText
from utils.texttospeech import TextToSpeech
from utils.alfredai_engine import AlfredChatbot

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

        # --- Utilities ---
        self.stt = SpeechToText(self.label, self.text_box)
        self.tts = TextToSpeech()
        self.alfred = AlfredChatbot()

        # --- Controls ---
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start Listening", command=self.start_listening, width=18, bg="lightgreen")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_listening, width=10, bg="lightcoral")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear Transcript", command=self.clear_transcript, width=15)
        self.clear_button.pack(side=tk.LEFT, padx=5)

    # --- Button actions ---
    def start_listening(self):
        # Start the speech-to-text pipeline in a background thread
        threading.Thread(target=self.listen_and_respond, daemon=True).start()

    def stop_listening(self):
        # Stop STT listening (uses class method)
        self.stt.stop()

    def clear_transcript(self):
        # Clear the transcript box using class method
        self.stt.clear()

    # --- Main pipeline: STT -> Alfred -> TTS ---
    def listen_and_respond(self):
        # 1. Start listening for speech
        self.stt.start()

        # Wait for a single utterance
        self.label.config(text="Listening...")
        with self.stt.mic as source:
            self.stt.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.stt.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.stt.recognizer.recognize_google(audio)
                self.text_box.insert(tk.END, f"You said: {text}\n")
                self.text_box.see(tk.END)
            except Exception as e:
                self.text_box.insert(tk.END, f"Error: {str(e)}\n")
                self.label.config(text="An error occurred.")
                return

        self.stt.stop()
        self.label.config(text="Thinking...")

        # 2. Send text to Alfred, get response
        response = self.get_alfred_response(text)
        self.text_box.insert(tk.END, f"Alfred: {response}\n")
        self.text_box.see(tk.END)

        # 3. Speak Alfred's response (TTS)
        self.label.config(text="Speaking...")
        asyncio.run(self.speak_and_play(response))
        self.label.config(text="Ready.")

    def get_alfred_response(self, prompt):
        # Use AlfredChatbot.chat() but capture its stdout output
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
        # Use edge-tts to synthesize, pydub to convert, simpleaudio to play
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