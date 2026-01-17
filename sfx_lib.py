import wave
from sfx_synth import *

NOTES = dict(zip('C- C# D- D# E- F- F# G- G# A- A# B-'.split(), range(12)))

EMPTY_SEQ = [[]]
MAX_CHANS = 16
RPB = 4


class Pat:
    def __init__(self, bpm, presets):
        self.chans = [(0, EMPTY_SEQ)] * MAX_CHANS
        self.presets = presets
        self.ticks = bpm_to_ticks(bpm, RPB)


def osc(freq, vol, decay):
    return [1, get_freq(freq), get_vol(vol), get_decay(decay)]


def rel_osc(freq, vol, decay):
    return [0, get_ratio(freq), get_ratio(vol), get_decay(decay)]


def change(frames, freq=None, vol=None):
    _, f, v, d = frames[0]
    return [[
        1,
        f if freq is None else get_freq(freq),
        v if vol is None else get_vol(vol),
        d
    ]] + frames[1:]


def seq(preset):
    return [data for n, params in preset for data in [params] * n]


def midi_to_freq(m):
    return 440 * 2 ** ((m - 69) / 12)


def note_to_freq(note):
    n, o = note[:2].upper(), int(note[2])
    return midi_to_freq(NOTES[n] + 12 * (o + 1))


def bpm_to_ticks(bpm, rpb):
    return round((FPS * 60) / (bpm * rpb))


def note_on(pat, note, pset, vol):
    return pat.presets[pset](note_to_freq(note), vol / 64)


def process_rows(pat, rows):
    frames = []
    for row in rows:
        for i, cmd in enumerate(row):
            if cmd is not None:
                pat.chans[i] = (0, note_on(pat, *cmd))
        for _ in range(pat.ticks):
            params = []
            for i in range(len(row)):
                pos, seq = pat.chans[i]
                params += seq[pos]
                if pos + 1 < len(seq):
                    pat.chans[i] = (pos + 1, seq)
            frames.append(params)
    return frames


def parse_rows(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        row = []
        for i, cell in enumerate(line.split('|')):
            if cell[0].isalpha():
                vol = int(cell[6:8]) if 'v' in cell else 64
                row.append((cell[:3], int(cell[3:5]), vol))
            else:
                row.append(None)
        rows.append(row)
    return rows


def extend_params(params):
    assert len(params) <= OSCS_NUM
    return params + [[0] * OSC_SIZE for _ in range(OSCS_NUM - len(params))]


def play(frames):
    sfx = SFX()
    samples = []
    for params in frames:
        sfx_update(sfx, extend_params(params))
        for _ in range(SR // FPS):
            samples.append(sfx_process(sfx))
    return samples


def save_wav(filename, samples):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b''.join(x.to_bytes(2, 'little', signed=True)
                               for x in samples))
