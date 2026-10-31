<img alt="Sol Prosthetics" src="../solprosthetics-logo.png" width="160">

# Bukang-liwayway ("Sunrise") v3.4, realistic — test print

**Status:** v3.4 test print. It has not been fitted to a child yet. · **Updated:** 2026-10-31
**Designer:** Hoofie Puppet · **License:** CC BY-NC-SA 4.0 (see the repo's LICENSE)

**Model 1, ages about 9 and under.**

![Bukang-liwayway v3.4](hand-hero.jpg)

This is a wrist-driven hand shaped from a real child's hand: a MakeHuman child model, smoothed and grown slightly so the shell is strong. Bending the wrist down pulls four braided lines, and the fingers close. Bending it back lets elastic cords open them again. The thumb clicks into one of three grip positions (open, middle, pinch) and is locked by a knob you turn by hand, no tools.

This is Model 1, Bukang-liwayway. The same realistic hand will be the starting point for Sinag (stronger grip and tensioner) and Tanghali (motor).

## What changed in v3.4 (from printing v3.3)

| Fix | What it does |
|---|---|
| Thumb mount braced | The thumb's hinge barrel used to hang over an open window, joined to the palm only at the knob end, so it started in mid-air when printed and came out loose or distorted (and supports scarred it). Everything the thumb doesn't use is now filled solid back to the palm wall; only the slot the thumb swings in stays open. The barrel now grows straight up out of the palm when printed. New script `cad/brace.py`. |
| Bigger click teeth | **12 teeth, 1 mm tall, 30° apart** (were 18 × 0.45 mm, 20°), on a wider ring on both the thumb and the palm, so they print clean and hold. 3 thumb positions: open, middle and pinch. |
| Thumb knob | Lifts 1.4 mm before its clip stops it (was 1 mm), so the taller teeth come free; 0.4 mm taller. Same M3 × 20 hex bolt, same use. |
| Support blocker | Now also fills the thumb slot and the bolt hole, so the slicer puts no support on the slot faces, the teeth or the bore. |
| Guides | Both PDF guides updated for v3.4 (new thumb knob page with the 3 clicks). |

## What changed in v3.3 (after the v3.2 test print)

| Fix | What it does |
|---|---|
| Thumb lock and knob | The thumb tongue and its mount have a ring of matching teeth, so the thumb clicks into set positions (20° apart) and can't slip. It is held by an **M3 × 20 hex bolt** whose head is pressed into a **hand knob** (`thumb-knob.stl`) that clips onto the mount: turn it back about 2 turns, swing the thumb one click, tighten by hand. The clip stops the knob coming right off. The bolt threads into a brass insert in the thumb. |
| Index knuckle | The insert moved to the index's **outer** arm, under the axle head, so tightening the M3 × 45 axle can no longer squeeze the index onto the palm and bind it. |
| Little finger | Bulked out so both its joints take the same **M3 × 12** as the other fingers (no more M3 × 10). |
| Palm cover | No snap pegs and no glue: **12 flush M3 × 5 flat-head screws into brass inserts all round** its edge. The wrist-end mouth of the cover is flared wider, like a glove, so the hand slides in more easily. |
| Wrist | Brass inserts in both ear pads; the two M3 × 6 wrist screws thread into them (blue threadlocker), so the hinge can't wear loose. Ear pads slightly bigger. |
| Pinhole in the palm | A tunnel mouth at the little finger's return cord broke through the surface as a small slit; it is now closed. Every line tunnel has at least 1 mm of plastic round it, checked by two new tests (`check_pits.py`, `check_tunnel_roof.py`). |
| Art holder (new, optional) | One TPU part, no screws (`art-holder.stl`): a sleeve that slides onto the index finger's middle segment with a tube on the thumb side. Push a pencil, pen, crayon, marker or paintbrush in; soft fins inside hold anything about 4.5–11.5 mm across. |
| Guides | Both PDF guides rewritten for v3.3. |

| | |
|---|---|
| ![Back of the hand](hand-back.jpg) | ![Palm side with the TPU cover and its 12 screws](hand-palm.jpg) |
| ![Side, with the cuff](hand-side.jpg) | ![Open wrist end](hand-open-wrist.jpg) |

> **Print at 100% only for now.** Never scale the STLs in the slicer: the screw holes, insert pockets and joint gaps would change size. Ready-made size sets, each with its own hardware card, come after the test fit.

## Guides

Both guides describe **v3.4**. For a size other than 100%, use the screw and insert list in that size's [`stl/HARDWARE.md`](stl/HARDWARE.md).

- [Printing and assembly guide (PDF, v3.4)](printing-and-assembly-guide.pdf)
- [Illustrated printing, assembly and stringing guide (PDF, v3.4)](assembly-and-stringing-illustrated.pdf)

## Size at 100%

| | |
|---|---|
| Child's hand the shape was made from | about 55 mm across the knuckles, 129 mm from wrist crease to middle fingertip |
| Wrist circumference (child) | about 97 mm, with a 1 mm liner gap inside the shell |
| Forearm circumference (child, mid-forearm) | about 110 mm, with a 1.5 mm liner gap inside the cuff |
| Child's palm length that fits | up to about **49 mm** from the wrist crease. The knuckle block in front of that holds the finger joints. |
| Finished hand | about 7 mm wider and 7–8 mm thicker than the child's hand (shell walls and liner) |

> [!CAUTION]
> **Always wear eye protection** when building or finishing the parts. Snipping supports and necks, drilling, trimming and cutting line can flick sharp bits of plastic into your eyes. The soldering iron for the inserts runs at about 240 °C: keep it in its stand and never leave it on alone. Print, set inserts and glue (E6000) in a room with fresh air. Keep cutters, the iron and loose screws away from small children: small parts are a choking risk.

> **Small parts, fiddly steps.** Many parts are small and need careful finishing: snipping supports, hand-drilling holes, setting hot brass inserts, threading thin line and tightening small screws. If you're building the hand for yourself (a teenager printing their own, say) and your grip or fine finger control is limited, ask someone to help with those steps. Children should always have an adult for the soldering iron and the cutters.

## Files (`stl/`, already turned to print direction)

| File | Part | Material | Qty | Supports |
|---|---|---|---|---|
| `palm_back_print.stl` | **Print this one:** the back of the hand (knuckles, thumb mount braced solid to the palm with its ring of teeth, wrist ears, line tunnels, logo, step for the cover) with a snip-off support under the wrist-end rim built in | PETG | 1 | Yes, normal supports, **with the blocker below**; 5 mm brim |
| `palm_back_print_support_blocker.stl` | Support blocker for `palm_back_print.stl`: keeps the slicer's supports out of every hole, line tunnel, the rim and the thumb hinge (slot, teeth, bolt hole). Same coordinates as the part, load the two together | — | — | — |
| `palm_back.stl` | The same back of the hand without the print aids (for reference) | PETG | — | — |
| `palm_flap_print.stl` | **Print this one:** the TPU palm cover with snip-off support fins and a 0.6 mm sole bar built in | **TPU 95A** | 1 | Build plate only (few or none); 5 mm brim |
| `palm_flap.stl` | The same cover without the print aids (for reference) | TPU 95A | — | — |
| `thumb.stl` | Thumb with its toothed tongue, pad and nail | PETG | 1 | Yes, **on the build plate only**; stands at 45°, with a brim |
| `thumb-knob.stl` | Thumb knob (clips onto the thumb mount; the M3 × 20 hex bolt head presses into it) | PETG | 1 | None |
| `finger-<name>-1/2/3.stl` | Finger segments (little finger has 2); tip segments have a nail you can paint | PETG | 1 of each (11) | Yes, **on the build plate only**; stand at 45°, nail side up, with a brim |
| `cuff.stl` | Forearm cuff: low tensioner swelling with flush line clamps, strap slots, vents | PETG | 1 | Few |
| `art-holder.stl` | Art holder, optional | **TPU 95A** | 1 | None; print slowly |
| `HARDWARE.md` | Hardware card for this size: every screw and insert | — | — | — |

**Print settings:** PETG (never PLA, it softens in the heat), 0.4 mm nozzle, 0.2 mm layers, 5 walls, 40–50% gyroid infill for the fingers, thumb, knob and back, 30% for the cuff. TPU cover and art holder: slow (20–30 mm/s), little or no retraction, 4 walls, 4 top and 4 bottom layers, 30% gyroid. Optional fuzzy skin on the cover's outer grip face only, kept off the 12 screw countersinks. Don't run the slicer's mesh repair or "remove small features" on any file.

### Supports

- **Screw holes never need support.** Every screw hole prints lying sideways and is small (2.6–3.4 mm, with 6.2 mm head recesses), so each layer only bridges a few millimetres over the top of the hole.
- **Fingers and thumb:** supports **on the build plate only**. That removes every support the slicer wants inside the screw holes; the supports that start on the bed under the low knuckle end stay.
- **Back of the hand:** it stands on its wrist end, so the line tunnels run almost straight up, but the rim across the back floats about 8 mm up. `palm_back_print.stl` holds that rim on 14 small posts with 0.8 mm necks on a thin sole. Keep normal supports on and load `palm_back_print_support_blocker.stl` with it (it also keeps supports out of the thumb hinge; the thumb mount is braced to the palm and needs none under it):
  - **Creality Print / OrcaSlicer / PrusaSlicer:** drag both files in together and answer **Yes** to loading them as one object with multiple parts. Right-click the blocker part → **Change type → Support blocker**.
  - **Cura:** turn off "Automatically drop models to the build plate" and "Ensure models are kept apart" before loading, so both keep their positions. Select the blocker → **Per Model Settings** → **Don't support overlaps**.
- **After printing the back:** snip each neck flush at the rim, lift the support off and sand the marks smooth. Check that every tunnel exit on the rim is clear before threading.

## Hardware

All stainless M3, no nuts. This is the 100% list; [`stl/HARDWARE.md`](stl/HARDWARE.md) has the list for the size you print.

| Item | Qty | Use |
|---|---|---|
| M3 × 45 **button-head** screw | 1 | Knuckle axle: in from the index side through the index, middle and ring knuckles, into the insert in the index's outer arm |
| M3 × 12 button-head screw | 8 | Middle and tip joints of the index, middle and ring fingers; the little finger's knuckle and tip joint |
| M3 × 20 **hex-head** bolt (DIN 933, fully threaded) | 1 | Thumb knob: head pressed into the knob, threads into the insert in the thumb |
| M3 × 6 button-head screw | 2 | Wrist hinge, into the inserts in the ear pads (blue threadlocker) |
| M3 × 5 **countersunk (flat-head)** screw | 12 | Palm cover, all round its edge; they sit flush |
| M3 × 4 countersunk (flat-head) screw | 4 | Line clamps in the tensioner swelling; they sit flush |
| M3 brass **heat-set insert**, 4.2 mm across × 4 mm long (double-knurled) | 16 | Index knuckle outer arm 1, thumb 1, cover step 12, wrist ear pads 2 |
| Blue (medium, removable) threadlocker | a drop each | Knuckle axle and the 2 wrist screws |
| PE braided fishing line #4, 50 lb (about 0.32 mm) | about 2 m | 4 flexor lines |
| 1 mm round elastic cord | about 1.5 m | 4 return cords |
| Bicycle inner tube, about 1 mm | 1 small piece | 5 grip pads |
| E6000 or contact cement | a little | Gluing the grip pads |
| Hook-and-loop strap, sew-on, 25 mm | 2 | Cuff |
| Thin cotton sock or stockinette (tube gauze) | 1, plus spares | Liner worn on the hand and forearm; wash daily |

One 2 mm hex key fits every button-head and flat-head screw; the thumb needs no tool.

## How it goes together

The PDF guides have every step in detail with pictures. In short:

1. **Set the 16 inserts** at about 240 °C for PETG, each from outside and flush: index knuckle outer arm, thumb tongue (from the toothed face), 12 in the cover step, 1 in each wrist ear pad.
2. **Clean the holes.** Run a 3.5 mm drill bit by hand through the 3.4 mm holes the screws slide through. **Don't drill the 2.6 mm pilot holes.** Run an M3 screw through every pilot hole once.
3. **Fingers:** each joint is a barrel in a cup on one M3 × 12, head flush in its recess.
4. **Knuckle axle:** M3 × 45 from the index side through the three knuckles into the index insert, with threadlocker. The little finger has its own M3 × 12.
5. **Thumb:** press the hex bolt's head into the knob, fit the thumb tongue into the mount (teeth to the knob side), push the bolt through, start the thread, click the knob over its rim, swing the thumb to the click you want (3 clicks, 30° apart) and tighten the knob by hand.
6. **Return cords, then flexor lines,** from the fingertip knot pockets through the channels and tunnels to the wrist end.
7. **Wrist:** the two M3 × 6 through the cuff arms into the ear inserts, threadlocker, tightened only until the cuff swings freely.
8. **Tensioner:** feed each line through the cuff, pull snug with the wrist straight and fingers open, and pin it with its M3 × 4 clamp screw.
9. **Grip pads:** inner tube glued into the fingertip and thumb recesses; cure 72 h before wearing.
10. **Palm cover:** lay it in its step and fit the 12 M3 × 5 flat-heads until flush. Don't overtighten. The cover stays on; the hand goes in through the wrist end.
11. **Straps and liner.**

**Art holder (optional):** slide it over the index fingertip onto the middle segment, tube on the thumb side, and push the tool in from the back, point forward. Set the thumb to its pinch click while it is on.

## Putting it on and caring for it

- Pull the liner (sock) on, slide the hand in through the open wrist end, then do up the cuff straps.
- **Check the child's skin every day,** especially in the heat. A closed shell hides red marks and pressure spots. If you see a mark that doesn't fade within about 20 minutes, stop using the hand until it has been checked.
- Wash the cover and shell with soap and water and let them drain and dry; wash the liner daily.
- If you can, fit the first few hands with a physical therapist or prosthetist. Every residual limb is different.

## Tested in CAD

- **Fingers:** no collisions with the fingers straight, at 30° and at 60° per joint.
- **Wrist:** the hand swings from about 52° down to 30° up with nothing rubbing, cover included.
- **Pinch:** the thumb (in its pinch click) meets the index fingertip at about 49–55° of finger curl.
- **Thumb:** clear of the palm in every click and when loosened; between clicks the teeth lock; the knob clears the palm and thumb at 0 and 1.4 mm lift, and its clip catches.
- **Thumb mount:** solid to the palm (no part of it starts in mid-air in print orientation), clear of the thumb's whole swing, the index finger, the child's hand and the cover.
- **Knuckle axle:** the path is clear through all three knuckles.
- **Line tunnels:** at least about 1 mm of plastic round every tunnel; no openings in the surface except the designed ones.
- **Print checks:** every STL is one closed, watertight solid.

**On the v3.4 print, check:** the thumb mount prints solid and clean with the new blocker; the 12 teeth print sharp on the thumb and the palm; the knob and clicks (does it hold in a hard pinch?), the axle with the moved insert, the 12 cover screws, the wrist inserts, threading, how far the fingers close, the pinch, getting the hand in and out, and the art holder.

## Source (`cad/`)

The hand is generated from the MakeHuman model by Python scripts (trimesh, manifold3d, scikit-image, scipy, shapely, embreex). Run `build_all.sh` to rebuild everything and run the checks (also needs fast_simplification).

| Script | Step |
|---|---|
| `extract.py` | Cuts the right arm out of the MakeHuman body and turns it into the hand frame |
| `skin.py` | Outer skin and child cavity |
| `thumb_solve.py` | Thumb pinch pose and hinge axis |
| `fingers2.py` (+ `fingers.py`, `joints.py`, `fingerskin.py`) | Finger segments: filleted barrel joints, screw holes, line channels, fingertip recesses and nails |
| `palm2.py` (+ `palm.py`, `cavity.py`) | Back of the hand, TPU palm cover with its 12 screw bosses, thumb |
| `thumb_lock.py` | Ring of 12 teeth on the thumb tongue and mount, the thumb insert, the clip-on knob (`thumb-knob.stl`), and the thumb-hinge support keep-out |
| `brace.py` | Fills the space round the thumb barrel back to the palm, clear of the thumb's swing, the index finger, the child's hand and the cover (called by `thumb_lock.py`) |
| `cuff2.py` | Forearm cuff with the tensioner swelling, line channels and clamps |
| `art_holder.py` | The optional art holder (`art-holder.stl`) and its fit checks |
| `sdf.py`, `sdfparts.py`, `lib_grid.py`, `rlib.py` | Smooth-shape (distance field) helpers |
| `orient.py`, `clean_stl.py` | Print orientation and clean STLs |
| `flap_print.py` | Adds the snip-off support fins and sole bar to the palm cover (`palm_flap_print.stl`) |
| `back_print.py` | Adds the snip-off rim support to the back of the hand (`palm_back_print.stl`) and makes its support blocker (holes, tunnels, rim, thumb hinge) |
| `hardware_card.py` | Writes `stl/HARDWARE.md` (screw lengths and inserts for this size) |
| `check_pits.py` | Looks at every part from six directions for holes or pits in the surface that aren't designed openings |
| `check_tunnel_roof.py` | Measures the plastic round every line tunnel from inside the tunnel |
| `check_*.py` | The other checks above |

`src/right-arm-oriented.stl` is the extracted arm, so the build can run without the full MakeHuman body. `src/logo_rects.json` is the pressed-in logo pattern.

## Change log

- 2026-10-18: v1 test print (boxy, kernelCAD) and v2 (organic CadQuery shapes). Both are superseded and removed; they are in the git history.
- 2026-10-19: v3, realistic hand. Shape from a MakeHuman child hand. Barrel joints follow the knuckle creases. Closed palm with a PETG back and a TPU flap closed by a tuck tongue and four tabs. Rubber grip pockets, crease vents and a drain. Hidden line tunnels and return cords. Logo on the curved back. Thumb on a friction hinge set by one screw. Knife edges trimmed and tunnel mouths rounded.
- 2026-10-19: v3.1. Every part rebuilt as smooth shapes: polished skin (no lumps or crease), rounded seams and edges, filleted tongues, barrels and knobs, no knife edges or thin rims, stray webs removed at the knuckle/thumb junction. Flap: straight rounded thumb-side edge, six knob tabs (tuck tongue removed). Cuff: tensioner is now a low, symmetric swelling (2.8 mm) centred on the forearm, clamps are flush M3 × 4 flat-head screws, rounded strap slots and vents, wrist clearance to 55° down. Back of the hand: logo centred and moved clear of the wrist end (34 mm), separate line hump replaced by a broad low swelling, surfaces polished.
- 2026-10-23: v3.1c. Flap closure redesigned: no knobs; the flap's edge lies flush in a recessed step, screwed on the little-finger side (3 × M3 × 4 flat-head) and closed with thin hook-and-loop elsewhere. Every line channel and tunnel is now cut into the smooth shape, so each exit is a rounded flare (no distorted holes); channels enlarged to 1.5–1.8 mm. Joints strengthened: 2.6 mm or more of plastic under every screw head, heads flush, blind pilot holes, thicker tongue rings, thin hoods trimmed. Final rounding pass on every part (nothing thinner than about 1.2 mm), shell walls round the cavity at least about 2.5 mm, separate vent slots, grip pads glued into plain recesses. Later the same day: thumb hinge eye joined to the thumb by a long filleted neck; cuff line channels follow the thick part of the tensioner wall and turn out through flared mouths; cuff clamp countersinks corrected (they were cut upside down); strands, ropes and thin fins removed from the back (nothing under 1.8 mm) and flap (nothing under 1.4 mm); flap laps simplified to clean rounded areas; vents kept 4 mm inside the flap's edge.
- 2026-10-23 (evening): v3.1e. Palm side redone: thin TPU cover with one even flush lip all round, 3 hinge screws on the little-finger side and snap bumps elsewhere (no hook-and-loop, no vents or pad pockets on the cover; raised oval grip instead); no seam swelling. Fixed: MCP tongue screw bores (were missing), wrist ear pilot holes (were 4.75 mm off the axis), cuff thumb-side hinge arm (was cut away), cuff vents (single slots), jagged fingertip recess rims. Logo smaller and nearer the knuckles.
- 2026-10-24: v3.1f. Cover opening made symmetric with an even step all round; cover is one clean piece (stray loops at its edge removed) with its 3 hinge screws, now M3 × 5. Knuckle tongue bores round and clean. Thumb-mount hole on the back closed. Cuff arms trimmed to the hand's swing so nothing sticks out; cuff lines enter at the front end and leave inside the cuff, so only the four clamp seats show on top (now staggered, each a separate round seat). Every finger joint hole goes all the way through. Shallow fingernails on every fingertip and the thumb.
- 2026-10-24 (later): v3.1g. Screw list corrected (9 × M3×12, 3 × M3×10, no M3×8). Cover snaps are now bigger push-through pegs (3 mm shaft, 4 mm mushroom head) that lock in recesses on the inside of the step. Knuckle screw holes fixed: each hole was drilled endlessly and cut a second, off-centre hole through the neighbouring knuckles; now each stops at its own knuckle, with a clean round ring round it.
- 2026-10-25: v3.2, fixes from the first full print. Shared M3 × 45 knuckle axle for index, middle and ring; open wrist end with rounded edges; much bigger line holes (2–3 mm) with funnel mouths; thumb hinge M3 × 20 deep in solid plastic, new thumb pad and nail; nail dips filled flush; heat-set inserts in the index knuckle and the cover step; cover screws centred on a wider hinge edge and the cover corner fixed; cuff trimmed separately to the hand and the cover; fingers and thumb print at 45°; hardware card per size.
- 2026-10-25 (later): print version of the back of the hand (`palm_back_print.stl`) with a snip-off rim support that keeps clear of the line tunnel exits, plus a matching support blocker; support notes for every part (screw holes need none; fingers and thumb on the build plate only); clean the 3.4 mm holes with a 3.5 mm drill.
- 2026-10-26: both PDF guides updated for v3.2 (knuckle axle, heat-set inserts, 45° printing, print versions and support blocker, open wrist end, hardware card, new grip pad sizes); the illustrated guide has new print-layout, insert and stringing pages.
- 2026-10-26 (later): support blocker fixed. The first version also filled the opening under the thumb mount, so that overhang printed without support and came out loose (the thumb screw could not bite). The blocker now covers only the line tunnels, the small holes and the rim; every overhang that needs support is left open for the slicer. Reprint the back of the hand with the new `palm_back_print_support_blocker.stl`; `palm_back_print.stl` itself is unchanged.
- 2026-10-30: v3.3, fixes from the v3.2 test print. Thumb: ring of teeth for set positions, held by a tool-free clip-on knob on an M3 × 20 hex bolt into a brass insert. Index knuckle insert moved to the outer arm so the axle can't bind the index. Little finger bulked out for M3 × 12. Palm cover held by 12 flush M3 × 5 screws into inserts all round (snap pegs removed, no glue), with a wider glove-like mouth at the wrist end. Brass inserts in both wrist ear pads. Slit at the little finger's return-tunnel mouth closed; new surface-pit and tunnel-wall checks. New optional TPU art holder. Both PDF guides rewritten for v3.3; new pictures.
- 2026-10-31: v3.4, from printing v3.3. Thumb barrel braced solid to the palm (it hung over an open window and printed loose); 12 bigger click teeth (1 mm, 30°, 3 positions) on the thumb and the palm; knob lifts 1.4 mm; support blocker also covers the thumb hinge; both PDF guides updated; new pictures.
