#!/usr/bin/env bash
# Stitch frames/ into aiol-loop.mp4 with crossfades. Needs ffmpeg. Run render.py first.
set -euo pipefail
cd "$(dirname "$0")"
FADE=${FADE:-1.2}        # crossfade seconds
SCALE=${SCALE:-1.5}      # multiply every scene hold time
inputs=(); filter=""; offset=0; i=0; n=$(wc -l < scenes.txt)
while IFS=$'\t' read -r path secs; do
  secs=$(python3 -c "print(round($secs * $SCALE, 3))")
  inputs+=(-loop 1 -t "$secs" -i "$path")
  if [[ $i -gt 0 ]]; then
    prev=$([[ $i -eq 1 ]] && echo "[0:v]" || echo "[v$((i-1))]")
    filter+="${prev}[$i:v]xfade=transition=fade:duration=$FADE:offset=$offset[v$i];"
  fi
  offset=$(python3 -c "print(round($offset + $secs - $FADE, 3))")
  i=$((i+1))
done < scenes.txt
last="[v$((n-1))]"
ffmpeg -y "${inputs[@]}" -filter_complex "${filter}${last}format=yuv420p[out]" -map "[out]" \
  -r 30 -c:v libx264 -preset medium -crf 20 -movflags +faststart -an aiol-loop.mp4
ls -la aiol-loop.mp4
