import glob
from os import environ
import os
from uuid import uuid4
from termcolor import colored
import requests

from moviepy.editor import VideoFileClip


from generative.llm.openai import giphy_search_terms

GIPHY_URL = 'https://api.giphy.com/v1/gifs/search'
LOOP_DUR = 864000 # 10 days (effectively forever) because no video should be longer than 10 days and not specifying a loop duration causes the clip to go full blank screen

def giphy_snippet(staging_dir: str, prompt: str, size):
  size = size if size else (300, 300)

  comp_source_gifs = f"{staging_dir}/gif"
  if os.path.exists(comp_source_gifs):
      print(colored("gif exists. skipping...", "blue"))
      print(colored(f"to re-select gif, delete {comp_source_gifs} and try again.", "blue"))
      gif_path = [f"{vp}" for vp in glob.glob(f"{comp_source_gifs}/*.gif")][0]

      return VideoFileClip(gif_path).resize(size).loop(LOOP_DUR)

  os.mkdir(comp_source_gifs)

  api_key = environ.get("GIPHY_API_KEY", None)
  if api_key is None:
      print(colored("GIPHY_API_KEY not found", "red"))
      return None

  terms = giphy_search_terms(prompt, 10)
  response = requests.get(GIPHY_URL, params= {
    'api_key': api_key,
    'q': terms,
    'limit': 5,
    'rating': 'pg-13',
  })

  if response.status_code == 200:
      gifs = response.json()["data"]
      urls = [gif["images"]["original"]["url"] for gif in gifs]

      for url in urls:
          id = uuid4()
          with open(f"{comp_source_gifs}/{id}.gif", "wb") as f:
              f.write(requests.get(url).content)

      input(colored(f"Select one gif to use. Remove the rest. Press enter to continue...", "yellow"))

      gif_path = [f"{vp}" for vp in glob.glob(f"{comp_source_gifs}/*.gif")][0]

      return VideoFileClip(gif_path).resize(size).loop(LOOP_DUR)

  else:
      print(colored(f"Failed to retrieve GIFs: {response.status_code} {response.json()}", "red"))
      if response.status_code == 414:
          print(colored(f"Offending query {terms}", 'red'))
      return None
