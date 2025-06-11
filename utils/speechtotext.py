"""
#############################################################
# File        : speechtotext.py                             #
# Authors     : Shrayanendra Nath Mandal, Preetish Majumdar #
# Date        : 2025-06-01                                  #
# Description : Speech to Text Converter                    #
#               API, Speech Recognition, and Speech to Text #
#############################################################
"""
import threading
import time
import os
import sys
from RealtimeSTT import AudioToTextRecorder
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
custom_log_path = "logs/speech.log"
rts_logger = logging.getLogger("realtimestt")
rts_logger.setLevel(logging.DEBUG)
custom_file_handler = logging.FileHandler(custom_log_path)
custom_file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d - RealTimeSTT: %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
custom_file_handler.setFormatter(formatter)
rts_logger.addHandler(custom_file_handler)
class SpeechToText:
    def __init__(self):
        self.recorder = AudioToTextRecorder()
        self.last_text = None
        self.listening = False

    def _internal_callback(self, text):
        self.last_text = text  # Store the recognized text
        # print(f"Recognized: {text}")  # Optional: useful for debugging/logging

    def start(self):
        if not self.listening:
            self.listening = True
            threading.Thread(target=self.recorder.text, args=(self._internal_callback,), daemon=True).start()

    def stop(self):
        if self.listening:
            self.recorder.stop()
            self.listening = False

    def get_last_text(self):
        return self.last_text
    
