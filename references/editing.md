# Editing, effects and review

## What the template does (no code changes needed)

- **Cuts** at every time in `timeline.json`; the first three shots are the slow intro.
- **Per-shot camera** (`Shot.tsx`): a zoom punch on the cut that settles (scaled about the arc top, so
  the arc stays put); the world turns slowly around the circle's centre so the surface slides under
  the words; RGB split for the first frames of hard cuts; a tiny shake once cuts are very fast.
  Strength = `energy`, rising from 0.55 to 1 across the film, +0.35 on big hits.
- **Rise**: at the cut where the words begin and at each phrase change, the new world slides up from
  below over the old one (planet-rise).
- **Flashes** on `bigHits`; a white flash at the first cut as the sun breaks over the opening limb.
- **Light leaks** that pulse on cuts, **film grain**, **vignette**.
- **Text on the arc** (`ArcText.tsx`): line1 above, line2 hugging the curve, both bent along circles
  concentric with the horizon; letters fade in one by one while the phrase lifts off the arc and
  sharpens from a blur. Ink flips light/dark per shot from the manifest. The last phrase grows 14%
  per cut.
- **End card**: cards share the time before the rise; `title` cards get a light sheen; then the opening
  world rises, sharpens and brightens back to frame 0 (the film loops).

## Knobs in project.json

| key | effect |
| --- | --- |
| `textStart` | when the first phrase appears (s). Default 53% of the end-card time. Earlier = more words, less pure picture. |
| `phrases` | 3-4 work best. Keep line1 ≤ 4 CJK characters or ≤ 2 short words; line2 ≤ ~18 characters. |
| `growLast` | `false` to stop the last phrase growing |
| `textSize` | `{line1, line2}` px at 1080p. Defaults: line1 84 (CJK) / 100 (Latin, no line2) / 72 (Latin over a line2); line2 32 |
| `fonts` | CSS font stacks for line1 / line2. Defaults: Songti SC + Iowan Old Style (macOS). For Japanese use `"Hiragino Mincho ProN"`; for Latin-only, a serif such as `"Iowan Old Style"` for both. |
| `ink` | `{shotName: "dark"}` overrides the automatic colour |
| `endCards` | `[{kind: "title", line1, line2}, {kind: "line", line1, line2}]`; one or two cards |
| `endColor` | end-card background |

Deeper changes (timings of effects, colours of leaks, sizes of the sun flare) live in `src/Shot.tsx`,
`src/Effects.tsx`, `src/Planet.tsx`, `src/EndCard.tsx`.

## Ordering the shots

- Alternate dark and light skies, warm and cool, photo and drawn - every cut should be a jolt of colour
  while the shape stays the same.
- Under each phrase's **first frames** use a calm, legible area above the arc (clear sky, plain paper,
  space). Busy tops (cherry blossoms, bright sunset bands) are fine later in a phrase.
- Movement by meaning: big → vast → journey → small/wonder. End the last phrase on something soft and
  bright (dandelion, fog, feather) so the cut to the dark end card lands.
- Avoid repeating a shot; if `order` is shorter than the cut count it cycles.

## Review checklist (look at the stills sheet)

1. Every shot: the curved edge meets the arc line at the centre of the frame; nothing important cropped.
2. Text: readable on every shot it sits over (check one frame per phrase per ink); not touching the edge.
3. First phrase visible ≥ 1.5 s; the last phrase fills the end of the cut sequence and grows.
4. Opening: limb glow rises, flash on the first cut. End: each card fully revealed before it leaves;
   last frame vs first frame difference small (`ffmpeg … blend=difference,signalstats` YAVG < ~6).
5. After the final render: `ffprobe` (3840×2160, 25 fps, frame count = duration×25), `blackdetect`
   (no unintended black), audio levels sane, a frame strip looked at end to end.

## Troubleshooting

- `npm ci` / symlink errors → the workspace is on exFAT/FAT: move it to the internal disk.
- Fonts render as a fallback → the named font is not installed; change `fonts` in project.json.
- A shot shows smeared stripes at the top → `bend` horizon too low/high for that image, or `disc`
  circle too high; fix parameters or `bg`.
- Render is slow → it is normal at `--scale=2` (4K); for drafts use `npm run render:hd`.
