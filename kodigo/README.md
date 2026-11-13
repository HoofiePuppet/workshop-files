<picture>
  <source media="(prefers-color-scheme: dark)" srcset="kodigo-logo.png">
  <source media="(prefers-color-scheme: light)" srcset="kodigo-logo-dark.png">
  <img alt="Kodigo" src="kodigo-logo-dark.png">
</picture>

# Kodigo — Parts Repository

*Your cheat sheet, floating in the air.*

**Status:** Planning · **Started:** 2026-11-13 · **Designer:** Hoofie Puppet
**License:** (c) 2026 Hoofie Puppet, CC BY-NC-SA 4.0 (see the repo's LICENSE)
**Shopping list:** [bill-of-materials.md](bill-of-materials.md)

![Kodigo concept: the clip-on module on ordinary glasses (left) and on its own printed frame (right)](kodigo-concept.jpg)

*AI-generated concept image, not an actual build.*

## What it is

Kodigo is a cheap, 3D-printed, Google Glass–style heads-up display. A tiny screen beside your eye shows text that seems to float in front of you: build instructions one step at a time, phone notifications and texts, the time and the battery level.

"Kodigo" is Filipino slang for the cheat sheet you sneak into an exam. This one feeds you the answers while your hands stay on the work.

It comes in two ways to wear it, with the **same module** for both:

- **Clip-on:** slides onto the arm of your own glasses.
- **Full frame:** a companion 3D-printed glasses frame (clear or no lenses) for people who don't wear glasses.

Both use one shared mounting rail, so a single Kodigo module moves between them.

## Official logo

- **kodigo-logo.png** is the official Kodigo logo: a glasses icon with three text lines in the lens, "KODIGO" in bright HUD green, and the tagline "DIY heads-up display · clip-on or full frame" in light gray. Transparent background, made for dark backgrounds.
- **kodigo-logo-dark.png** is the same logo in dark green and dark gray, for light backgrounds. GitHub picks the right one for your theme automatically.
- The **-2x** files are the same logos enlarged 2x. They're slightly soft because the original is small.
- It was cut from the first concept image (2026-11-13). Always use these files; don't redraw or restyle the logo.

## How it works

```
 [ ESP32-C3 ] --I2C--> [ OLED display ]
                              |  light
                              v
                       [ lens, 40 mm focal length ]   <- makes the text look
                              |                          about 1 m+ away
                              v
                       [ 50/50 beam splitter ]        <- see-through mirror at 45°
                              |
                              v
                          your eye  (sees the world AND the text)
```

- The screen sits slightly inside the lens's focal length (about 33–38 mm away), so your eye sees a sharp, enlarged image floating at a comfortable distance instead of a blur 3 cm from your face.
- The mirror reverses the picture, so the firmware draws the screen flipped.
- White OLED text reads best through the mirror. Indoors and at the workbench it's clear; bright Philippine sunlight washes it out.

## What it will show

| Feature | Plan |
|---------|------|
| Time | From the phone over Bluetooth (or WiFi time). |
| Battery level | Battery voltage read through a 100k/100k divider into the ESP32's ADC. |
| Notifications and texts | Forwarded from an Android phone over Bluetooth (Gadgetbridge-style companion app). |
| Build instructions | **Step mode:** instructions broken into short steps, one per screen (plus a small diagram if it fits). Next / previous with the buttons on the frame, so your hands stay free. Whole PDF pages are unreadable on a screen this small. |

## Build stages

1. **Optics test rig (now).** OLED, lens and beam splitter in a printed holder with adjustable spacing, on the bench. Goal: a sharp, comfortable image. No wearable parts yet.
2. **Electronics on the breadboard.** ESP32-C3 driving the OLED: clock, battery level, text over Bluetooth.
3. **Wearable module.** The housing, battery pod behind the ear, buttons, power switch.
4. **Mounting rail, clip-on adapter and companion frame.**

## Printed parts

| ID | Part | Material | Status | Notes |
|----|------|----------|--------|-------|
| KD-01 | Optics test rig | PETG | Not designed | Bench holder for the OLED, lens and beam splitter, with adjustable display-to-lens spacing (about 30–40 mm). |
| KD-02 | Display module housing | PETG | Not designed | Holds the OLED, lens, beam splitter, ESP32-C3 and buttons. Slides onto the mounting rail. |
| KD-03 | Battery pod | PETG | Not designed | Behind the ear, balances the weight of the module. Holds the LiPo, charger board and power switch. |
| KD-04 | Clip-on adapter | PETG / TPU | Not designed | Puts the mounting rail onto the arm of ordinary glasses. |
| KD-05 | Companion glasses frame | PETG | Not designed | For people who don't wear glasses. Mounting rail built into the right arm. |

## Open questions

- 0.96" vs 1.3" OLED: which is easier to read through the optics.
- Beam splitter cube vs a plain acrylic/glass plate.
- Exact mounting-rail profile shared by the clip-on adapter and the frame.
