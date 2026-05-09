#!/usr/bin/env bash
set -euo pipefail

# usage:
# ./gif.sh resim.png
# ./gif.sh /tam/yol/resim.png

INPUT="${1:-}"

FPS=30
QUALITY=100
FRAMES=120
SIZE=1024

[[ -z "$INPUT" ]] && {
    echo "usage: ./gif.sh image.png"
    exit 1
}

[[ -f "$INPUT" ]] || {
    echo "file not found: $INPUT"
    exit 1
}

command -v magick >/dev/null || {
    echo "missing: imagemagick"
    echo "install: sudo pacman -S imagemagick"
    exit 1
}

command -v gifski >/dev/null || {
    echo "missing: gifski"
    echo "install: sudo pacman -S gifski"
    exit 1
}

BASE="$(basename "$INPUT")"
BASE="${BASE%.*}"

OUTDIR="$(pwd)"
FRAMES_DIR="$OUTDIR/${BASE}_frames"
OUTPUT="$OUTDIR/${BASE}.gif"

rm -rf "$FRAMES_DIR"
mkdir -p "$FRAMES_DIR"

echo "[+] input:  $INPUT"
echo "[+] output: $OUTPUT"

for i in $(seq 0 $((FRAMES - 1))); do
    angle=$((i * 3))

    magick "$INPUT" \
        -resize "${SIZE}x${SIZE}" \
        -background none \
        -gravity center \
        -extent "${SIZE}x${SIZE}" \
        -virtual-pixel transparent \
        -distort SRT "$angle" \
        "$FRAMES_DIR/frame_$(printf "%03d" "$i").png"
done

gifski \
    --fps "$FPS" \
    --quality "$QUALITY" \
    -o "$OUTPUT" \
    "$FRAMES_DIR"/*.png

echo "[+] done: $OUTPUT"