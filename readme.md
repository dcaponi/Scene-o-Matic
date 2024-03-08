# Movie-Matic
The automatic movie assembler with generative AI tendencies.

This project allows you to programmatically create and manage projects that consist of multiple movies. Each movie within a project can contain several scenes, and each scene can contain multiple clips. This documentation outlines how to structure your projects and movies to use with the API effectively.

## Concepts
### Things
1. `Movies` - the final output video is called a movie, it is composed of...
2. `Scenes` - an arrangement of...
   1. scenes are built by describing one of the following arrangements and telling the program which clip to take audio from. You could specify multiple audios but that would probably be annoying
      1. stacking - placing a background then stacking some smaller clips or greenscreen clips on top of each other in layers
      2. vertical/horizontal - to get a presenter type video or side by side type video
      3. picture in picture - like the news or putting a streamer in the bottom corner
      4. montage - plays a bunch of videos in a row
3. `Clips` - image, audio, or video assets to add to a scene.
   1. you tell each clip where in the video it lives in relation to the final size (left bottom for example) and some left/down offset for fine tuning. You'll also tell it if it has a greenscreen to mask away for stacking
   2. You also tell each clip where to find the asset, or to create one using one of the machine learning extension
      1. audio: `.tiktok` for tik tok tts or `.xi_labs` for elevenlabs or `.whisper` for openai whisper
      2. video: `.sora` for openai sora or `.did` for d-id talking head type videos or `.rand` to have openai create some search terms based on a prompt and you'll get to choose from a selection of stock videos to merge into a background video.
      3. image: `.sd` for stable diffusion `.de` for dall-e and `.mj` for midjourney
   3. In vertical/horizontal scenes the clips are arranged in order from top down or left to right

### Things Details
#### Movie
* `title (string)`: The title of the movie.
* `scenes (array of Scene objects)`: A collection of scenes that make up the movie.
* `has_subtitles (boolean, optional)`: Indicates whether the movie includes subtitles. Defaults to false if not specified.
* `final_size (tuple of integers, optional)`: The final resolution of the movie, specified as [width, height]. If not provided, a default size may be applied.
* `duration (integer, optional)`: The total duration of the movie in seconds. If not provided, it might be calculated based on the content.

#### Scenes
* `clips (array of Clip objects)`: A collection of clips that are part of the scene.
* `arrangement (string)`: Defines how clips are arranged within the scene Must be one of
  *  `"stack"` - places a background image or video then stacks additional clips or greenscreen clips on top of each other in layers toward the viewer
  *  `"vertical"` - places clips starting at the top in a top-to-bottom arrangement
  *  `"horizontal"` - places clips starting at the left in a left-to-right arrangement
  *  `"montage"` - cuts one or more clips together to be played sequentially
* `use_audio (array of integers)`: Specifies which clips' audio tracks should be used in the scene. The integers represent the index of the clips within the clips array.

#### Clips
* `asset (string)`: The identifier or path to the media asset. 
  * You can use one of the following generative extensions. Generative extensions are arranged as `some prompt for the ai.model`
    *  __audio__: `.tiktok` for tik tok tts or `.xi_labs` for elevenlabs or `.whisper` for openai whisper
       *  **[Coming Soon]**`.mu` for mubert AI generated music
    *  __video__: `.rand` to have openai create some search terms based on a prompt. you'll get to choose from a selection of stock videos to merge into a video.
       *  **[Coming Soon]**`.sora` for openai sora or `.did` for d-id talking head type video
    *  __images__: **[Coming Soon]** image: `.sd` for stable diffusion `.dall-e` for dall-e and `.mj` for midjourney
* `prompt (string, optional)`: A text prompt associated with the clip, if applicable.
  * Used for generative type clips like generative tts prompts, video prompts etc
* `script (string, optional)`: A script or text to be used with the clip, if applicable. Also accepts path to `.txt` file
  * If going for a simple TTS without a generative script put your pre-written script here
* `voice (string, optional)`: The voice identifier for text-to-speech synthesis, if applicable.
  * See `voices.py` for a list of useable voices (or elevenlabs api for a list of those voices)
* `duration (integer, optional)`: The duration of the clip in seconds.
  * `Required` for *image clips* where there's no audio or other clip to determine how long a scene should be
* `has_greenscreen (boolean, optional)`: Indicates if the clip features a green screen that should be keyed out.
* `has_background (boolean, optional)`: Specifies if the clip includes a background.
  * Used primarily for text clips to give a semi-transparent background to make text more readable
* `override_audio (Clip object, optional)`: A clip that provides an audio override for the current clip.
  * Clip audio can be overridden with an audio file or TTS reading prompt. This is used on narrated compilation type videos.
* `size (tuple of integers, optional)`: The resolution of the clip, specified as `[width, height]`.
  * In situations like `arrangement: "horizontal` some defaults are assigned so clips scale properly.
* `location (tuple of integers)`: The on-screen location of the clip, specified as [left from start, down from start].
  * This is relative to the `anchor` and describes how many pixels left and below the top left pixel of the clip
* `anchor (tuple of strings)`: The anchor point for the clip's position, specified as [`("left" | "center" | "right")`, `("top" | "center" | "bottom")`]. Defaults `["left", "top"]`

### Caveats and Limitations
1. **[Coming Soon]** Theres no background music setting
2. Theres no scene transition, its just a jump cut
3. The types of videos this can make are very limited as custom animation or motions just don't exist right now.

### Recommended Video Types
1. explainer with a talking head presenter
2. narrated/musical montages
3. masked foreground on background (memes, presenters, etc)
4. *[Coming soon]* picture in picture (news casts, react videos, explainers)

## Up & Running
### Virtual Environments

To create one
`python3 -m venv .venv`

To activate it and get a nice clean package context
`source .venv/bin/activate`

To install packages for _this_ project
`pip3 install -r requirements.txt`

To add packages to this project (You should be in the virtual environment or you're going to have a bloated `requirements.txt`)
`pip3 install <package>`
`pip3 freeze > requirements.txt`

To get back to your home package context
`deactivate`

### Environment
Make sure you have all the keys exported to the environment from where you run this. You'll need the following
```sh
OPENAI_API_KEY=
ASSEMBLY_AI_API_KEY=
PEXELS_API_KEY=
ELEVEN_API_KEY=
```

OpenAI - generating scripts or using their TTS `whisper`
AssemblyAI - transcribing spoken word in a video and creating subtitle .srt files
Pexels - getting compilations of stock videos to use in a background
Elevenlabs - Better TTS than TikTok

### Running
right now its just keyed to read a `manifest.json` file. You can use the json below to make your own and see it in action.

run your handy `python main.py` from the `/app` directory (this one) and video generator go brrrrr


## Examples
```json
[
        {
        "title": "audio_only",
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [0],
                "clips": [
                    {
                        "asset": "write a funny script about kitty cats doing orange cat activities.whisper",
                        "voice": "echo"
                    }
                ]
            }
        ]
    },
    {
        "title": "narrated with generated script and caption",
        "final_size": [1080, 1920],
        "has_subtitles": true,
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [0],
                "clips": [
                    {
                        "asset": "orange cat kitty cat.rand",
                        "size": [1080, 1920],
                        "override_audio": {
                            "asset": "write a funny script about kitty cats doing orange cat activities.tiktok",
                            "voice": "en_us_004"
                        }
                    },
                    {
                        "asset": "orange cat story time",
                        "anchor": ["center", "top"],
                        "location": [0, 400]
                    }
                ]
            }
        ]
    },
    {
        "title": "narrated with pre-made script",
        "final_size": [1080, 1920],
        "has_subtitles": true,
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [0],
                "clips": [
                    {
                        "asset": "office pizza rainforrest friends clouds jungle.rand",
                        "size": [1080, 1920],
                        "override_audio": {
                            "asset": ".tiktok",
                            "script": "./assets/scripts/meeting.txt",
                            "voice": "en_male_funny"
                        }
                    }
                ]
            }
        ]
    },
    {
        "title": "vertically arranged clips",
        "scenes": [
            {
                "arrangement": "vertical",
                "use_audio": [1],
                "clips": [
                    {
                        "asset": "./assets/videos/cat-drama.mp4",
                    },
                    {
                        "asset": "./assets/videos/toothless.mp4",
                    },
                    {
                        "asset": "./assets/videos/stare.mp4",
                    }
                ]
            }
        ]
    },
    {
        "title": "multi scene",
        "final_size": [1080, 1920],
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [1],
                "clips": [
                    {
                        "asset": "./assets/background/code.jpg",
                        "size": [1080, 1920]
                    },
                    {
                        "asset": "./assets/videos/toothless.mp4",
                        "size": [1080, 1500],
                        "has_greenscreen": true,
                        "anchor": ["center", "bottom"]
                    },
                    {
                        "asset": "when the pipeline works",
                        "anchor": ["center", "top"],
                        "location": [0, 400]
                    }
                ]
            },
            {
                "arrangement": "stack",
                "use_audio": [1],
                "clips": [
                    {
                        "asset": "./assets/background/office.jpg",
                        "size": [1080, 1920]
                    },
                    {
                        "asset": "./assets/videos/stare.mp4",
                        "size": [1080, 1100],
                        "has_greenscreen": true,
                        "anchor": ["center", "bottom"]
                    },
                    {
                        "asset": "when it dont works",
                        "anchor": ["center", "top"],
                        "location": [0, 400]
                    }
                ]
            }
        ]
    },
    {
        "title": "side by side same clip",
        "final_size": [1920, 1080],
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [1],
                "clips": [
                    {
                        "asset": "./assets/background/code.jpg",
                        "size": [1920, 1080]
                    },
                    {
                        "asset": "./assets/videos/toothless.mp4",
                        "size": [960, 540],
                        "has_greenscreen": true,
                        "anchor": ["left", "bottom"]
                    },
                    {
                        "asset": "./assets/videos/toothless.mp4",
                        "size": [960, 540],
                        "has_greenscreen": true,
                        "anchor": ["right", "bottom"]
                    }
                ]
            }
        ]
    }
]
```

## Weird stuff
`override_audio` is used instead of simply specifying the audio clip and then choosing it with `use_audio` because some generative clips need to be told how long they are. Typically they're just going ot be as long as the AI generated script or sound bite. Therefore, providing an override is helpful here so that the generated clip can be told how long it should be during generation, instead of a user having to figure that out a priori. This also removes the need to assume audio clips will always be created first and remove any ambiguity in the event that multiple audios are to be used in the video (e.g. AI script narration with background music)