from __future__ import annotations
from dataclasses import dataclass, field
import json
import os
import sys
from typing import List, Optional
from moviepy.editor import CompositeAudioClip, AudioFileClip, VideoFileClip, VideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from termcolor import colored
from generative.generative_asset import generative_tts, generative_video
from formats.utils.edit_utils import create_caption

@dataclass
class Clip:
    asset: str
    override_audio: Optional[Clip] = None
    video: VideoFileClip = None
    audio: AudioFileClip = None
    subtitle: SubtitlesClip = None
    has_greenscreen: bool = False
    has_background: bool = True
    prompt: str = None
    script: str = None
    voice: str = None
    duration: int = None
    size: Optional[tuple[int, int]] = None
    location: tuple[int, int] = field(default_factory = lambda:(0, 0))
    anchor: tuple[str, str] = field(default_factory = lambda:("top", "left"))


@dataclass
class Scene:
    clips: List[Clip]
    video_clip: VideoClip = None
    arrangement: str = "vertical"
    audio: AudioFileClip = None
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
            movies = []
            for movie_data in data:
                movie = Movie(**movie_data)
                movie.staging_dir = f"./{projects_folder}/{movie_data.get('title')}"

                print(colored(f"[{movie.title}]: unpacking...", "blue"))

                if os.path.exists(f"{movie.staging_dir}/{movie.title}.mp4"):
                    print(colored(f"movie {movie.title} exists. skipping...", "blue"))
                    print(colored(f"to rebuild the movie, delete {movie.staging_dir}/{movie_data.get('title')}.mp4 and try again","blue"))
                    continue

                if not os.path.exists(movie.staging_dir):
                    os.mkdir(movie.staging_dir)

                scenes_data = movie_data.get("scenes", [])
                scenes = []

                for scene_data in scenes_data:
                    scene = Scene(**scene_data)

                    clips_data = scene_data.get("clips", [])
                    clips = []

                    for clip_data in clips_data:
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

                            if clip.video:
                                if scene.arrangement == "horizontal":
                                    clip.video.resize((1920 // len(clips_data), 1080))
                                elif scene.arrangement == "vertical":
                                    clip.video.resize((1080, 1920 // len(clips_data)))
                                else:
                                    if clip.size is not None:
                                        clip.video.resize(clip.size)
                                    else:
                                        print(colored(f"[{movie.title}]: For the arrangement {scene.arrangement}, a size is required"))

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

                        clips.append(clip)

                    scene.clips = clips
                    scene.audio = CompositeAudioClip([scene.clips[x].audio for x in scene.use_audio])
                    scenes.append(scene)

                movie.scenes = scenes
                movies.append(movie)

                print(colored(f"[{movie.title}]: finished unpacking movie!", "green"))
            return movies

    except FileNotFoundError:
        print(colored(f"Error: File {filepath} not found", "red"))
        sys.exit(1)
    except json.JSONDecodeError:
        print(colored(f"Error File {filepath} does not contain valid json", "red"))
        sys.exit(1)
