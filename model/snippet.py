from dataclasses import dataclass, field
from typing import Optional

from moviepy.editor import VideoFileClip, VideoClip, AudioFileClip
from termcolor import colored

from formats.utils.edit_utils import create_caption, remove_greenscreen
from generative.generative_asset import generative_image, generative_tts, generative_video


@dataclass
class VideoSpec:
    asset: str
    has_greenscreen: bool = False
    duration: int = None
    size: Optional[tuple[int, int]] = None
    location: tuple[int, int] = field(default_factory=lambda: (0, 0))
    anchor: tuple[str, str] = field(default_factory=lambda: ("left", "top"))
    clip: VideoFileClip = None

    def unpack(self, staging_dir):
        if self.asset.endswith(("jpg", "jpeg", "png", "gif")):
            self.clip = VideoFileClip(self.asset).set_duration(self.duration if self.duration else 0)

        elif self.asset.endswith(("mp4", "avi", "mkv")):
            self.clip = VideoFileClip(self.asset)
            if self.duration:
                self.clip = self.clip.set_duration(self.duration)

        elif self.asset.endswith(("d-id")):
            # asset-name.d-id -> go make a .mp4 using a talking head like d-id from asset script
            # clip.video = did_character(clip.script, clip.host_img) (maybe host_img could also end in .sd or .mj and it would make you a host)
            pass

        elif self.asset.endswith(("sora", "rand")):
            self.clip = generative_video(staging_dir, self)

        elif self.asset.endswith(("mj", "sd", "dall-e", "giphy")):
            self.clip = generative_image(staging_dir, self)

        if self.clip is not None and self.size is not None:
            self.clip = self.clip.resize(self.size)

        if self.has_greenscreen:
            self.clip = remove_greenscreen(self.clip)

        self.duration = self.clip.duration

        return self


@dataclass
class AudioSpec:
    asset: str
    voice: str = None
    script: str = None
    duration: int = None
    clip: AudioFileClip = None

    def unpack(self, staging_dir: str):
        if self.asset.endswith(("mp3", "wav", "ogg")):
            self.clip = AudioFileClip(self.asset)

        elif self.asset.endswith(("xi_labs", "tiktok", "whisper")):
            self.clip = generative_tts(staging_dir, self)

        else:
            print(colored(f"[{staging_dir.split('/')[-1]}]: no audio detected", "yellow"))

        self.duration = self.clip.duration

        return self


@dataclass
class CaptionSpec:
    asset: str
    has_background: bool = True
    size: Optional[tuple[int, int]] = None
    location: tuple[int, int] = field(default_factory=lambda: (0, 0))
    anchor: tuple[str, str] = field(default_factory=lambda: ("left", "top"))
    clip: VideoClip = None

    def unpack(self):
        self.clip = create_caption(
            text=self.asset,
            font="Courier-New-Bold",
            fontsize=70,
            color="white",
            size=self.size,
            pos=self.anchor,
            has_bg=self.has_background,
        )

        return self


@dataclass
class Snippet:
    video: Optional[VideoSpec] = None
    audio: Optional[AudioSpec] = None
    caption: Optional[CaptionSpec] = None

    def unpack(self, staging_dir: str):

        if self.audio:
            self.audio = AudioSpec(**self.audio).unpack(staging_dir)

        if self.video:
            self.video = VideoSpec(**self.video)
            if self.video.duration is None and self.audio:
                self.video.duration = self.audio.duration

            self.video.unpack(staging_dir)

            if self.audio:
                self.video.clip.set_audio(self.audio.clip)
            else:
                self.audio = AudioSpec(asset=self.video.asset, clip=self.video.clip.audio)

        if self.caption:
            self.caption = CaptionSpec(**self.caption).unpack()


        return self
