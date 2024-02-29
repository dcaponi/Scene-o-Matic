from os import environ
from openai import OpenAI

openai_client = OpenAI(api_key=environ.get("OPENAI_API_KEY"))

def openai_tts(text: str, speaker: str) -> bytes:
    return openai_client.audio.speech.create(
        model="tts-1",
        voice=speaker,
        input=text,
    ).content
