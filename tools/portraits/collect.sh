#!/bin/sh
# Moves downloaded portraits (~/Downloads/nhp_<id>.<ext>) into tools/portraits/raw/<id>.<ext>.
RAW="$(dirname "$0")/raw"
mkdir -p "$RAW"
for f in "$HOME"/Downloads/nhp_*; do
  [ -e "$f" ] || continue
  b=$(basename "$f"); ext=${b##*.}; id=${b%.*}; id=${id#nhp_}
  case "$id" in *" ("*) rm -f "$f"; continue ;; esac   # browser duplicates such as "x (1)"
  mv "$f" "$RAW/$id.$ext"
done
ls "$RAW" | wc -l
