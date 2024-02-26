import base64
import requests
from dotenv import load_dotenv
from os import getenv

from util.util import split_string

load_dotenv("../.env")
TIK_TOK_CHAR_LIMIT = 300

def tiktok_tts(text, speaker: str) -> bytes:
    if len(text) < TIK_TOK_CHAR_LIMIT:
        r = requests.post(
            f"{getenv('TIKTOK_TTS_URL')}",
            json={"text": text, "voice": speaker},
            headers={"Content-Type": "application/json"},
        )
        vstr = r.json()["data"]
        return base64.b64decode(vstr)
    else:
        text_parts = split_string(text, 299)
        audio_base64_chunks = [None] * len(text_parts)

        def __tiktok_tts_chunk(text: str, speaker: str, idx=0):
            r = requests.post(
                f"{getenv('TIKTOK_TTS_URL')}",
                json={"text": text, "voice": speaker},
                headers={"Content-Type": "application/json"},
            )
            audio_base64_chunks[idx] = r.json()["data"]

        audio_base64_chunks = [__tiktok_tts_chunk(text_part, speaker, idx) for idx, text_part in enumerate(text_parts)]

        audio_base64_chunks = "".join(audio_base64_chunks)
        return base64.b64decode(audio_base64_chunks)
