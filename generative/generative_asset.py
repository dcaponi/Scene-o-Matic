import os
import re
from moviepy.editor import concatenate_audioclips, AudioFileClip
from termcolor import colored
from generative.create_compilation import create_compilation
from generative.llm.openai import generate_script
from generative.tts.tts import tts

def generative_video(staging_dir, clip):
    duration = clip.duration if clip.duration else clip.audio.duration
    if duration == None:
        print(colored("For generative videos specify a duration or provide an audio override for the clip to match duration on", "red"))
        return None
    
    prompt, src = clip.asset.split(".")
    if src.lower() == 'rand':
        return create_compilation(staging_dir, prompt, clip.size, duration)
    if src.lower() == 'sora':
        pass

def generative_tts(staging_dir, clip):
    tts_path = f"{staging_dir}/tts/tts.mp3"

    if os.path.exists(tts_path):
        print(colored("tts reading exists. skipping...", "blue"))
        print(colored(f"to change script, delete {tts_path} and try again", "blue"))
        return AudioFileClip(tts_path)

    os.mkdir(f"{staging_dir}/tts")

    prompt, src = clip.asset.split(".")
    if clip.script is not None:
        if clip.script.endswith(".txt"):
            with open(clip.script, 'r') as f:
                script = _split_string_on_punctuation(f.read())
        else:
            script = _split_string_on_punctuation(clip.script)
    else:
        print(colored("generating script...", "blue"))
        script = generate_script(prompt, clip.duration)

    audio_clips = []
    for sentence in script:
        audio_clips.append(tts(src.lower(), clip.voice, sentence, staging_dir))

    cc = concatenate_audioclips(audio_clips)
    cc.write_audiofile(tts_path)

    return AudioFileClip(tts_path)


def _split_string_on_punctuation(text):
    pattern = r"[.?!]"
    substrings = re.split(pattern, text)
    substrings = [s.strip() for s in substrings if s.strip()]
    return substrings
