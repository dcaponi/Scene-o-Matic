import os
import threading
from moviepy.editor import *
from termcolor import colored

from model.model import movies_from_json
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
    
    movie_threads = [
        threading.Thread(
            target=write,
            args=(movie.video_clip, movie.staging_dir, movie.title, movie.has_subtitles, 8, ),
        ) 
    for movie in movies if movie.video_clip]


    for thread in movie_threads:
        thread.start()

    for thread in movie_threads:
        thread.join()
