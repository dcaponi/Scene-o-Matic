import glob
import shutil
from uuid import uuid4
from moviepy.video.fx.all import crop

import requests
from termcolor import colored
from generative.llm.openai import video_search_terms_array
from generative.video.compilation.stock_footage.pexels import get_video
from moviepy.editor import *

def create_compilation(project_dir: str, prompt: str, size=(1080, 1920), min_duration=60):

    comp_source_videos = f"{project_dir}/compilation_sources"
    comp_staging_dir = f"{comp_source_videos}/compilation.mp4"

    if os.path.exists(comp_staging_dir):
        print(colored("compiliation exists. skipping...", "blue"))
        print(colored(f"to remake compilation, delete {comp_staging_dir} and try again.", "blue"))
        return VideoFileClip(comp_staging_dir)

    clips = []
    video_search_terms = video_search_terms_array(prompt, min_duration // 10)
    os.mkdir(comp_source_videos)

    while sum(clip.duration for clip in clips) < min_duration:
        get_batch_stock_footage(comp_source_videos, video_search_terms, size)
        print(colored(f"The minimum duration is {min_duration} seconds.", "yellow"))
        print(colored(f"You need {min_duration - sum(clip.duration for clip in clips)} seconds of footage", "yellow"))
        input(colored(f"Remove or insert clips into {comp_source_videos} now. Press enter to continue...", "yellow"))
        video_paths = [f"{vp}" for vp in glob.glob(f"{comp_source_videos}/*.mp4")]
        for video_path in video_paths:
            clip = VideoFileClip(video_path)
            clip = crop(clip, width=size[0], height=size[1]).resize(size)

            clips.append(clip)
            os.remove(video_path)

    concatenate_videoclips(clips).without_audio().set_fps(30).write_videofile(comp_staging_dir, threads=8, audio=False)

    return VideoFileClip(comp_staging_dir)


def get_batch_stock_footage(comp_source_videos: str, video_search_terms, size=(1080, 1920)):
    video_urls = []
    for search_term in video_search_terms:
        video_url = get_video(search_term, size)
        if video_url != None and video_url not in video_urls and video_url != "":
            video_urls.append(video_url)

    video_paths = []
    for video_url in video_urls:
        video_id = uuid4()
        video_path = f"{comp_source_videos}/{video_id}.mp4"
        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)
        video_paths.append(video_path)
