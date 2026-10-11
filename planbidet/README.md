# Plan B(idet) — Parts Repository

*For when the water company has other plans.*

**Status:** In design · **Started:** 2026-10-11 · **Designer:** Hoofie Puppet
**License:** (c) 2026 Hoofie Puppet, CC BY-NC-SA 4.0 (see the repo's LICENSE)
**Shopping list:** [bill-of-materials.md](bill-of-materials.md)

## What it is

A battery-powered backup bidet for water outages. The water in the Philippines can be shut off for hours with no warning, and the power can go out too, so Plan B(idet) needs neither. It runs from a 5-gallon or 10-liter water bottle and a rechargeable battery.

## How it works

```
 [ water bottle ]
       |  suction tube (cut to length, weighted strainer at the bottom)
       v
 [ bottle-top collar ]  <- 12V diaphragm pump + battery mounted here
       |  spray hose
       v
 [ relief valve ]       <- dumps extra pressure back into the bottle
       |
       v
 [ control handle ]     <- power switch, hold-to-spray button,
                           speed knob (PWM controller)
       |  spray hose
       v
 [ sprayer blade ]      <- slips under the seat, beside the existing bidet,
                           hooks over the bowl rim
       v
 [ nozzle cap ]         <- turns 90° inward + angles 30–45° up
```

The pump never goes in the water. It's a self-priming diaphragm pump that sits on the collar above the bottle and pulls water up the suction tube.

## Printed parts

| ID | Part | Material | Status | Notes |
|----|------|----------|--------|-------|
| PB-01 | Bottle-top pump collar | PETG | Not designed | Sits over the bottle neck. Pump bolts on top; suction tube passes down the middle. Lifts off one bottle and onto the next. Needs bottle neck OD + pump mounting pattern. |
| PB-02 | Battery holder | PETG | Not designed | Mounts on the collar (PB-01) with screws, no adhesive. Size depends on the battery chosen. |
| PB-03 | Control handle (2 halves) | PETG | Not designed | Grooved grips on each side. Holds the power switch, the hold-to-spray button and the PWM speed knob. Sealed cable entry (cable gland). Electronics stay dry. |
| PB-04 | Sprayer blade | PETG | Not designed | Flat blade, about 6–7mm thick (existing bidet is ~8.5mm at the lid). Channel holds the silicone tube along its length. Enters beside the existing bidet. |
| PB-05 | Rim hook liner | TPU | Not designed | Slip-on / mechanical fit over the rim hook on PB-04 to protect the porcelain and add grip. No stick-on parts. |
| PB-06 | Nozzle caps (set of 2–3) | PETG | Not designed | Hold the 90° barbed elbow. Hole sizes 1.0 / 1.25 / 1.5mm (never smaller than 1.0mm) to tune spray strength; aim inward 90° and up 30–45°. Swappable. |

## How it attaches to the toilet

- **Chosen approach:** a rim hook plus seat weight. A J/C-shaped hook on the back of the blade drops over the bowl rim to set the position and stop it rotating; the seat sitting on the blade holds it down.
- No tools. It slides out when the water comes back.

## Safety (required in every build)

Too much water pressure can hurt, so Plan B(idet) limits pressure in several independent layers. If one fails, the others still protect the user.

1. **Pressure relief valve (the main safeguard).** A mechanical relief/bypass valve right after the pump. Above its set pressure it opens and dumps the extra water back into the bottle. It works even if the knob is turned all the way up or the electronics fail. Set it low (aim for well under 1 bar / about 15 psi at the nozzle to start; fine-tune in the bench test).
2. **Pick a modest pump.** Don't use the strongest sprayer pump available. Choose one with a moderate max pressure so the worst case is limited from the start.
3. **Hold-to-spray button.** The spray button is momentary: water only flows while it's held. Let go and the pump stops at once. The main power switch stays as a separate on/off.
4. **Speed knob max stop.** Limit the speed controller's top setting (a controller with a max-limit trim, or a fixed restrictor) so full knob is still comfortable. Always start with the knob at its lowest.
5. **Nozzle holes no smaller than 1.0mm.** Smaller holes make a sharper, harder jet.
6. **Hoses that can't pop off.** Tubing rated above the relief-valve pressure, and every barb secured with a clamp or zip tie.
7. **No hot water.** Lukewarm only, and test it on your wrist first. Hot water can scald, and PETG softens when it gets hot.
8. **Electrical.** Fuse on the battery lead; all electrics kept dry and away from the spray.

**Before first use:** spray into the bowl or a bucket, check the relief valve opens, check the spray at full knob is comfortable on the back of your hand, and check that releasing the button stops the water.

## Design rules

- PETG for all rigid parts; TPU only for the rim liner.
- No printed internal water channels. Silicone tubing carries the water and the prints only hold the tubing.
- No stick-on / adhesive-backed parts (hot, humid climate). Screws or mechanical fits only.
- Don't bend the tube 90° at the tip. Use the barbed elbow so the tube doesn't kink.
- Keep all electrics out of the water and away from spray.

## Measurements still needed

1. Seat/lid gap at the exact spot where the new blade will enter (beside the existing bidet).
2. Bowl rim thickness at that spot (for the hook).
3. Distance from the entry point inward to the spray target (about the bowl center).
4. How far forward the nozzle needs to sit from the back of the seat.
5. Bottle neck outside diameter (5-gallon and 10L bottles, if both will be used).
6. Pump body size, mounting-hole pattern and barb size (from the pump once it's chosen).
7. Optional: photo looking down at the back of the seat with the existing bidet in place.

## Open decisions

- Which pump (pressure and current draw).
- Relief valve set pressure (settle in the bench test).
- Which battery: 3S 18650 pack, or an off-the-shelf 12V rechargeable pack.
- Hose inner diameter (set by the pump's barbs).
- Countersunk or not on the collar and handle screw holes (decide when they're designed).
- Heat-set inserts or not, and their pilot holes (decide when they're designed).

## Build order

1. **Bench test first.** Buy the pump, then test it with the bottle, a short hose, the relief valve, the speed controller, the battery and a nozzle before printing anything. Set the relief valve, confirm the spray is strong enough but comfortable, and check the battery runtime.
2. Design and print the sprayer blade, rim liner and nozzle caps (PB-04 to PB-06). Test fit them on the toilet.
3. Design and print the bottle-top collar and battery holder (PB-01, PB-02) around the actual pump and battery.
4. Design and print the control handle (PB-03) around the actual switch and speed controller.
5. Assemble, then do a full test during a normal day before relying on it in an outage.

## Change log

- 2026-10-11: Repository started. Concept, name, attachment approach, pump type (diaphragm, outside the bottle) and battery power decided.
- 2026-10-11: Safety section added (relief valve, modest pump, hold-to-spray button, knob max stop, 1.0mm minimum nozzle hole, secured hoses, no hot water, fuse).
