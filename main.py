import os
import threading
from natsort import natsorted
from moviepy.editor import *

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
    existing_titles = [title.split(".")[0] for title in os.listdir(f"./{PRODUCTS_DIR}")]

    movies = movies_from_json("./manifest.json")
    for movie in movies:
        if movie.title not in existing_titles:
            for i, scene in enumerate(movie.scenes):
                scene.temp_file = f"{movie.temp_file}/{i}.mp4"

                for clip in scene.clips:
                    if clip.subtitle is not None:
                        clip.video = CompositeVideoClip([clip.video, clip.subtitle])

                if scene.arrangement == "stack":
                    built_scene = make_stacked_scene(scene.clips)
                if scene.arrangement == "vertical":
                    pass
                if scene.arrangement == "horizontal":
                    pass
                if scene.arrangement == "pip":
                    pass
                if scene.arrangement == "montage":
                    built_scene = make_montage_scene(scene.clips)

                duration = min([c.video.duration for c in scene.clips if c.video is not None and c.video.duration > 0])
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

    for d in os.listdir(f"./{PRODUCTS_DIR}"):
        built_clips = [
            VideoFileClip(f"./{PRODUCTS_DIR}/{d}/{built_scene}")
            for built_scene in natsorted(os.listdir(f"./{PRODUCTS_DIR}/{d}"))
            if built_scene.endswith(".mp4")
        ]
        if len(built_clips) > 0:
            final_movie = concatenate_videoclips(built_clips)
            movie_threads.append(
                threading.Thread(target=write, args=(final_movie, f"./{PRODUCTS_DIR}/{d}/{d}.mp4", None, 8, ))
            )

        [os.remove(f"./{PRODUCTS_DIR}/{d}/{built_scene}") for built_scene in os.listdir(f"./{PRODUCTS_DIR}/{d}")]

    for thread in movie_threads:
        thread.start()

    for thread in movie_threads:
        thread.join()

    subtitle_threads = []
    for movie in movies:
        if movie.has_subtitles:
            movie_folder = f"{movie.temp_file}/{movie.title}"
            subtitle_clip = create_subtitles(movie_folder)
            movie_clip = VideoFileClip(f"{movie_folder}.mp4")
            subtitled_movie = CompositeVideoClip([
                movie_clip, 
                subtitle_clip.set_duration(movie_clip.duration)
            ])
            subtitled_movie.set_fps(movie_clip.fps)

            subtitle_threads.append(
                threading.Thread(
                    target=write,
                    args=(subtitled_movie, f"{movie_folder}-subs.mp4", None, 8, ),
                )
            )

            os.remove(f"{movie_folder}.srt")
            os.remove(f"{movie_folder}.mp4")

    for thread in subtitle_threads:
        thread.start()

    for thread in subtitle_threads:
        thread.join()
