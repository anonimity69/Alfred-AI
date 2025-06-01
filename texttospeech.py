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


# Usage example
if __name__ == "__main__":
    tts = TextToSpeech(voice="en-GB-RyanNeural")
    tts.generate(
        text='''Very well, sir. I shall endeavour to remind you to hydrate at regular intervals.
Might I suggest a glass of water now, to get ahead of the curve, as it were? Staying ahead is always advisable.''',
        output_path="Outputs/alfred_edge_tts_water.mp3"
    )
