# ######################################                    #
# File: texttospeech.py                                     #
# Author: Shrayanendra Nath Mandal, Preetish Majumdar       #
# Date: 06/01/2025                                          #
# Description: Text to Speech convertor                     #
# ######################################                    #

import asyncio
import edge_tts

class TextToSpeech:
    def __init__(self, voice="en-GB-RyanNeural"):
        self.voice = voice

    async def speak(self, text: str, output_path: str):
        """Convert text to speech and save it as an audio file."""
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        await communicate.save(output_path)
        print(f"Speech saved to {output_path}")

    def generate(self, text: str, output_path: str):
        """Wrapper to run the async speak method."""
        asyncio.run(self.speak(text, output_path))
