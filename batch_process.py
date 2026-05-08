# -*- coding: utf-8 -*-
import csv
import os
import sys
from amzqr import amzqr

def run_batch():
    # Detect if running in Docker /app or local
    base_dir = '/app' if os.path.exists('/app') and os.path.isdir('/app') else os.getcwd()
    
    input_file = os.path.join(base_dir, 'inputs/order.csv')
    assets_dir = os.path.join(base_dir, 'inputs/assets')
    output_dir = os.path.join(base_dir, 'output')

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    print(f"Starting batch process from {input_file}...")

    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check if CSV is empty or headers are missing
        if not reader.fieldnames:
            print("Error: CSV file is empty or missing headers.")
            return

        count = 0
        for row in reader:
            words = row.get('words', '')
            if not words:
                continue
            
            # Extract parameters with defaults
            version = int(row.get('version', 1))
            level = row.get('level', 'H')
            picture_name = row.get('picture', None)
            colorized = row.get('colorized', 'False').lower() == 'true'
            contrast = float(row.get('contrast', 1.0))
            brightness = float(row.get('brightness', 1.0))
            save_name = row.get('save_name', None)

            # Handle picture path
            picture_path = None
            if picture_name:
                picture_path = os.path.join(assets_dir, picture_name)
                if not os.path.exists(picture_path):
                    print(f"Warning: Asset {picture_name} not found in {assets_dir}. Skipping picture.")
                    picture_path = None

            print(f"Processing: {words} -> {save_name or 'auto_name'}")
            
            try:
                ver, ecl, qr_name = amzqr.run(
                    words=words,
                    version=version,
                    level=level,
                    picture=picture_path,
                    colorized=colorized,
                    contrast=contrast,
                    brightness=brightness,
                    save_name=save_name,
                    save_dir=output_dir
                )
                print(f"Success: Generated {qr_name}")
                count += 1
            except Exception as e:
                print(f"Failed to generate QR for {words}: {str(e)}")

    print(f"\nBatch processing finished. Total generated: {count}")

if __name__ == '__main__':
    run_batch()
