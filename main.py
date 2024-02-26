import os
import threading
from typing import List
# from uploaders.upload import Uploader
from moviepy.editor import *
from formats.narrated_compilation import make_movie

from formats.utils.edit_utils import remove_bottom_third, remove_greenscreen, stack
from formats.utils.model import movies_from_json

scream_clip = remove_greenscreen(VideoFileClip("./assets/videos/cat-scream.mp4")).resize((1080, 1920))
stare_clip = remove_greenscreen(VideoFileClip("./assets/videos/stare.mp4")).resize((1080, 1440))
shuffle_clip = remove_greenscreen(VideoFileClip("./assets/videos/cat-truffleshuffle.mp4")).resize((1080, 1440))
huh_clip = remove_greenscreen(VideoFileClip("./assets/videos/cat-huh.mp4")).resize((1080, 1920))
chippi_clip = remove_greenscreen(VideoFileClip("./assets/videos/chippi.mp4")).resize((1080, 1440))

wtf_clip = remove_greenscreen(VideoFileClip("./assets/videos/wtfitpos.mp4")).resize((1080, 1200))
zone_clip = remove_greenscreen(VideoFileClip("./assets/videos/cat-zone.mp4")).resize((1080, 1440))
snore_clip = remove_greenscreen(VideoFileClip("./assets/videos/cat-snore.mp4")).resize((1080, 1440))
# cena_clip = remove_greenscreen(VideoFileClip("./assets/videos/cupid.mp4"))
concern_clip = remove_greenscreen(VideoFileClip("./assets/videos/dog-concern.mp4")).resize((1080, 1440))
toothless_clip = remove_bottom_third(remove_greenscreen(VideoFileClip("./assets/videos/toothless.mp4")).resize((1080, 1920)))
crunch_clip = remove_greenscreen(VideoFileClip("./assets/videos/cat-crunch.mp4")).resize((1080, 1440))
driving_clip = remove_greenscreen(VideoFileClip("./assets/videos/cat-driving.mp4")).resize((1080, 1440))

PRODUCTS_DIR = "output"

# yt_uploader = Uploader('youtube')

# def main():
# to_publish = []
# for dirpath, dirnames, filenames in os.walk("./output"):
#     for dirname in dirnames:
#         subfolder_path = os.path.join(dirpath, dirname)
#         to_publish.append((dirname, f"{subfolder_path}/final.mp4"))

# for tp in to_publish:
#     yt_uploader.upload_video(
#         tp[1],
#         tp[0],
#         "cursed coding advice",
#         "22",
#         ["agile", "scrum", "coding", "faang", "softwareengineering"],
#     )
# yt_uploader.upload_video(
#     "./output/agile/final.mp4",
#     "agile",
#     "absurd agile advice",
#     "22",
#     ["agile", "scrum", "coding", "faang", "softwareengineering"],
# )

# ig_uploader = Uploader('instagram')
# ig_uploader.upload_video(
#     "./output/agile/final.mp4"
# )

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

def write(clip, out, threads=8):
    clip.write_videofile(out, threads=threads)

if __name__ == "__main__":
    # main()
    threads = []
    existing_titles = [title.split(".")[0] for title in os.listdir(f"./{PRODUCTS_DIR}")]

    movies = movies_from_json("./manifest.json")
    for movie in movies:
        if movie.title not in existing_titles:
            if movie.arrangement == "stack":
                final_clip = None
                for clip in movie.clips:
                    if clip.video:
                        if clip.has_greenscreen:
                            clip.video = remove_greenscreen(clip.video)
                        if final_clip == None:
                            final_clip = clip.video
                        else:
                            final_clip = stack(clip.video, final_clip, clip.location, clip.anchor, False)

                duration = min([c.video.duration for c in movie.clips if c.video is not None and c.video.duration > 0])

                final_clip = final_clip.resize(movie.final_size).set_audio(movie.audio).set_duration(duration)

                threads.append(
                    threading.Thread(target=write, args=(final_clip, f"./{PRODUCTS_DIR}/{movie.title}.mp4", 8, ))
                )

    # Starting each thread
    for thread in threads:
        thread.start()

    # Optionally, wait for all threads to complete
    for thread in threads:
        thread.join()
