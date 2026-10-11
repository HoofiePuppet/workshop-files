# AutoPooper 3000 — Bill of Materials

**Status:** In development · Items marked **TBD** are still being decided.
Stainless hardware throughout. Button head = ISO 7380. Countersunk = 90° flat head, ISO 10642 / DIN 7991. Washers = DIN 125. Nylocs = DIN 985. Acorn nuts = DIN 1587. Square nuts = DIN 562. Numbers in brackets, like (+2), are spares.
Sourcing: Lazada PH / LazMall for most hardware and electronics.

Printed parts and their print settings are in [README.md](README.md#printing).

## Brass Inserts (All The Same Type)

Every insert on this build is an M3 brass insert, 4mm outside diameter × 5mm long, GLUED in with 2-part epoxy in a Ø4.4 × 5.5mm blind hole, pushed to the bottom, full cure before use. None are heat-set with a soldering iron.

| Qty | Where |
|---|---|
| 9 (+2) | Drum wall: sifter feet |
| 4 | Container: in-slip pockets |
| 4 | Container deck: rear support |
| 4 | Container deck: belt guard |
| 2 | Rear support post: hall-sensor arm |
| 8 (+2) | Container: EB lid ledge |
| 8 (+2) | Container: electronics-bay floor (trays) |
| 4 (+2) | Container back wall: ACF rear vent panel |
| 43 (+8 spare) | TOTAL |


## Screws, Bolts, Nuts & Washers

Stainless throughout. Button head = ISO 7380. Countersunk = 90° flat head, ISO 10642 / DIN 7991. Washers = DIN 125. Nylocs = DIN 985. Acorn nuts = DIN 1587. Square nuts = DIN 562.

| Qty | Item | Where |
|---|---|---|
| 9 (+2) | M3 × 20 button head + M3 washer | Sifter → drum inserts |
| 6 (+2) | M5 bolt, hex or socket head, length: measure the stack | Pulley + stub plate + flange coupler → drum |
| 12 (+4) | M5 washer | Both sides of the pulley bolts |
| 6 (+2) | M5 nyloc | Pulley bolts |
| TBD | M3 countersunk through-bolt + M3 washer + M3 nyloc | Flange coupler → drum (6-hole flange) |
| 4 | M3 screw | Bristle guard at the dump hole |
| 4 | M3 screw, length at test-fit | In-slips → container inserts |
| 5 (+2) | M3 square nut + M3 × 6 cup-point grub screw | Shaft collars (4 rollers + 1 rear stub) |
| 2 | M8 socket head (Ø13 head), length TBD; DIN 433 Ø15 washer or none | Spindle bracket → seat |
| TBD | M8 | Retainer cap → bracket (on hold) |
| 8 | M3 × 16 socket head + M3 washer | Rear support (4) + belt guard (4) → deck inserts |
| 2 (+2) | M3 × 50 socket head + M3 washer + M3 nyloc | Rear support cap |
| 2 | M3 × 8 button head + M3 washer | Hall-sensor arm → support inserts |
| 1 | M3 × 6 self-tapping | Hall sensor board → arm |
| 9 (+3) | M3 × 8 self-tapping pan head | Wire clips → container |
| 1 | M6 jack screw (length TBD) | Motor slide plate |
| 4 (+2) | M3 × 16 countersunk + M3 acorn nut | Receptacle lid → tray |
| 2 | M3 button head + M3 acorn nut (length TBD) | Receptacle handle |
| 4 (+2) | M3 × 16 countersunk + M3 acorn nut | Accessories lid → tray |
| 2 (+1) | M3 × 30 button head + M3 acorn nut | Accessories handle |
| 8 (+2) | M3 × 12 button or socket head | EB lid → ledge inserts |
| 4 (+2) | M3 self-tapping, about 10mm, pan/button head | RP lid (rear panel) |
| 8 (+2) | M3 × 10 button head + M3 washer | Electronics trays → floor inserts |
| 4 (+2) | M4 × 8 pan/button head + M4 washer | Power supply → power tray (from below) |
| 6 (+2) | M3 × 8 self-tapping pan head | Arduino Mega → standoffs |
| 4 | M3 × 12 button head + washer + nyloc | Stepper driver → tray |
| 2 | M3 × 12 button head + washer + nyloc | Mains fuse holder → tray |
| 10 | M3 × 16 button head + M3 × 6 nylon spacer + nyloc | Buck, fan MOSFET, RGB MOSFET board, divider board, ESP32 carrier (2 each) |
| 2 | M3 × 20 button head + washer + nyloc | Terminal block → tray |
| 4 (+2) | M4 × 35 countersunk + M4 nyloc | ACF fan → wall |
| 4 (+2) | M3 × 10 countersunk | ACF rear vent panel → inserts |
| 2 (+2) | M3 × 8 self-tapping pan/button head | Fill-sensor cap → deck |
| 2 | M3 × 10 self-tapping pan/button head | Cat-sensor carrier → container underside |
| 1 | M20 × 1.5 nylon cable gland + locknut | Power cord, back wall |


## Bearings, Shafts & Drive

| Qty | Item | Where |
|---|---|---|
| 14 | 608 skate bearing | 4 rollers (in TPU sleeves) + 8 spindle bracket (bare) + 2 rear support (bare) |
| 2 | 8mm hardened linear shaft (printer type), 150mm | Drum rollers; grind a 6 × 0.4mm flat at each end |
| 1 | 8mm hardened linear shaft, 150mm, cut into 36 + 36 + 42mm | Bracket roller rods (2) + rear stub (1) |
| 1 | NEMA23 stepper + planetary gearbox, body ≤ 110mm, ≤ 60mm square (not bought) | Motor bay, under the spindle pulley |
| 1 | Stepper driver, TB6600 or DM542 | Control tray |
| 1 | HTD 920-8M-20 timing belt (920mm, 115 teeth, 20mm wide) | Spindle pulley ↔ motor pulley |
| 1 | HTD 8M 20-tooth pulley, 20mm belt, bore = gearbox shaft | Motor |
| 1 | Printed HTD 40-tooth pulley (with magnet pocket) | Drum rear flange |
| 1 | Stainless 6-hole flange coupler, Ø56mm flange, Ø14mm keyed bore | Drum rear |
| 1 (+1) | Ø6 × 3mm neodymium magnet | Pulley rear face (home position) |


## Electronics

| Qty | Item | Notes |
|---|---|---|
| 1 | Power supply, 24V 15A 360W (Chen Liang P360W24V / S-360-24 type) | Set to 230V; fan side up; keep the clear terminal cover on |
| 1 | Arduino Mega 2560 (clone OK) | Runs everything; fed 5.0V into its 5V pin |
| 1 | LM2596S adjustable buck converter | Set to 5.0V with a multimeter BEFORE connecting the Mega |
| 1 (+1) | ESP32-WROOM-32 DevKit, 38-pin, USB | Phone page over WiFi; on a 5 × 7cm perfboard with female headers |
| 1 | 22mm anti-vandal momentary push button, RGB ring, 24V, common anode | Flush button in the EB lid |
| 1 | 3-channel logic-level low-side MOSFET board | Button LED colours (red, green, blue) |
| 1 | Logic-level MOSFET module | Carbon-filter fan on/off |
| 1 | 120 × 120 × 25mm 24V fan | Carbon filter |
| 1 set | 47k + 10k resistors (¼W metal film) + 100nF capacitor on a small perfboard | Button signal 24V → 4.2V for the Mega |
| 1 set | 1k + 2k resistors (×2 sets) + one 10k | Radar and ESP32 serial dividers, ESP32 wake pull-up |
| 1 | Inline fuse holder + 0.5A fuse | 24V feed to the button |
| 1 | 5 × 20mm fuse holder + T3.15A slow-blow fuse | Mains live, before the supply |
| 1 | Terminal block, 6 to 8 way | Power distribution |
| 1 | HLK-LD2410C 24GHz mmWave presence sensor | Cat sensor under the bowl |
| 1 (+1) | VL53L1X time-of-flight breakout, 5V-compatible | Receptacle-full sensor (add a 4-channel I2C level shifter if not 5V-compatible) |
| 1 (+1) | KY-003 hall-effect module (A3144), digital, 3-pin | Drum home sensor |
| 1 | Rechargeable motion-sensor LED cabinet bar, about 20cm (fits 200 × 22 × 10mm), dimmable, warm white (about 3000K), night-sensing mode, USB-C | Drum night light; battery, no wiring |
| optional | KY-006 passive buzzer + 1k trimmer | Sound (undecided) |


## Wiring: Cables (How Much)

Colours: red +24V, orange +5V, black every ground, other colours for signals. Mains: brown live, blue neutral, green/yellow earth. Solder at the device end, JST-XH plug at the electronics-bay end. Lengths include about 30% slack.

| Buy | Cable | Run |
|---|---|---|
| 2m | 3-core 22–24 AWG | Drum home sensor (KY-003) → Mega |
| 2m | 5-core 22–24 AWG | Cat sensor (LD2410C) → Mega |
| 1m | 4-core 22–26 AWG, outside Ø 4.5mm or less | Receptacle-full sensor (VL53L1X) → Mega |
| 1m | 5-core 22 AWG | Flush button → control tray |
| 0.5m | 6-core 22–26 AWG or ribbon | ESP32 carrier ↔ Mega |
| 2m | 4-core 18 AWG (20 AWG if the motor is 2A or less) | Stepper motor → driver |
| 1.5m | 2-core 22 AWG | Carbon-filter fan → its MOSFET |
| 2m red + 2m black | 18 AWG silicone wire | Supply → terminal block → driver |
| 1 kit | 22 AWG stranded hook-up wire, 6 colours | Buck, Mega and ESP32 5V, fan MOSFET, button fuse branch, short signal runs |
| 1m | 1.0mm² (18 AWG) brown, 300/500V rated | Mains: fuse holder → supply L |
| 1 | 3-core earthed mains cord, 0.75mm² or more (retro coiled) | Wall → cable gland |


## Wiring: Connectors & Routing Parts

| Qty | Item | Where |
|---|---|---|
| 2 pairs | JST-XH 3-pin plug + socket pigtails | Home sensor |
| 2 pairs | JST-XH 4-pin | Fill sensor |
| 3 pairs | JST-XH 5-pin | Flush button + cat sensor |
| 2 pairs | JST-XH 6-pin | ESP32 carrier |
| 2 pairs | JST-XH 2-pin | Carbon-filter fan |
| 1 pair | JST-VH 4-pin (3.96mm), or 4 × Wago 221-412 | Motor disconnect in the motor bay |
| 10 | Insulated fork terminals, red, M3.5/M4 | Power-supply screw terminals |
| 1 kit | Bootlace ferrules 0.5–1.5mm² + crimper | Screw terminals |
| 40 each | Dupont jumpers, male-male + male-female (or a Mega screw-terminal shield) | Mega header pins |
| 9 (+3) | Printed wire clips + M3 × 8 self-tappers | Motor-bay ceiling (6) + right wall (3) |
| 1 pack | Cable ties, 2.5–3.6mm wide | Rear-support tie anchors, bay tidying |
| 1m | Braided sleeve 6mm (optional) | Motor + sensor bundle in the motor bay |
| 1–2m | Nylon trimmer line 2–2.4mm | Fishing wires through the channels |
| 1 | Heat-shrink assortment | Tag the button R/G/B wires |


## Consumables

| Item | For |
|---|---|
| THF-based PVC solvent cement (Neltex or S-Blue) | Welding drum tiles and container pieces |
| Half-face respirator 3M 6200 + 6001 or 60921 cartridges | Solvent welding |
| 2-part epoxy (slow-set for the stub rod) | All 43 brass inserts, stub rod, magnet, signs, Mark II logo inlays |
| Closed-cell EPDM or silicone sponge strip 10 × 3mm, non-adhesive, 5m | Sifter edge seal |
| Neutral-cure clear silicone | Fan wire hole in the duct |
| Activated carbon pellets 3–4mm + 15 × 20cm zippered mesh bags | Carbon filter (250–300 g per fill) |
| Slow-cure epoxy + opaque epoxy pigment, paste or liquid (bright yellow) or a yellow oil-based paint pen; alcohol, 400–600 sandpaper, masking tape, plastic card, razor blades, 800 wet-and-dry; glow powder (optional) | MIN/MAX fill lines |
| Paper towel | Receptacle liner |
| Clumping clay litter, 3.5–4 L (3–3.5 kg) per fill | The drum |
| Dremel grinding stone / cut-off wheel | Flats on the rods, cutting rods |
| Long-arm 2mm ball-end hex key, 1.5mm hex key | Sifter screws, grub screws |
| Compact litter scoop (blade ≤ 10cm wide, ≤ 28cm long) | Accessories drawer |
