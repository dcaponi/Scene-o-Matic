from uuid import uuid4
from moviepy.editor import *
from termcolor import colored
from formats.utils.create_compilation import create_compilation
from subtitle.subtitle import create_subtitles
from llm.openai import generate_script
from moviepy.video.tools.subtitles import SubtitlesClip
from tts.tts import tts
import re

from llm.openai import generate_script

MAX_DURATION_SECONDS = 60


def split_string_on_punctuation(text):
    pattern = r"[.?!]"
    substrings = re.split(pattern, text)
    substrings = [s.strip() for s in substrings if s.strip()]
    return substrings

def make_movie(topic: str, bg: str, outdir: str, title=None):
    title = title or uuid4()

    print(colored(f"Starting assembly for {title}", "blue"))

    if not os.path.exists(f"./{outdir}/{title}"):
        os.mkdir(f"./{outdir}/{title}")

    script_path = f"./{outdir}/{title}/script.txt"
    audio_path = f"./{outdir}/{title}/final.mp3"
    subtitles_path = f"./{outdir}/{title}/subtitles.srt"
    combined_video_path = f"./{outdir}/{title}/raw.mp4"

    new_script = False
    new_audio = False

    if os.path.exists(script_path):
        print(colored("Using found script", "green"))
        with open(script_path, "r") as f:
            script = split_string_on_punctuation(f.read())
    else:
        print(colored("No script found, creating...", "blue"))
        new_script = True
        script = generate_script(
            f"""
            Give a description about some unhinged conspiracy theories related to the following topic. Content must be under 30 seconds in length.
            The topic is: {topic}
            Keep the jokes PG-13 and coding or office politics related (some curse words are ok like ass, and shit). Be enthusiastic in your delivery. Avoid typical cliche programmer jokes.
            Do not include any commentary or mention this prompt, simply give me the script for the video. You're the only one presenting.
            We're not going for "so bad its good". Don't include an introduction like "hey there programmers", just launch right into it.
            Use hyperbolic phrases. Mix in bad politics and workplace relationship advice.
            """,
            MAX_DURATION_SECONDS,
        )
        print(colored("Created script!", "green"))
        with open(script_path, "w") as f:
            f.write("".join(script))

    if not os.path.exists(audio_path) or new_script:
        print(colored("Creating audio from script...", "blue"))
        new_audio = True
        audio_paths = []
        for sentence in script:
            current_tts_path = f"./{outdir}/{title}/{uuid4()}.mp3"
            tts("tiktok", "en_male_funny", sentence, filename=current_tts_path)
            audio_clip = AudioFileClip(current_tts_path)
            audio_paths.append(audio_clip)
            os.remove(current_tts_path)

        audio_clip = concatenate_audioclips(audio_paths)
        audio_clip.write_audiofile(audio_path)
        print(colored("Audio created!", "green"))
    else:
        print(colored("Using found audio.", "green"))

    audio_clip = AudioFileClip(audio_path)

    if not os.path.exists(combined_video_path):
        print(colored("Creating compilation video...", "blue"))
        final_clip = create_compilation(f"./{outdir}/{title}", bg, script, audio_clip.duration)
        final_clip = final_clip.subclip(0, min(final_clip.duration, audio_clip.duration))
        final_clip.write_videofile(combined_video_path, threads=8)
        print(colored("Compilation video created!", "green"))
    else:
        final_clip = VideoFileClip(combined_video_path)
        if final_clip.duration != audio_clip.duration and new_audio:
            print(colored("Rewriting compilation video for new audio...", "blue"))
            final_clip = create_compilation(f"./{outdir}/{title}", bg, script, audio_clip.duration)
            final_clip = final_clip.subclip(0, min(final_clip.duration, audio_clip.duration))
            final_clip.write_videofile(combined_video_path, threads=8)
            print(colored("Compilation video created!", "green"))

    if not os.path.exists(subtitles_path) or new_audio:
        print(colored("Creating subtitles...", "blue"))
        create_subtitles(audio_path, subtitles_path)
        print(colored("Created subtitles!", "green"))

    generator = lambda txt: TextClip(
        txt,
        font=f"./fonts/bold_font.ttf",
        fontsize=100,
        color="#FFFF00",
        stroke_color="black",
        stroke_width=5,
    )

    result = CompositeVideoClip(
        [
            VideoFileClip(combined_video_path).set_audio(audio_clip),
            SubtitlesClip(subtitles_path, generator).set_pos(("center", "center")),
        ]
    )

    print(colored("Creating finished video...", "blue"))
    result.write_videofile(f"./{outdir}/{title}/final.mp4", threads=8)
    print(colored("Enjoy your video!", "green"))
