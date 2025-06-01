import os
from datetime import datetime
import asyncio
import threading
from pydub import AudioSegment
from pydub.playback import play

def play_audio_file(path):
    try:
        audio = AudioSegment.from_file(path, format="mp3")
        play(audio)
    except Exception as e:
        print(f"⚠️ Audio Playback Error: {e}")

def async_play_audio(path):
    threading.Thread(target=play_audio_file, args=(path,), daemon=True).start()

def get_log_path():
    os.makedirs("logs", exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    return os.path.join("logs", filename)

def log_text(log_path, text):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

async def run_blocking_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)
