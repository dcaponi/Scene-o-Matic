from moviepy.editor import concatenate_videoclips
from formats.utils.edit_utils import remove_greenscreen, stack, h_arrange, v_arrange
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

def make_horizontal_arranged_scene(clips: list[Clip]):
    built_scene = None
    for clip in clips:
        if clip.video:
            if clip.has_greenscreen:
                clip.video = remove_greenscreen(clip.video)
            if built_scene == None:
                built_scene = clip.video
            else:
                built_scene = h_arrange(built_scene, clip.video)

    return built_scene


def make_vertical_arranged_scene(clips: list[Clip]):
    built_scene = None
    for clip in clips:
        if clip.video:
            if clip.has_greenscreen:
                clip.video = remove_greenscreen(clip.video)
            if built_scene == None:
                built_scene = clip.video
            else:
                built_scene = v_arrange(built_scene, clip.video)

    return built_scene
