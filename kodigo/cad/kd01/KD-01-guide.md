# Kodigo KD-01: Optics Test Rig

**Designer:** Hoofie Puppet · **License:** CC BY-NC-SA 4.0 · **Version:** v1, 2026-11-13

A bench rig for finding the best screen-to-lens distance and splitter angle before designing the wearable module (KD-02). Every part slides on one rail and locks with a single screw. A millimetre scale on the rail shows each part's distance from the lens.

```
  OLED carriage (H)        lens (B)          splitter (D/E on F, G)
  [screen]--- 25-50 mm --->( lens )--- 25-45 mm --->  /  45°
                                                      |
                                                    your eye (look in from the front of the rail)
```

## Parts (print 1 of each unless noted)

| File | Part | Notes |
|---|---|---|
| KD01-A_base_rail | Rail, 160 × 64 mm | Scale engraved on top, nut channel underneath |
| KD01-B_lens_holder | Lens holder | For your 25 mm / 40 mm Cardboard lens |
| KD01-C_lens_retainer_ring | Lens retainer (C-ring) | Squeeze it and push it in behind the lens. Print 2 (they're tiny) |
| KD01-D1 + E1 | Splitter frame + cover, **1.5 mm acrylic** | For the 1 × 1⅜ in acrylic piece with the HUD film on it |
| KD01-D2 + E2 | Splitter frame + cover, **film only** | For the HUD film on its own (0.3 mm) |
| KD01-F_splitter_turret | Turntable | The frame's tab plugs into it. Turn it to set the angle |
| KD01-G_splitter_foot | Turret foot | Degree marks every 5° around 45°; the long mark is 45° |
| KD01-H_oled_carriage | Screen carriage | Its pointer marks the front of the screen glass |
| KD01-J1_oled_adapter_1.3in | 1.3" OLED adapter | **Provisional.** Uses typical board size; check against your screen |
| KD01-J2_oled_adapter_0.96in | 0.96" OLED adapter | **Provisional**, same as J1 |

STEP files are included for editing. `kd01.py` is the parametric source (CadQuery), so I can resize any part from your measurements.

## Print settings

- **PETG**, 0.2 mm layers, 3 walls, 20 % infill, **no supports**. Every file is already oriented flat side down.
- The rail (A) is the biggest print; everything else is small.
- The lens holder (B) prints lying down with the bore vertical, so the lens seat comes out round.

## Hardware

| Qty | Item | Used for |
|---|---|---|
| 3 | M3 × 12 screw + M3 nut | Locking each part to the rail |
| 2 | M3 × 10 screw + M3 nut | OLED adapter to carriage |
| 1 | M3 × 8 screw | Turret lock (threads straight into the plastic) |
| 4 | M2 × 10 screw + M2 nut | OLED board to adapter (0.96" boards may need M1.6 if the holes are small) |

## Assembly

1. **Rail nuts:** turn the rail over. Drop 3 M3 nuts into the channel underneath; it holds them so they can't spin. Turn the rail back over.
2. **Feet:** each part has a groove underneath that fits the raised key on the rail. Set it on the key and screw an M3 × 12 down through the slot into a nut. Snug is enough.
3. **Lens:** drop the lens into the holder's round pocket, then squeeze a retainer ring and push it in behind the lens until it touches. Set the holder's pointer on **0**.
4. **Splitter:** lay the acrylic piece in frame D1 with the **film side up** (toward the cover). Press cover E1 onto the 4 pegs. Plug the frame's tab into the turret, drop the turret into its foot, and line its pointer line up with the long **45°** mark. Lock it with the M3 × 8 screw in the side of the foot.
   - The film side ends up facing the lens and your eye, which is correct.
5. **Screen (when it arrives):** M2 screws go through the board's corner holes and the adapter's slots, with nuts at the back and the header pins at the top. Fix the adapter to the carriage with 2 M3 × 10 screws through the slots.

## Using it

1. Put the screen's pointer at **35 mm** and the splitter at about **30 mm**.
2. Look into the splitter from the front of the rail (the side with the scale), as if it were the lens of your glasses.
3. Slide the screen carriage slowly between **30 and 40 mm** until the text is sharp and comfortable. Closer than ~40 mm makes the text look farther away.
4. Turn the turret a few degrees either side of 45° until the text sits straight in front of you.
5. Use the adjustment slots to centre the screen:
   - **Up/down:** the vertical slots in the carriage (±3 mm).
   - **Sideways:** the slots in the adapter.
6. **Write down** the screen distance, splitter distance and angle that look best. Those numbers set the size of the wearable module (KD-02).

## Measure when your OLEDs arrive

Send me these for each screen and I'll make the exact adapter:

- board width × height
- mounting hole diameter
- hole spacing (centre to centre)
- glass width × height and thickness
- where the header pins sit

## Hidden mark

The identifying mark is engraved in places you can't see once the rig is assembled: under the rail (full text), under each foot and the turret, on the back of the splitter tab, and on the front of each OLED adapter (under the board). The wording (`KODIGO KD-01 HOOFIE PUPPET` / `HP-KD01`) is a placeholder until you choose the final mark. It's one setting in `kd01.py`, so changing it means regenerating the files. The retainer rings and covers are too thin to carry a mark.
