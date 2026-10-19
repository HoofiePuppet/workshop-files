#!/bin/sh
# Sol Prosthetics realistic hand: full rebuild from the MakeHuman export, in order.
# Needs: python3 with numpy scipy trimesh manifold3d scikit-image shapely embreex
set -e
cd "$(dirname "$0")"
python3 extract.py src/makehuman-body-smooth.stl 10   # right arm, oriented hand frame, wrist at y = 0
python3 skin.py           # outer skin and child cavity distance fields (src/skin.npz)
python3 thumb_solve.py    # thumb pinch pose and hinge axis (build/thumb_solution.json)
python3 fingers.py        # finger segments, joints, channels, palm with MCP knuckles (build/)
python3 palm.py           # PETG back, TPU flap, thumb (build/)
python3 cuff.py           # forearm cuff with tensioner (build/)
python3 mouths.py         # round every line-channel mouth
python3 open_parts.py     # blunt knife edges (opening with a 0.22 mm ball)
python3 orient.py         # print orientation -> stl/
python3 clean_stl.py      # one closed solid per STL
# checks
python3 check_fingers.py -4 0 30 60
python3 check_thumb.py
python3 check_wrist.py
python3 check_tenodesis.py
python3 check_walls.py
python3 check_palm_walls.py
python3 check_thin.py
