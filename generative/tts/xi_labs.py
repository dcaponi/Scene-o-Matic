from os import environ
import requests
from elevenlabs import Voice, VoiceSettings, generate
from termcolor import colored

BASE_URL="https://api.elevenlabs.io/v1"

def voices() -> dict:
    try:
        response = requests.request("GET", f"{BASE_URL}/voices", headers={"xi-api-key": environ.get("ELEVEN_API_KEY")})
        voice_data = response.json()
        voice_list = {}

        for voice in voice_data['voices']:
            voice_list[voice['name'].lower()] = voice['voice_id']

        return voice_list
    except Exception as e:
        print(colored(f"Elevenlabs Failure: {e}", "red"))
        return []

def elevenlabs_tts(text: str, speaker: str) -> bytes:
    return generate(
        text=text,
        voice=Voice(
            voice_id=speaker,
            settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True),
        ),
    )

voices()