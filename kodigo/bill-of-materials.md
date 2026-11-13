# Kodigo — Bill of Materials

**Status:** Planning · **Updated:** 2026-11-13 (captions, translation, app)
Sourcing: Shopee / Lazada PH. Prices are rough estimates; check current listings.
Search terms are what to type into Shopee or Lazada.

## A. Buy: optics test rig (first)

| # | Item | Qty | Est. ₱ | Search term | Notes | Status |
|---|------|-----|--------|-------------|-------|--------|
| A1 | ESP32-C3 SuperMini board | 1 | ~220 | `ESP32-C3 SuperMini` | The brain. Bluetooth + WiFi, USB-C. Buy 2 for a spare. | To buy |
| A2 | 1.3" OLED, SH1106, I2C | 1 | ~250 | `1.3 OLED SH1106 I2C` | Main screen: fits more caption lines. White reads best through the mirror. | To buy |
| A3 | 0.96" OLED, SSD1306, I2C, 128×64 | 1 | ~150 | `0.96 OLED SSD1306 I2C white` | For comparison through the optics. | To buy |
| A3b | Full-colour OLED, SSD1351, SPI, 128×128 *(optional)* | 1 | ~700–900 | `SSD1351 OLED 128x128 RGB` | Any text colour in software. Costs more and uses more battery than mono. | To buy |
| A4 | Bi-convex lenses, 25 mm dia, 40 mm focal length | 1 pair | — | `Google Cardboard lens 25mm 40mm` | Focusing lens. Display sits about 33–38 mm from it. | Have |
| A5 | HUD reflective film, static cling, 0.3 mm PET, 15 × 12.5 cm | 1 | ~88 | `AUMOTOP HUD reflective film` | **Main splitter.** Makes the text brighter; no glue. Try it alone in a printed frame or on an acrylic piece. About 20 pieces per sheet. | To buy |
| A5b | Clear acrylic sheet, 4 × 4 in, 1.5 mm | 1–2 | ~20–37 each | `custom cut acrylic sheet clear 4x4 1.5mm` | Backing for the film. Score and snap into 1 × 1⅜ in pieces (12 per sheet: 8 full size + 4 at 1 × 1¼ in). | To buy |
| A5c | Beam splitter cube, glass, 50/50, 10–15 mm *(optional)* | 1 | ~825 | `beam splitter prism 15mm 1:1` | Comparison only: brightest, no ghost, but glass, heavy and pricey. Not "polarizing". | Optional |
| A6 | Mini breadboard + Dupont jumpers | 1 set | ~120 | `mini breadboard dupont jumper wire` | Wiring the test rig without soldering. | To buy |

## B. Buy: wearable build (later)

| # | Item | Qty | Est. ₱ | Search term | Notes | Status |
|---|------|-----|--------|-------------|-------|--------|
| B1 | LiPo 3.7 V ~400 mAh (e.g. 602030) | 1 | ~180 | `lipo 3.7v 400mah 602030` | Behind-the-ear battery, with a protection circuit. | To buy |
| B2 | TP4056 USB-C charger module, with protection | 2 | ~40 each | `TP4056 type-c protection module` | Charges the LiPo. One spare. | To buy |
| B3 | 6×6 mm tactile buttons | 1 pack | ~50 | `tactile switch 6x6 pack` | Next / previous step. | To buy |
| B4 | Mini slide switch | 1 pack | ~40 | `SS12D00 slide switch` | Power on/off. | To buy |
| B5 | 100k resistors | 1 pack | ~40 | `100k ohm resistor pack` | Voltage divider for the battery-level reading. | To buy |
| B5b | BH1750 light sensor module *(optional)* | 1 | ~100 | `BH1750 light sensor module` | Automatic brightness. Shares the OLED's I2C wires. | To buy |
| B6 | 30 AWG silicone wire | 1 roll | ~120 | `30AWG silicone wire` | Thin, flexible wiring inside the frame. | To buy |
| B7 | M2 screws + heat-set inserts kit *(optional)* | 1 kit | ~200 | `M2 heat set insert screw kit` | Assembling the printed housing. | To buy |

**Estimated total still to buy:** about ₱1,550 (test rig about ₱840, wearable about ₱710), plus about ₱900 for the optional colour OLED and light sensor.

**Phone:** an Android phone with Chrome runs the Kodigo app as-is. iPhone needs the free WebBLE app (or Bluefy); see README.md.

## Making the splitter pieces (acrylic)

1. Leave the protective film on; mark lines with a pen.
2. Score each line 8–10 times with a sharp box cutter along a metal ruler (fresh blade, short extension, hand behind the ruler).
3. Snap over a table edge, groove up. Long strips first (1⅜ in), then 1 in pieces.
4. Sand edges (400 grit), peel the protective film. Wear safety glasses when snapping.
5. Clean, then lay the HUD film on (static cling), cut about 1 mm smaller than the acrylic, smoothed with a card. Film side faces the screen and eye.

## C. Print

| ID | Part | Qty | Material | Status |
|----|------|-----|----------|--------|
| KD-01 | Optics test rig | 1 | PETG | Not designed |
| KD-02 | Display module housing | 1 | PETG | Not designed |
| KD-03 | Battery pod | 1 | PETG | Not designed |
| KD-04 | Clip-on adapter | 1 | PETG / TPU | Not designed |
| KD-05 | Companion glasses frame | 1 | PETG | Not designed |
