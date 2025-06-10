"""
#############################################################
# File        : main.py                                     #
# Authors     : Shrayanendra Nath Mandal, Preetish Majumdar #
# Date        : 2025-06-06                                  #
# Description : Alfred AI Assistant - Key Activated Listen  #
#############################################################
"""

import os
import time
import uuid
import subprocess
from utils.alfredai_engine import AlfredChatbot
from utils.speechtotext import SpeechToText
from utils.texttospeech import TextToSpeech

# Create audio output directory if it doesn't exist
AUDIO_OUTPUT_DIR = "AudioOutput"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def play_audio_mac(audio_file):
    # Use afplay to play audio on macOS
    subprocess.run(["afplay", audio_file])

def main():
    print("Initializing Alfred AI Assistant...")
    bot = AlfredChatbot()
    stt = SpeechToText()
    tts = TextToSpeech(voice="en-GB-RyanNeural")

    print("Alfred is ready. Say 'exit' or 'quit' to stop.\n")

    try:
        while True:
            print("Listening... Please speak clearly.")
            stt.start()
            time.sleep(5)  # Adjust duration as needed
            stt.stop()

            user_input = stt.get_last_text()
            if user_input and user_input.lower() in ["exit", "quit"]:
                print("Alfred: Very well, sir. Until next time.")
                break

            if not user_input:
                print("Alfred: I beg your pardon, sir. I didn't quite catch that.")
                continue

            print(f"\nYou said: {user_input}")
            alfred_response = bot.chat(user_input)

            audio_file = os.path.join(AUDIO_OUTPUT_DIR, f"alfred_reply_{uuid.uuid4()}.mp3")
            tts.generate(alfred_response, audio_file)
            play_audio_mac(audio_file)  # Play the generated audio

    except KeyboardInterrupt:
        print("\nAlfred: Very well, sir. I shall take my leave.")
    finally:
        stt.stop()

if __name__ == "__main__":
    main()

