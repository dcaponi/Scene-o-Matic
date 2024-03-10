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
class Snippet:
    asset: str
    prompt: str = None
    script: str = None
    voice: str = None
    duration: int = None
    has_greenscreen: bool = False
    has_background: bool = True
    override_audio: Optional[Snippet] = None
    video: VideoFileClip = None
    audio: AudioFileClip = None
    subtitle: SubtitlesClip = None
    size: Optional[tuple[int, int]] = None
    location: tuple[int, int] = field(default_factory = lambda:(0, 0))
    anchor: tuple[str, str] = field(default_factory = lambda:("left", "top"))


@dataclass
class Scene:
    snippets: List[Snippet]
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

        snippets = []

        for snippet_data in scene_data.get("snippets", []):
            snippet = Snippet(**snippet_data)

            if snippet.override_audio:
                print(colored(f"[{movie.title}]: detected audio override for", "blue"))

                audio_override = Snippet(**snippet.override_audio)

                if audio_override.asset.endswith(('mp3', 'wav', 'ogg')):
                    print(colored(f"[{movie.title}]: assigning audio...", "blue"))
                    snippet.audio = AudioFileClip(audio_override.asset)

                if audio_override.asset.endswith(("xi_labs", "tiktok", "whisper")):
                    print(colored(f"[{movie.title}]: creating audio from tts for...", "blue"))
                    snippet.audio = generative_tts(movie.staging_dir, audio_override)

                print(colored(f"[{movie.title}]: overide audio complete!", "green"))

            if os.path.exists(snippet.asset):
                print(colored(f"[{movie.title}]: creating moviepy objects...", "blue"))

                if snippet.asset.endswith(('jpg', 'jpeg', 'png', 'gif')):
                    snippet.video = VideoFileClip(snippet.asset).set_duration(snippet.duration)

                elif snippet.asset.endswith(('mp3', 'wav', 'ogg')):
                    snippet.audio = AudioFileClip(snippet.asset)

                elif snippet.asset.endswith(('mp4', 'avi', 'mkv')):
                    snippet.video = VideoFileClip(snippet.asset)
                    if snippet.audio is None:
                        snippet.audio = snippet.video.audio

                print(colored(f"[{movie.title}]: Finished assigning assets!", "green"))

            else:
                print(colored(f"[{movie.title}]: detected generative asset...", "blue"))

                if snippet.asset.endswith(('xi_labs', 'tiktok', 'whisper')): 
                    print(colored(f"[{movie.title}]: generating audio from tts...", "blue"))
                    snippet.audio = generative_tts(movie.staging_dir, snippet)
                elif snippet.asset.endswith(('d-id')): # asset-name.d-id -> go make a .mp4 using a talking head like d-id from asset script
                    # clip.video = did_character(clip.script, clip.host_img) (maybe host_img could also end in .sd or .mj and it would make you a host)
                    pass
                elif snippet.asset.endswith(('sora', 'rand')): 
                    print(colored(f"[{movie.title}]: generating video from prompt...", "blue"))
                    snippet.video = generative_video(movie.staging_dir, snippet)
                elif snippet.asset.endswith(('mj', 'sd', 'dall-e')): # asset-name.dall-e -> go make an image using a prompt
                    # clip.video = midjourney(prompt)
                    pass

                # This assumption isnt great as it falls apart if someone needs a caption ending with a file extension for some reason
                # more importantly it falls over if an asset isnt found and we shouldn't assume its part of the caption
                # Now it'll return a weird video with no background and a messed up looking caption which is obvious something is off
                # but it may be better to do a good ol' fashioned clip.type check... so much for being clever :)
                else:
                    if snippet.asset.endswith(('mp3', 'wav', 'ogg', 'mp4', 'avi', 'mkv')):
                        print(colored(f"[{movie.title}]: looks like a file asset {snippet.asset} was specified but doesn't exist", "yellow"))
                        print(colored(f"[{movie.title}]: If this was meant to be a file, check the path and try again, otherwise, assumes asset is a TextClip", "yellow"))

                    print(colored(f"[{movie.title}]: generating caption...", "blue"))
                    snippet.video = create_caption(
                        text=snippet.asset,
                        font="Courier-New-Bold",
                        fontsize=70,
                        color="white",
                        size=snippet.size,
                        pos=snippet.anchor,
                        has_bg=snippet.has_background,
                    )

                print(colored(f"[{movie.title}]: finished generating assets!", "green"))

            if snippet.video is not None and snippet.size is not None:
                snippet.video = snippet.video.resize(snippet.size)

            if snippet.video and snippet.video.duration is None:
                if snippet.audio is not None and snippet.audio.duration is not None and snippet.audio.duration > 0:
                    snippet.video.duration = snippet.audio.duration
                elif snippet.duration is not None and snippet.duration > 0:
                    snippet.video.duration = snippet.duration

                if snippet.video.duration is None and snippet.asset.endswith(('mp3', 'wav', 'ogg', 'mp4', 'avi', 'mkv')):
                    print(colored(f"[{movie.title}]: clip duration could not be determined from video or audio source", "red"))
                    print(colored(f"[{movie.title}]: clip duration must be specified explicitly", "red"))
                    continue

            snippets.append(snippet)

        scene.snippets = snippets
        scene.audio = CompositeAudioClip([scene.snippets[x].audio for x in scene.use_audio])
        scenes.append(scene)

    print(colored(f"[{movie.title}]: finished unpacking movie!", "green"))
    movie.scenes = scenes
    result_queue.put(movie)
