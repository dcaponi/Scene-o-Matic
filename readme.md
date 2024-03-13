# Movie-Matic
The automatic movie assembler with generative AI tendencies.

This project allows you to programmatically create and manage projects that consist of multiple movies. Each movie within a project can contain several scenes, and each scene can contain multiple snippets. This documentation outlines how to structure your projects and movies to use with the API effectively.

## Concepts
### Things
1. **Movies**: the final output video is called a movie, it is composed of...
2. **Scenes**: an arrangement of...
   - Scenes are built by describing one of the following arrangements and telling the program which snippet to take audio from. You could specify multiple audios but that would probably be annoying
      - **stacking**: placing a background then stacking some smaller snippets or greenscreen snippets on top of each other in layers
      - **vertical/horizontal**: to get a presenter type video or side by side type video
      - **picture in picture**: like the news or putting a streamer in the bottom corner
      - **montage**: plays a bunch of videos in a row
3. **Snippets**: image, audio, or video assets to add to a scene.
   - You tell each snippet where in the video it lives in relation to the final size (left bottom for example) and some left/down offset for fine-tuning. You'll also tell it if it has a greenscreen to mask away for stacking
   - You also tell each snippet where to find the asset, or to create one using one of the machine learning extension
      - **audio**: `.tiktok` for TikTok TTS or `.xi_labs` for ElevenLabs or `.whisper` for OpenAI Whisper
      - **video**: **[Coming Soon]** `.sora` for OpenAI Sora or `.did` for D-ID talking head type videos or `.rand` to have OpenAI create some search terms based on a prompt and you'll get to choose from a selection of stock videos to merge into a background video.
      - **image**: `.giphy` for selected Giphy gifs, **[Coming Soon]** `.sd` for Stable Diffusion `.de` for DALL-E and `.mj` for Midjourney
   - In vertical/horizontal scenes, the snippets are arranged in order from top down or left to right.

### Things Details
#### Movie
- **title (string)**: The title of the movie.
- **scenes (array of Scene objects)**: A collection of scenes that make up the movie.
- **has_subtitles (boolean, optional)**: Indicates whether the movie includes subtitles. Defaults to false if not specified.
- **final_size (tuple of integers, optional)**: The final resolution of the movie, specified as [width, height]. If not provided, a default size may be applied.
- **duration (integer, optional)**: The total duration of the movie in seconds. If not provided, it might be calculated based on the content.

#### Scenes
- **snippets (array of Snippet objects)**: A collection of snippets that are part of the scene.
- **arrangement (string)**: Defines how snippets are arranged within the scene. Must be one of
  - `"stack"`: places a background image or video then stacks additional snippets or greenscreen snippets on top of each other in layers toward the viewer
  - `"vertical"`: places snippets starting at the top in a top-to-bottom arrangement
  - `"horizontal"`: places snippets starting at the left in a left-to-right arrangement
  - `"montage"`: cuts one or more snippets together to be played sequentially
- **use_audio (array of integers)**: Specifies which snippets' audio tracks should be used in the scene. The integers represent the index of the snippets within the snippets array.

#### Snippets
A `snippet` is a grouping of one of the following types: `audio` `video` or `caption`

##### Audio only snippet
```json
{
    "audio": {
        "asset": "write a funny script about kitty cats doing orange cat activities.whisper",
        "voice": "echo"
    }
}
```

##### Audio and Video snippets. Overlay audio onto video's native audio
```json
{
    "audio": {
        "asset": "./assets/music/son_of_preacher_man.mp3"
    }
},
{
    "video": {
        "asset": "./assets/videos/vincent.mp4",
        "size": [1080, 1000],
        "has_greenscreen": true,
        "anchor": ["center", "bottom"]
    }
}
```

##### Audio and Video in same snippet (override existing video audio)
```json
{
    "audio": {
        "asset": "write a funny script about kitty cats doing orange cat activities.whisper",
        "voice": "echo"
    },
    "video": {
        "asset": "./assets/videos/compilation.mp4",
        "size": [1080, 1920]
    }
}
```

- **asset (string)**: The identifier or path to the media asset (e.g. `path/to/video.mp4`). You can use one of the following generative extensions. Generative extensions are arranged as `some prompt for the ai.model`
  - **audio**: `.tiktok` for TikTok TTS or `.xi_labs` for ElevenLabs or `.whisper` for OpenAI Whisper
     - **[Coming Soon]** `.mu` for Mubert AI-generated music
  - **video**: `.rand` to have OpenAI create some search terms based on a prompt. you'll get to choose from a selection of stock videos to merge into a video.
     - **[Coming Soon]** `.sora` for OpenAI Sora or `.did` for D-ID talking head type video
  - **images**: **[Coming Soon]** image: `.sd` for Stable Diffusion `.dall-e` for DALL-E and `.mj` for Midjourney
  - A note on generative extensions. If you choose a generative extension for video, `audio` or a `duration` must be provided so the generated video duration can be known. If you choose generative audio and video, audio will be generated first and that duration will be used. 
- **prompt (string, optional)**: A text prompt associated with the snippet, if applicable.
  - Used for generative type snippets like generative TTS prompts, video prompts etc
- **script (string, optional)**: A script or text to be used with the snippet, if applicable. Also accepts the path to `.txt` file
  - If going for a simple TTS without a generative script put your pre-written script here
- **voice (string, optional)**: The voice identifier for text-to-speech synthesis, if applicable.
  - See `voices.py` for a list of useable voices (or ElevenLabs API for a list of those voices)
- **duration (integer, optional)**: The duration of the snippet in seconds.
  - `Required` for *image snippets* where there's no audio or other snippet to determine how long a scene should be
  - Duration cannot exceed provided asset's duration. If you specify a 10s duration on a 5s video the video will halt after 5s
- **has_greenscreen (boolean, optional)**: Indicates if the snippet features a green screen that should be keyed out.
- **has_background (boolean, optional)**: Specifies if the snippet includes a background.
  - Used primarily for text snippets to give a semi-transparent background to make text more readable
- **size (tuple of integers, optional)**: The resolution of the snippet, specified as `[width, height]`.
  - In situations like `arrangement: "horizontal` some defaults are assigned so snippets scale properly.
- **location (tuple of integers)**: The on-screen location of the snippet, specified as [left from start, down from start].
  - This is relative to the `anchor` and describes how many pixels left and below the top-left pixel of the snippet
- **anchor (tuple of strings)**: The anchor point for the snippet's position, specified as [`("left" | "center" | "right")`, `("top" | "center" | "bottom")`]. Defaults `["left", "top"]`


### Caveats and Limitations
1. Theres no background music volume setting
2. Theres no scene transition, its just a jump cut
3. The types of videos this can make are very limited as custom animation or motions just don't exist right now
4. No Brady Bunch or PIP arrangement (PIP is on the way) or side by side arrangements of stacked scenes (but you can make this by combinining 2 or 3 runs of simpler videos)
   1. Actually for brady bunch, you'd do one run of 3 movies vertically or horizontally arranged w/ 3 snippets and do a second run simply doing whatever the opposite arrangement was (so if you made 3 horizontally arranged 3 snippet movies, just vertically arrange them in a final movie)
      1. 2 runs of the tool because you need to write the first 3 movies to disk before proceeding. The design philosophy here is simplicity, flexibility, and extendability and making every type of video arrangement would be a Herculean effort which is why we only provide simple formats that can be combined to more complex videos.

### Recommended Video Types
1. explainer with a talking head presenter
2. narrated/musical montages
3. masked foreground on background (memes, presenters, etc)
4. **[Coming Soon]** picture in picture (news casts, react videos, explainers)

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
                "snippets": [
                    {
                        "audio": {
                            "asset": "write a funny script about kitty cats doing orange cat activities.whisper",
                            "voice": "echo"
                        }
                    }
                ]
            }
        ]
    },
    {
        "title": "including audio track",
        "final_size": [1080,1920],
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [0],
                "snippets": [
                    {
                        "video": {
                            "asset": "./assets/background/code.jpg",
                            "size": [1080,1920]
                        },
                        "audio": {
                            "asset": "./assets/music/elevator.mp3",
                            "duration": 7
                        }
                    },
                    {
                        "video": {
                            "asset": "./assets/videos/vincent.mp4",
                            "size": [1080, 1000],
                            "has_greenscreen": true,
                            "anchor": ["center", "bottom"]
                        }
                    },
                    {
                        "caption": {
                            "asset": "looking for the api documentation but it keeps sending you to the marketing site",
                            "anchor": ["center", "top"],
                            "location": [0, 400]
                        }
                    }
                ]
            }
        ]
    },
    {
        "title": "adding 'background music'",
        "final_size": [1080,1920],
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [0,1],
                "snippets": [
                    {
                        "video": {
                            "asset": "./assets/background/bed.jpg",
                            "size": [1080,1920]
                        },
                        "audio": {
                            "asset": "./assets/music/elevator.mp3"
                        }
                    },
                    {
                        "video": {
                            "asset": "./assets/videos/cat-snore.mp4",
                            "size": [1080, 1400],
                            "has_greenscreen": true,
                            "anchor": ["center", "bottom"]
                        }
                    },
                    {
                        "caption": {
                            "asset": "sleepping through a pager dookie because I'm dropping my notice tomorrow",
                            "anchor": ["center", "top"],
                            "location": [0, 400]
                        }
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
                "snippets": [
                    {
                        "video": {
                            "asset": "orange cat kitty cat.rand",
                            "size": [1080, 1920]
                        },
                        "audio": {
                            "asset": "write a funny script about kitty cats doing orange cat activities.tiktok",
                            "voice": "en_us_006"
                        }
                    },
                    {
                        "caption": {
                            "asset": "orange cat story time",
                            "anchor": ["center", "top"],
                            "location": [0, 400]
                        }
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
                "snippets": [
                    {
                        "video": {
                            "asset": "office pizza rainforrest friends clouds jungle.rand",
                            "size": [1080, 1920]
                        },
                        "audio": {
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
        "title": "vertically arranged snippets",
        "scenes": [
            {
                "arrangement": "vertical",
                "use_audio": [1],
                "snippets": [
                    {   
                        "video": {
                            "asset": "./assets/videos/cat-drama.mp4",
                            "size": [1080, 640]
                        }
                    },
                    {   
                        "video": {
                            "asset": "./assets/videos/toothless.mp4",
                            "size": [1080, 640]
                        },
                        "audio": {
                            "asset": "./assets/music/elevator.mp3",
                            "duration": 7
                        }
                    },
                    {   
                        "video": {
                            "asset": "./assets/videos/stare.mp4",
                            "size": [1080, 640]
                        }
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
                "snippets": [
                    {   
                        "video": {
                            "asset": "./assets/background/code.jpg",
                            "size": [1080, 1920]
                        }
                    },
                    {   
                        "video": {
                            "asset": "./assets/videos/toothless.mp4",
                            "duration": 7,
                            "size": [1080, 1500],
                            "has_greenscreen": true,
                            "anchor": ["center", "bottom"]
                        }
                    },
                    {
                        "caption": {
                            "asset": "when the pipeline works",
                            "anchor": ["center", "top"],
                            "location": [0, 400]
                        }
                    }
                ]
            },
            {
                "arrangement": "stack",
                "use_audio": [1],
                "snippets": [
                    {   
                        "video": {
                            "asset": "./assets/background/office.jpg",
                            "size": [1080, 1920]
                        }
                    },
                    {
                        "video": {
                            "asset": "./assets/videos/stare.mp4",
                            "duration": 7,
                            "size": [1080, 1100],
                            "has_greenscreen": true,
                            "anchor": ["center", "bottom"]
                        }
                    },
                    {
                        "caption": {
                            "asset": "when it dont works",
                            "anchor": ["center", "top"],
                            "location": [0, 400]
                        }
                    }
                ]
            }
        ]
    },
    {
        "title": "side by side same snippet",
        "final_size": [1920, 1080],
        "scenes": [
            {
                "arrangement": "stack",
                "use_audio": [1],
                "snippets": [
                    {   
                        "video": {
                            "asset": "./assets/background/code.jpg",
                            "size": [1920, 1080]
                        }
                    },
                    {
                        "video": {
                            "asset": "./assets/videos/toothless.mp4",
                            "size": [960, 540],
                            "has_greenscreen": true,
                            "anchor": ["left", "bottom"]
                        }
                    },
                    {
                        "video": {
                            "asset": "./assets/videos/toothless.mp4",
                            "size": [960, 540],
                            "has_greenscreen": true,
                            "anchor": ["right", "bottom"]
                        }
                    }
                ]
            }
        ]
    }
]
```