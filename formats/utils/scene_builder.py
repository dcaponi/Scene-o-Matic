from moviepy.editor import concatenate_videoclips
from ast import List
from formats.utils.edit_utils import remove_greenscreen, stack
from formats.utils.model import Clip


def make_stacked_scene(clips: list[Clip]):
    built_scene = None
    for clip in clips:
        if clip.video:
            if clip.has_greenscreen:
                clip.video = remove_greenscreen(clip.video)
            if built_scene == None:
                built_scene = clip.video
            else:
                built_scene = stack(
                    clip.video, built_scene, clip.location, clip.anchor, False
                )
    return built_scene

def make_montage_scene(clips: list[Clip]):
    videos = []
    for clip in clips:
        if clip.video:
            videos.append(clip.video)
    return concatenate_videoclips(videos)