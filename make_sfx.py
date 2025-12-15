import random
from IPython.display import Audio
from synth import *

FPS = 60

def save_audio(filename, samples):
    with open(filename, "wb") as f:
        f.write(Audio(samples, rate=SR).data)

def aosc(freq, vol, decay):
    return [1, get_freq(freq), get_vol(vol), get_decay(decay)]

def rosc(freq, vol, decay):
    return [0, get_ratio(freq), get_ratio(vol), get_decay(decay)]

def play(data, repeat):
    sfx = SFX()
    samples = []
    for _ in range(repeat):
        for count, voice in data:
            for _ in range(count + 1):
                sfx_update(sfx, voice)
                for _ in range(SR // FPS):
                    samples.append(sfx_process(sfx))
    return samples

def make_note(params, freq, vol):
    new_params = []
    for is_abs, step, amp, decay in params:
        if is_abs:
            step = get_freq(freq)
            amp = get_vol(vol)
        new_params.append([is_abs, step, amp, decay])
    return new_params

def encode_rle(data):
    res = []
    for x in data:
        if res and res[-1][1] == x:
            res[-1][0] += 1
        else:
            res.append([1, x])
    return res

def encode_delta(data, offs):
    res = []
    prev = [None] * len(data[0][1])
    for count, row in data:
        delta = [(i + offs, x) for i, (x, p) in enumerate(zip(row, prev)) if x != p]
        res.append([count, delta])
        prev = row
    return res

def encode_indices(data):
    res = []
    for count, pairs in data:
        row = []
        for idx, val in pairs:
            if row and idx == row[-1][0] + row[-1][1]:
                row[-1][1] += 1
                row[-1][2].append(val)
            else:
                row.append([idx, 1, [val]])
        res.append([count, row])
    return res

def encode_binary(data):
    res = []
    for count, row in data:
        for i, (idx, size, vals) in enumerate(row):
            x = idx | (size << 6) | ((i == len(row) - 1) << 15)
            res.append(x)
            res += vals
        res.append(count)
    return res

def pack(data, offs):
    offs *= VOICE_SIZE
    rows = []
    for count, params in data:
        rows.append([count, sum(params, [])])
    return encode_binary(encode_indices(encode_delta(rows, offs)))

def make_params(data, offs):
    new_data = []
    for count, row in data:
        params = [[0] * VOICE_SIZE for _ in range(VOICES_NUM)]
        params[offs:offs + len(row)] = row
        new_data.append([count, params])
    return new_data

preset = [
    aosc(freq=0, vol=1, decay=0.2),
    rosc(freq=1.2, vol=1, decay=0.1),
    rosc(freq=1.4, vol=1, decay=0.1),
    rosc(freq=1.6, vol=1, decay=0.1),
]

preset_data = [
    (0, make_note(preset, 200, 0.2)),
    (60, make_note(preset, 200, 0))
]

data = preset_data

packed = pack(data, 12)
print(packed)

data = make_params(data, 0)
samples = play(data, 5)
save_audio('test.wav', samples)
