import os
import threading
from natsort import natsorted
from moviepy.editor import *

from formats.utils.model import movies_from_json
from formats.utils.scene_builder import make_stacked_scene

PRODUCTS_DIR = "output"

# def main():

# topics = [
#     (
#         "interviews",
#         "Big tech owns stock in all the major players in the coding interview prep industry. They proliferate these insane 12 round interviews so people will buy the prep courses which lines the pockets of these big shot executives who perpetuate the industry.",
#         "cloud office code",
#     ),
#     (
#         "rto",
#         "Tech giants need everyone to return to the office so everyone can resume buying $20 salads at restaurants which the executives secretly own. They also want you stuck in traffic so you don't have time to build competing products.",
#         "meetings corporations microsoft",
#     )
# ]

# [make_movie(t, bg, PRODUCTS_DIR, title) for title, t, bg in topics]

def write(clip: VideoFileClip, out, temp_audio=None, threads=8):
    # Need to set a temp_audiofile or else it will dump all the audios to the directory from where this is running.
    # Thats bad because we do an incremental write for each scene (0.mp3, 1.mp3) which means overlap
    # Overlap is bad because moviepy wont make another temp audio file if the 1.mp3 from a previous movie exists so you get
    # weird audio bugs if you don't do this.
    clip.write_videofile(out, threads=threads, temp_audiofile=temp_audio)


if __name__ == "__main__":
    # main()
    scene_threads = []
    movie_threads = []
    existing_titles = [title.split(".")[0] for title in os.listdir(f"./{PRODUCTS_DIR}")]

    movies = movies_from_json("./manifest.json")
    for movie in movies:
        if movie.title not in existing_titles:
            outdir = f"./{PRODUCTS_DIR}/{movie.title}"
            os.mkdir(outdir)

            for i, scene in enumerate(movie.scenes):
                scene.temp_file = f"{outdir}/{i}.mp4"

                if scene.arrangement == "stack":
                    built_scene = make_stacked_scene(scene.clips)
                if scene.arrangement == "vertical":
                    pass
                if scene.arrangement == "horizontal":
                    pass
                if scene.arrangement == "pip":
                    pass
                if scene.arrangement == "montage":
                    pass

                duration = min([c.video.duration for c in scene.clips if c.video is not None and c.video.duration > 0])
                duration = min([duration, scene.audio.duration])

                built_scene = built_scene.resize(movie.final_size).set_audio(scene.audio).set_duration(duration)
                scene_threads.append(
                    threading.Thread(target=write, args=(built_scene, f"{scene.temp_file}", f"{outdir}/{i}.mp3", 8, ))
                )

    for thread in scene_threads:
        thread.start()

    for thread in scene_threads:
        thread.join()

    for d in os.listdir(f"./{PRODUCTS_DIR}"):
        final_movie = concatenate_videoclips([VideoFileClip(f"./{PRODUCTS_DIR}/{d}/{built_scene}") for built_scene in natsorted(os.listdir(f"./{PRODUCTS_DIR}/{d}"))])
        movie_threads.append(
            threading.Thread(target=write, args=(final_movie, f"./{PRODUCTS_DIR}/{d}/{d}.mp4", None, 8, ))
        )

        [os.remove(f"./{PRODUCTS_DIR}/{d}/{built_scene}") for built_scene in os.listdir(f"./{PRODUCTS_DIR}/{d}")]

    for thread in movie_threads:
        thread.start()

    for thread in movie_threads:
        thread.join()
