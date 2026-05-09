#!/usr/bin/env bash
set -euo pipefail

# Configuration
ASSETS_DIR="/mnt/samsung/orion-backup-local/projects/amazing-qr/portfolio/assets"
GIF_SCRIPT="/mnt/samsung/orion-backup-local/projects/amazing-qr/portfolio/gif.sh"
TEMP_DIR="/mnt/samsung/orion-backup-local/projects/amazing-qr/portfolio/temp_gifs"

# Create temp directory
mkdir -p "$TEMP_DIR"

echo "Starting batch GIF generation for files in $ASSETS_DIR"

# Loop through all png files in assets
for img in "$ASSETS_DIR"/*.png; do
    [ -e "$img" ] || continue
    
    filename=$(basename "$img")
    echo "Processing $filename..."
    
    # Run all 4 modes
    for mode in 1 2 3 4; do
        echo "  Applying mode $mode..."
        # Run the script. It will create TEMP_DIR/stem-mode/stem-mode.gif
        "$GIF_SCRIPT" "$img" "$mode" "$TEMP_DIR" > /dev/null 2>&1
        
        # Get the stem and mode name (copied logic from gif.sh to predict paths)
        stem=$(basename "$img" | sed 's/\.[^.]*$//' | sed 's/[^A-Za-z0-9._-]/_/g')
        case "$mode" in
            1) mname="still" ;;
            2) mname="zoom-in" ;;
            3) mname="pan" ;;
            4) mname="pulse-rotate" ;;
        esac
        
        # Move the generated gif to assets
        source_gif="$TEMP_DIR/${stem}-${mname}/${stem}-${mname}.gif"
        target_gif="$ASSETS_DIR/${stem}-${mname}.gif"
        
        if [ -f "$source_gif" ]; then
            mv "$source_gif" "$target_gif"
            echo "    Created: $(basename "$target_gif")"
        else
            echo "    Error: Failed to create $source_gif"
        fi
    done
done

# Cleanup
echo "Cleaning up..."
rm -rf "$TEMP_DIR"

echo "All done! 32 GIFs should be in $ASSETS_DIR"
