import os
import re
from moviepy.editor import concatenate_audioclips, AudioFileClip
from termcolor import colored
from generative.video.compilation.create_compilation import create_compilation
from generative.llm.openai import generate_script
from generative.tts.tts import tts

def generative_video(staging_dir, snippet):
    duration = snippet.duration if snippet.duration else snippet.audio.duration
    if duration == None:
        print(colored("For generative videos specify a duration or provide an audio override for the snippet to match duration on", "red"))
        return None

    prompt, src = snippet.asset.split(".")
    if src.lower() == 'rand':
        return create_compilation(staging_dir, prompt, snippet.size, duration)
    if src.lower() == 'sora':
        pass
    if src.lower() == "d-id":
        pass

def generative_tts(staging_dir, snippet):
    tts_path = f"{staging_dir}/tts/tts.mp3"

    if os.path.exists(tts_path):
        print(colored("tts reading exists. skipping...", "blue"))
        print(colored(f"to change script, delete {tts_path} and try again", "blue"))
        return AudioFileClip(tts_path)

    if not os.path.exists(f"{staging_dir}/tts"):
        os.mkdir(f"{staging_dir}/tts")

    prompt, src = snippet.asset.split(".")
    if snippet.script is not None:
        if snippet.script.endswith(".txt"):
            with open(snippet.script, 'r') as f:
                script = _split_string_on_punctuation(f.read())
        else:
            script = _split_string_on_punctuation(snippet.script)
    else:
        print(colored("generating script...", "blue"))
        script = generate_script(prompt, snippet.duration)

    audio_clips = []
    for sentence in script:
        audio_clips.append(tts(src.lower(), snippet.voice, sentence, staging_dir))

    cc = concatenate_audioclips(audio_clips)
    cc.write_audiofile(tts_path)

    # Write the audio file so we can retry later steps in the pipeline without re-generating the TTS which may cost money
    return AudioFileClip(tts_path)


def _split_string_on_punctuation(text):
    pattern = r"[.?!]"
    substrings = re.split(pattern, text)
    substrings = [s.strip() for s in substrings if s.strip()]
    return substrings
