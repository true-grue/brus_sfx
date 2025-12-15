import math

SR = 44100

TABLE_SIZE = 1024
TABLE_BITS = 6
AMP_BITS = 15
RATIO_BITS = 10
DECAY_BITS = 6
DECAY_SCALE = 64
VOICES_NUM = 16
VOICE_SIZE = 4

VOICE_ABS = 0
VOICE_AMP = 1
VOICE_DECAY = 2
VOICE_STEP = 3

SINE_TABLE = [int(32767 * math.sin(2 * math.pi * i / TABLE_SIZE)) for i in range(TABLE_SIZE)]

class Voice:
    def __init__(self):
        self.amp = 0
        self.target_amp = 0
        self.decay = 0
        self.step = 0
        self.phase = 0

class SFX:
    def __init__(self):
        self.voices = [Voice() for _ in range(VOICES_NUM)]
        self.decay_counter = 0

def get_vol(val):
    return min(round(val * 32768), 65535)

def get_decay(sec):
    steps = (sec * SR) / DECAY_SCALE
    k = math.exp(math.log(0.01) / steps)
    return round(k * 32768)

def get_freq(freq):
    return min(round((TABLE_SIZE * freq * (1 / SR)) * (1 << TABLE_BITS)), 65535)

def get_ratio(x):
    return min(round(x * (1 << RATIO_BITS)), 65535)

def sfx_update(sfx, params):
    abs_amp = 0
    abs_step = 0
    for i in range(VOICES_NUM):
        v = sfx.voices[i]
        is_abs, step, amp, decay = params[i]
        if is_abs:
            abs_amp = amp
            abs_step = step
        else:
            amp = (abs_amp * amp) >> RATIO_BITS
            step = (abs_step * step) >> RATIO_BITS
        if amp:
            v.target_amp = amp        
        v.step = step
        v.decay = decay

def limit(x, x_min, x_max):
    y = x_min if x < x_min else x
    return x_max if y > x_max else y

def sfx_process(sfx):
    acc = 0
    is_decay = (sfx.decay_counter & (DECAY_SCALE - 1)) == 0
    for v in sfx.voices:
        v.amp += (v.target_amp - v.amp) >> DECAY_BITS
        pos = (v.phase >> TABLE_BITS) & (TABLE_SIZE - 1)
        acc += (SINE_TABLE[pos] * v.amp) >> AMP_BITS
        v.phase = (v.phase + v.step) & 0xffff
        if is_decay:
            v.target_amp = (v.target_amp * v.decay) >> AMP_BITS
    sfx.decay_counter += 1
    return limit(acc, -32768, 32767)
