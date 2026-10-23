# Sol Prosthetics — Bill of Materials

**Status:** Bukang-liwayway v3.1g (realistic) test print · **Updated:** 2026-10-24
Quantities are for one Bukang-liwayway v3.1g hand ([bukang-liwayway/](bukang-liwayway/README.md)) at 100%.
Sourcing: Lazada PH / Shopee PH / local hardware store unless noted.

## A. Buy — Models 1 and 2 (mechanical)

| # | Item | Qty per hand | Spec / what to look for | Status |
|---|------|--------------|--------------------------|--------|
| A1 | PETG filament | ~100–135 g + supports | Any colour; skin tones look most natural; bright colours if the child wants. | To buy |
| A2 | TPU filament | under 10 g | **95A.** For the palm cover. | To buy |
| A3 | Braided line | ~2 m | Braided fishing line (not mono), about 50 lb / 20 kg test. | To buy |
| A4 | M3 × 12 stainless button-head screws | 9 | Index and middle (3 joints each), ring middle and tip joints, thumb hinge. They thread into the plastic, no nuts. | To buy |
| A4a | M3 × 10 stainless button-head screws | 3 | Ring knuckle, little knuckle and little tip joint. | To buy |
| A4b | M3 × 6 stainless screws | 2 | Wrist hinge. | To buy |
| A4c | M3 × 4 stainless countersunk (flat-head) screws | 4 | Line clamps on top of the cuff. | To buy |
| A4d | M3 × 5 stainless countersunk (flat-head) screws | 3 | Palm cover hinge edge. | To buy |
| A7 | 1 mm round elastic cord | ~1.5 m | Return cords that open the fingers. | To buy |
| A8 | Bicycle inner tube | 1 small piece | 5 fingertip grip pads and two thumb-hinge washers. Any vulcanizing shop has old tubes. | To buy |
| A9 | Contact cement (e.g. Rugby) | a little | Glues the grip pads into their recesses. | To buy |
| A5 | Hook-and-loop straps | 2 | Sew-on, **not** stick-on, 25 mm, for the cuff. | To buy |
| A6 | Liner material | 1 piece | Washable foam or mesh, about 1–1.5 mm, for inside the cuff and the back of the hand. | TBD |

## B. Buy — Model 3 (Tanghali, phase 2)

| # | Item | Qty | Spec / what to look for | Status |
|---|------|-----|--------------------------|--------|
| B1 | Force-sensitive resistor (FSR), Interlink **FSR 402 Short**, part no. **34-00015** (solder tabs; 34-00017 = female contacts) | 1–2 (+1 spare) | Main muscle sensor: sits in a TPU pocket in the cuff liner over the forearm muscle and reads the muscle bulging (force myography). No electrodes or gel, cheap, two wires to replace. Standard FSR 402 (30-81794) also works; FSR 406 (30-73258, ~38 mm square) for a larger muscle area. Buy genuine Interlink; test one first. | To test |
| B1a | 10 kΩ resistor | 1 per FSR | Voltage divider so the board's analog pin can read the FSR. | To test |
| B1b | MyoWare 2.0 muscle sensor | 1 | **Optional** plug-in, only for a child whose muscle doesn't bulge enough for the FSR. With electrode pads. | Optional |
| B2 | Microcontroller | 1 | Small board (e.g. Arduino Nano class). **TBD** | Not yet |
| B3 | Servo or gearmotor | 1–2 | Light, enough torque to close the fingers. **TBD** | Not yet |
| B4 | Battery + charger | 1 | Rechargeable, with protection. **TBD** | Not yet |
| B5 | Fuse + holder | 1 | Sized for the motor. | Not yet |
| B6 | Electrode pads (spare) | pack | Only with the optional MyoWare (B1b). Disposable, replace often in the heat. | Optional |

## C. Print (Bukang-liwayway v3.1g)

| File | Part | Qty | Material | Status |
|------|------|-----|----------|--------|
| `palm_back.stl` | Back of the hand | 1 | PETG | v3.1g test print |
| `palm_flap.stl` | Palm cover | 1 | TPU 95A | v3.1g test print |
| `thumb.stl` | Thumb | 1 | PETG | v3.1g test print |
| `finger-*.stl` | Finger segments (index, middle, ring 3 each; little 2) | 11 | PETG | v3.1g test print |
| `cuff.stl` | Forearm cuff | 1 | PETG | v3.1g test print |

## Notes

- Print at 100% only for now (screw holes are sized for M3). Sized STLs from the Hand Sizer number come later.
- Keep a few spare finger segments and a spare palm cover printed; they're the parts most likely to wear.
