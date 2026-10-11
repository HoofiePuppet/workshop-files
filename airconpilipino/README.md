![Aircon Pilipino](airconpilipino-logo.png)

# Aircon Pilipino

**Status:** Released · **Build cost:** about ₱500 · **Designer:** Hoofie Puppet
**License:** (c) 2026 Hoofie Puppet, CC BY-NC-SA 4.0 (see the repo's LICENSE)
**Shopping list:** [bill-of-materials.md](bill-of-materials.md) · **Logo:** [LOGO.md](LOGO.md)

A personal cooling device for the Philippine heat, worn on the inside of the wrist. A Peltier module cools the skin where the blood flow is close to the surface, helping cool the whole body. It runs from a USB power bank. There are a few devices like this to build, but this one is a little different in structure, assembly and parts.

## How it works

```
 power bank (USB) --> MT3608 boost converter
                        |  IN  --> 4010 fan (always running, at power-bank voltage)
                        |  OUT --> TEC1-12706 Peltier, set to about 7–8 V
                        v
 wrist <-- cool side | Peltier | hot side --> thermal grease --> heatsink --> fan blows the heat away
```

## ⚠️ Safety (read before soldering)

- **Make sure the Peltier module can't freeze-burn your skin.** Set the MT3608 output before wearing it, start low and test it for a short time.
- **NEVER run it without the fan spinning.** Without the fan the hot side heats up within seconds and the "cool" side quickly gets hot against your skin.
- **If the fan stops, take it off your wrist straight away.**
- About 7–8 V on the Peltier is comfortable. Go up or down to what is comfortable and safe for you; too high cancels out the cold side.

## Files

| File | Part | Material |
|---|---|---|
| Container.stl | Cage | PETG |
| Lid_A.stl | Lid A (fan lid, glued to the cage) | PETG |
| Lid_B.stl | Lid B (MT3608 box lid) | PETG |

## Print

- All parts in **PETG** for overall strength.
- Print the cage at a **45° angle** for maximum strength, with **more than 3 walls** and **tree supports**. The tree supports are easy to remove.
- Add a **brim** to keep the other parts down.

## Set the MT3608 (before final soldering)

1. Solder the **fan** to the MT3608 **V+ IN** and **V− IN**.
2. Solder the **Peltier module** to the MT3608 **V+ OUT** and **V− OUT**.
3. Plug into the power bank and turn the MT3608 trim screw while measuring the output with a multimeter. Set it to about **7–8 V**.

This keeps the Peltier at the voltage you set, while the fan runs continuously at the power bank's voltage.

## Assembly

1. Slide the Peltier module in through the bottom of the cage. Make sure the letters **TEC1-12706** are visible: that's the cool side that touches your wrist.
2. Through the top of the cage, use a cotton swab to spread thermal grease on top of the Peltier module.
3. Drop the heatsink in.
4. Place the fan in, sticker side down, and pull the wires through the side hole.
5. Put a small amount of epoxy at each corner and attach Lid A.
6. Twist the wires together, pull them through the hole in the MT3608 box, and solder.
7. Fit Lid B on the MT3608 box. Use hot glue so you can get back in later.
8. Attach the 22mm watch straps and plug into your power bank.

Build photos are on the Aircon Pilipino page of the Hoofie Puppet's Workshop BBS website.
