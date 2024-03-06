## Virtual Environments

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

## Concepts
1. `Movies` - the final output video is called a movie, it is composed of...
   1. You need to describe the title and final size as that will inform everything else
2. `Scenes` - an arrangement of...
   1. scenes are built by describing one of the following arrangements and telling the program which clip to take audio from. You could specify multiple audios but that would probably be annoying
      1. stacking - placing a background then stacking some smaller clips or greenscreen clips on top of each other in layers
      2. vertical/horizontal - to get a presenter type video or side by side type video
      3. picture in picture - like the news or putting a streamer in the bottom corner
      4. montage - plays a bunch of videos in a row
3. `Clips` - image, audio, or video assets to add to a scene.
   1. you tell each clip where in the video it lives in relation to the final size (left bottom for example) and some left/down offset for fine tuning. You'll also tell it if it has a greenscreen to mask away for stacking
   2. You also tell each clip where to find the asset, or to create one using one of the machine learning extension
      1. audio: `.mu` for mubert or `.tiktok` for tik tok tts or `.xi_labs` for elevenlabs or `.whisper` for openai whisper
      2. video: `.sora` for openai sora or `.did` for d-id talking head type videos or `.rand` to have openai create some search terms based on a prompt and you'll get to choose from a selection of stock videos to merge into a background video.
      3. image: `.sd` for stable diffusion `.dall-e` for dall-e and `.mj` for midjourney
   3. In vertical/horizontal scenes the clips are arranged in order from top down or left to right

## Ergonomics
1. Array ordering of clips affects how they are arrainged
   1. in `stack` scenes, first clip is on the bottom, and later clips are stacked on top.
   2. In `horizontal` first is left, later fill in from the right
   3. In `vertical` first is on top, then second and so on
   4. In `montage` first is shown first, followed by the rest in sequential order
2. In the clip you can either elect to use its audio with `use_audio` in the final scene or add a free standing audio asset which will be useful for background music. You can override the clip audio (or create clip audio from scratch) by assigning an audio `Clip` to the clip in question. You'll still need to identify the clip in `use_audio` and you'll lose the original clip audio here.
3. In 

## Caveats and Limitations
1. Theres no background music setting
2. Theres no scene transition, its just a jump cut
3. The types of videos this can make are very limited as custom animation or motions just don't exist right now.

## Recommended Video Types
1. explainer with a talking head presenter
2. narrated/musical montages
3. greenscreen on background of some kind (memes, presenters, etc)
4. picture in picture (news casts, react videos, explainers)

## Notes
use_audio lets us select which audio clips make it into the final scene
thats useful for background music and talking clips within the scene
or stacking 2 side-by-side clips with alternating dialog

audio_asset lets us create audio to be added to a clip which is useful for
d-id readings or narrated compilations or simply overriding the clip's original audio

host_img - image of a headshot of someone to speak words using d-id
type - ???
duration - required if asset is a pic and theres no video or audio to set duration for
size - required for all clips *unless using `horizontal` or `vertical` arrangements*
anchor - (left|right|center, top|center|bottom) defaults left top
location - left, down from anchor position defaults 0, 0
voice - one of the voices in voices.py must match ai model
script - a script to be spoken with a tts
prompt - a prompt for an image or video asset
generative assets ending in .tiktok or .sora start with the prompt (e.g. this is the prompt write something about it .sora) if its a tts it will use openai chatgpt to generate the script
has-background - used for text assets to give it a more distinct background
has-greenscreen - a higher up in the stack clip has a greenscreen that should be removed
asset - path to file or a prompt for a generative asset


arrangement - stack, montage, horizontal, vertical, pip. (Vertical and horizontal will distribute the clips to fill the final size evenly)
use_audio - array of clip indices whos audio should be mixed into the final video

title - obvi
has_subtitles - if true, generate subtitle srt and burn to the video
final_size - final size of the produced video required unless using `horizontal` or `vertical` arrangements defaults to 1080, 1920


## Examples
```json
[
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
                            "asset": "write a funny script about kitty cats doing orange cat activities.whisper",
                            "voice": "echo"
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
                        "asset": "./assets/videos/cat-drama.mp4"
                    },
                    {
                        "asset": "./assets/videos/toothless.mp4"
                    },
                    {
                        "asset": "./assets/videos/stare.mp4"
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