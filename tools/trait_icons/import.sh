#!/bin/sh
# Moves downloaded trait paintings (~/Downloads/nht_<id>.<ext>) into tools/trait_icons/raw/<id>.<ext>,
# then writes each as a 256 x 256 PNG for the game:
#   f_<item> -> Assets/Resources/TraitIcons/Functions/<item>.png
#   b_<item> -> Assets/Resources/TraitIcons/Behaviors/<item>.png
HERE="$(cd "$(dirname "$0")" && pwd)"
RAW="$HERE/raw"
OUT="$HERE/../../Assets/Resources/TraitIcons"
mkdir -p "$RAW" "$OUT/Functions" "$OUT/Behaviors"
for f in "$HOME"/Downloads/nht_*; do
  [ -e "$f" ] || continue
  b=$(basename "$f"); ext=${b##*.}; id=${b%.*}; id=${id#nht_}
  case "$id" in *" ("*) rm -f "$f"; continue ;; esac   # browser duplicates such as "x (1)"
  mv "$f" "$RAW/$id.$ext"
done
for f in "$RAW"/*; do
  [ -e "$f" ] || continue
  b=$(basename "$f"); id=${b%.*}
  case "$id" in f_*) dir=Functions ;; b_*) dir=Behaviors ;; *) continue ;; esac
  dst="$OUT/$dir/${id#?_}.png"
  [ "$dst" -nt "$f" ] && continue
  sips -s format png -Z 256 "$f" --out "$dst" >/dev/null
done
echo "$(ls "$RAW" | wc -l) raw, $(ls "$OUT/Functions" "$OUT/Behaviors" | grep -c '\.png$') in the game"
