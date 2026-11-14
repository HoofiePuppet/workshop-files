# Kuwago — Bill of Materials

**Status:** v2.3 designed · **Updated:** 2026-11-14
Sourcing: Shopee / Lazada PH. Search terms are what to type into Shopee or Lazada; check current listings for prices.

## A. Electronics

| # | Item | Qty | Search term | Notes | Status |
|---|------|-----|-------------|-------|--------|
| A1 | Raspberry Pi Zero | 1 | `raspberry pi zero` | The brain. Pi Zero 2 W (same size and pins) is a drop-in upgrade. | Have |
| A2 | Pimoroni LiPo SHIM | 1 | `pimoroni lipo shim` | Boosts the battery to 5 V; low-battery pin. | Have |
| A3 | LiPo 3.7 V 2000 mAh, PKCELL LP803860, JST | 1 | `LP803860 2000mah` | In the rear strap pod. ~2½–3 h runtime. | Have |
| A4 | Night-vision camera, OV5647 5 MP, 2 IR LEDs | 1 | `raspberry pi night vision camera OV5647 IR` | Fixed IR camera with light-sensor IR LEDs. | Have |
| A5 | Pi Zero camera ribbon (22-pin to 15-pin) | 1 | `pi zero camera cable` | Have a 30 cm one; 10–15 cm is tidier (A11). | Have |
| A6 | Rocker switch | 1 | `mini rocker switch` | Wired to SHIM EN + GND. | Have |
| A7 | **3.5" HDMI screen, MPI3508, 480 × 320** | 1 | `MPI3508 3.5 inch HDMI` | **Must say HDMI and show an HDMI port.** The cheap "3.5 inch Raspberry Pi LCD" SPI screens are too laggy for goggles. | To buy |
| A8 | Mini-HDMI cable, **90° down-angle** head, FPV flat-ribbon type | 1 | `FPV mini HDMI 90 degree ribbon cable` | v2 has only ~7 mm under the Pi for the plug. Full HDMI head at the screen end. | To buy |
| A9 | microSD card, 8 GB+ | 1 | `microSD 16GB` | Raspberry Pi OS Lite. | Check |
| A10 | Thin hookup wire, red/black | 1 | `22awg silicone wire` | Screen power from the SHIM, switch wiring. | Check |
| A11 | Shorter Pi Zero camera ribbon, 10–15 cm *(optional)* | 1 | `pi zero camera cable 15cm` | Tidier than folding the long one. | Optional |
| A12 | Waveshare 3.5" HDMI LCD (E), 640 × 480 *(upgrade)* | 1 | `waveshare 3.5 inch HDMI LCD E` | Sharper screen; gets its own tray. | Later |
| A13 | Raspberry Pi Zero 2 W *(upgrade)* | 1 | `raspberry pi zero 2 w` | Smoother picture. | Later |
| A14 | **TP4056 USB-C LiPo charger, protected** | 1 | `TP4056 type c protection` | The LiPo SHIM does **not** charge. Goes in the battery pod. | To buy |
| A15 | JST-PH 2-pin extension lead, ~40 cm | 1 | `JST PH 2.0 2 pin extension` | Battery pod to goggles, along the strap. | To buy |
| A16 | MAX17048 LiPo fuel gauge *(optional)* | 1 | `MAX17048 fuel gauge` | On-screen battery % bar (I2C). | Optional |

## B. Optics

| # | Item | Qty | Search term | Notes | Status |
|---|------|-----|-------------|-------|--------|
| B1 | Bi-convex lenses, Ø25 mm, 40–45 mm focal length | 1 pair | `Google Cardboard lens 25mm 40mm` | Centre 5.0 mm, edge ~2.5 mm thick. | Have |

## C. Hardware

| # | Item | Qty | Search term | Notes | Status |
|---|------|-----|-------------|-------|--------|
| C1 | M2.5 screws, 5–10 mm | ~16 | `M2.5 screw assortment` | Pi 4 × 5 · face 4 × 5 · camera retainer 2 × 8 · tray cap 2 × 6 · pod lid 2 × 6 · thumbscrews 2 × 8–10. | Check |
| C1b | M2.5 nuts | 2 | (in the assortment) | Lens-plate thumbscrews. | Check |
| C2 | Elastic head strap, 25–40 mm | 1 | `elastic headband strap 38mm` | An old goggle or headlamp strap works. | To buy |
| C3 | Foam for the face seal | 1 | `EVA foam sheet 3mm` or `VR face cushion` | Soft, dark, wipeable. | To buy |
| C4 | 550 paracord, ~55 cm | 1 | `550 paracord` | Gutted, as a solid flexible sleeve for the battery lead; its ends tuck into the 4.2 mm cable sockets. | Have |

## D. Printed parts (PLA) — STLs in [`stl/`](stl/), settings in the [build guide](Kuwago-Build-Guide.pdf)

| # | Part | File | Qty | Status |
|---|------|------|-----|--------|
| D1 | Shell | kw-01-shell | 1 | Ready |
| D2 | Owl face (flush) | kw-02-owl-face | 1 | Ready |
| D3 | Lens / focus plate | kw-03-lens-plate | 1 | Ready |
| D4 | Lens rings | kw-04-lens-ring | 2 | Ready |
| D5 | Screen tray — MPI3508 | kw-05-screen-tray-mpi3508 | 1 | v0: regenerate after measuring the screen |
| D6 | Face shroud | kw-06-face-shroud | 1 | Ready |
| D7 | Camera retainer | kw-07-camera-retainer | 1 | Ready |
| D8 | Battery pod + lid | kw-08 / kw-09 | 1 + 1 | Ready |
| D9 | Thumb knobs | kw-10-thumb-knob | 2 | Ready |
| D10 | Brow accent, translucent amber *(optional)* | kw-11-brow-accent | 1 | Ready |
| D11 | Logo inlays, green (12 pieces) | kw-12-logo-inlays | 1 plate | Ready |
