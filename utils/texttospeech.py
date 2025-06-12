"""
#############################################################
# File        : texttospeech.py                             #
# Authors     : Shrayanendra Nath Mandal, Preetish Majumdar #
# Date        : 2025-06-01                                  #
# Description : Text to Speech using Edge TTS               #
#############################################################
"""

import asyncio
import edge_tts
import tempfile
import os
import platform
import subprocess

class TextToSpeech:
    def __init__(self, voice="en-GB-RyanNeural"):
        self.voice = voice

    async def _speak_async(self, text):
        # Generate audio using edge-tts
        communicate = edge_tts.Communicate(text, self.voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_audio_path = f.name
        await communicate.save(temp_audio_path)

        # Play audio (cross-platform)
        if platform.system() == "Windows":
            subprocess.run(["start", "/min", temp_audio_path], shell=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["afplay", temp_audio_path])
        else:  # Linux
            subprocess.run(["mpg123", temp_audio_path])

        # Optionally delete the file later
        # os.remove(temp_audio_path)

    def speak(self, text):
        asyncio.run(self._speak_async(text))
