![AutoPooper 3000](autopooper-logo.png)

# AutoPooper 3000

**Status:** In development · **Designer:** Hoofie Puppet
**License:** (c) 2026 Hoofie Puppet, CC BY-NC-SA 4.0 (see the repo's LICENSE)
**Shopping list:** [bill-of-materials.md](bill-of-materials.md) · **Logo:** [LOGO.md](LOGO.md)

A 3d printed, Arduino-controlled cat litter box built round a rotating drum about 600mm across. It works like a toilet: press and hold the button and the drum turns, sifts and drops the clumps into the receptacle. **It never cycles on its own.** A person always starts the flush.

## How it works

```
 cat uses the drum  ->  person holds the flush button (~1 s)
                            |
          radar sees a cat? ---- yes --> flush refused
                            | no
          receptacle full?  ---- yes --> blinking amber, flush refused
                            | no
 NEMA23 gearmotor --belt 2:1--> drum turns to the 234° dump stop
                            |
 sifter keeps clean litter, clumps drop out the dump hole into the receptacle
                            |
 drum returns home (hall sensor + magnet), fill sensor checks the receptacle
```

## The two main parts

### The drum
A sphere about 600mm across that turns on four rollers. Comes as **Drum Mark I** (raised logo, one print) or **Drum Mark II** (flush pockets with 18 glued-in logo inlays, e.g. glow-in-the-dark PLA). Everything else on the two drums is the same.

| # | Feature |
|---|---|
| D01 | Front face & logo (Mark I or Mark II) |
| D02 | Night light (rechargeable motion-sensor LED bar, snap-in, no wiring) |
| D03 | Removable two-piece sifter with sponge edge seal |
| D04 | Sifter screws & glued-in brass inserts (9) |
| D05 | Fill lines: MIN 3.5 L / MAX 4 L |
| D06 | Tiles & solvent welding |
| D07 | Dump hole & bristle dust guard |
| D08 | Rear hub spool |
| D09 | Spindle pulley (40T) & home magnet |
| D10 | Rear stub & bearing |

### The container
The base (865 × 650 × 300mm) that holds everything.

| # | Feature |
|---|---|
| C01 | In-slips & rollers (drum rests on 4 rollers) |
| C02 | Spindle bracket & cap (rear hub cradle) |
| C03 | Paw lip (keeps paws out of the drum gap) |
| C04 | Receptacle (clumps land here; paper-towel liner) |
| C05 | Accessories drawer (liner bags + compact scoop) |
| C06 | Sealed electronics bay & RGB flush button |
| C07 | Receptacle-full sensor (VL53L1X) |
| C08 | Cat sensor (HLK-LD2410C radar under the bowl) |
| C09 | Belt drive & guard |
| C10 | Motor bay & wiring |
| C11 | Carbon filter (ACF) |
| C12 | Power inlet (cable gland, fused mains) |
| C13 | NEMA23 gearmotor |
| C14 | Wire route & clips |

## Safety

- Never cycles on its own. Hold the flush button about 1 second to flush.
- The radar refuses a flush if a cat is in or near the drum, and a full receptacle also blocks the flush.
- No screw or sharp edge can be reached by a paw; the paw lip covers the drum gap.
- **Mains wiring by a competent person only.** Mains is fused (T3.15A slow-blow) before the power supply; earthed cord through a cable gland.
- Solvent welding: half-face respirator (3M 6200 + 6001 or 60921 cartridges), ventilated space.
- No stick-on / adhesive-backed parts anywhere (hot, humid climate). Screws, glued-in inserts, snap fits or epoxy only.

## Naming

- Use only **Drum Mark I** and **Drum Mark II** for the two drums, never file version numbers.
- The waste tray is the **receptacle**; the small front-left drawer is the **accessories drawer**.

## Printing

### Print Settings & Infill (Where It Has To Be Solid)

Everything is PETG (dark charcoal matte) unless it says otherwise. Default: 3 walls / 5% infill. Dry the filament at 50°C for 12 hours first, every time. "Modifier" means a slicer modifier shape loaded with the part (load both files together, answer Yes to "single object with multiple parts", change the shape to Modifier, set 100% infill).

| Part | Walls / infill | Notes |
|---|---|---|
| Drum (all tiles), Mark I (raised logo) or Mark II (flush inlays) | 3 walls / 5% | Pick one drum; same tiles and cut rules |
| Drum Mark II: logo inlays | 100% | Separate plate, already face-down. Glow-in-the-dark PLA (or any colour), elephant-foot comp. 0.15, no brim; glued in flush with epoxy |
| Drum tiles with the 9 sifter insert holes | 100% round each hole (drum insert-zone modifier) | Or print those tiles at 40% gyroid, 4 to 5 walls |
| Drum tile(s) holding the rear hub (Ø120 hub + both flanges) | 100% | Steel bearings roll on it |
| Sifter slot half + hollow half | 3 walls / 5%, feet 100% (boss modifiers) | Or about 7 walls. Never edit the feet |
| Sifter screen | 3 walls / 5% |   |
| Spindle pulley (40T) | 100% | Real print: 240.56 g, 8h 49m |
| Rear stub plate | 100% |   |
| Shaft collars (5) | 100% | Outer face down, no supports |
| Spacer rings (9) | flat, 3 layers at 0.2mm |   |
| Roller sleeves (4) | TPU, 2 to 3 walls / 100% | Slow, little or no retraction |
| In-slips L + R | default | Print standing upright |
| Spindle bracket | 4 walls / 40% gyroid | Base down (it carries the belt load) |
| Retainer cap | as the bracket |   |
| Rear support + its cap | 4 walls / 40% gyroid | Base down; tie tunnels bridge, no support |
| Belt guard | 3 walls | Roof down |
| Container | 3 walls / 5% | Cut into 6 pieces (see splitting below) |
| Receptacle tray + lid + handle | 3 walls / 5% | Tray split in 2 |
| Accessories tray + lid + handle | 3 walls / 5% | Lid laid flat, countersunk face up |
| EB lid | 3 walls / 5% | Top face up |
| RP lid (rear panel) | 3 walls / 5% | Outer face up |
| Power tray + control tray | 3 walls / 15% |   |
| Fill-sensor cap | 3 walls / 20% | Top face up |
| Cat-sensor carrier | 3 walls / 15% | Plate down |
| Radar test covers + drum plate | 100% | Same skin as the real container |
| ACF divider grille + rear vent panel | 3 walls / 20% | Flat |
| Night-light diffuser | 100% | White or natural PETG, face down |
| Wire clips | 100% | Lying flat on the C-shaped face |
| Push-to-flush sign | two colours | Swap filament at 3mm; glued in |
| Nameplate | two colours | Swap filament at 4mm; glued in |
| Bristle dust guard | TPU 85A: base 30% gyroid 4 walls, bristles 0% / 2 walls | 15mm brim |


### Slicing The Logo Inlays (Drum Mark II)

The 18 inlays come as one plate (Logo_Inlays_v1_PrintPlate_facedown.stl, 178 × 85mm). They are already laid face-down: the side you see on the drum is the side on the bed, so they look mirrored from above. That is correct. Import and slice as they are. One colour per piece, so no filament swap is needed. Change these settings for this print only; everything not listed stays on your regular profile.

| Setting | Value | Why |
|---|---|---|
| Orientation | As exported. No auto-orient, no "lay on face" | The face must be on the bed |
| Profile | Regular (not ultrafast) | Clean letter edges; same profile as the drum so the fit matches |
| Infill | 100% (sparse and internal solid infill about 100mm/s) | Solid pieces seat flat, glue well and glow evenly |
| Elephant-foot compensation | 0.15mm | The face is the first layer; a flared edge catches at the pocket mouth |
| Brim / skirt | None touching the parts | A brim leaves a lip on the face edge |
| Ironing | Off | It would only smooth the hidden back |
| Outer wall speed | 30–40mm/s | The letter outline is what you see round each letter |
| Inner wall speed | about 80mm/s |   |
| First layer speed | about 20mm/s | An even face |
| Top surface speed | default | Hidden back side |
| Supports | None | Flat 2mm pieces |
| Glow-in-the-dark PLA | 5–10°C hotter than normal PLA (often 210–220°C), moderate retraction, dry spool, nozzle 0.4mm or bigger | The glow powder makes it flow less easily and can clog small nozzles |
| Flow | drop 2–3% if edges come out fat or rough |   |
| Nozzle | Hardened tip (the Unicorn nozzle is fine) | Glow powder is abrasive; purge with normal filament afterwards |
| Bed surface | Your choice | It becomes the face finish: smooth plate = glossy, textured PEI = matte |
| Removing | Let the bed cool first | Thin 2mm pieces bend if pried off warm |
| Fit test (optional) | Inlay_FitTest_Coupon_v1.stl upright as exported, PETG, regular drum profile, 3 walls / 5%; its inlays in the inlay filament | Rows: 1 dot = 0.10, 2 = 0.15, 3 = 0.20mm per side. The drum uses 0.15 |


### Splitting: Drum Tiles

The drum is cut into tiles in the slicer. Load the drum and its insert-zone modifier together first, then cut, so each tile keeps its little solid cylinders. Never cut within 10mm of an insert-hole centre. Send the planned cuts to check before printing.

| Cut direction | Safe | Avoid |
|---|---|---|
| Height (Z, as exported) | 0–55, 115–211, 235–272, 297–363, 526–600mm | 55–99 fill lines + labels; 72–114 paw; 211–235; 272–297; 363–392; 398–525 logo (or pockets) + light cradle |
| Front-to-back (Y) | below 123, 196–235, 255–276, 296–305, 326–335, 356–393, above 440 (subtract 23 when measuring from the drum edge in the slicer) | the front lip and light cradle (below 76), the groove ring (84–89), 123–176 and 393–440 (MIN/MAX labels) |
| Side-to-side (X) | below 586 or above 662 | 586–662 (sifter area); 177–233, 345–393, 506–562 (labels); 185–559 through the front face |


### Splitting: Container

The container (865 × 650 × 300mm) is too big for a 400mm bed. Grid cut 3 · 2 · 1 with planes at X −83, X 286 and Y 25: 6 pieces, the biggest 387 × 350 × 300. Plug connectors, Close cut on, Lap if possible. Glue with THF PVC solvent cement, respirator on. Keep every seam 10mm clear of:

| Keep clear of | Why |
|---|---|
| Spindle-bracket seat and its holes | Carries the drum and the belt pull |
| In-slip pockets and their 4 insert holes | Roller fit |
| Cat-sensor pocket, cover rebate and pilots | Radar skin must stay even |
| Fill-sensor pocket, cap rebate and pilots |   |
| EB lid inserts (8) and bay-floor inserts (8) |   |
| ACF rebate, duct, fan holes and panel inserts | Air seal |
| RP lid pilots (4) |   |
| Accessories bay and lid recess | A seam would leave a step inside the drawer bay |
| Wire-trunk ports, sensor wire channels, paw lip | Better avoided; a glued seam through them is OK |


## Build order (summary)

1. Dry all filament (50°C, 12 hours).
2. Bench-test the radar with the printed test covers and a tub of litter before printing the container.
3. Print and weld the drum tiles; glue in the sifter inserts; colour the fill lines last.
4. Print the container in 6 pieces and weld them; glue in all container inserts.
5. Fit the in-slips and rollers, spindle bracket, rear support and belt drive; lower the drum in; fit the cap and belt guard.
6. Wire the electronics bay (mains by a competent person), set the buck converter to 5.0V before connecting the Mega.
7. Fit the receptacle, accessories drawer, carbon filter, sensors and night light; test the flush with no cat present.

Full step-by-step details for every part are in the AutoPooper 3000 build explorer on the Hoofie Puppet's Workshop BBS website.
