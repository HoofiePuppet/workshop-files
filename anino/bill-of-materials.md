<p align="center"><img src="anino-logo.png" alt="ACS Anino logo" width="320"></p>

# ACS Anino: bill of materials

Everything for the full-body suit, built one section at a time. Prices are rough US-dollar estimates for
hobby-grade parts; local prices and shipping will differ. The search terms work on Lazada and Shopee.
Per-section parts are listed with the quantity for all seven sections (torso front, torso back, two arms,
two legs and the hood).

| Part | Section | Qty | Unit | Subtotal | Notes | Search term |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Raspberry Pi 4 (2 GB) | Hub (torso front) | 1 | $45 | $45 | Reads the cameras and slices the image. A Pi Zero 2 W (about $15) can work with a single camera | `Raspberry Pi 4 Model B 2GB` |
| USB webcam, wide-angle | Hub (torso front) | 2 | $15 | $30 | Back camera feeds the front; front camera feeds the back. Start with one | `USB webcam wide angle 1080p` |
| Small WiFi router | Hub (torso front) | 1 | $15 | $15 | Dedicated network linking the Pi to every section. Test latency early | `mini travel wifi router` |
| ESP32 dev board | Every section | 7 | $6 | $42 | One controller per section, WLED-style pixel firmware | `ESP32 DevKit V1 30 pin` |
| WS2811 12 mm pixel string (50 pixels) | Every section | 20 | $9 | $180 | About 1,000 pixels split across the sections; check the spacing in the listing | `WS2811 12mm 50 pixels string 5V` |
| Level shifter chip (74AHCT125) | Every section | 7 | $1 | $7 | Optional; helps avoid flicker on the pixel data line | `74AHCT125 level shifter` |
| Buck converter 12 V to 5 V, 5 A | Every section | 7 | $4 | $28 | Local 5 V power, one per section | `DC DC buck converter 12V to 5V 5A` |
| Buck converter 12 V to 5 V, 3 A | Hub (torso front) | 1 | $6 | $6 | Powers the Pi | `12V to 5V 3A USB buck converter` |
| Inline blade fuse holder with fuse | Every section | 7 | $2 | $14 | A short stays inside its own section | `inline blade fuse holder 12V` |
| XT30 connector pair (2-pin power) | Every section | 7 | $2 | $14 | Same plug on every section to the 12 V trunk | `XT30 connector male female pair` |
| JST-SM 3-pin connector pairs (pack of 50) | Every section | 1 | $10 | $10 | Pixel string to controller | `JST SM 3 pin connector pair` |
| Capacitor and resistor kit | Every section | 1 | $6 | $6 | Smoothing and data-line protection | `electrolytic capacitor resistor assortment kit` |
| 12 V Li-ion battery pack (3S, about 10 Ah) | Power trunk | 1 | $45 | $45 | A USB power bank cannot supply enough current | `12V 3S 18650 battery pack 10Ah` |
| Battery charger for the pack | Power trunk | 1 | $15 | $15 |  | `12.6V 3S lithium battery charger` |
| Main fuse and holder (15 A) | Power trunk | 1 | $4 | $4 |  | `blade fuse holder 15A` |
| Silicone wire, 18 AWG power and 24 AWG signal | Power trunk | 1 | $25 | $25 | Thin 12 V trunk along the suit | `silicone wire 18AWG 24AWG kit` |
| Loose non-stretch coverall, light color | Suit | 1 | $25 | $25 | Cut into sections | `cotton coverall overall loose` |
| Separable zippers (per joint) | Suit | 7 | $3 | $21 | Shoulders, hips, hood and torso front/back | `separable open end zipper` |
| White diffusion fabric (per meter) | Suit | 2 | $3 | $6 | Softens the pixels | `white ripstop nylon fabric` |
| Mesh fabric | Suit | 1 | $8 | $8 | Underarms, back and face | `polyester mesh fabric` |
| Snaps and hook-and-loop pack | Suit | 1 | $10 | $10 | Mounts the pixel strings | `velcro hook and loop tape snap buttons` |
| TPU filament, 1 kg | Printed parts | 1 | $22 | $22 | Flexible strain relief and clips | `TPU filament 1.75mm 1kg` |
| PLA or PETG filament, 1 kg | Printed parts | 1 | $18 | $18 | Camera mounts and section cases | `PETG filament 1.75mm 1kg` |
| **Total (rough)** | | | | **$596** | | |

## Optional upgrades

| Part | Qty | Notes |
| --- | ---: | --- |
| Side webcams (left and right), about $15 each | 2 | For a 360-degree view once front and back work |
| Pixel sections for gloves and boots | 4 | Only if the main sections work well |
| Spare ESP32 and 5 V converter, about $10 | 1 of each | Handy for swapping a failed section |

## Power estimate

About 15 A at 5 V with every pixel lit at moderate brightness (around 75 W). Plan on an hour or so from a
10 Ah 12 V pack, longer if you dim the pixels.

(c) 2026 Hoofie Puppet. Designs, pictures and build guides: CC BY-NC-SA 4.0.
