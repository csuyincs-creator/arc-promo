# Finding material

## Wikimedia Commons (default source)

```bash
node $SKILL/scripts/search_commons.mjs [--min=2000] [--wide] "query" "query" ...
node $SKILL/scripts/fetch_commons.mjs <raw-dir> "name|width|File title.jpg" ...
```
`search_commons.mjs` prints only CC0 / public-domain bitmaps with size and author. `--wide` keeps
landscape-format images (good for `bend`). Query tips that work:

| Need | Query |
| --- | --- |
| CC0 landscapes | `intitle:Unsplash <subject>` (Unsplash uploads on Commons are CC0): `intitle:Unsplash glacier OR iceberg`, `intitle:Unsplash sea of clouds`, `intitle:Unsplash salt flat` |
| Earth from orbit | `Earth limb sunset ISS`, `ISS aurora` (NASA = public domain) |
| Planets | `Pluto in True Color`, `Neptune Full`, `Solar Dynamics Observatory sun`, `Earthrise Apollo 8` |
| Planet maps for `sphere` | `Mars Viking MDIM21 ClrMosaic`, `Jupiter Global Map`, `Moon LRO color` |
| Round natural objects | `intitle:Unsplash dandelion`, `soap bubble`, `Bentley snowflake photomicrograph` |
| Illustration / science art | `Haeckel Kunstformen der Natur <group>`, `Harmonia Macrocosmica Cellarius`, old maps `Blaeu world map` |
| Webb / Hubble | `Cosmic Cliffs Carina Webb`, `Webb First Deep Field`, `Pillars of Creation NIRCam` |

Parallelise searching across themes (several queries per call; or subagents per movement of the
film when the user asked for a big search) but **download in one paced queue**: Commons rate-limits
(HTTP 429) resized thumbnails hard. `fetch_commons.mjs` retries with back-off; width `0` downloads the
original file (no resize) - use it for the 429 stragglers, and wait a minute or two between batches.
If a file keeps failing, substitute a different image rather than stalling.

Record for each image: `credit` (author, title, "via Wikimedia Commons"), `license` (`CC0` /
`Public domain`), `url` (the File: page). Never use CC BY-SA/BY images unless you add proper attribution
and the user agrees; never use images without a clear licence.

## NASA base maps

`fetch_base_maps.sh <raw>` downloads `earth_night` (Black Marble 2016), `earth_day` (Blue Marble with
clouds), `moon` (LRO), `mars_map` (Viking) - all public domain. `earth_night` is required for the
default `earth_rise` opening.

## The user's own pictures

Copy into `raw/` with short ASCII names. Ask (once) whether they own them / may use them in a public
video if that is unclear. Phone photos of a horizon (sea, rooftops, fields) make excellent `bend` shots;
round things they own (a cup from above, a plate, a vinyl record, an eye, a fruit) make `disc` shots.

## Generated images

Only if an image-generation tool is genuinely available in the session (check; do not assume). Prompt
for the arc composition directly: "a huge curved horizon of <subject> filling the lower 40% of a 16:9
frame, top of the curve at 60% height, plain <colour> sky above, macro photograph". Then use `bend`
with `horizon≈0.6` or `disc`. Credit the tool. Otherwise use `procedural` shots.
