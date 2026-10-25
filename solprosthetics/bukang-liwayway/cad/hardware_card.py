"""Hardware card for one printed size: every screw and every heat-set insert, with the insert length that fits
each spot at this size. Reads build/joints.json and build/palm.json (written by the part scripts).
usage: python3 hardware_card.py [size_percent]  -> stl/HARDWARE.md"""
import json, sys, os
from collections import Counter

size = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('SIZE', '100')
J = json.load(open('build/joints.json')); PJ = json.load(open('build/palm.json'))
INS_D, THUMB_EXT, LB, W_SLOT = 5.5, 2.8, 15.0, 7.5 / 2


def insert_for(depth):
    """Insert length that fits a pocket of this depth (inserts: M3, 4.2 mm across, 4 or 5 mm long)."""
    if depth >= 5.3:
        return '5 mm (4 mm also fine)'
    if depth >= 4.0:
        return '4 mm'
    return None


screws, inserts = [], []
ax = J['axle']
ia = J['index']['joints'][0]
screws.append((f"M3 × {ax['screw_len']} button head", 'Knuckle axle: in from the index side, through index, middle and ring knuckles'))
ins = insert_for(ia.get('insert_depth', 0)) if ia.get('insert') else None
inserts.append(('Index knuckle, inner arm (side facing the middle finger)', ins or 'none: axle threads into the plastic'))
names = {'index': 'Index', 'middle': 'Middle', 'ring': 'Ring', 'little': 'Little'}
jn = {0: 'knuckle', 1: 'middle joint', 2: 'tip joint'}
for n in ('index', 'middle', 'ring', 'little'):
    for j, inf in enumerate(J[n]['joints']):
        if j == 0 and n != 'little':
            continue
        lbl = jn[j] if not (n == 'little' and j == 1) else 'tip joint'
        screws.append((f"M3 × {inf['screw_len']} button head", f"{names[n]} {lbl}"))
th = PJ.get('thumb_screw', 16)
screws.append((f"M3 × {th} button head", 'Thumb hinge (threads straight into the plastic, no insert)'))
# thumb hinge: no insert; its threaded end is buried in the solid thumb mount, so the screw bites ~9.5 mm deep
for k, fs in enumerate(PJ['flap_screws']):
    screws.append((f"M3 × {fs['screw_len']} flat head (countersunk)", 'Palm cover hinge edge'))
    d = min(INS_D, fs['petg_under_step'] - 0.4)
    inserts.append((f'Palm cover step, screw {k + 1}', (insert_for(d) if fs.get('insert') else None) or 'none: screw threads into the plastic'))
screws += [('M3 × 6 button head', 'Wrist hinge')] * 2
try:
    for c_ in json.load(open('build/cuff.json'))['clamps']:
        screws.append((f"M3 × {c_.get('screw_len', 4)} flat head (countersunk)", 'Line clamps in the cuff'))
except FileNotFoundError:
    screws += [('M3 × 4 flat head (countersunk)', 'Line clamps in the cuff')] * 4

out = [f'# Bukang-liwayway hardware card: {size}% set', '',
       'All screws are stainless M3 from a hardware store. Inserts are M3 brass heat-set inserts, 4.2 mm across',
       '(the double-knurled kind). Set inserts at about 240 °C for PETG, let the iron\'s weight push them in, and',
       'press them flush with something flat and cool.', '', '## Screws', '', '| Screw | Qty | Where |', '|---|---|---|']
by = {}
for s, w in screws:
    by.setdefault(s, []).append(w)
for s, ws in by.items():
    c = Counter(ws)
    out.append(f"| {s} | {len(ws)} | {'; '.join(f'{w} ×{k}' if k > 1 else w for w, k in c.items())} |")
out += ['', '## Heat-set inserts', '', '| Where | Insert length |', '|---|---|']
out += [f'| {w} | {l} |' for w, l in inserts]
lens = Counter(l.split(' ')[0] for _, l in inserts if l[0].isdigit())
out += ['', 'Totals: ' + ', '.join(f'{v} × {k} mm insert' for k, v in sorted(lens.items())), '']
os.makedirs('stl', exist_ok=True)
open('stl/HARDWARE.md', 'w').write('\n'.join(out))
print('\n'.join(out))
