// Sol Prosthetics — Model 1 "Bukang-liwayway" (Sunrise), v1 test print, 100% scale.
// Wrist-driven: bending the wrist down pulls the flexor lines and closes the fingers.
// Frame: X across the hand (thumb side = -X, right hand), Y toward the fingertips,
// Z up from the palm side (z = 0) to the back of the hand.
// Hardware: M3 stainless screws. Joints: clearance 3.4 + head recess on one side,
// 2.6 pilot on the other side so the screw threads into the plastic (no nut).

const B = (x0: number, x1: number, y0: number, y1: number, z0: number, z1: number) =>
  box(x1 - x0, y1 - y0, z1 - z0).translate(x0, y0, z0);
const capX = (x0: number, x1: number, y: number, z: number, r: number) =>
  cylinder(x1 - x0, r, 48).alongAxis([1, 0, 0]).translate(x0, y, z);
const capY = (y0: number, y1: number, x: number, z: number, r: number) =>
  cylinder(y1 - y0, r, 48).alongAxis([0, 1, 0]).translate(x, y0, z);
const capZ = (z0: number, z1: number, x: number, y: number, r: number) =>
  cylinder(z1 - z0, r, 48).translate(x, y, z0);

const CLR = 1.7;   // M3 clearance radius (3.4)
const PIL = 1.3;   // M3 pilot radius (2.6) — screw threads into PETG
const HEAD = 3.0;  // M3 head recess radius (6.0), 2 mm deep

// ---------- One finger segment ----------
// Joint axis on local X at the origin; the segment runs along +Y.
// Proximal end: fork (two arms) that takes the previous segment's tongue.
// Distal end: tongue for the next fork, or a rounded fingertip.
function phalanx(L: number, tip: boolean) {
  const bodyEnd = tip ? L : L - 6.5;
  let s = capX(-7, 7, 0, 0, 6).union(B(-7, 7, 0, bodyEnd, -6, 6));
  if (tip) s = s.union(capX(-7, 7, L, 0, 6));
  else s = s.union(B(-2.8, 2.8, L - 7, L, -6, 6), capX(-2.8, 2.8, L, 0, 6));
  s = s.subtract(
    B(-3.1, 3.1, -7, 6.8, -7, 7),            // fork slot (6.2 wide for a 5.6 tongue)
    capX(-8, -3, 0, 0, CLR),                  // screw clearance, near arm
    capX(-8, -5, 0, 0, HEAD),                 // head recess
    capX(-4, 8, 0, 0, PIL),                   // pilot, far arm
    capY(-8, L + 8, 0, -3.2, 1.1),            // flexor line channel (palm side)
    capY(-8, L + 8, 0, 3.2, 1.1),             // return channel (back side)
  );
  if (!tip) s = s.subtract(capX(-3, 3, L, 0, CLR)); // tongue hole
  return s;
}

// ---------- Palm ----------
const FX = [-23.25, -7.75, 7.75, 23.25];     // index, middle, ring, little
const KY = 62, KZ = 15;                       // knuckle axis
let palm = B(-33, 33, 0, 55.5, 0, 30).fillet(3);
for (const x of FX) palm = palm.union(B(x - 2.8, x + 2.8, 55, KY, KZ - 5.5, KZ + 5.5), capX(x - 2.8, x + 2.8, KY, KZ, 5.5));
palm = palm.union(
  B(32, 37, -8, 8, 6, 18), capX(32, 37, -8, 12, 6),         // wrist ear, right
  B(-37, -32, -8, 8, 6, 18), capX(-37, -32, -8, 12, 6),     // wrist ear, left
);
const diag = (x: number) => {
  const a = [x, 56.5, 11.8], b = [x, 49, 31];
  const d = [0, b[1] - a[1], b[2] - a[2]];
  const len = Math.hypot(d[1], d[2]);
  const u: [number, number, number] = [0, d[1] / len, d[2] / len];
  return cylinder(len + 6, 1.1, 32).alongAxis(u).translate(a[0], a[1] - 3 * u[1], a[2] - 3 * u[2]);
};
const vents: any[] = [];
for (const x of [-15.5, 0, 15.5]) for (const y of [12, 24, 36]) vents.push(capZ(24, 31, x, y, 3));
palm = palm.subtract(
  B(-28, 28, -1, 48, 4, 25),                                   // hand cavity, open at the wrist
  B(-24, 24, -1, 44, -1, 5),                                   // open palm side, U-shaped (straps hold the hand)
  B(-34, -27, 29, 47, 5, 9), B(27, 34, 29, 47, 5, 9),          // palm strap slots (16 mm strap)
  ...FX.map(x => capX(x - 3.5, x + 3.5, KY, KZ, CLR)),         // knuckle screw holes
  ...FX.map(x => capY(54, KY + 8, x, KZ - 3.2, 1.1)),          // flexor line through each tongue
  ...FX.map(x => diag(x)),                                      // line up to the back of the hand
  ...FX.map(x => B(x - 1.25, x + 1.25, -1, 50, 28.2, 31)),     // line grooves on the back
  ...vents,
  capX(30, 38, -8, 12, PIL), capX(-38, -30, -8, 12, PIL),      // wrist screw pilots
);
// Thumb tongue, angled 35 degrees toward the fingertips so the thumb opposes the fingers.
const TP: [number, number, number] = [-33, 18, 8];
palm = palm.union(
  B(-44, -30, 15.2, 20.8, 2.5, 13.5).union(capY(15.2, 20.8, -44, 8, 5.5))
    .subtract(capY(14, 22, -44, 8, CLR)).rotateZ(-35, TP),
);

// ---------- Thumb (positionable: set the angle, tighten the screw) ----------
let thumb = capX(-7, 7, 0, 0, 6).union(B(-7, 7, 0, 26, -6, 6), capX(-7, 7, 26, 0, 6));
thumb = thumb.subtract(
  B(-3.1, 3.1, -7, 6.8, -7, 7), capX(-8, -3, 0, 0, CLR), capX(-8, -5, 0, 0, HEAD), capX(-4, 8, 0, 0, PIL),
);

// ---------- Gauntlet ----------
const GZ = 12;
const TX = [-15, -5, 5, 15];
let g = capY(-112, -17, 0, GZ, 32.5).union(
  // tensioner block, 45-degree underside so it prints standing up without supports
  extrudePolygon([[-32, 36], [-32, 50], [-55, 50], [-69, 36]], 40).rotate([1, 1, 1], 120).translate(-20, 0, 0),
  // wrist ears with 45-degree gussets underneath
  extrudePolygon([[31, -40.3], [41.3, -30], [41.3, -15], [31, -15]], 12).translate(0, 0, 6),
  B(37.3, 41.3, -15.5, -8, 6, 18), capX(37.3, 41.3, -8, 12, 6),
  extrudePolygon([[-31, -15], [-41.3, -15], [-41.3, -30], [-31, -40.3]], 12).translate(0, 0, 6),
  B(-41.3, -37.3, -15.5, -8, 6, 18), capX(-41.3, -37.3, -8, 12, 6),
);
const gv: any[] = [];
// diamond vents: 45-degree sides print without supports when the gauntlet stands up
for (const x of [-12, 0, 12]) for (const y of [-104, -92, -80, -68]) gv.push(extrudePolygon([[0, -4.5], [4.5, 0], [0, 4.5], [-4.5, 0]], 19).translate(x, y, 28));
g = g.subtract(
  capY(-113, -16, 0, GZ, 29.5),                                 // forearm space
  B(-24, 24, -113, -16, -30, -8),                               // open underside
  capX(37, 42, -8, 12, CLR), capX(39.3, 42, -8, 12, HEAD),      // wrist screws
  capX(-42, -37, -8, 12, CLR), capX(-42, -39.3, -8, 12, HEAD),
  ...TX.map(x => capZ(42.5, 51, x, -43.5, PIL)),                // tension screws
  ...TX.map(x => B(x - 1, x + 1, -43.5, -31, 48.5, 51)),        // line grooves to each screw
  B(-31, -23, -50, -23, -6, -2), B(23, 31, -50, -23, -6, -2),   // strap slots (25 mm)
  B(-31, -23, -100, -73, -6, -2), B(23, 31, -100, -73, -6, -2),
  ...gv,
);

// ---------- Assembly (straight fingers, as built) ----------
const LEN = [[22, 15.5, 13], [24, 16.5, 14], [22, 15.5, 13], [18, 15.5, 12]];
const NAMES = ['index', 'middle', 'ring', 'little'];
const a = assembly('bukang-liwayway');
a.part('palm', palm.color('#ffb000'));
a.part('gauntlet', g.color('#ff7a00'));
a.part('thumb', thumb.rotateZ(90).rotateY(-35).translate(-44, 18, 8).rotateZ(-35, TP).color('#ffd23f'));
FX.forEach((x, i) => {
  const [p, m, d] = LEN[i];
  a.part(`${NAMES[i]}-1`, phalanx(p, false).translate(x, KY, KZ).color('#ffd23f'));
  a.part(`${NAMES[i]}-2`, phalanx(m, false).translate(x, KY + p, KZ).color('#ffd23f'));
  a.part(`${NAMES[i]}-3`, phalanx(d, true).translate(x, KY + p + m, KZ).color('#ffd23f'));
});
return a.model();
