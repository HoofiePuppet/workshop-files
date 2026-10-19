import numpy as np
from sdf import Grid
import os
def load_skin(path=None):
    path = path or os.environ.get('SKIN', 'src/skin.npz')
    d = np.load(path); g = Grid.__new__(Grid); g.o = d['o']; g.p = float(d['p']); g.n = d['n']
    return d, g
