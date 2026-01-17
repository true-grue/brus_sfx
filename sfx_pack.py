import json
from sfx_lib import extend_params


def pack_seen(frames):
    abs_seen = {}
    rel_seen = {}
    data = []
    for params in frames:
        indexes = []
        for param in params:
            param = tuple(param)
            seen = abs_seen
            is_rel = param[0] == 0
            if is_rel:
                seen = rel_seen
            param = param[1:]
            if param not in seen:
                seen[param] = len(seen) | (is_rel << 8)
            indexes.append(seen[param])
        data.append(indexes)
    return data, abs_seen, rel_seen


def pack_rle(data):
    res = []
    for x in data:
        if res and res[-1][1] == x:
            res[-1][0] += 1
        else:
            res.append([1, x])
    return [[count] + row for count, row in res]


def pack_delta(data):
    res = []
    prev = [None] * len(data[0])
    for row in data:
        delta = [(i, x) for i, (x, p) in enumerate(zip(row, prev))
                 if x != p]
        res.append(delta)
        prev = row
    return res


def pack_binary(data):
    res = []
    for row in data:
        new_row = []
        for i, (x, y) in enumerate(row):
            new_row.append(x << 9 | y | (i == 0) << 15)
        res += new_row
    return res


def pack(frames):
    data, abs_seen, rel_seen = pack_seen(frames)
    packed = pack_binary(pack_delta(pack_rle(data)))
    return packed, abs_seen, rel_seen


def unpack(packed, abs_seen, rel_seen):
    abs_idx = {v: k for k, v in abs_seen.items()}
    rel_idx = {v & 255: k for k, v in rel_seen.items()}
    frames = []
    row = [None] * 17
    for x in packed:
        if x & 32768:
            row = row.copy()
            frames.append(row)
        x &= 32767
        v = x & 511
        i = x >> 9
        if i == 0:
            row[i] = v
        else:
            seen_idx = abs_idx if v < 256 else rel_idx
            row[i] = [int(v < 256)] + list(seen_idx[v & 255])
    return frames


with open('frames.json') as f:
    frames = json.loads(f.read())
    frames = [extend_params(params) for params in frames]


packed, abs_seen, rel_seen = pack(frames)

a_table = sum([list(k) for k in abs_seen], [])
r_table = sum([list(k) for k in rel_seen], [])

print(f'SONG_ABS = {a_table}')
print(f'SONG_REL = {r_table}')
print(f'SONG = {packed}')
