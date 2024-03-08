from moviepy.editor import concatenate_videoclips
from termcolor import colored
from formats.utils.edit_utils import remove_greenscreen, stack, h_arrange, v_arrange
from formats.utils.model import Clip

def arrange_clips(clips: list[Clip], arrangement: str):
    """
    arranges clips according to the specified arrangement
    montage - plays clips consecutiviely from first to last
    stack - places clips back to front toward viewer
    vertical/horizontal - places clips left to right / top to bottom
    pip - places clips in background, then picture in picture at specified location
    """

    if arrangement == "montage":
        return concatenate_videoclips([clip.video for clip in clips if clip.video])

    built_scene = None
    for clip in clips:
        if clip.video:
            if clip.has_greenscreen:
                clip.video = remove_greenscreen(clip.video)
            if built_scene == None:
                built_scene = clip.video
            else:
                if arrangement == "stack":
                    built_scene = stack(
                        clip.video, 
                        built_scene, 
                        clip.location, 
                        clip.anchor, 
                        False
                    )
                elif arrangement == "vertical":
                    built_scene = v_arrange(built_scene, clip.video)
                    built_scene = built_scene.resize((1080, 1920))
                elif arrangement == "horizontal":
                    built_scene = h_arrange(built_scene, clip.video)
                    built_scene = built_scene.resize((1920, 1080))
                elif arrangement == "pip":
                    pass
                else:
                    print(colored("unrecognized scene arrangement", "red"))
                    return None

    return built_scene
