<img alt="Sol Prosthetics" src="solprosthetics-logo.png" width="300">

# Sol Prosthetics — Parts Repository

*Open-source hands for Filipino kids. Built for the heat.*

**Status:** In design · **Started:** 2026-10-17 · **Designer:** Hoofie Puppet
**License:** (c) 2026 Hoofie Puppet, CC BY-NC-SA 4.0 (see the repo's LICENSE)
**Shopping list:** [bill-of-materials.md](bill-of-materials.md)
**Hand sizer:** on the workshop BBS, Projects page → "Run the Hand Sizer"

## What it is

3D-printed prosthetic hands for children in the Philippines who are missing a hand, from about age 6 to 18 (some adults too). Most families here can't get or afford a prosthesis, so these are designed to be cheap, easy to print, and easy to fix with parts from any hardware store. They are made for a hot, humid climate: no PLA, no glued structure, a washable liner, and parts that won't warp in a hot jeepney.

Sol (sun) because it's hot here.

This is an assistive device, not a medical device. Fit every hand with the child's parent or guardian, and with a physical or occupational therapist whenever possible.

## Official logo

- **solprosthetics-logo.png** is the official Sol Prosthetics logo: a pixel-art mechanical hand with jointed fingers and a sun in the palm, orange rays around it, and "SOL PROSTHETICS" in chunky yellow pixel letters. Black background.
- **solprosthetics-logo-3x.png** is the full-size original (1254 × 1254) for big uses like stickers and banners.
- The black background is part of the design (the yellow doesn't read on white), so it works on both GitHub themes as-is.
- Made 2026-10-17 with ChatGPT from the Sol Prosthetics logo prompt. Always use these files; don't redraw or restyle the logo.
- On the website it's **images/solprosthetics-featured.png**.

## The models

Each model is its own design. The child gets the model for their age; the sizer can override it (a small 12-year-old may fit Model 1 better).

| # | Name | Ages | Type |
|---|------|------|------|
| 1 | **Bukang-liwayway** ("Sunrise") | ~6–9 | Simple mechanical. Light, bright colours. |
| 2 | **Sinag** ("Ray") | ~10–13 | Mechanical, stronger grip, adjustable tension. |
| 3 | **Tanghali** ("High Noon") | ~14–18+ | Motor hand run by a pressure (FSR) muscle sensor in the cuff: no electrodes or gel, cheap and easy to repair. MyoWare as an optional plug-in. |

Models 1 and 2 close the fingers by cable when the child bends the wrist (needs a working wrist and some palm). An elbow-driven version for kids missing more of the forearm is an open decision.

## Sizing

Two measurements of the child's **good** hand:

1. **Width** across the knuckles.
2. **Length** from the wrist crease to the tip of the middle finger.

```
print scale = (child width + child length) ÷ (model width + model length at 100%)
```

Round **up** to the next 5% so the child grows into it. Optional: measure around the thickest part of the affected forearm to check the cuff (forearm + 10 mm liner vs. the cuff's inside circumference at that scale).

The Hand Sizer page does all of this and makes a fitting card to keep for refits. **The model sizes in the sizer are placeholders** until each model is designed; update them in the sizer's SysOp setup.

This replaces the Enabling the Future multi-hand spreadsheet, which works out to the same formula.

## Printed parts

**Newest: Bukang-liwayway v3.2 (realistic), test print, [bukang-liwayway/](bukang-liwayway/README.md).** Shaped from a real child's hand, with a closed palm (rigid PETG back + thin TPU cover that screws on along one edge and snaps shut, open at the wrist end so the hand goes in), one knuckle axle for three fingers, brass heat-set inserts, rubber grip pads, fingernails, hidden lines and the logo on the back. Printing, assembly and stringing guides (PDF, still v3.1g; the v3.2 hardware card is `stl/HARDWARE.md`) are in the same folder. The same realistic hand will be the starting point for Sinag and Tanghali.

![Bukang-liwayway v3.2](bukang-liwayway/hand-hero.jpg)

All parts are in [bukang-liwayway/](bukang-liwayway/README.md). Part IDs: SP1 = Bukang-liwayway, SP2 = Sinag, SP3 = Tanghali.

| ID | Part | Material | Status | Notes |
|----|------|----------|--------|-------|
| SP1-01 | Back of the hand (`palm_back.stl`) | PETG | **v3.2 test print** | Realistic shape, logo pressed into the back, knuckle block with the finger joints and the knuckle axle, thumb mount, hidden line tunnels, wrist ears, flush step for the cover. |
| SP1-07 | Palm cover (`palm_flap.stl`) | TPU 95A | **v3.2 test print** | Thin closed palm with a raised grip oval. Screwed along the little-finger edge (3 × M3×5 flat-head into heat-set inserts), 7 push-through snap pegs elsewhere. |
| SP1-02 | Finger segments (11) | PETG | **v3.2 test print** | Barrel joints on the knuckle creases, fingernails on the tips. A broken segment is a quick reprint, not a new hand. |
| SP1-06 | Thumb | PETG | **v3.2 test print** | Friction hinge on one M3×20: swing to the grip, tighten one screw. |
| SP1-03 | Forearm cuff | PETG | **v3.2 test print** | Open palm side, strap slots, vents, low tensioner swelling with 4 flush line clamps. |
| SP1-04 | Fingertip pads | Bicycle inner tube | **v3.2** | Rubber pads glued into shallow recesses with E6000 or contact cement. |
| SP1-05 | Return cords | Elastic cord | **v3.2** | Open the fingers again; run hidden inside the fingers and the back of the hand. |
| SP2-xx | Sinag parts | PETG / TPU | Not designed | Starts from the proven Bukang-liwayway hand; adds stronger grip and an adjustable tensioner. |
| SP3-xx | Tanghali parts | PETG / TPU | Not designed | Phase 2. Adds a sealed electronics box, motor/servo mount and battery holder. |

## Design rules

- **No PLA.** It softens around 55–60 °C. PETG or ASA for rigid parts, TPU for pads and flexible parts.
- **No stick-on parts.** Screws, pins and mechanical fits (hot, humid climate). The only glue is contact cement for the rubber fingertip pads.
- **Hardware-store parts.** Stainless screws in one common size, braided line, hook-and-loop straps. A parent should be able to fix it with one tool.
- **Washable, ventilated liner** inside the cuff. Kids sweat into it all day.
- **Modular and reprintable.** Every part can be swapped on its own.
- **Light.** Keep weight down, especially far from the elbow. Kids tire quickly.
- **Electronics (Tanghali) stay sealed** from sweat and rain.

## Safety (every fitting)

1. **Skin checks.** After the first hour, the first day and the first week, look for red marks or rubbing. Red marks that don't fade within about 20 minutes mean the fit needs changing.
2. **No sharp edges.** Sand or round every edge and print seam that touches skin.
3. **Small parts.** Make sure pins and screws can't come loose for younger children.
4. **Heat.** Don't leave the hand in direct sun or a hot vehicle. Check it isn't hot before putting it on.
5. **Pinch points.** Check finger joints and the wrist hinge can't pinch the child's skin.
6. **Tanghali only:** fused battery, no exposed wiring, and the hand must open if the battery dies.
7. **Consent.** The parent or guardian agrees to the fitting and knows how to check the skin.

## Open decisions

- Elbow-driven version for children without a working wrist.
- Strap and liner material.
- Tanghali: motor or servo choice, microcontroller, battery. Sensor: FSR (force myography) first, MyoWare optional.
- Each model's real 100% size (then update the sizer).

## Build order

1. Design Bukang-liwayway (Model 1). Print a test hand at 100%, then measure it and put its real sizes into the sizer. **Bukang-liwayway v3.2 (realistic) is on the printer for its second test print: [bukang-liwayway/](bukang-liwayway/README.md)**.
2. Test fit with a child (with a therapist if possible). Fix what the fitting shows.
3. Design Sinag from the proven Model 1.
4. Bench-test an FSR muscle sensor in a cuff (and the motor) before designing Tanghali.

## Change log

- 2026-10-17: Repository started. Name (Sol Prosthetics), the three models, sizing rule and Hand Sizer decided.
- 2026-10-17: Official logo added (solprosthetics-logo.png).
- 2026-10-18: Bukang-liwayway v1 test print (boxy, kernelCAD). Joints use M3 stainless screws that thread into the plastic (no nuts).
- 2026-10-18: Bukang-liwayway v2: organic CadQuery shapes, pressed-in logo, hidden line tunnels.
- 2026-10-19: Bukang-liwayway v3 (realistic) in [bukang-liwayway/](bukang-liwayway/README.md): shape from a MakeHuman child hand, barrel joints on the knuckle creases, closed palm (PETG back + TPU flap with tuck tongue and four tabs), inner-tube grip pads, crease vents and drain, hidden lines, logo on the curved back, friction-hinge thumb.
- 2026-10-19: Removed the superseded v1/v2 files; they remain in the git history. v3 now lives in bukang-liwayway/.
- 2026-10-24: Bukang-liwayway v3.1g replaces v3 in [bukang-liwayway/](bukang-liwayway/README.md): every part rebuilt as smooth shapes, thin TPU palm cover (screwed hinge edge + push-through snaps), fingernails, through-holes at every joint, cleaner cuff tensioner and line routing, printing/assembly and illustrated stringing guides (PDF). The v3 files remain in the git history.
- 2026-10-24: Tanghali's muscle sensor is now a force-sensitive resistor (Interlink FSR 402 Short, 34-00015) instead of MyoWare, to cut e-waste (no disposable electrodes), cost and repair effort; MyoWare stays an optional plug-in. Added to the bill of materials.
- 2026-10-25: Bukang-liwayway v3.2, fixes from the first full print: one M3 × 45 knuckle axle for index, middle and ring; open wrist end with rounded edges; 2–3 mm line holes; deeper thumb hinge screw (M3 × 20); heat-set inserts; fingers and thumb print at 45°; per-size hardware card (`stl/HARDWARE.md`).
