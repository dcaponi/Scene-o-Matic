from __future__ import annotations

import os
import sys
import json
import queue
import threading

from termcolor import colored
from typing import List, Optional
from dataclasses import dataclass, field

from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import CompositeAudioClip, AudioFileClip, VideoFileClip, VideoClip

from formats.utils.edit_utils import create_caption
from generative.generative_asset import generative_tts, generative_video

@dataclass
class Clip:
    asset: str
    prompt: str = None
    script: str = None
    voice: str = None
    duration: int = None
    has_greenscreen: bool = False
    has_background: bool = True
    override_audio: Optional[Clip] = None
    video: VideoFileClip = None
    audio: AudioFileClip = None
    subtitle: SubtitlesClip = None
    size: Optional[tuple[int, int]] = None
    location: tuple[int, int] = field(default_factory = lambda:(0, 0))
    anchor: tuple[str, str] = field(default_factory = lambda:("top", "left"))





@dataclass
class Scene:
    clips: List[Clip]
    video_clip: VideoClip = None
    audio: AudioFileClip = None
    arrangement: str = "vertical"
    use_audio: List[int] = field(default_factory=lambda: [0])





@dataclass
class Movie:
    title: str
    scenes: List[Scene]
    has_subtitles: bool = False
    publish_destinations: List[str] = field(default_factory=lambda: [])
    final_size: tuple[int, int] = field(default_factory=lambda: (1080, 1920))
    duration: int = 0
    staging_dir: str = None





def movies_from_json(filepath, projects_folder):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            movie_jobs = queue.Queue()
            movies = []
            threads = []
            
            for movie_data in data:
                thread = threading.Thread(target=unpack_movie, args=(movie_data, projects_folder, movie_jobs, ))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
            while not movie_jobs.empty():
                movies.append(movie_jobs.get())
            return movies
        
    except FileNotFoundError:
        print(colored(f"Error: File {filepath} not found", "red"))
        sys.exit(1)
    except json.JSONDecodeError:
        print(colored(f"Error File {filepath} does not contain valid json", "red"))
        sys.exit(1)





def unpack_movie(movie_data, projects_folder, result_queue):
    movie = Movie(**movie_data)
    movie.staging_dir = f"./{projects_folder}/{movie_data.get('title')}"

    print(colored(f"[{movie.title}]: unpacking...", "blue"))

    if os.path.exists(f"{movie.staging_dir}/{movie.title}.mp4"):
        print(colored(f"movie {movie.title} exists. skipping...", "blue"))
        print(colored(f"to rebuild the movie, delete {movie.staging_dir}/{movie_data.get('title')}.mp4 and try again","blue"))
        return

    if not os.path.exists(movie.staging_dir):
        os.mkdir(movie.staging_dir)

    scenes = []

    for scene_data in movie_data.get("scenes", []):
        scene = Scene(**scene_data)

        clips = []
        
        for clip_data in scene_data.get("clips", []):
            clip = Clip(**clip_data)

            if clip.override_audio:
                print(colored(f"[{movie.title}]: detected audio override for", "blue"))

                audio_override = Clip(**clip.override_audio)

                if audio_override.asset.endswith(('mp3', 'wav', 'ogg')):
                    print(colored(f"[{movie.title}]: assigning audio...", "blue"))
                    clip.audio = AudioFileClip(audio_override.asset)

                if audio_override.asset.endswith(("xi_labs", "tiktok", "whisper")):
                    print(colored(f"[{movie.title}]: creating audio from tts for...", "blue"))
                    clip.audio = generative_tts(movie.staging_dir, audio_override)

                print(colored(f"[{movie.title}]: overide audio complete!", "green"))

            if os.path.exists(clip.asset):
                print(colored(f"[{movie.title}]: creating moviepy objects...", "blue"))

                if clip.asset.endswith(('jpg', 'jpeg', 'png', 'gif')):
                    clip.video = VideoFileClip(clip.asset).set_duration(clip.duration)

                elif clip.asset.endswith(('mp3', 'wav', 'ogg')):
                    clip.audio = AudioFileClip(clip.asset)

                elif clip.asset.endswith(('mp4', 'avi', 'mkv')):
                    clip.video = VideoFileClip(clip.asset)
                    if clip.audio is None:
                        clip.audio = clip.video.audio

                print(colored(f"[{movie.title}]: Finished assigning assets!", "green"))

            else:
                print(colored(f"[{movie.title}]: detected generative asset...", "blue"))

                if clip.asset.endswith(('xi_labs', 'tiktok', 'whisper')): 
                    print(colored(f"[{movie.title}]: generating audio from tts...", "blue"))
                    clip.audio = generative_tts(movie.staging_dir, clip)
                elif clip.asset.endswith(('d-id')): # asset-name.d-id -> go make a .mp4 using a talking head like d-id from asset script
                    # clip.video = did_character(clip.script, clip.host_img) (maybe host_img could also end in .sd or .mj and it would make you a host)
                    pass
                elif clip.asset.endswith(('sora', 'rand')): 
                    print(colored(f"[{movie.title}]: generating video from prompt...", "blue"))
                    clip.video = generative_video(movie.staging_dir, clip)
                elif clip.asset.endswith(('mj', 'sd', 'dall-e')): # asset-name.dall-e -> go make an image using a prompt
                    # clip.video = midjourney(prompt)
                    pass

                else:
                    print(colored(f"[{movie.title}]: generating caption...", "blue"))
                    clip.video = create_caption(
                        text=clip.asset,
                        font="Courier-New-Bold",
                        fontsize=70,
                        color="white",
                        size=clip.size,
                        pos=clip.anchor,
                        has_bg=clip.has_background,
                    )

                print(colored(f"[{movie.title}]: finished generating assets!", "green"))

            if clip.video is not None and clip.size is not None:
                clip.video = clip.video.resize(clip.size)

            clips.append(clip)

        scene.clips = clips
        scene.audio = CompositeAudioClip([scene.clips[x].audio for x in scene.use_audio])
        scenes.append(scene)

    print(colored(f"[{movie.title}]: finished unpacking movie!", "green"))
    movie.scenes = scenes
    result_queue.put(movie)
