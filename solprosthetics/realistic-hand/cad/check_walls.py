"""Skin thickness over every line channel: outer field sampled along the channel centre lines."""
import json, sys, numpy as np
from scipy.interpolate import RegularGridInterpolator
from lib_grid import load_skin
d, g = load_skin()
F = RegularGridInterpolator(g.axes(), d['outer'], bounds_error=False, fill_value=10)
ch = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'build/finger_channels.json'))
bad = 0
for i, c in enumerate(ch):
    P = np.array(c['pts']); seg = []
    for a, b in zip(P[:-1], P[1:]):
        for t in np.linspace(0, 1, 12): seg.append(a + t * (b - a))
    seg = np.array(seg)
    seg = seg[np.linalg.norm(seg - P[-1], axis=1) > 2.6]   # the last 2.6 mm open into the knot pocket on purpose
    v = F(seg)
    wall = -v - c['r']        # skin left between channel and outer surface
    k = np.argmin(wall)
    if wall[k] < 0.6:
        bad += 1; print(f'channel {i} r{c["r"]}: thinnest skin {wall[k]:.2f} mm at {seg[k].round(1)}')
print('channels', len(ch), 'thin', bad)
