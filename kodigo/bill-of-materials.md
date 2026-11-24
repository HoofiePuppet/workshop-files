# Kodigo — Bill of Materials

**Status:** Planning · **Updated:** 2026-11-21 (parts chosen, KD-01 + KD-05 designed, KD-06 bracelet added)
Sourcing: Shopee / Lazada PH. Prices are rough estimates; check current listings.
Search terms are what to type into Shopee or Lazada.

## A. Buy: optics test rig (first)

| # | Item | Qty | Est. ₱ | Search term | Notes | Status |
|---|------|-----|--------|-------------|-------|--------|
| A1 | ESP32-C3 SuperMini board | 3 | ~183 each | `ESP32-C3 SuperMini` | The brain. Get the variant with the pin header **loose** (CHENJ, LazMall, variant A1). One board gets pins for the breadboard rig, one gets wires soldered straight on for the glasses, the third goes in the bracelet (see section B2). | To buy |
| A2 | 1.3" OLED, SH1106, I2C | 1 | ~201 | `1.3 OLED SH1106 I2C` | Bigger text through the lens. **White** (EstarDyn, LazMall). 35.5 × 33.5 mm. Pin order **VDD GND SCK SDA** (power first). | To buy |
| A3 | 0.96" OLED, SSD1306, I2C, 128×64 | 1–2 | ~99 | `0.96 OLED SSD1306 I2C white` | Smaller, lighter module. **White** (FU Labs). Pin order **GND VCC SCL SDA** (ground first). Wire by the printed labels. | To buy |
| A3b | Full-colour OLED, SSD1351, SPI, 128×128 *(optional)* | 1 | ~700–900 | `SSD1351 OLED 128x128 RGB` | Any text colour in software. Costs more and uses more battery than mono. | To buy |
| A4 | Bi-convex lenses, 25 mm dia, 40 mm focal length | 1 pair | — | `Google Cardboard lens 25mm 40mm` | Focusing lens. Display sits about 33–38 mm from it. | Have |
| A5 | HUD reflective film, static cling, 0.3 mm PET, 15 × 12.5 cm | 1 | ~88 | `AUMOTOP HUD reflective film` | **Main splitter.** Makes the text brighter; no glue. Try it alone in a printed frame or on an acrylic piece. About 20 pieces per sheet. | To buy |
| A5b | Clear acrylic sheet, 4 × 4 in, 1.5 mm | 1–2 | ~20–37 each | `custom cut acrylic sheet clear 4x4 1.5mm` | Backing for the film. Score and snap into 1 × 1⅜ in pieces (12 per sheet: 8 full size + 4 at 1 × 1¼ in). | To buy |
| A5c | Beam splitter cube, glass, 50/50, 10–15 mm *(optional)* | 1 | ~825 | `beam splitter prism 15mm 1:1` | Comparison only: brightest, no ghost, but glass, heavy and pricey. Not "polarizing". | Optional |
| A6 | Breadboard (400 holes) + Dupont jumpers | 1 set | — | — | Wiring the test rig. Need 4 female-to-male jumpers per OLED. | Have |
| A7 | Double-sided perfboards + male pin headers | — | — | — | Small cut piece = button/resistor board behind the ear. | Have |
| A8 | LiPo 3.7 V 2000 mAh (PKCELL LP803860) | 1 | — | — | Old cell from the night-vision project. Bench power for the rig via a TP4056 — **check first** (not swollen, ≥ 3.0 V; under 2.5 V = retire). Too big for the glasses. | Have (check) |

## B. Buy: wearable build (later)

| # | Item | Qty | Est. ₱ | Search term | Notes | Status |
|---|------|-----|--------|-------------|-------|--------|
| B1 | LiPo 3.7 V 400 mAh, **802035** (8 × 20 × 35 mm) | 1 | ~180 | `lipo 3.7v 400mah 802035` | Behind-the-ear battery, ~7 h. Must have a protection circuit. (602030 is only 300 mAh.) KD-03 is sized for this. | To buy |
| B2 | TP4056 USB-C charger module, with protection | 3 | ~40 each | `TP4056 type-c protection module` | Charges the LiPo: one for the glasses, one for the bracelet, one spare. | To buy |
| B3 | Tactile buttons **6 × 6 × 5 mm, 4-pin through-hole** | 1 pack | ~50 | `tactile switch 6x6x5 4 pin` | Next / previous step. Not SMD. An assorted-height pack is fine. | To buy |
| B4 | Mini slide switch | 1 pack | ~40 | `SS12D00 slide switch` | Power on/off. | To buy |
| B5 | 100k resistors (1 %, blue body) | 2 | — | — | Battery-level divider. From the 600-pc assortment (brown-black-black-orange-brown). | Have |
| B5b | BH1750 light sensor, GY-302 board *(optional)* | 1 | ~113 | `GY-302 BH1750` | Automatic brightness. Shares the OLED's I2C wires; leave ADDR unconnected. ~14 × 19 mm. | To buy |
| B6 | 30 AWG silicone wire | 1 roll | ~120 | `30AWG silicone wire` | Thin, flexible wiring inside the frame. | To buy |
| B7 | M2 screws + heat-set inserts kit *(optional)* | 1 kit | ~200 | `M2 heat set insert screw kit` | Assembling the printed housing. | Have |
| B8 | Elastic retainer band, flat about 5 mm wide (or 3 mm round cord) *(optional)* | 1 | — | `flat elastic band 5mm` | Threads through the two ear sleeves and goes behind your head so the glasses stay on. Start longer than needed, tie, then trim. | Have |

## B2. Buy: bracelet (KD-06, wrist remote)

The bracelet is its own small ESP32-C3 with 3 buttons. It sends commands to the glasses over Bluetooth. Build it after the glasses firmware works.

| # | Item | Qty | Est. ₱ | Search term | Notes | Status |
|---|------|-----|--------|-------------|-------|--------|
| C1 | ESP32-C3 SuperMini board | 1 | ~183 | `ESP32-C3 SuperMini` | Counted in A1 (third board). | To buy |
| C2 | LiPo 3.7 V 250 mAh, **502030** (5 × 20 × 30 mm) | 1 | ~100–130 | `lipo 3.7v 502030 250mah` | With protection circuit. The case is sized for these dimensions; check the real cell before printing. | To buy |
| C3 | TP4056 USB-C charger module | 1 | ~40 | `TP4056 type-c protection module` | Counted in B2. About 26 × 17 mm. Its USB-C port is the bracelet's charging port. | To buy |
| C4 | Tactile buttons 6 × 6 × 5 mm, 4-pin through-hole | 3 | — | — | From the pack in B3. Soldered on a small perfboard (about 31 × 9 mm). | To buy |
| C5 | Mini slide switch (SS12D00) | 1 | — | — | From the pack in B4. Power on/off. | To buy |
| C6 | **Watch strap, 20 mm, spring-bar type** (silicone or nylon) | 1 | ~100–150 | `20mm watch strap silicone quick release` | Any standard 20 mm strap works. Get one with regular spring bars. | To buy |
| C7 | Spring bars, 20 mm, spare *(optional)* | 2–4 | ~30 | `spring bar 20mm watch` | Spares in case one is lost or bent. | Optional |
| C8 | M2 × 10 mm screws | 4 | — | — | Lid to base. Whole-mm length. From the M2 kit (B7); check the kit includes 10 mm. | Have (check) |
| C9 | M2 heat-set inserts (3.2 mm OD, 4 mm long) | 4 | — | — | From the M2 kit (B7). | Have |
| C10 | Perfboard, wire, double-sided tape | — | — | — | Perfboards and silicone wire already listed (A7, B6). Tape holds the battery and boards. | Have |

**Estimated total still to buy:** about ₱1,800 (test rig about ₱700, wearable about ₱600, bracelet about ₱500), plus the optional colour OLED and light sensor.

**Phone:** an Android phone with Chrome runs the Kodigo app as-is. iPhone needs the free beacio Safari extension (iOS 26.2+) or the free Bluefy app; see README.md. beacio works only in a normal Safari tab, not from a home-screen icon.

## Making the splitter pieces (acrylic)

1. Leave the protective film on; mark lines with a pen.
2. Score each line 8–10 times with a sharp box cutter along a metal ruler (fresh blade, short extension, hand behind the ruler).
3. Snap over a table edge, groove up. Long strips first (1⅜ in), then 1 in pieces.
4. Sand edges (400 grit), peel the protective film. Wear safety glasses when snapping.
5. Clean, then lay the HUD film on (static cling), cut about 1 mm smaller than the acrylic, smoothed with a card. Film side faces the screen and eye.

## C. Print

| ID | Part | Qty | Material | Status |
|----|------|-----|----------|--------|
| KD-01 | Optics test rig (12 parts, `kd01.py`) | 1 set | PETG | Designed v1, not printed |
| KD-02 | Display module housing | 1 | PETG | Not designed |
| KD-03 | Battery pod | 1 | PETG | Not designed |
| KD-04 | Clip-on adapter (uses Kodigo rail v1) | 1 | PETG / TPU | Not designed |
| KD-05 | Companion glasses frame + snap-in nose pieces (`kd05.py`) | 1 + 1 nose | PETG (nose: TPU, 2 walls, 10–15% gyroid; or PETG with silicone pads) | Printed and worn (v3) |
| KD-05-E | Ear sleeve (`KD05-E_ear_sleeve`), optional | 2 | TPU, 2 walls (PETG: 4 walls) | Printed, fit tested |
| KD-06 | Bracelet case: base, lid, 3 button plungers (`kd06.py`), 20 mm watch strap | 1 set | PETG | Designed v1, not printed |
