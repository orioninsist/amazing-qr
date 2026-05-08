import csv
import json
import os
import sys
import re
from amzqr import amzqr

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to underscores.
    """
    # Remove protocol
    value = re.sub(r'^https?://', '', str(value))
    # Replace non-alphanumeric with underscore
    value = re.sub(r'[^\w\s-]', '_', value).strip().lower()
    # Replace whitespace and hyphens with underscore
    value = re.sub(r'[-\s]+', '_', value)
    # Limit length
    return value[:50]

def run_batch():
    # Detect if running in Docker /app or local
    base_dir = '/app' if os.path.exists('/app') and os.path.isdir('/app') else os.getcwd()
    
    input_csv = os.path.join(base_dir, 'inputs/order.csv')
    input_json = os.path.join(base_dir, 'inputs/order.json')
    assets_dir = os.path.join(base_dir, 'inputs/assets')
    output_dir = os.path.join(base_dir, 'output')
    report_file = os.path.join(output_dir, 'report.json')

    data = []
    if os.path.exists(input_json):
        print(f"Reading batch data from {input_json}...")
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif os.path.exists(input_csv):
        print(f"Reading batch data from {input_csv}...")
        with open(input_csv, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    else:
        print(f"Error: No order.csv or order.json found in {os.path.join(base_dir, 'inputs')}!")
        return

    if not data:
        print("Error: Input file is empty.")
        return

    print(f"Starting batch process for {len(data)} items...")
    
    results = []
    count = 0
    
    for idx, row in enumerate(data, 1):
        words = row.get('words', '').strip()
        if not words:
            continue
        
        # --- Smart Defaults ---
        # 1. Version: Auto-detect if missing or invalid
        try:
            version_val = row.get('version', 1)
            version = int(version_val) if version_val and str(version_val).strip() != '' else 1
        except:
            version = 1
            
        # 2. Level: Always 'H' for premium unless specified
        level = row.get('level', 'H')
        if not level or str(level).strip() == '':
            level = 'H'
        
        # 3. Picture Handling
        picture_name = row.get('picture', None)
        picture_path = None
        if picture_name and str(picture_name).strip() != 'nan' and str(picture_name).strip() != '':
            picture_path = os.path.join(assets_dir, str(picture_name).strip())
            if not os.path.exists(picture_path):
                print(f"Warning: Asset {picture_name} not found in {assets_dir}. Skipping picture.")
                picture_path = None

        # 4. Colorized: Default to True if picture exists, False otherwise
        colorized_raw = row.get('colorized', None)
        if colorized_raw is None or str(colorized_raw).strip() == '' or str(colorized_raw).strip() == 'nan':
            colorized = True if picture_path else False
        else:
            colorized = str(colorized_raw).lower() == 'true'

        # 5. Contrast & Brightness
        try:
            contrast_val = row.get('contrast', 1.0)
            contrast = float(contrast_val) if contrast_val and str(contrast_val).strip() != '' else 1.0
            brightness_val = row.get('brightness', 1.0)
            brightness = float(brightness_val) if brightness_val and str(brightness_val).strip() != '' else 1.0
        except:
            contrast, brightness = 1.0, 1.0

        # 6. Save Name: Auto-generate if missing
        save_name = row.get('save_name', None)
        if not save_name or str(save_name).strip() == '' or str(save_name).strip() == 'nan':
            ext = '.gif' if picture_name and str(picture_name).lower().endswith('.gif') else '.png'
            slug = slugify(words) or f"qr_{idx}"
            save_name = f"{slug}{ext}"
        else:
            save_name = str(save_name).strip()

        print(f"Processing [{idx}/{len(data)}]: {words} -> {save_name}")
        if picture_path:
            print(f"  - Using background: {picture_name} (Colorized: {colorized})")
        
        item_report = {
            "input": row,
            "status": "pending",
            "output_file": save_name,
            "error": None
        }
        
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
            print(f"  - Success: Generated {qr_name}")
            item_report["status"] = "success"
            item_report["output_file"] = qr_name
            count += 1
        except Exception as e:
            error_msg = str(e)
            print(f"  - Failed: {error_msg}")
            item_report["status"] = "failed"
            item_report["error"] = error_msg
        
        results.append(item_report)

    # Save report
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\nBatch processing finished. Total generated: {count}")
    print(f"Report saved to {report_file}")

if __name__ == '__main__':
    run_batch()
