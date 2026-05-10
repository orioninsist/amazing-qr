#!/usr/bin/env bash
set -euo pipefail

DURATION=3
FPS=15
SIZE=800x800
QUALITY=80

usage() {
  printf 'Usage: %s INPUT_IMAGE\n' "$(basename "$0")" >&2
}

need_command() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'Required command not found: %s\n' "$1" >&2
    exit 127
  }
}

frame_count() {
  awk -v d="$DURATION" -v f="$FPS" 'BEGIN { n=int(d*f+0.5); if (n < 1) n=1; print n }'
}

safe_stem() {
  basename "$1" | sed 's/\.[^.]*$//' | sed 's/[^A-Za-z0-9._-]/_/g'
}

write_still_frames() {
  input=$1
  frames_dir=$2
  frames=$(frame_count)
  tmp="$frames_dir/.base-still.png"

  magick "$input" -auto-orient -colorspace sRGB \
    -filter LanczosSharp -resize "${SIZE}^" -gravity center -extent "$SIZE" \
    -strip -define png:compression-level=9 "$tmp"

  i=0
  while [ "$i" -lt "$frames" ]; do
    cp "$tmp" "$frames_dir/frame_$(printf '%04d' "$i").png"
    i=$((i + 1))
  done
  rm -f "$tmp"
}

write_zoom_frames() {
  input=$1
  frames_dir=$2
  zoom_percent=${3:-10}
  frames=$(frame_count)
  base="$frames_dir/.base-zoom.png"

  magick "$input" -auto-orient -colorspace sRGB \
    -filter LanczosSharp -resize "${SIZE}^" -gravity center -extent "$SIZE" \
    -strip "$base"

  export -f frame_count safe_stem
  # We can use a simpler approach for zoom without complex export if we just use a loop but with lower overhead
  # Or use a single magick command with -morph or similar.
  # But let's just stick to the loop for now but with faster settings.
  
  i=0
  while [ "$i" -lt "$frames" ]; do
    scale=$(awk -v i="$i" -v n="$frames" -v z="$zoom_percent" \
      'BEGIN { t=(n<=1?0:i/(n-1)); printf "%.6f", 100 + z*t }')
    magick "$base" -filter Lanczos -resize "${scale}%" \
      -gravity center -crop "$SIZE+0+0" +repage \
      -define png:compression-level=1 "$frames_dir/frame_$(printf '%04d' "$i").png" &
    
    # Simple parallelism: wait every 8 frames
    if (( (i+1) % 8 == 0 )); then wait; fi
    i=$((i + 1))
  done
  wait
  rm -f "$base"
}

write_pan_frames() {
  input=$1
  frames_dir=$2
  direction=${3:-left-to-right}
  frames=$(frame_count)
  base="$frames_dir/.base-pan.png"

  magick "$input" -auto-orient -colorspace sRGB \
    -filter LanczosSharp -resize "${SIZE}^" -resize 112% \
    -gravity center -strip "$base"

  read -r base_w base_h target_w target_h <<EOF
$(magick identify -format '%w %h ' "$base"; magick -size "$SIZE" xc:none -format '%w %h' info:)
EOF

  i=0
  while [ "$i" -lt "$frames" ]; do
    offset=$(awk -v i="$i" -v n="$frames" -v d="$direction" \
      -v bw="$base_w" -v bh="$base_h" -v tw="$target_w" -v th="$target_h" 'BEGIN {
      t=(n<=1?0:i/(n-1));
      max_x=bw-tw; max_y=bh-th;
      x=int(max_x/2); y=int(max_y/2);
      if (d=="left-to-right") x=int(max_x*t);
      else if (d=="right-to-left") x=int(max_x*(1-t));
      else if (d=="top-to-bottom") y=int(max_y*t);
      else y=int(max_y*(1-t));
      printf "%dx%d+%d+%d", tw, th, x, y;
    }')
    magick "$base" -filter Lanczos -crop "$offset" +repage \
      -define png:compression-level=1 "$frames_dir/frame_$(printf '%04d' "$i").png" &
    
    if (( (i+1) % 8 == 0 )); then wait; fi
    i=$((i + 1))
  done
  wait
  rm -f "$base"
}

write_pulse_rotate_frames() {
  input=$1
  frames_dir=$2
  max_degrees=${3:-2}
  frames=$(frame_count)
  base="$frames_dir/.base-pulse.png"

  magick "$input" -auto-orient -colorspace sRGB \
    -filter LanczosSharp -resize "${SIZE}^" -resize 108% \
    -gravity center -strip "$base"

  i=0
  while [ "$i" -lt "$frames" ]; do
    vals=$(awk -v i="$i" -v n="$frames" -v md="$max_degrees" 'BEGIN {
      pi=atan2(0,-1);
      t=(n<=1?0:i/(n-1));
      wave=sin(2*pi*t);
      zoom=1.04 + 0.02*wave;
      angle=md*wave;
      printf "%.6f %.6f", zoom, angle;
    }')
    set -- $vals
    zoom=$1
    angle=$2
    magick "$base" -background none -virtual-pixel edge \
      -filter Lanczos -distort SRT "$zoom $angle" \
      -gravity center -crop "$SIZE+0+0" +repage \
      -define png:compression-level=1 "$frames_dir/frame_$(printf '%04d' "$i").png" &
    
    if (( (i+1) % 8 == 0 )); then wait; fi
    i=$((i + 1))
  done
  wait
  rm -f "$base"
}

make_gif() {
  frames_dir=$1
  out_gif=$2

  first_frame=$(find "$frames_dir" -maxdepth 1 -type f -name '*.png' | sort | sed -n '1p')
  [ -n "$first_frame" ] || {
    printf 'No PNG frames were created in %s\n' "$frames_dir" >&2
    exit 1
  }

  frames_total=$(find "$frames_dir" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
  gif_fps=$(awk -v n="$frames_total" -v d="$DURATION" 'BEGIN { printf "%.6f", n/d }')
  width=$(magick identify -format '%w' "$first_frame")

  gifski \
    --output "$out_gif" \
    --fps "$gif_fps" \
    --quality "$QUALITY" \
    --motion-quality "$QUALITY" \
    --lossy-quality "$QUALITY" \
    --extra \
    --repeat 0 \
    --width "$width" \
    "$frames_dir"/frame_*.png
}

if [ "$#" -lt 1 ]; then
  usage
  exit 2
fi

input=$1
[ -f "$input" ] || {
  printf 'Input image not found: %s\n' "$input" >&2
  exit 1
}

need_command magick
need_command gifski
need_command awk
need_command find
need_command sort

printf '\nGIF efekti secin:\n\n'
printf '1) Sabit kare\n'
printf '   Resmi 4 saniye boyunca sabit tutar; temiz ve titresimsiz cikti verir.\n\n'
printf '2) Yakinlasma\n'
printf '   Resme yumusak bicimde 10%% zoom-in uygular.\n\n'
printf '3) Kaydirma\n'
printf '   Resmi soldan saga yavasca kaydirir; genis kompozisyonlar icin uygundur.\n\n'
printf '4) Nabiz ve donus\n'
printf '   Hafif zoom ve cok kucuk acili donusla daha canli bir hareket verir.\n\n'
choice="${2:-}"
if [ -z "$choice" ]; then
  printf 'Seciminiz [1-4]: '
  read -r choice
fi

case "$choice" in
  1) mode=still; title='Sabit kare' ;;
  2) mode=zoom-in; title='Yakinlasma' ;;
  3) mode=pan; title='Kaydirma' ;;
  4) mode=pulse-rotate; title='Nabiz ve donus' ;;
  *) printf 'Gecersiz secim: %s\n' "$choice" >&2; exit 2 ;;
esac

stem=$(safe_stem "$input")
base_out_dir="${3:-output}"
out_dir="${base_out_dir}/${stem}-${mode}"
frames_dir="$out_dir/frames"
out_gif="$out_dir/${stem}-${mode}.gif"

rm -rf "$frames_dir"
mkdir -p "$frames_dir"

printf '\n%s baslatildi: %s\n' "$title" "$input"
printf 'Frame klasoru: %s\n' "$frames_dir"

case "$mode" in
  still) write_still_frames "$input" "$frames_dir" ;;
  zoom-in) write_zoom_frames "$input" "$frames_dir" 10 ;;
  pan) write_pan_frames "$input" "$frames_dir" left-to-right ;;
  pulse-rotate) write_pulse_rotate_frames "$input" "$frames_dir" 2 ;;
esac

printf 'GIF olusturuluyor: %s\n' "$out_gif"
make_gif "$frames_dir" "$out_gif"

printf '\nTamamlandi.\n'
printf 'GIF: %s\n' "$out_gif"
printf 'Frame dosyalari: %s/frame_0000.png ...\n' "$frames_dir"
