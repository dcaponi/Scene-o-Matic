from os import getenv
import requests
from termcolor import colored

PEXELS_API_KEY = getenv("PEXELS_API_KEY")

def get_video(search_term: str):
    headers = {"Authorization": PEXELS_API_KEY}

    url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=1"

    r = requests.get(url, headers=headers)
    response = r.json()

    video_urls = []
    video_url = ""

    try:
        video_urls = response["videos"][0]["video_files"]
    except:
        print(colored("[-] No Videos found.", "red"))
        print(colored(response, "red"))

    for video in video_urls:
        # Check if video has a download link
        if ".com/external" in video["link"]:
            video_url = video["link"]

    return video_url
