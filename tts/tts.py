from tts.elevenlabs import elevenlabs_tts
from tts.openai import openai_tts
from tts.tiktok import tiktok_tts
from tts.voices import tiktok, openai
from dotenv import load_dotenv

load_dotenv("../.env")

TIK_TOK_CHAR_LIMIT = 300

def tts(
    source: str = "tiktok",
    text_speaker: str = "en_male_funny",
    req_text: str = "TikTok Text To Speech",
    filename: str = "voice.mp3",
):
    audio_data = None

    if source in sources():
        if text_speaker in voices()[source]:
            if source == "tiktok":
                audio_data = tiktok_tts(req_text, text_speaker)
            if source == "elevenlabs":
                audio_data = elevenlabs_tts(req_text, text_speaker)
            if source == "openai":
                audio_data = openai_tts(req_text, text_speaker)
        else:
            print(f"voice not known to {source}")
    else: 
        print("source currently not supported")

    if audio_data:
        with open(filename, "wb") as out:
            out.write(audio_data)
    else:
        print("no audio data returned")


def voices():
    return {"tiktok": tiktok, "openai": openai}

def sources():
    return ["tiktok", "openai"]
