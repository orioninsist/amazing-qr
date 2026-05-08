#!/bin/bash

# =================================================================
# Amazing-QR Asset Synchronization Script
# Purpose: Automatically populates inputs/order.csv with all 
#          images and GIFs found in the inputs/assets directory.
# =================================================================

# Define paths
ASSETS_DIR="inputs/assets"
ORDER_CSV="inputs/order.csv"
GITHUB_URL="https://github.com/orioninsist"

# Check if assets directory exists
if [ ! -d "$ASSETS_DIR" ]; then
    echo "Error: Directory $ASSETS_DIR not found!"
    exit 1
fi

# Write header to order.csv (This will overwrite existing content)
echo "words,picture" > "$ORDER_CSV"

# Find all image and gif files
# Supported formats: .jpg, .jpeg, .png, .gif (case-insensitive)
count=0
find "$ASSETS_DIR" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" \) | sort | while read -r filepath; do
    filename=$(basename "$filepath")
    echo "$GITHUB_URL,$filename" >> "$ORDER_CSV"
    ((count++))
done

# Since the while loop runs in a subshell when piped, we need to count differently or use a temporary file
# But for simplicity, let's just count after writing
final_count=$(grep -c "^http" "$ORDER_CSV")

echo "---------------------------------------------------"
echo "✅ Asset synchronization complete!"
echo "📍 Target File: $ORDER_CSV"
echo "🖼️  Total Assets Processed: $final_count"
echo "---------------------------------------------------"
echo "You can now run your batch generation process."
