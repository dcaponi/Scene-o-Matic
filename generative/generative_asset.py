import re
from moviepy.editor import concatenate_audioclips
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
    prompt, src = clip.asset.split(".")
    if clip.script is not None:
        script = _split_string_on_punctuation(clip.script)
    else:
        print(colored("generating script...", "blue"))
        script = generate_script(prompt, clip.duration)

    audio_clips = []
    for sentence in script:
        audio_clips.append(tts(src.lower(), clip.voice, sentence, staging_dir))

    return concatenate_audioclips(audio_clips)


def _split_string_on_punctuation(text):
    pattern = r"[.?!]"
    substrings = re.split(pattern, text)
    substrings = [s.strip() for s in substrings if s.strip()]
    return substrings
