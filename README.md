# arc-promo

**简体中文** · [中文说明](README.zh-CN.md)

An agent skill that turns a message plus some pictures into a 15–30 s, 4K cinematic promo
film in the "one horizon arc" match-cut style.

Every shot is the top edge of a round world, always at the same place in the frame, so hard
cuts read as a single horizon changing identity: Earth's limb at dawn → a soap bubble → the
Sun → a chalk blueprint → Mars → a lavender field → a snowflake. Cuts land on the music and
accelerate; the message appears a phrase at a time *on* the curve; the last word grows with
each cut; a title card follows; then the dawn rises again so the film loops.

```
a message  +  a folder of images (optional)  →  out/promo_4k.mp4
```

## What it does

| Stage | What happens |
| --- | --- |
| **Story** | Turns your message into 3–4 short phrases that build one sentence, plus 1–2 end cards. Bilingual is supported (e.g. Chinese + English per phrase). |
| **Material** | Uses your images; if you give none, searches Wikimedia Commons for CC0 / public-domain images only, and downloads NASA base maps for the planet shots. |
| **Shots** | Classifies each image (landscape → `bend`, round object → `disc`, planet map → `sphere`, pattern → `texture`, drawn → `procedural`) and renders it onto the arc at 4480×2400 with a contact sheet you can review. |
| **Cut** | Either the bundled 20.06 s track's cut grid (37 shots, 8 big hits), or the rhythm of a reference video, or beats detected in any audio file you supply. |
| **Render** | Remotion → 4K MP4, plus a 1080p H.264 version, `CREDITS.md`, and the project source. |

## Requirements

- macOS or Linux, workspace on **APFS / HFS+** (or ext4): `node_modules` needs symlinks, so
  exFAT / FAT external drives fail.
- `ffmpeg` + `ffprobe` on `PATH`
- Node.js ≥ 18
- Python 3 (`numpy`, `pillow` are installed into a local `.venv` by the setup script)
- Network on first setup: `npm ci` and a one-off ~140 MB headless Chrome download for Remotion

## Install as a skill

Clone this repo into the directory your agent scans for skills, keeping the folder name
`arc-promo`:

```bash
git clone https://github.com/csuyincs-creator/arc-promo.git ~/.agents/skills/arc-promo
```

Any equivalent skills directory works — what matters is that `SKILL.md` ends up at
`<skills-dir>/arc-promo/SKILL.md`.

The skill loads from `SKILL.md`; `scripts/`, `references/`, `template/` and `assets/` must stay
next to it.

## Use

Just ask for the film — the skill triggers on promo / 宣传片 / 短片 / trailer requests and on
"remake that arc video" requests.

> Make a 20-second promo for my coffee brand. Message: 每杯 / 都是 / 一次 / 出发.
> The target line: 每一次出发，都值得被认真对待.
> Use the photos in ~/Pictures/coffee, 4K please.

Or point it at a reference for the rhythm:

> Same style, but cut to this song from 0:42, 20 seconds long.

Outputs land in `out/` inside a scratch workspace: `promo_4k.mp4`, `promo_1080p.mp4`,
`CREDITS.md`, and the full Remotion project.

## Soundtrack and rights

The bundled track (`assets/default-music/music.wav`, 20.06 s) is **third-party music**: its
copyright belongs to its original composer, not to this repo. License it or replace it before
publishing.

To use your own music:

```bash
$PY scripts/analyze_music.py --audio song.mp3 --start 42 --length 20 --out <ws>
$PY scripts/analyze_music.py --video reference.mp4 --out <ws>    # copy a film's cut rhythm
```

Both regenerate `src/data/timeline.json`, so the edit follows the new track. The two demo
files in `assets/default-music/` restore the default when copied back.

## Images and licensing

- Only **CC0 / public-domain** images are sourced automatically, and only from Wikimedia
  Commons, with `credit`, `license` and `url` recorded per shot in `shots.json`.
- `make_credits.py` turns that into `CREDITS.md`; shots without a recorded licence are flagged
  as `UNKNOWN` rather than silently shipped.
- The skill will not copy a reference film's branding (logos, product names, wordmarks) onto
  the end cards — that would make the piece read as someone else's official ad.

## Repository layout

```
SKILL.md                     the skill itself (loaded by the agent)
references/
  shot-types.md              shot types and their parameters
  sourcing.md                how to search and download CC0 material
  editing.md                 ordering rules and the review checklist
  example-demo/              a complete worked example (shots.json, project.json)
scripts/
  setup_workspace.sh         template + npm ci + .venv
  analyze_music.py           video/audio → cut grid (timeline.json)
  fetch_base_maps.sh         NASA base maps for planet shots
  search_commons.mjs         Wikimedia Commons search
  fetch_commons.mjs          paced downloader
  gen_shots.py               renders every shot onto the arc
  gridsheet.py               contact sheet with a 10% grid for reading horizon rows
  check_circle.py            verifies a circle's centre/radius
  shot_sheet.py              review sheet of finished shots
  make_credits.py            shots.json + timeline + project → CREDITS.md
template/                    the Remotion project (Arc, Shot, Planet, EndCard, Effects…)
assets/default-music/        default soundtrack + its cut grid
```

## Limits

- The agent cannot hear the result. Sync is verified visually (cut times, levels, frame
  strips), not by ear — the skill says so when delivering.
- 4K render takes roughly 3–6 minutes for a 20 s film; the first Remotion run in a new
  workspace downloads headless Chrome.
- Planet shots need the NASA base maps; without them those shots are skipped rather than faked.

## Licence

No licence file is included. Third-party music and photographs keep their own terms.
