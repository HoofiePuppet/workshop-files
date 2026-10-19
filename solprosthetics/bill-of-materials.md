# Sol Prosthetics — Bill of Materials

**Status:** Bukang-liwayway v3 (realistic) test print · **Updated:** 2026-10-19
Quantities are for one Bukang-liwayway v3 hand ([bukang-liwayway/](bukang-liwayway/README.md)) at 100%.
Sourcing: Lazada PH / Shopee PH / local hardware store unless noted.

## A. Buy — Models 1 and 2 (mechanical)

| # | Item | Qty per hand | Spec / what to look for | Status |
|---|------|--------------|--------------------------|--------|
| A1 | PETG filament | ~100 g | Any colour; skin tones look most natural; bright colours if the child wants. | To buy |
| A2 | TPU filament | ~10 g | **95A.** For the palm flap. | To buy |
| A3 | Braided line | ~2 m | Braided fishing line (not mono), about 50 lb / 20 kg test. | To buy |
| A4 | M3 × 12 stainless screws | 5 | Finger joints (4) and thumb hinge (1). They thread into the plastic, no nuts. | To buy |
| A4a | M3 × 10 stainless screws | 6 | Finger joints. | To buy |
| A4b | M3 × 8 stainless screw | 1 | Little-finger knuckle. | To buy |
| A4c | M3 × 6 stainless screws | 6 | Wrist hinge (2) and line clamps in the tensioner bump (4). | To buy |
| A7 | 1 mm round elastic cord | ~1.5 m | Return cords that open the fingers. | To buy |
| A8 | Bicycle inner tube | 1 small piece | Grip pads (8) and two thumb-hinge washers. Any vulcanizing shop has old tubes. | To buy |
| A9 | Contact cement (e.g. Rugby) | a little | **Optional.** Backup only, if a grip pad lifts out of its lip. | Optional |
| A5 | Hook-and-loop straps | 2 | Sew-on, **not** stick-on, 25 mm, for the cuff. | To buy |
| A6 | Liner material | 1 piece | Washable foam or mesh, about 1–1.5 mm, for inside the cuff and the back of the hand. | TBD |

## B. Buy — Model 3 (Tanghali, phase 2)

| # | Item | Qty | Spec / what to look for | Status |
|---|------|-----|--------------------------|--------|
| B1 | MyoWare 2.0 muscle sensor | 1 | With electrode pads. | Not yet |
| B2 | Microcontroller | 1 | Small board (e.g. Arduino Nano class). **TBD** | Not yet |
| B3 | Servo or gearmotor | 1–2 | Light, enough torque to close the fingers. **TBD** | Not yet |
| B4 | Battery + charger | 1 | Rechargeable, with protection. **TBD** | Not yet |
| B5 | Fuse + holder | 1 | Sized for the motor. | Not yet |
| B6 | Electrode pads (spare) | pack | Disposable, replace often in the heat. | Not yet |

## C. Print (Bukang-liwayway v3)

| File | Part | Qty | Material | Status |
|------|------|-----|----------|--------|
| `palm_back.stl` | Back of the hand | 1 | PETG | v3 test print |
| `palm_flap.stl` | Palm flap | 1 | TPU 95A | v3 test print |
| `thumb.stl` | Thumb | 1 | PETG | v3 test print |
| `finger-*.stl` | Finger segments (index, middle, ring 3 each; little 2) | 11 | PETG | v3 test print |
| `cuff.stl` | Forearm cuff | 1 | PETG | v3 test print |

## Notes

- Print at 100% only for now (screw holes are sized for M3). Sized STLs from the Hand Sizer number come later.
- Keep a few spare finger segments and a spare palm flap printed; they're the parts most likely to wear.
