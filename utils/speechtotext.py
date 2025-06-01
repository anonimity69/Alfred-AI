# ###################################### #
# File: speechtotext.py                  #
# Author: Shrayanendra Nath Mandal       #
# Date: 06/01/2025                       #
# Description: Speech to Text convertor  #
# ###################################### #
import threading
import speech_recognition as sr

class SpeechToText:
    def __init__(self, callback=None):
        """
        Initialize the SpeechToText engine.
        :param callback: A function to receive transcribed text or errors.
        """
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.listening = False
        self.callback = callback or self.default_callback

    def default_callback(self, message):
        """ Default handler if no callback is provided. """
        print(message)

    def transcribe(self):
        """ Continuously listen and transcribe speech to text. """
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio)
                    self.callback(f"You said: {text}")
                except sr.WaitTimeoutError:
                    self.callback("Timeout — no speech detected.")
                except sr.UnknownValueError:
                    self.callback("Didn't catch that.")
                except sr.RequestError as e:
                    self.callback(f"API error: {e}")

    def start(self):
        """ Start listening in a separate thread. """
        if not self.listening:
            self.listening = True
            threading.Thread(target=self.transcribe, daemon=True).start()
            self.callback("Listening...")

    def stop(self):
        """ Stop listening. """
        self.listening = False
        self.callback("Recognition stopped.")

