from __future__ import annotations

import sys
import json
import queue
import threading
from typing import List

from termcolor import colored

from model.movie import Movie

def movies_from_json(filepath, projects_folder):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            movie_jobs = queue.Queue()
            movies: List[Movie] = []
            threads = []
            
            for movie_data in data:
                thread = threading.Thread(target=unpack_movie, args=(movie_data, projects_folder, movie_jobs, ))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            while not movie_jobs.empty():
                movies.append(movie_jobs.get())

            return movies
        
    except FileNotFoundError:
        print(colored(f"Error: File {filepath} not found", "red"))
        sys.exit(1)
    except json.JSONDecodeError:
        print(colored(f"Error File {filepath} does not contain valid json", "red"))
        sys.exit(1)


def unpack_movie(movie_data, projects_folder, result_queue):
    movie = Movie(**movie_data).unpack(projects_folder)
    result_queue.put(movie)
