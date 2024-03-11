from moviepy.editor import *
from moviepy.video.fx.all import crop
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout

V_SIZE = (1080, 1920)
H_SIZE = (1920, 1080)


def create_caption(text, font, fontsize, color, size, pos=("center", 300), has_bg=False):
    """Creates a caption clip for writing text on a video"""
    overlay = TextClip(
        text,
        font=font,
        fontsize=fontsize,
        color=color,
        stroke_width=4,
        method="caption",
        size=size if size is not None else (0.9 * 1080, 0),
    )
    if has_bg:
        im_width, im_height = overlay.size
        if color == "white":
            color_clip = ColorClip(
                size=(int(im_width * 1.1), im_height), color=(0, 0, 0)
            ).set_opacity(0.6)
        else:
            color_clip = ColorClip(
                size=(int(im_width * 1.1), im_height), color=(255, 255, 255)
            )
        return CompositeVideoClip([color_clip, overlay]).set_pos(pos)

    return overlay.set_pos(pos)





def _normalize_durations(clip_a, clip_b, minimize=True, min_duration=10):
    """
    Determins the length to equalize two clips to.
    If minimize=True - sets both clips to the shorter clip, else sets both clips to the longer clip
    min_duration specified if neither clip has a duration (likely true with image clips)
    """

    if clip_a.duration is None and clip_b.duration is None:
        duration = min_duration
    if clip_a.duration is None and clip_b.duration is not None:
        clip_a.duration = clip_b.duration
    if clip_a.duration is not None and clip_b.duration is None:
        clip_b.duration = clip_a.duration

    if minimize:
        duration = min(clip_a.duration, clip_b.duration)
    else:
        duration = max(clip_a.duration, clip_b.duration)

    return (clip_a.subclip(0, duration), clip_b.subclip(0, duration))





def _position(clip, location=(0, 0), anchor=("left", "top"), border_thickness=0, border_color=(255, 255, 255)):
    """
    Positions a clip by anchoring it relative to the final movie 
    and offsetting it left and down by the given location. 
    optionally applies a border.
    """

    return clip.set_position(
        anchor
    ).margin(
        border_thickness,
        border_color
    ).margin(
        top=location[1] - 2 * border_thickness,
        left=location[0] - 2 * border_thickness,
        opacity=0
    )





def remove_greenscreen(clip: VideoClip):
    """Removes the greenscreen on greenscreen videos"""

    return clip.fx(vfx.mask_color, color=[0, 255, 0], thr=120, s=7)





def remove_bottom_third(clip, width=1080):
    """Crops the bottom third out of a video"""

    return clip.crop(
        x1=0, 
        y1=0, 
        x2=clip.size[0], 
        y2=int(clip.size[1] * 2 / 3)
    ).resize((width, clip.size[1]))





def stack(fg_clip, bg_clip, location=(0, 0), anchor=("left", "top"), minimize=True):
    """
    Stacks a foreground clip onto a background clip in a 
    position described by an anchor and a location left and down from that anchor point. 
    Also normalizes the durations
    """

    bg, fg = _normalize_durations(bg_clip, fg_clip, minimize)
    fg = _position(fg, location, anchor)

    return CompositeVideoClip([bg, fg])





def v_arrange(top_clip, bottom_clip, minimize=True, min_duration=10):
    """
    Arranges clips top and bottom and sets duration to the shorter clip
    if neither clip has a duration, sets output clip to specified duration.
    Also normalizes the durations
    """

    top_clip, bottom_clip = _normalize_durations(top_clip, bottom_clip, minimize, min_duration)
    return clips_array([[top_clip], [bottom_clip]]).resize(V_SIZE)





def h_arrange(left_clip, right_clip, minimize=True, min_duration=10):
    """
    Arranges clips side by side and sets duration to the shorter clip
    if neither clip has a duration, sets output clip to specified duration.
    Also normalizes the durations
    """

    left_clip, right_clip = _normalize_durations(left_clip, right_clip, minimize, min_duration)
    return clips_array([[left_clip, right_clip]]).resize(H_SIZE)





def image_montage(image_clips, duration, fade_duration=0, img_size=(1920, 1080)):
    """Gives each clip an equal amount of screen time up to the specified duration"""

    clips = []
    if fade_duration > 0:
        for i, clip in enumerate(image_clips):
            clip = clip.set_duration((duration + fade_duration * 2) // len(image_montage))
            if i > 0:
                clip = clip.fx(fadein, fade_duration)
            else:
                clip = clip.fx(fadeout, fade_duration)
            clips.append(clip.set_start(i * (duration + fade_duration)).resize(img_size))
    else:
        clips = [clip.set_duration(duration/ len(image_clips)).resize(img_size) for clip in image_clips]
    
    return concatenate_videoclips(clips)





def pip_arrange(pip_clip, clip, pip_location=(0, 0), pip_anchor=("left", "top"), minimize=True, border_thickness=0, border_color=(255, 255, 255)):
    """
    Places a picture in picture clip somewhere in a larger clip using the _position function. 
    Also normalizes the durations.
    """
    pip, clip = _normalize_durations(pip_clip, clip, minimize)
    pc = _position(pip, pip_location, pip_anchor, border_thickness, border_color)

    return CompositeVideoClip([clip, pc])

