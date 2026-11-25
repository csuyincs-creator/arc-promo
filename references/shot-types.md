# Shot types and parameters (shots.json)

Geometry (fixed, shared with the Remotion template): output canvas 4480×2400 = the 3840×2160 frame
plus 320 px margin left/right and 240 px on top. The arc is a circle of radius 3700 px whose top
is at 60% of the frame height, horizontally centred. Every entry:

```json
{"name": "dune", "type": "bend", "src": "dune", ...params, "credit": "...", "license": "CC0", "url": "..."}
```
`src` is a file stem in `raw/` (`.jpg/.png/...` found automatically). `name` is the output stem and
what `project.json` refers to. Add `"ink": "light"|"dark"` to override the auto text colour.

## Choosing a type

| The picture shows… | Type | Why |
| --- | --- | --- |
| A landscape / seascape / skyline with a horizon | `bend` | its horizon row is wrapped onto the arc - a "tiny planet" |
| Earth's limb from orbit (ISS photos) | `bend` with `rot` to level the limb first | |
| A round object on a background: planet disc, Sun, bubble, dandelion, fruit slice, plate, eye | `disc` | its circle is scaled onto the arc |
| An equirectangular map (Earth, Moon, Mars, Jupiter…) | `sphere` | rendered as a planet whose limb is the arc |
| A texture or busy image with no horizon: a field, ice, a botanical plate, a crowd | `texture` | poured into the disc with a flat paper background above |
| Nothing suitable / need a graphic beat | `procedural` | blueprint, globe, collage, topo, thin_film |

## bend

| param | meaning |
| --- | --- |
| `horizon` | horizon row as a fraction of the (rotated) image height, 0 top … 1 bottom. Read it off the 10% grid sheet: the line where land/sea meets sky. |
| `xc` | which column sits at the centre of the arc (0..1, default 0.5) - put the subject there |
| `rot` | degrees to rotate the source first (PIL: positive = counter-clockwise; use positive when the horizon falls to the right) |
| `zoom` | >1 magnifies (default fits the arc width; needs ≥ ~3800 px wide sources for 4K) |
| `clear_above` | blank every canvas row above this (px) - removes something cropped at the top |
| `paste` | `{cx, cy, half, x, y, scale}`: cut a square (centre cx,cy half-size half, source px) and set it at (x, y) px relative to the arc top centre - e.g. lift the Earth in *Earthrise* into frame |

The sky above the horizon stays sky; things far above (balloons, aurora, the Milky Way) bend
gently. If `horizon` is near 0 or 1 there is too little sky/ground and edges smear - pick another image.

## disc

| param | meaning |
| --- | --- |
| `circle` | `[cx, cy, r]` in source pixels, or `"auto"` for a bright object on a dark background |
| `thr` | auto mode: luminance threshold 0..1 (raise it if a glow/corona inflates the circle - for the SDO Sun images use a manual circle at the bright limb) |
| `rot` | rotate about the circle centre (degrees) - e.g. turn a snowflake so an arm points up at the arc |
| `bg` | `[r,g,b]`: replace everything outside the circle with paper of this colour (use when the photo's surroundings are ugly or run out) |

The visible part is only the top ~25% of the circle (the frame shows ~860 px below the arc top),
scaled by 3700/r. Small circles (r < 600 px) look soft; fine for 0.2-0.3 s shots, not for slow ones.
Always verify with `check_circle.py` - estimating circles from a thumbnail is error-prone.

## sphere

| param | meaning |
| --- | --- |
| `top_lat` | latitude at the top of the limb. The visible band spans roughly `top_lat` (at the limb) down to `top_lat − 40°` at the bottom centre. `0` with a banded planet gives bands parallel to the arc. |
| `lon0` | longitude at the centre |
| `light` | sun direction `[x, y, z]` in view space (x right, y up, z toward viewer). `[-0.4, 0.8, 0.5]` = lit from upper left; `[0.9, 0.4, 0.3]` = low side light (terminator crosses the frame); `[0, 0.2, -1]` = night side |
| `albedo`, `ambient` | brightness of the map; light on the dark side |
| `atmo`, `atmo_w` | rim glow colour `[r,g,b]` (0..1) and thickness (px). Earth `[0.32,0.6,1]`/70, Mars `[0.9,0.45,0.3]`/45 |
| `night` | a city-lights map stem (Black Marble) shown on the unlit side |
| `spin` | roll in degrees so bands are not exactly parallel |

## texture

| param | meaning |
| --- | --- |
| `bg` | `[r,g,b]` paper colour above the arc - pick a strong contrast with the texture (cream behind purple, navy behind ice, lavender behind black plates) |
| `fit`, `xc`, `yc` | scale (≥1 zooms in) and which part of the texture shows |
| `rim` | bright edge line strength (0..1) |
| `shade` | darkening toward the bottom (0..1) - makes it read as a rounded object |

## procedural

`{"type": "procedural", "kind": "blueprint" | "globe" | "collage" | "topo" | "thin_film"}`.
Optional: `color` (background `[r,g,b]`, blueprint/globe/collage), `base` (collage disc colour),
`seed` (collage). Light-ink shots: blueprint, topo, thin_film. Dark-ink: globe, collage.

## earth_rise (opening and loop)

`{"name": "earth_rise", "type": "earth_rise", "night": "earth_night", "top_lat": 52, "lon0": 60}` -
writes `earth_rise.jpg` (Earth's night side) and `earth_rise_glow.jpg` (the sunrise band along the
limb, screen-blended and brightened over the first shot; the end card sinks it, blurs it, then
raises it back so frame N ≈ frame 0). If `project.json`'s `opening` is a different shot, the film
opens on that shot instead (no glow layer) and the end card uses it.

## Performance and quality notes

- Sources should be ≥ 3840 px wide for `bend`/`texture`; ≥ 2048 px maps for `sphere` (8K Earth is best).
- One shot takes ~1-2 s; the whole list of ~40 about a minute.
- `manifest.json` records each shot's text ink (`light`/`dark`) from the brightness just above the arc.
