import os
import threading
from moviepy.editor import *
from termcolor import colored

from formats.utils.model import movies_from_json
from formats.utils.scene_builder import arrange_snippets

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

            for snippet in scene.snippets:
                if snippet.subtitle is not None:
                    snippet.video = CompositeVideoClip([snippet.video, snippet.subtitle])

            built_scene = arrange_snippets(scene.snippets, scene.arrangement)

            if built_scene == None:
                continue

            snippet_durations = [
                snippet.video.duration
                for snippet in scene.snippets
                if (
                    snippet.video is not None
                    and snippet.video.duration is not None
                    and snippet.video.duration > 0
                )
                or (
                    snippet.video is not None
                    and snippet.audio is not None
                    and snippet.audio.duration is not None
                    and snippet.audio.duration > 0
                )
            ]

            if len(snippet_durations) > 0:
                duration = min(snippet_durations)
                duration = min([duration, scene.audio.duration])

            if built_scene:
                scene.video_clip = (
                    built_scene.resize(movie.final_size)
                    .set_audio(scene.audio)
                    .set_duration(duration)
                    .set_fps(30)
                )

    for movie in movies:
        scene_snippets = [scene.video_clip for scene in movie.scenes if scene.video_clip]
        if len(scene_snippets) > 0:
            final_movie = concatenate_videoclips(scene_snippets)
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
