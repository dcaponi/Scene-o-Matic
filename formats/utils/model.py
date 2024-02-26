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
    type: Optional[str] = None
    fade_duration: int = 0
    size: Optional[tuple[int, int]] = None
    location: tuple[int, int] = field(default_factory = lambda:(0, 0))
    anchor: tuple[str, str] = field(default_factory = lambda:("top", "left"))

@dataclass
class Movie:
    title: str
    clips: List[Clip]
    audio: AudioFileClip = None
    arrangement: str = "vertical"
    publish_destinations: List[str] = field(default_factory=lambda: [])
    use_audio: List[int] = field(default_factory=lambda: [0])
    final_size: tuple[int, int] = field(default_factory=lambda: (1080, 1920))
    duration: int = 0

def movies_from_json(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            movies = []

            for movie_data in data:
                clips_data = movie_data.get("clips", [])
                clips = []

                for clip_data in clips_data:
                    clip = Clip(**clip_data)
                    clips.append(clip)

                movie = Movie(**movie_data)
                movie.clips = clips

                for clip in movie.clips:
                    if os.path.exists(clip.asset):
                        if clip.asset.endswith(('jpg', 'jpeg', 'png', 'gif')):
                            clip.video = VideoFileClip(clip.asset).set_duration(0).resize(clip.size)
                        elif clip.asset.endswith(('mp3', 'wav', 'ogg')):
                            clip.audio = AudioFileClip(clip.asset)
                        elif clip.asset.endswith(('mp4', 'avi', 'mkv')):
                            clip.video = VideoFileClip(clip.asset).resize(clip.size)
                            clip.audio = clip.video.audio
                    else:
                        clip.video = create_caption(
                            text=clip.asset,
                            pos=clip.anchor,
                            font="Courier-New-Bold",
                            fontsize=70,
                            color="white",
                            has_bg=True,
                        )
                
                audios = [movie.clips[x].audio for x in movie.use_audio]
                movie.audio = CompositeAudioClip(audios)
                movies.append(movie)
            return movies
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error File {filepath} does not contain valid json")
        sys.exit(1)
