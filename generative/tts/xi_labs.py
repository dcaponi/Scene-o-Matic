from os import environ
import requests
from elevenlabs import Voice, VoiceSettings, generate

BASE_URL="https://api.elevenlabs.io/v1"

def voices() -> dict:
    response = requests.request("GET", f"{BASE_URL}/voices", headers={"xi-api-key": environ.get("ELEVEN_API_KEY")})
    voice_data = response.json()
    voice_list = {}

    for voice in voice_data['voices']:
        voice_list[voice['name'].lower()] = voice['voice_id']

    return voice_list

def elevenlabs_tts(text: str, speaker: str) -> bytes:
    return generate(
        text=text,
        voice=Voice(
            voice_id=speaker,
            settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True),
        ),
    )

voices()