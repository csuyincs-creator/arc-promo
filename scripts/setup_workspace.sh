#!/bin/bash
# Create an arc-promo workspace: the Remotion template, node modules and a Python env.
#   setup_workspace.sh <workspace-dir>
# The workspace must live on APFS/HFS+ (not exFAT/FAT): node_modules needs symlinks.
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
WS="${1:?usage: setup_workspace.sh <workspace-dir>}"
mkdir -p "$WS"
WS="$(cd "$WS" && pwd)"
MP=$(df -P "$WS" | tail -1 | awk '{print $NF}')
if mount | grep -E " on $MP \(" | grep -qiE "exfat|msdos|fat32"; then
  echo "ERROR: $WS is on an exFAT/FAT volume ($MP). Use a folder on the internal disk (e.g. the session scratchpad) and copy results out at the end." >&2
  exit 1
fi
cp -R "$SKILL/template/." "$WS/"
mkdir -p "$WS/raw" "$WS/public/shots" "$WS/src/data" "$WS/out/stills"
# Default soundtrack + its cut list (used unless the user asks for other music; analyze_music.py overwrites both).
cp "$SKILL/assets/default-music/music.wav" "$WS/public/music.wav"
cp "$SKILL/assets/default-music/timeline.json" "$WS/src/data/timeline.json"
cd "$WS"
npm ci --no-audit --no-fund >/dev/null 2>&1 || npm install --no-audit --no-fund >/dev/null
python3 -m venv .venv
./.venv/bin/pip install -q numpy pillow
echo "workspace ready: $WS"
echo "python: $WS/.venv/bin/python   scripts: $SKILL/scripts"
