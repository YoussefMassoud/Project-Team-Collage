from moviepy import ImageClip
import inspect

print(dir(ImageClip))
try:
    clip = ImageClip("test_assets/red.png")
    print(dir(clip))
except Exception as e:
    print(e)
