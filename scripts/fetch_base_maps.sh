#!/bin/bash
# Public-domain NASA maps used by the earth_rise opening and the sphere shots.
#   fetch_base_maps.sh <raw-dir>      -> earth_night.jpg earth_day.jpg moon.jpg mars_map.jpg
set -uo pipefail
RAW="${1:?usage: fetch_base_maps.sh <raw-dir>}"; mkdir -p "$RAW"; cd "$RAW"
UA="Mozilla/5.0 (Macintosh) media-fetch/1.0"
get() { [ -s "$1" ] && { echo "have $1"; return; }; curl -sfL -m 300 -A "$UA" -o "$1" "$2" && echo "got $1" || echo "FAILED $1 ($2)"; }
# Black Marble 2016 (city lights), 13500x6750 -> downscaled to 8192 wide
if [ ! -s earth_night.jpg ]; then
  get earth_night_full.jpg "https://assets.science.nasa.gov/content/dam/science/esd/eo/images/imagerecords/144000/144898/BlackMarble_2016_3km.jpg"
  [ -s earth_night_full.jpg ] && ffmpeg -loglevel error -y -i earth_night_full.jpg -vf scale=8192:4096:flags=lanczos -q:v 2 earth_night.jpg && rm earth_night_full.jpg
fi
get earth_day.jpg "https://svs.gsfc.nasa.gov/vis/a000000/a003600/a003615/flat_earth_Largest_still.0330.jpg"   # Blue Marble with clouds, 8192x4096
get moon.jpg "https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_2k.jpg"                        # LRO colour mosaic
[ -s mars_map.jpg ] || node "$(dirname "$0")/fetch_commons.mjs" . "mars_map|4096|Mars Viking MDIM21 ClrMosaic 1km.jpg"
ls -la earth_night.jpg earth_day.jpg moon.jpg mars_map.jpg 2>/dev/null
