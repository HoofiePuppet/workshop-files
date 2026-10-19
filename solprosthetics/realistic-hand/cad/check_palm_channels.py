import json, numpy as np
from scipy.interpolate import RegularGridInterpolator as RGI
from lib_grid import load_skin
from cavity import cavity_field
d, g = load_skin(); FO = RGI(g.axes(), d['outer'], bounds_error=False, fill_value=20)
FC = RGI(g.axes(), cavity_field(d, g), bounds_error=False, fill_value=20)
for i, c in enumerate(json.load(open('build/palm_channels.json'))):
    P = np.array(c['pts'])[1:-2]
    wo = -FO(P) - c['r']; wc = FC(P) - c['r']
    print(i, 'skin min %.2f at %s' % (wo.min(), P[wo.argmin()].round(1)), ' cavity min %.2f at %s' % (wc.min(), P[wc.argmin()].round(1)))
