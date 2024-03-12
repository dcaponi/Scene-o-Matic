import os
from typing import List
from dataclasses import dataclass, field

from termcolor import colored

from model.scene import Scene

from moviepy.editor import VideoClip, concatenate_videoclips

@dataclass
class Movie:
    title: str
    scenes: List[Scene]
    video_clip: VideoClip = None
    has_subtitles: bool = False
    publish_destinations: List[str] = field(default_factory=lambda: [])
    final_size: tuple[int, int] = field(default_factory=lambda: (1080, 1920))
    staging_dir: str = None

    def unpack(self, projects_folder):
        self.staging_dir = f"./{projects_folder}/{self.title}"

        if os.path.exists(f"{self.staging_dir}/{self.title}.mp4"):
            print(colored(f"movie {self.title} exists. skipping...", "blue"))
            print(colored(f"to rebuild the movie, delete {self.staging_dir}/{self.title}.mp4 and try again","blue"))
            return self

        if not os.path.exists(self.staging_dir):
            os.mkdir(self.staging_dir)

        self.scenes = [Scene(**scene).unpack(self.staging_dir) for scene in self.scenes]

        for scene in self.scenes:
            if scene.video_clip:
                scene.video_clip = scene.video_clip.resize(self.final_size)

        scenes_to_splice = [scene.video_clip.resize(self.final_size) for scene in self.scenes if scene.video_clip]
        if len(scenes_to_splice) > 0:
            self.video_clip = concatenate_videoclips(scenes_to_splice)

        return self
