import assemblyai as aai
import srt_equalizer
from termcolor import colored
from dotenv import load_dotenv
from os import getenv

load_dotenv("../.env")

ASSEMBLY_AI_API_KEY = getenv("ASSEMBLY_AI_API_KEY")

aai.settings.api_key = ASSEMBLY_AI_API_KEY

transcriber = aai.Transcriber()

def create_subtitles(audio_path: str, output_path: str):
    transcript = transcriber.transcribe(audio_path) # also accepts web urls

    subtitles = transcript.export_subtitles_srt()

    with open(output_path, "w") as f:
        f.write(subtitles)

    srt_equalizer.equalize_srt_file(output_path, output_path, 10)

    print(colored("[+] Subtitles generated.", "green"))

    return output_path
