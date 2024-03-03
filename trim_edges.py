from moviepy.editor import *
from moviepy.video.fx.all import crop
import os
import threading


def write(clip, outdir):
    clip.write_videofile(outdir, threads=8)


threads = []
for p in os.listdir("./assets/background/videos"):
  if p.endswith("mp4"):
    clip = VideoFileClip(f"./assets/background/videos/{p}")
    clip = crop(clip, x1=335, width=600).resize((1080, 1920))
    threads.append(
        threading.Thread(
            target=write, args=(clip, f"./assets/background/videos/staging/{p}")
        )
    )


for t in threads:
    t.start()

for t in threads:
    t.join()
