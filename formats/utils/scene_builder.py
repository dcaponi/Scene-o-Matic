from moviepy.editor import concatenate_videoclips
from termcolor import colored
from formats.utils.edit_utils import remove_greenscreen, stack, h_arrange, v_arrange
from formats.utils.model import Snippet
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
            if snippet.has_greenscreen:
                snippet.video = remove_greenscreen(snippet.video)
            if built_scene == None:
                built_scene = snippet.video
            else:
                if arrangement == "stack":
                    built_scene = stack(
                        snippet.video, 
                        built_scene, 
                        snippet.location, 
                        snippet.anchor, 
                        False
                    )
                elif arrangement == "vertical":
                    built_scene = v_arrange(built_scene, snippet.video)
                    built_scene = built_scene.resize((1080, 1920))
                elif arrangement == "horizontal":
                    built_scene = h_arrange(built_scene, snippet.video)
                    built_scene = built_scene.resize((1920, 1080))
                elif arrangement == "pip":
                    pass
                else:
                    print(colored("unrecognized scene arrangement", "red"))
                    return None

    return built_scene
