#!/bin/sh
# Sol Prosthetics Bukang-liwayway v3.2 (realistic): full rebuild, in order.
# Needs: python3 with numpy scipy trimesh manifold3d scikit-image shapely embreex fast_simplification
set -e
cd "$(dirname "$0")"
# python3 extract.py src/makehuman-body-smooth.stl 10   # needs the full MakeHuman body (not included); src/right-arm-oriented.stl is its output
python3 skin.py           # smooth outer skin and child cavity distance fields (src/skin.npz)
# stage 1: v3 joint layout (axes, radii, screws) that the smooth parts are built on
python3 fingers.py
python3 thumb_solve.py
python3 palm.py
rm -rf build_v3 && cp -r build build_v3
# stage 2: the smooth v3.2 parts
python3 fingers2.py       # finger segments: barrel joints, knuckle axle, inserts, line channels, nails
python3 thumb_solve.py    # thumb pinch pose and hinge axis for the final fingers
python3 palm2.py          # back of the hand, TPU cover, thumb
python3 thumb_lock.py      # v3.3: thumb rosette lock (teeth, insert in the tongue, M3 x 12)
python3 cuff2.py          # forearm cuff, tensioner, line channels and clamps
python3 orient.py         # print orientation -> stl/
python3 clean_stl.py      # one closed solid per STL
python3 flap_print.py stl/palm_flap.stl stl/palm_flap_print.stl   # TPU cover + snip-off support fins
python3 back_print.py stl/palm_back.stl stl/palm_back_print.stl  # palm back + snip-off rim support (tabs between tunnel exits)
python3 hardware_card.py  # stl/HARDWARE.md
python3 art_holder.py     # v3.3 accessory: pen / pencil / crayon / brush holder on the index finger -> stl/art-holder-*.stl
# checks
python3 check_fingers.py -4 0 30 60
python3 check_thumb.py
python3 check_wrist.py
python3 check_tenodesis.py
python3 check_walls.py
python3 check_palm_walls.py
python3 check_thin.py
python3 check_pits.py build/palm_back.stl   # v3.3: pinholes / slits in the outer skin (only designed openings may show)
python3 check_tunnel_roof.py              # v3.3: plastic between each line tunnel and the outside
