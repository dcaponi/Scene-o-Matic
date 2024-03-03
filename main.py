import os
import threading
from natsort import natsorted
from moviepy.editor import *
from termcolor import colored

from formats.utils.model import movies_from_json
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
        if not os.path.exists(f"{PRODUCTS_DIR}/{movie.title}/{movie.title}.mp4"):
            for i, scene in enumerate(movie.scenes):
                scene.temp_file = f"{movie.temp_file}/{i}.mp4"

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

    finished_movies = [movie.title for movie in movies]
    for d in os.listdir(f"./{PRODUCTS_DIR}"):
        built_clips = [
            VideoFileClip(f"./{PRODUCTS_DIR}/{d}/{built_scene}")
            for built_scene in natsorted(os.listdir(f"./{PRODUCTS_DIR}/{d}"))
            if built_scene.endswith(".mp4") and built_scene not in finished_movies
        ]
        if len(built_clips) > 0:
            final_movie = concatenate_videoclips(built_clips)
            movie_threads.append(
                threading.Thread(target=write, args=(final_movie, f"./{PRODUCTS_DIR}/{d}/{d}.mp4", None, 8, ))
            )

        # for d in os.listdir(f"./{PRODUCTS_DIR}"):
        #     [os.remove(f"./{PRODUCTS_DIR}/{d}/{built_scene}") for built_scene in os.listdir(f"./{PRODUCTS_DIR}/{d}") if built_scene.endswith("mp4") or built_scene.endswith("mp3")]

    for thread in movie_threads:
        thread.start()

    for thread in movie_threads:
        thread.join()

    subtitle_threads = []
    for movie in movies:
        if os.path.exists(f"{movie_folder}/{movie.title}-subs.mp4"):
            print(colored(f"subtitled movie {movie_folder}/{movie.title}-subs.mp4 exists...", "blue"))
            print(f"To recreate, delete {movie_folder}/{movie.title}-subs.mp4 and try again", "blue")
            continue

        if movie.has_subtitles:
            movie_folder = f"./output/{movie.title}"
            print(colored(f"creating subtitles for {movie.title}", "blue"))
            subtitle_clip = create_subtitles(f"{movie_folder}/subtitles", f"{movie_folder}/{movie.title}.mp4")
            movie_clip = VideoFileClip(f"{movie_folder}/{movie.title}.mp4")
            subtitled_movie = CompositeVideoClip([
                movie_clip, 
                subtitle_clip.set_duration(movie_clip.duration)
            ])
            subtitled_movie.set_fps(movie_clip.fps)

            subtitle_threads.append(
                threading.Thread(
                    target=write,
                    args=(subtitled_movie, f"{movie_folder}/{movie.title}-subs.mp4", None, 8, ),
                )
            )

    for thread in subtitle_threads:
        thread.start()

    for thread in subtitle_threads:
        thread.join()
