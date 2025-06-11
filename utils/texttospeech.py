"""
#############################################################
# File        : texttospeech.py                             #
# Authors     : Shrayanendra Nath Mandal, Preetish Majumdar #
# Date        : 2025-06-01                                  #
# Description : GUI-based Alfred AI Assistant using Gemini  #
#               API, Speech Recognition, and Text to Speech #
#############################################################
"""
import pyttsx3

class TextToSpeech:
    def __init__(self, voice="english"):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 180)
        voices = self.engine.getProperty("voices")
        
        # Choose a voice that matches
        for v in voices:
            if "Ryan" in v.name or "en_GB" in v.id:
                self.engine.setProperty("voice", v.id)
                break

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
