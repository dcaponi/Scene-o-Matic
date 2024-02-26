from dataclasses import dataclass, field
import json
import os
import sys
from typing import List, Optional
from moviepy.editor import CompositeAudioClip, AudioFileClip, VideoFileClip

from formats.utils.edit_utils import create_caption

@dataclass
class Clip:
    asset: str
    video: VideoFileClip = None
    audio: AudioFileClip = None
    has_greenscreen: bool = False
    prompt: str = None
    script: str = None
    host_img: str = None
    type: Optional[str] = None
    fade_duration: int = 0
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
    publish_destinations: List[str] = field(default_factory=lambda: [])
    final_size: tuple[int, int] = field(default_factory=lambda: (1080, 1920))
    duration: int = 0

def movies_from_json(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            movies = []

            for movie_data in data:
                scenes_data = movie_data.get("scenes", [])
                scenes = []

                for scene_data in scenes_data:
                    clips_data = scene_data.get("clips", [])
                    clips = []

                    for clip_data in clips_data:
                        clip = Clip(**clip_data)
                        if os.path.exists(clip.asset):
                            if clip.asset.endswith(('jpg', 'jpeg', 'png', 'gif')):
                                clip.video = VideoFileClip(clip.asset).set_duration(0).resize(clip.size)
                            elif clip.asset.endswith(('mp3', 'wav', 'ogg')):
                                clip.audio = AudioFileClip(clip.asset)
                            elif clip.asset.endswith(('mp4', 'avi', 'mkv')):
                                clip.video = VideoFileClip(clip.asset).resize(clip.size)
                                clip.audio = clip.video.audio
                            elif clip.asset.endswith(('11l', 'tt', 'whisper')): # asset-name.tts -> go make a .mp3 using a tts from asset script
                                # clip.audio = 11labs_tts(clip.script)
                                pass
                            elif clip.asset.endswith(('d-id')): # asset-name.d-id -> go make a .mp4 using a talking head like d-id from asset script
                                # clip.video = did_character(clip.script, clip.host_img)
                                pass
                            elif clip.asset.endswith(('sora')): # asset-name.sora -> go make a .mp4 from sora using a prompt
                                # clip.video = sora_clip(prompt)
                                pass
                        else:
                            clip.video = create_caption(
                                text=clip.asset,
                                pos=clip.anchor,
                                font="Courier-New-Bold",
                                fontsize=70,
                                color="white",
                                has_bg=True,
                            )
                        clips.append(clip)

                    scene = Scene(**scene_data)
                    scene.clips = clips
                    scene.audio = CompositeAudioClip([scene.clips[x].audio for x in scene.use_audio])
                    scenes.append(scene)

                movie = Movie(**movie_data)
                movie.scenes = scenes
                movies.append(movie)
            return movies

    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error File {filepath} does not contain valid json")
        sys.exit(1)
