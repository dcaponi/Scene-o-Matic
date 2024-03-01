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

def create_subtitles(movie_path: str, size=(1080, 1920)):

    transcript = transcriber.transcribe(f"{movie_path}.mp4") # also accepts web urls

    subtitles = transcript.export_subtitles_srt()

    with open(f"{movie_path}.srt", "w") as f:
        f.write(subtitles)

    srt_equalizer.equalize_srt_file(f"{movie_path}.srt", f"{movie_path}.srt", 10)

    print(colored("[+] Subtitles generated.", "green"))

    generator = lambda txt: TextClip(
        txt,
        font=f"./fonts/bold_font.ttf",
        fontsize=100,
        color="#FFFF00",
        stroke_color="black",
        stroke_width=5,
    )

    subtitle_clip = SubtitlesClip(f"{movie_path}.srt", generator).set_pos(("center", "center")).set_fps(24)

    return subtitle_clip
