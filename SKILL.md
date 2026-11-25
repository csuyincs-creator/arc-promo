---
name: arc-promo
description: Make a 15-30 s cinematic promo video (宣传片 / 宣传视频 / 短片 / trailer) in the "one horizon arc" match-cut style - every shot is the curved edge of a world (real planets, landscapes bent into tiny planets, round macro objects, procedural art) all sitting on the same arc, cut on the beats of a music track, with the user's message (any language; bilingual supported) set along the curve and a looping sunrise end card. Use when someone wants a promo/launch film from a message plus pictures or topics, wants to remake "that arc video" (the one where every shot is the rim of a round world) with their own content, or gives a reference video or song whose cut rhythm the edit should follow. Uses its bundled soundtrack by default (other music only on request). Sources free public-domain/CC0 images itself if none are given. Renders 4K with Remotion.
---

# Arc promo

A short film where **every shot is the top edge of a round world, at exactly the same place
in the frame**, so hard cuts read as one horizon changing identity: Earth's limb at dawn → a soap
bubble → the Sun → a chalk blueprint → Mars → a lavender field → a snowflake … The cuts land on
the music and get faster; the message appears a phrase at a time *on* the curve; the last word
grows with each cut; a title card; then the dawn rises again so the film loops.

Inputs the user gives (ask only for what is missing - the message is the one thing you cannot invent):

| Input | Forms it can take | Default |
| --- | --- | --- |
| **Message** | 3-4 short phrases that build one sentence; optional second language per phrase; 1-2 end cards (title + full line) | none - ask |
| **Music** | **default: the bundled soundtrack** - do not ask. Only if the user asks for other music: a reference **video** (its cuts are copied exactly) or any **audio** file (beats detected) + optional start offset / length | the bundled track, 20.06 s |
| **Material** | a folder of images, and/or **topics to find online** ("oceans, deserts, Chinese mountains, microscopy") | find ~40 images from the message's theme |
| Output folder | where the MP4s and source go | the working directory |

Music is not something to ask about: the bundled soundtrack is the default. Everything after that is your job. Scripts are in this skill's `scripts/` folder (its path is shown
when the skill loads; below it is `$SKILL`). Read `references/shot-types.md` before writing the shot
list, `references/sourcing.md` before searching, `references/editing.md` before ordering and reviewing.

## 0. Workspace

The workspace must be on APFS/HFS+ (node_modules needs symlinks; exFAT/FAT external drives fail).
Use the session scratchpad and copy results to the user's folder at the end.

```bash
bash $SKILL/scripts/setup_workspace.sh <ws>      # template + npm ci + .venv (numpy, pillow)
```
`$PY` below means `<ws>/.venv/bin/python -I`. Needs `ffmpeg`, `node` ≥ 18, `python3`. The first
Remotion command in a new workspace downloads a headless Chrome (~140 MB); if that first run errors, just run it again.

## 1. Music → the cut list

**Default: use the bundled soundtrack.** Unless the user specifically asks for different music, do
nothing here: `setup_workspace.sh` already installed `assets/default-music/music.wav` and its cut list
(`timeline.json`: 37 shots, 8 big hits, end card at 15.96 s, film 20.06 s — the cut grid of the
bundled track). Do not ask the user about music. Plan for 36 shots after the opening.

Only when the user supplies or names other music:

```bash
$PY $SKILL/scripts/analyze_music.py --video ref.mp4 --out <ws>                    # copy a film's rhythm
$PY $SKILL/scripts/analyze_music.py --audio song.mp3 --start 42 --length 20 --out <ws>   # any track
```
It overwrites `public/music.wav` and `src/data/timeline.json`, and prints the shot count `N` (≈35-40
for 20 s). To go back to the default, copy both files from `assets/default-music/` again. In audio mode pick `--start` at a section with a build (a drop/chorus that starts soft);
re-run with `--end-card <s>` if the title card should land on a specific hit.

Rights: the bundled track is third-party music; its copyright belongs to its original composer, not
to this skill.

## 2. Plan the story, then the material

Write the phrases first; the film is about them. Plan `N-1` shots plus the opening in four movements
that track the phrases (adapt the themes to the message):

1. **Slow intro (shots 1-3) and pre-text section** - mixed scales, maximum contrast: cosmos / macro / drawn.
2. **Phrase 1** - the big subject (for "the world": planets, Earth from orbit).
3. **Phrase 2-3** - the subject in the user's terms (landscapes, people's places, journeys…).
4. **Last phrase** (the word grows on every cut, cuts ~0.2-0.3 s) - wonder in small things; end on
   something soft and white (dandelion, fog, feather) before the dark title card.

Material: use the user's images first (copy into `<ws>/raw/`, short lowercase names). Fill the rest
from Wikimedia Commons (`references/sourcing.md`: CC0/public domain only; search in parallel batches,
download with retries; NASA base maps via `fetch_base_maps.sh`). If the user asks for generated
images and an image-generation tool is actually available in this session, use it and record the
tool as the credit; otherwise use the five procedural shots (`blueprint`, `globe`, `collage`, `topo`,
`thin_film`) for the drawn/graphic beats. Aim for ~N+5 candidates so weak ones can be dropped.

## 3. Shots on the arc

For each image decide its **type** and parameters (`references/shot-types.md`):
`bend` (landscape - horizon row onto the arc), `disc` (something round - its circle onto the arc),
`sphere` (a planet map), `texture` (a pattern poured into the disc), `procedural`, `earth_rise`
(the opening/loop; needs `earth_night`).

```bash
$PY $SKILL/scripts/gridsheet.py <ws>/out/raw_sheet.jpg 4 <ws>/raw/*.jpg      # 10% grid: read horizon rows
$PY $SKILL/scripts/check_circle.py <ws>/raw/bubble.jpg <ws>/out/c.jpg 1686,1736,765   # verify a circle
# write <ws>/shots.json (see references/example-demo/shots.json), then:
$PY $SKILL/scripts/gen_shots.py --config <ws>/shots.json --raw <ws>/raw --out <ws>/public/shots --manifest <ws>/src/data/manifest.json
$PY $SKILL/scripts/shot_sheet.py <ws>/public/shots <ws>/out/shots_sheet.jpg
```
**Look at the sheet.** Every shot must show a clear curved edge meeting the red line at the centre.
Fix bad ones (`--only name1,name2` regenerates just those): wrong circle, horizon not on the line,
blurry upscales, cropped subjects. ~1 s per shot at 4480×2400.

## 4. Project file

Write `<ws>/src/data/project.json` (example: `references/example-demo/project.json`):
`opening`, `order` (N-1 names; cycles if shorter - avoid repeats), `phrases` [{line1, line2}],
optional `textStart` (s; default 53% of the end-card time), `growLast`, `endCards`
[{kind: title|line, line1, line2}], optional `fonts`, `textSize`, `ink` overrides.
Order for contrast: alternate dark/light skies and warm/cool colours between neighbours; put the
most legible shots (calm sky above the arc) under each phrase's first frames.

## 5. Review, render, deliver

```bash
cd <ws> && npx tsc --noEmit
SCALE=0.5 node stills.mjs 0 20 40 90 200 250 300 350 380 395 420 470 500 && ./sheet.sh out/s.jpg 4 000 020 040 090 200 250 300 350 380 395 420 470 500
```
Check against `references/editing.md` (text legible on every shot, arc continuous across cuts,
end cards fully revealed before they leave, last frame ≈ first frame). Then:

```bash
npm run render          # 4K: out/promo_4k.mp4 (--scale=2); ~3-6 min for 20 s
ffmpeg -i out/promo_4k.mp4 -vf scale=1920:1080:flags=lanczos -c:v libx264 -crf 18 -c:a copy -movflags +faststart out/promo_1080p.mp4
$PY $SKILL/scripts/make_credits.py <ws>/shots.json src/data/timeline.json src/data/project.json CREDITS.md --music-note "..."
```
Verify the file (ffprobe size/fps/frames; `blackdetect`; a frame strip you look at), copy the MP4s,
`CREDITS.md` and the workspace source (without `node_modules`, `.venv`, `raw`) to the output folder.

## Rules

- **Only CC0 / public-domain** images unless the user supplies their own. Record `credit`, `license`,
  `url` in shots.json for every sourced image; CREDITS.md is generated from it.
- **Do not copy a reference film's branding** (logos, product names, wordmarks) onto the end cards -
  that makes the piece read as the brand's official ad. Use the user's own title.
- **Music rights**: the bundled track, and any track the user brings, is third-party — say plainly
  that it must be licensed or replaced before publishing.
- You cannot hear the result: say that sync was checked visually (cut times, levels), not by ear.
