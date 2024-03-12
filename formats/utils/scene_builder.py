from moviepy.editor import concatenate_videoclips
from termcolor import colored
from formats.utils.edit_utils import stack, h_arrange, v_arrange
from model.snippet import Snippet
from moviepy.editor import VideoClip

def arrange_snippets(snippets: list[Snippet], arrangement: str):
    """
    arranges snippets according to the specified arrangement
    montage - plays snippets consecutiviely from first to last
    stack - places snippets back to front toward viewer
    vertical/horizontal - places snippets left to right / top to bottom
    pip - places snippets in background, then picture in picture at specified location
    """

    if arrangement == "montage":
        return concatenate_videoclips([snippet.video for snippet in snippets if snippet.video])

    built_scene: VideoClip = None
    for snippet in snippets:
        if snippet.video:
            if built_scene == None:
                built_scene = snippet.video.clip
            else:
                if arrangement == "stack":
                    built_scene = stack(
                        snippet.video.clip, 
                        built_scene, 
                        snippet.video.location, 
                        snippet.video.anchor, 
                        False
                    )
                elif arrangement == "vertical":
                    built_scene = v_arrange(built_scene, snippet.video.clip)
                    built_scene = built_scene.resize((1080, 1920))
                elif arrangement == "horizontal":
                    built_scene = h_arrange(built_scene, snippet.video.clip)
                    built_scene = built_scene.resize((1920, 1080))
                elif arrangement == "pip":
                    pass
                else:
                    print(colored("unrecognized scene arrangement", "red"))
                    return built_scene

    for snippet in snippets:
        if snippet.caption:

            built_scene = stack(
                snippet.caption.clip, 
                built_scene, 
                snippet.caption.location, 
                snippet.caption.anchor, 
                False
            )
    return built_scene
