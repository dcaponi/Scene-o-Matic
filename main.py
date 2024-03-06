import os
import threading
from moviepy.editor import *
from termcolor import colored

from formats.utils.model import movies_from_json
from formats.utils.scene_builder import (
    make_stacked_scene,
    make_montage_scene,
    make_vertical_arranged_scene,
    make_horizontal_arranged_scene,
)

from subtitle.subtitle import create_subtitles

PRODUCTS_DIR = "output"


def write(
    clip: CompositeVideoClip | VideoClip | VideoFileClip,
    directory: str,
    filename: str,
    has_subtitles=True,
    threads=8,
):
    # Need to set a temp_audiofile or else it will dump all the audios to the directory from where this is running.
    # Thats bad because we do an incremental write for each scene (0.mp3, 1.mp3) which means overlap
    # Overlap is bad because moviepy wont make another temp audio file if the 1.mp3 from a previous movie exists so you get
    # weird audio bugs if you don't do this.
    clip.write_videofile(
        f"{directory}/{filename}.mp4",
        threads=threads,
        temp_audiofile=f"{directory}/{filename}.mp3",
        codec="libx264",
    )

    if has_subtitles:
        print(colored(f"creating subtitles...", "green"))
        subtitle_clip = create_subtitles(directory, f"{directory}/{filename}.mp4")

        subtitled_movie = CompositeVideoClip(
            [clip, subtitle_clip.set_duration(clip.duration)]
        )
        subtitled_movie.set_fps(clip.fps)

        subtitled_movie.write_videofile(
            f"{directory}/{filename}.mp4",
            threads=threads,
            temp_audiofile=f"{directory}/{filename}.mp3",
            codec="libx264",
        )


if __name__ == "__main__":
    movie_threads = []

    movies = movies_from_json("./manifest.json", PRODUCTS_DIR)
    for movie in movies:

        for i, scene in enumerate(movie.scenes):
            if os.path.exists(f"{movie.staging_dir}{i}.mp4"):
                print(colored(f"scene {movie.staging_dir}{i}.mp4 exists...", "blue"))
                print(colored(f"To recreate, delete {movie.staging_dir}{i}.mp4 and try again", "blue"))
                continue

            for clip in scene.clips:
                if clip.subtitle is not None:
                    clip.video = CompositeVideoClip([clip.video, clip.subtitle])

            if scene.arrangement == "stack":
                built_scene = make_stacked_scene(scene.clips)
            elif scene.arrangement == "vertical":
                built_scene = make_vertical_arranged_scene(scene.clips)
                if movie.final_size is not None:
                    built_scene.resize(movie.final_size)
                else:
                    built_scene.resize((1080, 1920))
            elif scene.arrangement == "horizontal":
                built_scene = make_horizontal_arranged_scene(scene.clips)
                if movie.final_size is not None:
                    built_scene.resize(movie.final_size)
                else:
                    built_scene.resize((1920, 1080))
            elif scene.arrangement == "pip":
                pass
            elif scene.arrangement == "montage":
                built_scene = make_montage_scene(scene.clips)
            else:
                print(colored("unrecognized scene arrangement", "red"))
                continue

            duration = min(
                [
                    c.video.duration
                    for c in scene.clips
                    if c.video is not None
                    and c.video.duration is not None
                    and c.video.duration > 0
                ]
            )
            duration = min([duration, scene.audio.duration])

            scene.video_clip = (
                built_scene.set_duration(duration).set_audio(scene.audio).set_fps(30)
            )

    for movie in movies:
        scene_clips = [scene.video_clip for scene in movie.scenes]
        if len(scene_clips) > 0:
            final_movie = concatenate_videoclips(scene_clips)
            movie_threads.append(
                threading.Thread(
                    target=write,
                    args=(final_movie, movie.staging_dir, movie.title, movie.has_subtitles, 8, ),
                )
            )

    for thread in movie_threads:
        thread.start()

    for thread in movie_threads:
        thread.join()
