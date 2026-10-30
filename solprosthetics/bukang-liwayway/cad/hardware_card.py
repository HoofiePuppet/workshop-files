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
where_ = ('Index knuckle, outer arm (under the axle head; push in from outside, flush in the recess)' if ia.get('insert_arm') == 'outer'
          else 'Index knuckle, inner arm (side facing the middle finger)')
inserts.append((where_, ins or 'none: axle threads into the plastic'))
names = {'index': 'Index', 'middle': 'Middle', 'ring': 'Ring', 'little': 'Little'}
jn = {0: 'knuckle', 1: 'middle joint', 2: 'tip joint'}
for n in ('index', 'middle', 'ring', 'little'):
    for j, inf in enumerate(J[n]['joints']):
        if j == 0 and n != 'little':
            continue
        lbl = jn[j] if not (n == 'little' and j == 1) else 'tip joint'
        screws.append((f"M3 × {inf['screw_len']} button head", f"{names[n]} {lbl}"))
th = PJ.get('thumb_screw', 16)
if PJ.get('thumb_lock'):     # v3.3 rosette lock: screw threads into an insert in the thumb's tongue
    if PJ.get('thumb_knob'):   # v3.3b: tool-free knob, the hex head is pushed into the knob's pocket
        screws.append((f"M3 × {th} hex head (DIN 933, fully threaded)", 'Thumb knob (head pushed into the knob; threads into the insert in the thumb tongue)'))
    else:
        screws.append((f"M3 × {th} button head", 'Thumb lock (threads into the insert in the thumb tongue)'))
    inserts.append(('Thumb tongue, face with the teeth (push in from that face, flush)', '4 mm'))
else:
    screws.append((f"M3 × {th} button head", 'Thumb hinge (threads straight into the plastic, no insert)'))
cov = Counter()
for k, fs in enumerate(PJ['flap_screws']):
    screws.append((f"M3 × {fs['screw_len']} flat head (countersunk)", 'Palm cover, all round its edge'))
    d = min(INS_D, fs['petg_under_step'] - 0.4)
    cov[(insert_for(d) if fs.get('insert') else None) or 'none: screw threads into the plastic'] += 1
for l, k in cov.items():          # v3.3: the cover is screwed all round (no snaps), one row per insert length
    inserts += [('Palm cover step, all round the cover (push in from outside, flush with the step)', l)] * k
screws += [('M3 × 6 button head', 'Wrist hinge (into a brass insert in the hand; tighten until the cuff swings freely, blue threadlocker)')] * 2
inserts += [('Wrist hinge, both ear pads of the hand (push in from outside, flush)', '4 mm')] * 2
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
_ic = Counter(inserts)
out += [f'| {w} ×{k} | {l} |' if k > 1 else f'| {w} | {l} |' for (w, l), k in _ic.items()]
lens = Counter(l.split(' ')[0] for _, l in inserts if l[0].isdigit())
out += ['', 'Totals: ' + ', '.join(f'{v} × {k} mm insert' for k, v in sorted(lens.items())), '']
if os.path.exists('build/art_holder.json'):     # v3.3 accessory
    ah = json.load(open('build/art_holder.json'))
    out += ['## Accessory: art holder (optional)', '',
            f"One TPU 95A part (stl/art-holder.stl), no screws. Slides over the index fingertip onto its middle segment; push the tool into the tube, point forward. Holds about {ah['fin_gap']:.1f}–{ah['bore'] - 0.3:.1f} mm across (round, hex or triangular).", '']
os.makedirs('stl', exist_ok=True)
open('stl/HARDWARE.md', 'w').write('\n'.join(out))
print('\n'.join(out))
