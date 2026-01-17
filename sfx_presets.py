import random
from sfx_lib import *


def none(freq, vol):
    return EMPTY_SEQ


def kick(freq, vol):
    os = [
        osc(freq=freq, vol=0, decay=0.2),
        rel_osc(freq=8.5, vol=0.5, decay=0.01),
        rel_osc(freq=1.01, vol=0.5, decay=0.2),
        rel_osc(freq=8.505, vol=0.5, decay=0.01),
    ]
    return [
        change(os, vol=vol),
        change(os, freq=freq*0.7),
        change(os, freq=freq*0.5),
        change(os, freq=freq*0.4),
        change(os, freq=freq*0.2),
        change(os, freq=freq*0.1),
    ]


def snare(freq, vol):
    frames = []
    cur_freq = freq * 2
    for i in range(8):
        v = vol if i == 0 else 0
        os = [osc(freq=cur_freq, vol=v * 2, decay=0.3)]
        cur_freq *= 0.9
        r_ratio = 6.5
        for _ in range(3):
            r_vol = (7 - i) * 0.01
            os.append(rel_osc(freq=r_ratio, vol=r_vol, decay=0.1))
            r_ratio += 0.5
        frames.append(os)
    frames.append(change(frames[-1], vol=0))
    return frames


def space(freq, vol):
    d = 300
    os = [
        osc(freq=freq, vol=vol / 8, decay=d),
        rel_osc(freq=1.02, vol=1, decay=d),
        rel_osc(freq=1.1, vol=1, decay=d),
        rel_osc(freq=1.23, vol=1, decay=d),
        rel_osc(freq=1.26, vol=1, decay=d),
        rel_osc(freq=1.31, vol=1, decay=d),
        rel_osc(freq=1.39, vol=1, decay=d),
        rel_osc(freq=1.41, vol=1, decay=d),
    ]
    return [
        os,
        change(os, vol=0)
    ]


def bass(freq, vol):
    d = 1.5
    os = [
        osc(freq=freq, vol=0, decay=d),
        rel_osc(freq=3, vol=0.25, decay=d),
        rel_osc(freq=3.5, vol=0.2, decay=d),
        rel_osc(freq=6, vol=0.4, decay=0.2),
    ]
    return [
        change(os, vol=vol / 4),
        change(os, freq=freq+2, vol=vol / 4),
        change(os, vol=vol / 4),
        os,
    ]


def saw(freq, vol):
    d = 1
    v = 0.7
    freq *= 2
    os = [
        [1, get_freq(freq), get_vol(0), get_decay(d)],
        [0, get_ratio(2), get_ratio(v**1), get_decay(d)],
        [0, get_ratio(3), get_ratio(v**2), get_decay(d)],
        [0, get_ratio(4), get_ratio(v**3), get_decay(d)],
        [0, get_ratio(5), get_ratio(v**4), get_decay(d)],
        [0, get_ratio(6), get_ratio(v**5), get_decay(d)],
        [0, get_ratio(7), get_ratio(v**6), get_decay(d)],
        [0, get_ratio(8), get_ratio(v**7), get_decay(d)],
    ]
    return [
        change(os, freq=freq+1, vol=vol / 8),
        change(os, freq=freq+2),
        change(os, freq=freq+1),
        change(os, freq=freq-1),
        change(os, freq=freq-2),
        change(os, freq=freq-1),
        change(os, freq=freq+1),
        change(os, freq=freq+2),
        change(os, freq=freq+1),
        change(os, freq=freq-1),
        change(os, freq=freq-2),
        change(os, freq=freq-1),
    ]


def square(freq, vol):
    d = 2
    v = 0.6
    os = [
        [1, get_freq(freq), get_vol(0), get_decay(d)],
        [0, get_ratio(3), get_ratio(v**1), get_decay(d)],
        [0, get_ratio(5), get_ratio(v**2), get_decay(d)],
        [0, get_ratio(7), get_ratio(v**3), get_decay(d)],
        [0, get_ratio(9), get_ratio(v**4), get_decay(d)],
        [0, get_ratio(11), get_ratio(v**5), get_decay(d)],
    ]
    return [
        change(os, freq=freq+3, vol=vol / 6),
        change(os, freq=freq+3),
        change(os, freq=freq+3),
        change(os, freq=freq-3),
        change(os, freq=freq-3),
        change(os, freq=freq-3),
        change(os, freq=freq+3),
        change(os, freq=freq+3),
        change(os, freq=freq+3),
        change(os, freq=freq-3),
        change(os, freq=freq-3),
        change(os, freq=freq-3),
        change(os, freq=freq+3),
        change(os, freq=freq+3),
        change(os, freq=freq+3),
        change(os, freq=freq-3),
        change(os, freq=freq-3),
        change(os, freq=freq-3),
    ]


def bell(freq, vol):
    freq *= 2
    os = [
        osc(freq=freq, vol=0, decay=1),
        rel_osc(freq=2.505, vol=0.5, decay=0.5),
    ]
    return [
        change(os, vol=vol / 4),
        os,
    ]


PRESETS = dict(
    none=none,
    kick=kick,
    snare=snare,
    space=space,
    bass=bass,
    square=square,
    saw=saw,
    bell=bell
)
