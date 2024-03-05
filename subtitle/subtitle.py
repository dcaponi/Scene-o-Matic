import os
import assemblyai as aai
import srt_equalizer
from termcolor import colored
from dotenv import load_dotenv
from os import getenv
from moviepy.editor import AudioClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip


load_dotenv("../.env")

ASSEMBLY_AI_API_KEY = getenv("ASSEMBLY_AI_API_KEY")

aai.settings.api_key = ASSEMBLY_AI_API_KEY

transcriber = aai.Transcriber()

def create_subtitles(output_path: str, movie_path: str):

    generator = lambda txt: TextClip(
        txt,
        font=f"./fonts/bold_font.ttf",
        fontsize=100,
        color="#FFFF00",
        stroke_color="black",
        stroke_width=5,
    )

    out_file = f"{output_path}/subtitles.srt"

    if os.path.exists(out_file):
        print(colored("subtitles exist. skipping...", "blue"))
        print(colored(f"to recreate subtitles, delete {out_file} and try again", "blue"))
        return SubtitlesClip(f"{out_file}", generator).set_pos(("center", "center")).set_fps(24)

    transcript = transcriber.transcribe(movie_path) # also accepts web urls

    subtitles = transcript.export_subtitles_srt()

    with open(out_file, "w") as f:
        f.write(subtitles)

    srt_equalizer.equalize_srt_file(out_file, out_file, 10)

    print(colored("[+] Subtitles generated.", "green"))

    return SubtitlesClip(out_file, generator).set_pos(("center", "center")).set_fps(24)
