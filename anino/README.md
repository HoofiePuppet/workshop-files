<p align="center"><img src="anino-logo.png" alt="ACS Anino logo: a glass-like human silhouette breaking into violet and amber pixels above the word ANINO and the tagline Wear the background." width="420"></p>

# ACS Anino: a do-it-yourself active camouflage suit

*"Anino" is Filipino for shadow. Wear the background.*

**Status:** planning · **Started:** 2026-11-19 · **Designer:** Hoofie Puppet
**License:** (c) 2026 Hoofie Puppet, CC BY-NC-SA 4.0 (see the repo's LICENSE)

ACS Anino ("Active Camouflage Suit") is a loose, full-body suit covered in small LED pixels. Cameras on the
back of the suit watch the scene behind you, and a Raspberry Pi shows that picture on the pixels on your front,
so your outline blends into the background. It is built from cheap, common parts and made to be built one
section at a time by an ordinary maker with a hobby printer.

**Status:** planning. Concept, name, logo, parts list and section plan are done. The module case is next.

## What Anino is for

Anino is a maker project, a costume and an engineering experiment, not a product claim. It exists to:

- show how camera-based "see-through" camouflage works, using parts an ordinary maker can buy;
- make a wearable piece for costume, stage, art and photography: a person who seems to fade into the backdrop;
- be a modular test bed, so better pixels, cameras and software can be swapped in later without starting over.

It does not hide you from infrared or thermal cameras, and it does not work up close or from every direction.

## What it does

Cameras on the back of the suit watch the scene behind you, and the pixels on your front show that scene. A viewer
in front of you sees something close to what is behind you where your body would be. Cameras on the front can feed
the pixels on your back the same way.

## The theory

If every spot on the front of your body shows the light that would be coming from the scene behind that spot, the
eye reads the background instead of a body. Two things have to be right:

- **Perspective:** the picture has to look as if it was taken from where the viewer's eye is looking through you.
- **Brightness and color:** the pixels have to be bright and colorful enough to match the real background.

A flat picture can only be correct from one direction and distance. When the viewer moves, the real background
shifts differently from the picture (parallax), and the illusion breaks. That is why Anino aims for a soft, coarse
match instead of a perfect one. This is the principle of disruptive camouflage: you don't need to erase the body,
only to match its brightness and color and break up its outline until the eye stops seeing a person.

There are two ways to put the picture on the body:

| Approach | How it works | Trade-off |
| --- | --- | --- |
| **Own light (Anino)** | LED pixels or screens make their own light | Readable in daylight and works on its own; costs power, wiring and heat on the body |
| **Reflected light (projector)** | A cloak covered in retroreflective cloth is lit by a projector beside the viewer's eye | Cheap cloth, but the projector must be near the viewer, so it can't be worn alone |

A black or light-absorbing cloak can't help a projector: a projector can only add light, never darken a surface, and
a black surface reflects almost nothing back to show.

## Inspiration

- **Researchers' camera cloaks.** Videos of "invisible man" style demos, where a hand held in front of a camera-backed
  panel seems to vanish. The best-known research is the optical camouflage work from Susumu Tachi's lab at the
  University of Tokyo, first described in 2003: a coat covered in retroreflective material, a camera behind the
  wearer and a projector at the viewer's side.
- **The two-tablet trick.** A video of someone with a tablet on each side of their body, one filming and the other
  showing, to look as if there is a hole through them. It proved the idea works with ordinary screens.
- **Flexible OLED is out of reach.** The screens that would suit a suit best are expensive and not sold to ordinary
  makers, so Anino asks how close cheap, coarse LED pixels can get.
- **Making it for the average maker.** Take something that normally needs a lab, and design it so it can be built in
  sections with a hobby printer and basic tools.

## What it can and can't do

Nobody can make a person truly invisible. Anino is an **outline breaker**, built on a budget. It works best:

- for a viewer straight in front of you, since the picture is right from one direction only;
- at a distance and in dim light, where coarse pixels and a soft match are enough to hide the shape;
- with slow movement, because the picture has to keep up with you.

Up close, from the side, or in bright light it will read as a glowing blob, and moving viewers will see the
picture shift (parallax).

## How it works

```
[ back camera ] --USB--> [ Pi 4 hub ] --WiFi--> [ ESP32 in every section ]
  sees the scene          cuts the picture              |  drives that section's
  behind you              into slices                   v  strings of pixels
                                               [ pixels on your front ]
                                                 show the scene behind you
```

The pixels are coarse on purpose: roughly one every 5 to 8 cm and about 1,000 in all. That is plenty to break up
a silhouette, it keeps the power draw sane, and a white diffusion layer over them softens the dots into a smooth
picture. The pixels make their own light, so they stay readable in daylight, which a projector cannot do.

## Sections

The suit is a loose, non-stretch coverall cut into seven sections, each a small self-contained module:

| Section | Carries |
| --- | --- |
| Torso front | The Pi 4 hub, the back camera, its own pixels |
| Torso back | The front camera, its own pixels |
| Left arm, right arm | Pixels |
| Left leg, right leg | Pixels |
| Hood | Pixels, mesh face panel |

Every section has:

- its own **pixels**, sewn or snapped onto that piece of the suit;
- its own **ESP32** (WLED-style pixel firmware) that takes its slice of the picture from the Pi over WiFi, so no
  data cable runs between sections;
- its own small **5 V converter and fuse** taking power from a thin 12 V trunk, so a short stays inside its own
  section;
- the same **two-pin XT30 plug** and the same **printed case**: design once, print seven.

Sections join with separable zippers at the shoulders, hips and hood. A loose fit lets air move, which matters in
Philippine heat, and mesh panels under the arms, on the back and over the face let the electronics breathe.

## Power

A 3S (12 V) Li-ion pack feeds a thin trunk line, with a 15 A main fuse. A USB power bank cannot supply the current
(about 15 A at 5 V with everything lit), so do not use one.

## Build stages

1. Plan: concept, name, logo, parts list, section plan. (done)
2. Module design: one printed case for the ESP32, 5 V converter, fuse and plug. (now)
3. Torso front: the Pi, one camera and pixels. Prove the camera-to-pixels loop and measure the lag.
4. Torso back, with the second camera.
5. Arms, one at a time.
6. Legs, one at a time.
7. Hood last: mesh face panel, wiring and comfort.
8. Outdoor test at dusk, then the optional extras (side cameras, gloves and boots).
9. Mk II: try one or two LED matrix panels on the chest (only after Mk I works).

## Versions

- **Mk I (the plan now):** pixel strings over the whole suit. Coarse dots softened by the white diffusion fabric. Cheap, flexible, and it covers the whole body. This is what the parts list builds.
- **Mk II (planned, not built):** flexible 16x16 LED matrix panels (256 pixels, about 16 cm square) on the big flat areas first: chest and back, then thighs. A much finer picture, but more current and more money, so it goes on in patches, not as a full-body skin.
- **Later ideas:** depth cameras or head tracking so the picture is corrected for where the viewer stands, and side cameras for 360 degrees.

## Files

- [bill-of-materials.md](bill-of-materials.md): every part with quantities, rough costs and Lazada/Shopee search terms
- [anino-logo.png](anino-logo.png): the logo (violet and amber on black)

No STLs yet: the module case comes first.

Project page: https://hoofiepuppet.neocities.org/anino.html

(c) 2026 Hoofie Puppet. Designs, pictures and build guides: CC BY-NC-SA 4.0.
