import json
from os import environ
import re
from openai import OpenAI
from termcolor import colored

openai_client = OpenAI(api_key=environ.get("OPENAI_API_KEY"))

def video_search_terms_array(prompt: str, amount=1):
    prompt = f"""
    Generate {amount} search terms for stock videos for the given prompt.
    Prompt: {prompt}

    The search terms must be returned as a JSON-Array of strings.

    Each search term should consist of 1-3 words, always add the subject of the video.

    Here is an example of a JSON-Array of strings:
    ["search term 1", "search term 2", "search term 3"]

    Search terms should be related to the subject of the video.

    ONLY RETURN THE JSON-ARRAY OF STRINGS.
    DO NOT RETURN ANYTHING ELSE.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4", temperature=0.4, messages=[{"role": "system", "content": prompt}]
    )
    terms = response.choices[0].message.content
    return _ensure_array(terms)

def generate_script(video_subject: str, duration_seconds: int):
    prompt = f"""
    Generate a script for a video, depending on the subject of the video.
    The duration for the average human to read the script should be as close to but no longer than {duration_seconds}.
    Subject: {video_subject}

    The search terms must be returned as a JSON-Array of strings where each string is a sentence.

    Here is an example of a JSON-Array of strings:
    ["This is a sentance.", "Here's something exciting!", "Is this a question?"]

    Do not refernce this prompt in your response. Do not use any special characters. 
    Only use commas, periods, exclaimation points, or question marks. Do not use hyphens either.

    Be direct and don't start or end with unnecessary things like, "welcome to this video".

    The script should be related to the subject of the video.

    ONLY RETURN THE RAW SCRIPT. DO NOT RETURN ANYTHING ELSE.
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4", temperature=0.9, messages=[{"role": "system", "content": prompt}]
        )
        sentences = response.choices[0].message.content
        return _ensure_array(sentences)
    except Exception as e:
        print(colored(f"Openai Failure: {e}", "red"))
        return []

def _ensure_array(gpt_response):
    try:
        terms = json.loads(gpt_response)
        return terms
    except:
        print(
            colored(
                "[*] GPT returned an unformatted response. Attempting to clean...",
                "yellow",
            )
        )
        terms = re.findall(r"\[.*\]", gpt_response)

        if not terms:
            print(colored("[-] Could not parse response.", "red"))
            return []

        return json.loads(terms)
