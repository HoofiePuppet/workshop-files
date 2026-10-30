# Sol Prosthetics — Bill of Materials

**Status:** Bukang-liwayway v3.3 (realistic) test print · **Updated:** 2026-10-30
Quantities are for one Bukang-liwayway v3.3 hand ([bukang-liwayway/](bukang-liwayway/README.md)) at 100%.
Sourcing: Lazada PH / Shopee PH / local hardware store unless noted.

## A. Buy — Models 1 and 2 (mechanical)

| # | Item | Qty per hand | Spec / what to look for | Status |
|---|------|--------------|--------------------------|--------|
| A1 | PETG filament | ~100–135 g + supports | Any colour; skin tones look most natural; bright colours if the child wants. Colour depends on what filament is in stock and can be swapped. | To buy |
| A2 | TPU filament | under 10 g (+ a few g for the art holder) | **95A.** For the palm cover and the optional art holder. | To buy |
| A3 | Braided line | ~2 m | PE braided fishing line (not mono), #4, about 50 lb / 0.32 mm. | To buy |
| A4 | M3 × 45 stainless button-head screw | 1 | Knuckle axle through the index, middle and ring knuckles. | To buy |
| A4a | M3 × 12 stainless button-head screws | 8 | Middle and tip joints of the index, middle and ring fingers; little finger knuckle and tip joint. | To buy |
| A4c | M3 × 20 stainless **hex-head** bolt (DIN 933, fully threaded) | 1 | Thumb knob (head pressed into the knob). | To buy |
| A4d | M3 × 6 stainless button-head screws | 2 | Wrist hinge, into inserts. | To buy |
| A4e | M3 × 4 stainless countersunk (flat-head) screws | 4 | Line clamps on top of the cuff. | To buy |
| A4f | M3 × 5 stainless countersunk (flat-head) screws | 12 | Palm cover, all round its edge. | To buy |
| A4g | M3 brass heat-set inserts, 4.2 mm across × 4 mm, double-knurled | 16 | Index knuckle 1, thumb 1, cover step 12, wrist ear pads 2. Other sizes use other lengths: see each size's `HARDWARE.md`. | To buy |
| A4h | Blue (medium, removable) threadlocker | a drop each | Knuckle axle and wrist screws. | To buy |
| A7 | 1 mm round elastic cord | ~1.5 m | Return cords that open the fingers. | To buy |
| A8 | Bicycle inner tube | 1 small piece | 5 fingertip grip pads. Any vulcanizing shop has old tubes. | To buy |
| A9 | E6000 or contact cement | a little | Glues the grip pads. Sand both surfaces dull, clean with alcohol, cure 72 h before wearing. | To buy |
| A5 | Hook-and-loop straps | 2 | Sew-on, **not** stick-on, 25 mm, for the cuff. | To buy |
| A6 | Liner | 1 + spares | Thin cotton sock or stockinette (tube gauze), worn on the hand and forearm; wash daily. | To buy |

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

## C. Print (Bukang-liwayway v3.3)

| File | Part | Qty | Material | Status |
|------|------|-----|----------|--------|
| `palm_back_print.stl` | Back of the hand (with snip-off print supports; load `palm_back_print_support_blocker.stl` with it) | 1 | PETG | v3.3 test print |
| `palm_flap_print.stl` | Palm cover (with snip-off print supports) | 1 | TPU 95A | v3.3 test print |
| `thumb.stl` | Thumb | 1 | PETG | v3.3 test print |
| `thumb-knob.stl` | Thumb knob | 1 | PETG | v3.3 test print |
| `finger-*.stl` | Finger segments (index, middle, ring 3 each; little 2) | 11 | PETG | v3.3 test print |
| `cuff.stl` | Forearm cuff | 1 | PETG | v3.3 test print |
| `art-holder.stl` | Art holder (optional) | 1 | TPU 95A | v3.3 test print |

## Notes

- Print at 100% only for now; never scale in the slicer (screw holes and insert pockets are sized for M3). Sized STLs from the Hand Sizer number come later.
- Keep a few spare finger segments and a spare palm cover printed; they're the parts most likely to wear.
