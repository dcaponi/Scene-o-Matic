import glob
import shutil
from uuid import uuid4
from moviepy.video.fx.all import crop

import requests
from termcolor import colored
from generative.llm.openai import video_search_terms_array
from stock_footage.pexels import get_video
from moviepy.editor import *

def create_compilation(staging_dir: str, prompt: str, size=(1080, 1920), min_duration=60):
    clips = []
    video_search_terms = video_search_terms_array(prompt, min_duration // 10)
    outdir = f"{staging_dir}/videos"
    os.mkdir(outdir)

    while sum(clip.duration for clip in clips) < min_duration:
        get_batch_stock_footage(outdir, video_search_terms)
        print(colored(f"The minimum duration is {min_duration} seconds.", "yellow"))
        print(colored(f"You need {min_duration - sum(clip.duration for clip in clips)} seconds of footage", "yellow"))
        input(colored(f"Remove or insert clips into {outdir} now. Press enter to continue...", "yellow"))
        video_paths = [f"{vp}" for vp in glob.glob(f"{outdir}/*.mp4")]
        for video_path in video_paths:
            clip = VideoFileClip(video_path).without_audio().set_fps(30)
            clip = crop(clip, width=size[0], height=size[1]).resize(size)

            clips.append(clip)
            os.remove(video_path)

    shutil.rmtree(outdir)
    return concatenate_videoclips(clips).set_fps(30)


def get_batch_stock_footage(outdir: str, video_search_terms):
    video_urls = []
    for search_term in video_search_terms:
        video_url = get_video(search_term)
        if video_url != None and video_url not in video_urls and video_url != "":
            video_urls.append(video_url)

    video_paths = []
    for video_url in video_urls:
        video_id = uuid4()
        video_path = f"{outdir}/{video_id}.mp4"
        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)
        video_paths.append(video_path)
