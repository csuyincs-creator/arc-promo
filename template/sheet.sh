#!/bin/sh
# usage: sheet.sh out.jpg cols f1 f2 ...   (labels each tile with its frame number)
out=$1; cols=$2; shift 2; n=$#; rows=$(( (n + cols - 1) / cols )); args=""; fl=""; i=0
for f in "$@"; do args="$args -i out/stills/f$f.jpg"; fl="$fl[$i:v]scale=800:450,drawtext=text='$f':fontcolor=yellow:fontsize=22:x=8:y=8:box=1:boxcolor=black@0.5[v$i];"; i=$((i+1)); done
cat=""; i=0; for f in "$@"; do cat="$cat[v$i]"; i=$((i+1)); done
ffmpeg -loglevel error -y $args -filter_complex "${fl}${cat}concat=n=$n:v=1:a=0,tile=${cols}x${rows}" -frames:v 1 "$out"
