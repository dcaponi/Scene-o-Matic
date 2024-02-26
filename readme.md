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
      4. montage - plays a bunch of images in a row
3. `Clips` - image, audio, or video assets to add to a scene.
   1. you tell each clip where in the video it lives in relation to the final size (left bottom for example) and some left/down offset for fine tuning. You'll also tell it if it has a greenscreen to mask away for stacking
   2. You also tell each clip where to find the asset, or to create one using one of the machine learning extension
      1. audio: `.mu` for mubert or `.tt` for tik tok tts or `.11l` for elevenlabs
      2. video: `.sora` for openai sora or `.did` for d-id talking head type videos
      3. image: `.sd` for stable diffusion `.dall-e` for dall-e and `.mj` for midjourney
   3. In vertical/horizontal scenes the clips are arranged in order from top down or left to right
## Caveats and Limitations
1. Theres no background music setting
2. Theres no scene transition, its just a jump cut
3. The types of videos this can make are very limited as custom animation or motions just don't exist right now.

## Recommended Video Types
1. explainer with a talking head presenter
2. narrated/musical montages
3. greenscreen on background of some kind (memes, presenters, etc)
4. picture in picture (news casts, react videos, explainers)