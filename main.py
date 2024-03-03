import os
import threading
from natsort import natsorted
from moviepy.editor import *
from termcolor import colored

from formats.utils.model import Clip, Scene, movies_from_json
from formats.utils.scene_builder import make_stacked_scene, make_montage_scene

from subtitle.subtitle import create_subtitles

PRODUCTS_DIR = "output"

def write(clip: CompositeVideoClip | VideoClip | VideoFileClip, out, temp_audio=None, threads=8):
    # Need to set a temp_audiofile or else it will dump all the audios to the directory from where this is running.
    # Thats bad because we do an incremental write for each scene (0.mp3, 1.mp3) which means overlap
    # Overlap is bad because moviepy wont make another temp audio file if the 1.mp3 from a previous movie exists so you get
    # weird audio bugs if you don't do this.

    clip.write_videofile(
        out,
        threads=threads,
        temp_audiofile=temp_audio,
        codec="libx264",
    )

if __name__ == "__main__":
    # main()
    scene_threads = []
    movie_threads = []

    movies = movies_from_json("./2-mar-24.json")
    for movie in movies:
        for i, scene in enumerate(movie.scenes):
            
            scene.temp_file = f"{movie.temp_file}/{i}.mp4"

            if os.path.exists(scene.temp_file):
                print(colored(f"scene {scene.temp_file} exists...", "blue"))
                print(colored(f"To recreate, delete {scene.temp_file}.mp4 and try again", "blue"))
                continue

            for clip in scene.clips:
                if clip.subtitle is not None:
                    clip.video = CompositeVideoClip([clip.video, clip.subtitle])

            if scene.arrangement == "stack":
                built_scene = make_stacked_scene(scene.clips)
            elif scene.arrangement == "vertical":
                pass
            elif scene.arrangement == "horizontal":
                pass
            elif scene.arrangement == "pip":
                pass
            elif scene.arrangement == "montage":
                built_scene = make_montage_scene(scene.clips)
            else:
                print(colored("unrecognized scene arrangement", "red"))
                continue

            duration = min([c.video.duration for c in scene.clips if c.video is not None and c.video.duration is not None and c.video.duration > 0])
            duration = min([duration, scene.audio.duration])

            built_scene = built_scene.resize(movie.final_size).set_duration(duration).set_audio(scene.audio).set_fps(30)

            scene_threads.append(
                threading.Thread(
                    target=write,
                    args=(
                        built_scene,
                        f"{scene.temp_file}",
                        f"{movie.temp_file}/{i}.mp3",
                        8,
                    ),
                )
            )

    for thread in scene_threads:
        thread.start()

    for thread in scene_threads:
        thread.join()

    for movie in movies:
        scene_clips = [VideoFileClip(scene.temp_file) for scene in movie.scenes]
        if len(scene_clips) > 0:
            movie_file = f"./{PRODUCTS_DIR}/{movie.title}/{movie.title}-subs.mp4" if movie.has_subtitles else f"./{PRODUCTS_DIR}/{movie.title}/{movie.title}.mp4"
            final_movie = concatenate_videoclips(scene_clips)
            movie_threads.append(
                threading.Thread(target=write, args=(final_movie, movie_file, None, 8, ))
            )

    for thread in movie_threads:
        thread.start()

    for thread in movie_threads:
        thread.join()

    subtitle_threads = []
    for movie in movies:
        if os.path.exists(f"./output/{movie.title}/{movie.title}.mp4"):
            print(colored(f"subtitled movie ./output/{movie.title}/{movie.title}.mp4 exists...", "blue"))
            print(colored(f"To recreate, delete ./output/{movie.title}/{movie.title}.mp4 and try again", "blue"))
            continue

        if movie.has_subtitles:
            movie_folder = f"./output/{movie.title}"
            print(colored(f"creating subtitles for {movie.title}", "green"))
            subtitle_clip = create_subtitles(f"{movie_folder}/subtitles", f"{movie_folder}/{movie.title}-subs.mp4")
            movie_clip = VideoFileClip(f"{movie_folder}/{movie.title}-subs.mp4")
            subtitled_movie = CompositeVideoClip([
                movie_clip, 
                subtitle_clip.set_duration(movie_clip.duration)
            ])
            subtitled_movie.set_fps(movie_clip.fps)

            subtitle_threads.append(
                threading.Thread(
                    target=write,
                    args=(subtitled_movie, f"{movie_folder}/{movie.title}.mp4", None, 8, ),
                )
            )

    for thread in subtitle_threads:
        thread.start()

    for thread in subtitle_threads:
        thread.join()
