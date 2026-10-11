# Plan B(idet) — Bill of Materials

**Status:** In design · **Updated:** 2026-10-11
Sourcing: Lazada PH / LazMall unless noted. Exact specs marked **TBD** are settled once the pump is chosen.

## A. Buy

| # | Item | Qty | Spec / what to look for | Status |
|---|------|-----|--------------------------|--------|
| A1 | Diaphragm water pump | 1 | 12V DC, self-priming. Sprayer or RV type; about 60 psi is plenty (the knob turns it down). Check the listed current draw (amps) and barb size. | To buy |
| A2 | PWM DC motor speed controller with knob | 1 | 12V, rated above the pump's current (about 5A+ for a typical spray pump). Must fit inside the handle (PB-03). | To buy |
| A3 | Power switch | 1 | Rocker or latching push button, rated above the pump's current. | To buy |
| A4 | Battery pack | 1 | 12V class: 3S 18650 pack with BMS (11.1–12.6V), or an off-the-shelf 12V rechargeable pack. Must handle the pump's current. | To buy |
| A5 | Battery charger | 1 | Matched to the battery chosen in A4. | To buy |
| A6 | Inline fuse holder + fuse | 1 | Fuse sized just above the pump's running current. | To buy |
| A7 | Battery connector pair | 1 | XT30 or similar, so the battery unplugs for charging. | To buy |
| A8 | Wire | ~2 m | 18 AWG two-core (red/black), for battery → handle → pump. | To buy |
| A9 | Silicone tubing, food-safe | ~2–3 m | ID to match the pump barbs (**TBD**). Suction line + spray line. | To buy |
| A10 | 90° barbed elbow | 2 | Plastic, 4–6mm, to match the tubing. One spare. | To buy |
| A11 | Suction strainer / weighted end | 1 | Keeps the suction tube on the bottom of the bottle and catches debris. | To buy |
| A12 | Cable gland | 1–2 | Small (PG7 or similar), for sealed cable entry into the handle. | To buy |
| A13 | Zip ties / small hose clamps | a few | Secure tubing onto the barbs. | To buy |
| A14 | Screws (+ nuts or heat-set inserts) | **TBD** | For the pump mount, battery holder and handle halves. Sizes set by the pump's mounting holes. | TBD |
| A15 | 5-gallon or 10L water bottle | 1 | Already on hand. | Have |

## B. Print

| ID | Part | Qty | Material | Status |
|----|------|-----|----------|--------|
| PB-01 | Bottle-top pump collar | 1 | PETG | Not designed |
| PB-02 | Battery holder | 1 | PETG | Not designed |
| PB-03 | Control handle (2 halves) | 1 set | PETG | Not designed |
| PB-04 | Sprayer blade | 1 | PETG | Not designed |
| PB-05 | Rim hook liner | 1 | TPU | Not designed |
| PB-06 | Nozzle caps (1.0 / 1.25 / 1.5mm holes) | 3 | PETG | Not designed |

## Wiring (simple version)

```
Battery (+) → fuse → power switch → PWM controller IN (+)
Battery (−) ─────────────────────→ PWM controller IN (−)
PWM controller OUT (+/−) → pump (+/−)
```

The switch and PWM controller live in the handle; the battery and pump sit on the bottle collar.

## Notes

- Buy A1, A2, A4 and A9–A11 first for the bench test. Everything else waits until the test confirms the spray strength.
- An ordinary 5V USB power bank can't run a 12V pump on its own.
