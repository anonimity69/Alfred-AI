import asyncio
import os
from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play

async def run_pipeline(stt, alfred, tts, update_response_box, log, last_audio_path_container):
    """
    Runs the main pipeline:
    1. Capture speech (async)
    2. Get Alfred response
    3. Text to speech and playback
    """
    try:
        update_response_box("🎙️ Listening...")
        text = await capture_speech_async(stt)

        if not text:
            update_response_box("🤖 Didn't catch that. Try again.")
            return

        update_response_box(f"👤 You: {text}")
        log(f"You: {text}")

        response = alfred.chat(text)

        if not response:
            update_response_box("🤖 Alfred encountered an issue.")
            return

        update_response_box(f"🤖 Alfred: {response}")
        log(f"Alfred: {response}")

        audio_file = os.path.join("Outputs", datetime.now().strftime("%H-%M-%S") + ".mp3")
        await tts.speak(response, audio_file)
        last_audio_path_container["path"] = audio_file

        audio = AudioSegment.from_file(audio_file, format="mp3")
        play(audio)

    except Exception as e:
        update_response_box(f"⚠️ Error: {e}")


async def run_pipeline_with_audio(stt, alfred, tts, update_response_box, log, audio_data, last_audio_path_container):
    """
    Pipeline for when you already have recorded audio_data (on button release).
    """
    try:
        text = ""
        try:
            text = stt.recognizer.recognize_google(audio_data)
        except Exception:
            text = ""

        if not text:
            update_response_box("🤖 Didn't catch that. Try again.")
            return

        update_response_box(f"👤 You: {text}")
        log(f"You: {text}")

        response = alfred.chat(text)

        if not response:
            update_response_box("🤖 Alfred encountered an issue.")
            return

        update_response_box(f"🤖 Alfred: {response}")
        log(f"Alfred: {response}")

        audio_file = os.path.join("Outputs", datetime.now().strftime("%H-%M-%S") + ".mp3")
        await tts.speak(response, audio_file)
        last_audio_path_container["path"] = audio_file

        audio = AudioSegment.from_file(audio_file, format="mp3")
        play(audio)

    except Exception as e:
        update_response_box(f"⚠️ Error: {e}")


async def capture_speech_async(stt):
    """
    Runs speech to text in a separate thread asynchronously.
    """
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, blocking_capture, stt)
    return await future


def blocking_capture(stt):
    """
    Blocking call to capture audio and transcribe.
    """
    with stt.mic as source:
        stt.recognizer.adjust_for_ambient_noise(source)
        try:
            audio = stt.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            return stt.recognizer.recognize_google(audio)
        except Exception:
            return ""
