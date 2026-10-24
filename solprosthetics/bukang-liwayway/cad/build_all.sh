#!/bin/sh
# Sol Prosthetics Bukang-liwayway v3.1 (realistic): full rebuild from the MakeHuman export, in order.
# Needs: python3 with numpy scipy trimesh manifold3d scikit-image shapely embreex
set -e
cd "$(dirname "$0")"
# python3 extract.py src/makehuman-body-smooth.stl 10   # needs the full MakeHuman body (not included); src/right-arm-oriented.stl is its output
python3 skin.py           # smooth outer skin and child cavity distance fields (src/skin.npz)
python3 thumb_solve.py    # thumb pinch pose and hinge axis (build/thumb_solution.json)
python3 fingers2.py       # finger segments as smooth fields: filleted joints, exact screws and channels
python3 palm2.py          # back of the hand, TPU flap, thumb (smooth fields)
python3 cuff2.py          # forearm cuff with the low tensioner swelling and flared line channels
python3 orient.py         # print orientation -> stl/
python3 clean_stl.py      # one closed solid per STL
python3 flap_print.py stl/palm_flap.stl stl/palm_flap_print.stl   # TPU cover + snip-off stabilizer fins
# checks
python3 check_fingers.py -4 0 30 60
python3 check_thumb.py
python3 check_wrist.py
python3 check_tenodesis.py
python3 check_walls.py
python3 check_palm_walls.py
python3 check_thin.py
