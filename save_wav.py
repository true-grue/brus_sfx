import json
from sfx_lib import *


with open('frames.json') as f:
    frames = json.loads(f.read())

samples = play(frames)

save_wav('1.wav', samples)
