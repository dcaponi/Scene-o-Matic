import os
from moviepy.editor import AudioFileClip
from termcolor import colored
from generative.tts.xi_labs import elevenlabs_tts
from generative.tts.openai import openai_tts
from generative.tts.tiktok import tiktok_tts
from generative.tts.voices import tiktok, whisper, elevenlabs
from dotenv import load_dotenv

load_dotenv("../.env")

TIK_TOK_CHAR_LIMIT = 300

def tts(
    source: str,
    text_speaker: str,
    req_text: str,
    staging_dir: str
):
    audio_data = None

    filename = f"{staging_dir}/voice.mp3"

    if source in sources():
        if text_speaker in voices()[source]:
            if source == "tiktok":
                audio_data = tiktok_tts(req_text, text_speaker)
            if source == "xi_labs":
                audio_data = elevenlabs_tts(req_text, voices()[source][text_speaker]) # translate voice name to voice id because elevenlabs api
            if source == "whisper":
                audio_data = openai_tts(req_text, text_speaker)
        else:
            print(colored(f"voice {text_speaker} not known to {source}", "red"))
            return None
    else: 
        print(colored(f"source {source} currently not supported", "red"))
        return None

    if audio_data:
        with open(filename, 'wb') as f:
            f.write(audio_data)

        audio_clip = AudioFileClip(filename)
        os.remove(filename)
        return audio_clip

    else:
        print(colored("no audio data returned", "red"))
        return None


def voices():
    return {"tiktok": tiktok, "whisper": whisper, "xi_labs": elevenlabs}

def sources():
    return ["tiktok", "whisper", "xi_labs"]
