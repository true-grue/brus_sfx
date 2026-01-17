import math

SR = 44100
FPS = 60
TABLE_SIZE = 1024
TABLE_BITS = 6
AMP_BITS = 15
RATIO_BITS = 10
DECAY_BITS = 6
DECAY_SCALE = 64
OSCS_NUM = 16
OSC_SIZE = 4
OSC_ABS = 0
OSC_AMP = 1
OSC_DECAY = 2
OSC_STEP = 3

SINE_TABLE = [int(32767 * math.sin(2 * math.pi * i / TABLE_SIZE))
              for i in range(TABLE_SIZE)]


class Osc:
    def __init__(self):
        self.amp = 0
        self.target_amp = 0
        self.decay = 0
        self.step = 0
        self.phase = 0


class SFX:
    def __init__(self):
        self.oscs = [Osc() for _ in range(OSCS_NUM)]
        self.decay_counter = 0


def get_vol(val):
    return round(val * 32768) & 0xffff


def get_decay(sec):
    steps = (sec * SR) / DECAY_SCALE
    k = math.exp(math.log(0.01) / steps)
    return round(k * 32768) & 0xffff


def get_freq(freq):
    return round((TABLE_SIZE * freq * (1 / SR)) * (1 << TABLE_BITS)) & 0xffff


def get_ratio(x):
    return round(x * (1 << RATIO_BITS)) & 0xffff


def sfx_update(sfx, params):
    abs_amp = 0
    abs_step = 0
    for i in range(OSCS_NUM):
        v = sfx.oscs[i]
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
    for v in sfx.oscs:
        v.amp += (v.target_amp - v.amp) >> DECAY_BITS
        pos = (v.phase >> TABLE_BITS) & (TABLE_SIZE - 1)
        acc += (SINE_TABLE[pos] * v.amp) >> AMP_BITS
        v.phase = (v.phase + v.step) & 0xffff
        if is_decay:
            v.target_amp = (v.target_amp * v.decay) >> AMP_BITS
    sfx.decay_counter += 1
    return limit(acc, -32768, 32767)
