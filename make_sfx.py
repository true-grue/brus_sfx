import wave
from synth import *


def abs_osc(freq, vol, decay):
    return [1, get_freq(freq), get_vol(vol), get_decay(decay)]


def rel_osc(freq, vol, decay):
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
        delta = [(i + offs, x) for i, (x, p) in enumerate(zip(row, prev))
                 if x != p]
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


def extend_rows(data):
    new_data = []
    for count, row in data:
        params = row + [[0] * VOICE_SIZE for _ in range(VOICES_NUM - len(row))]
        new_data.append([count, params])
    return new_data


def note(preset, **kwargs):
    row = preset[0]
    aosc_row = [
        1,
        get_freq(kwargs['freq']) if 'freq' in kwargs else row[1],
        get_vol(kwargs['vol']) if 'vol' in kwargs else row[2],
        get_decay(kwargs['decay']) if 'decay' in kwargs else row[3]
    ]
    return [aosc_row] + preset[1:]


def save_sfx(name, rows, offs, rep):
    with open(f'{name}.txt', 'w') as f:
        f.write(str(pack(rows, offs)))
    samples = play(extend_rows(rows), rep)
    with wave.open(f'{name}.wav', 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b''.join(x.to_bytes(2, 'little', signed=True)
                               for x in samples))


def laser():
    o = [
        abs_osc(freq=0, vol=0, decay=0.5),
        rel_osc(freq=2, vol=0.7, decay=0.5),
        rel_osc(freq=4, vol=0.5, decay=0.2),
        rel_osc(freq=6, vol=0.25, decay=0.2),
    ]
    return [
        (0, note(o, freq=1000, vol=0.2)),
        (0, note(o, freq=900, vol=0)),
        (0, note(o, freq=800)),
        (0, note(o, freq=700)),
        (0, note(o, freq=600)),
        (0, note(o, freq=500)),
        (0, note(o, freq=450)),
        (0, note(o, freq=400)),
        (0, note(o, freq=350)),
        (0, note(o, freq=300)),
        (0, note(o, freq=250)),
        (0, note(o, freq=200)),
        (8, note(o, freq=100, decay=0.1)),
    ]


def player():
    o = [
        abs_osc(freq=0, vol=0, decay=1),
        rel_osc(freq=1.5, vol=0.5, decay=0.3),
        rel_osc(freq=2.2, vol=0.5, decay=0.1),
        rel_osc(freq=3.1, vol=0.5, decay=0.1),
    ]
    return [
        (1, note(o, freq=370, vol=0.2)),
        (1, note(o, freq=570, vol=0.2)),
        (1, note(o, freq=270, vol=0.2)),
        (1, note(o, freq=670, vol=0.2)),
        (1, note(o, freq=270, vol=0.2)),
        (1, note(o, freq=570, vol=0.2)),
        (1, note(o, freq=530, vol=0.2)),
        (1, note(o, freq=570, vol=0.2)),
        (1, note(o, freq=530, vol=0.2)),
        (1, note(o, freq=570, vol=0.2)),
        (1, note(o, freq=530, vol=0.2)),
        (1, note(o, freq=570, vol=0.15)),
        (1, note(o, freq=530, vol=0.15)),
        (1, note(o, freq=570, vol=0.15)),
        (1, note(o, freq=530, vol=0.15)),
        (1, note(o, freq=570, vol=0.1)),
        (1, note(o, freq=530, vol=0.1)),
        (1, note(o, freq=570, vol=0.05)),
        (1, note(o, freq=530, vol=0.)),
    ]


save_sfx('player', player(), 0, 1)
