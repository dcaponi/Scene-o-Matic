from __future__ import annotations
from dataclasses import dataclass, field
import json
import os
import sys
from typing import List, Optional
from moviepy.editor import CompositeAudioClip, AudioFileClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from termcolor import colored
from generative.generative_asset import generative_tts, generative_video
from subtitle.subtitle import create_subtitles
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
    host_img: str = None
    type: Optional[str] = None
    duration: int = None
    size: Optional[tuple[int, int]] = None
    location: tuple[int, int] = field(default_factory = lambda:(0, 0))
    anchor: tuple[str, str] = field(default_factory = lambda:("top", "left"))


@dataclass
class Scene:
    clips: List[Clip]
    temp_file: str = ""
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
    temp_file: str = None


def movies_from_json(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            movies = []
            for movie_data in data:
                staging_dir = f"./output/{movie_data.get('title')}"
                try:
                    os.mkdir(staging_dir)
                except FileExistsError:
                    print(colored(f"{staging_dir} exists!"))

                scenes_data = movie_data.get("scenes", [])
                scenes = []

                for scene_data in scenes_data:
                    clips_data = scene_data.get("clips", [])
                    clips = []

                    for i, clip_data in enumerate(clips_data):
                        clip = Clip(**clip_data)
                        if clip.override_audio:
                            print(colored("detected audio override", "blue"))
                            audio_override = Clip(**clip.override_audio)
                            if audio_override.asset.endswith(('mp3', 'wav', 'ogg')):
                                print(colored("assigning audio...", "blue"))
                                clip.audio = AudioFileClip(audio_override.asset)
                            if audio_override.asset.endswith(("11l", "tiktok", "whisper")):
                                print(colored("creating audio from tts...", "blue"))
                                clip.audio = generative_tts(staging_dir, audio_override)
                            print(colored("overide audio complete!", "blue"))

                        if os.path.exists(clip.asset):
                            print(colored("creating moviepy objects...", "blue"))
                            if clip.asset.endswith(('jpg', 'jpeg', 'png', 'gif')):
                                clip.video = VideoFileClip(clip.asset).set_duration(clip.duration).resize(clip.size)
                            elif clip.asset.endswith(('mp3', 'wav', 'ogg')):
                                clip.audio = AudioFileClip(clip.asset)
                            elif clip.asset.endswith(('mp4', 'avi', 'mkv')):
                                clip.video = VideoFileClip(clip.asset).resize(clip.size)
                                if clip.audio is None:
                                    clip.audio = clip.video.audio

                        else:
                            print(colored("detected generative asset...", "blue"))
                            if clip.asset.endswith(('11l', 'tiktok', 'whisper')): # asset-name.tts -> go make a .mp3 using a tts from asset script
                                print(colored("generating audio from tts...", "blue"))
                                clip.audio = generative_tts(staging_dir, clip)
                            elif clip.asset.endswith(('d-id')): # asset-name.d-id -> go make a .mp4 using a talking head like d-id from asset script
                                # clip.video = did_character(clip.script, clip.host_img) (maybe host_img could also end in .sd or .mj and it would make you a host)
                                pass
                            elif clip.asset.endswith(('sora', 'rand')): # asset-name.sora -> go make a .mp4 from sora using a prompt
                                print(colored("generating video from prompt...", "blue"))
                                clip.video = generative_video(staging_dir, clip)
                            elif clip.asset.endswith(('mj', 'sd', 'dall-e')): # asset-name.dall-e -> go make an image using a prompt
                                # clip.video = midjourney(prompt)
                                pass

                            else:
                                print(colored("generating caption...", "blue"))
                                clip.video = create_caption(
                                    text=clip.asset,
                                    font="Courier-New-Bold",
                                    fontsize=70,
                                    color="white",
                                    size=clip.size,
                                    pos=clip.anchor,
                                    has_bg=clip.has_background,
                                )

                        clips.append(clip)

                    scene = Scene(**scene_data)
                    scene.clips = clips
                    scene.audio = CompositeAudioClip([scene.clips[x].audio for x in scene.use_audio])
                    scenes.append(scene)

                movie = Movie(**movie_data)
                movie.temp_file = staging_dir
                movie.scenes = scenes
                movies.append(movie)
            return movies

    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error File {filepath} does not contain valid json")
        sys.exit(1)
