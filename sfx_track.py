import sys
import json
import traceback
import importlib
import tkinter as tk
import numpy as np
import sounddevice as sd
from sfx_lib import Pat, parse_rows, process_rows, play, save_wav
import sfx_presets


TEXT_ATTRS = dict(
    fg='#d6d6d6',
    bg='#2e2e2e',
    font=('Consolas', 12),
    insertbackground='red',
    blockcursor=True,
    undo=True,
    wrap=tk.NONE
)


def load_data(path, widget):
    with open(path) as f:
        data = f.read()
        widget.insert('1.0', data)
    return data


def save_data(widget, path):
    with open(path, 'w') as f:
        data = widget.get('1.0', tk.END)
        f.write(data.strip() + '\n')
    return data


def play_pattern(conf_file, conf_w, rows_w):
    try:
        conf = json.loads(save_data(conf_w, conf_file))
        save_data(rows_w, conf['pattern'])
        start = 'insert linestart'
        end = tk.END
        if rows_w.tag_ranges('sel'):
            start = 'sel.first linestart'
            end = 'sel.last lineend'
        rows = rows_w.get(start, end).replace('===..', 'C-000')
        importlib.reload(sfx_presets)
        presets = {int(k): sfx_presets.PRESETS[v]
                   for k, v in conf['presets'].items()}
        frames = process_rows(Pat(conf['bpm'], presets), parse_rows(rows))
    except:
        traceback.print_exc() 
        return
    sd.stop()
    sd.play(np.array(play(frames), dtype=np.int16), samplerate=44100)
    with open('frames.json', 'w') as f:
        f.write(json.dumps(frames))


def main(conf_file):
    root = tk.Tk()
    root.geometry('800x800')
    root.title('Brus-16 Tracker')
    paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True)
    conf_w = tk.Text(paned, **TEXT_ATTRS)
    rows_w = tk.Text(paned, width=60, **TEXT_ATTRS)
    paned.add(rows_w)
    paned.add(conf_w)
    conf = json.loads(load_data(conf_file, conf_w))
    load_data(conf['pattern'], rows_w)   
    root.bind('<F5>', lambda e: play_pattern(conf_file, conf_w, rows_w))
    root.mainloop()


main(sys.argv[1])
