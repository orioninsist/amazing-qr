import csv
import json
import os
import sys
import re
from amzqr import amzqr
from tqdm import tqdm

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

def process_items(data, assets_dir, output_dir):
    """
    Core processing loop that can be called by CLI or Gradio.
    Yields progress info.
    """
    if not data:
        yield "Error: Input data is empty.", None
        return

    print(f"Starting batch process for {len(data)} items...")
    
    results = []
    count = 0
    pbar = tqdm(total=len(data), desc="Processing QRs")
    for idx, row in enumerate(data, 1):
        pbar.update(1)
        words = str(row.get('words', '')).strip()
        if not words:
            continue
        
        # --- Smart Defaults ---
        # 1. Version: Auto-detect if missing or invalid
        try:
            version_val = row.get('version', 1)
            version = int(version_val) if version_val and str(version_val).strip() != '' and str(version_val).strip() != 'nan' else 1
        except:
            version = 1
            
        # 2. Level: Always 'H' for premium unless specified
        level = row.get('level', 'H')
        if not level or str(level).strip() == '' or str(level).strip() == 'nan':
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
            contrast = float(contrast_val) if contrast_val and str(contrast_val).strip() != '' and str(contrast_val).strip() != 'nan' else 1.0
            brightness_val = row.get('brightness', 1.0)
            brightness = float(brightness_val) if brightness_val and str(brightness_val).strip() != '' and str(brightness_val).strip() != 'nan' else 1.0
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

        status_msg = f"Processing [{idx}/{len(data)}]: {words} -> {save_name}"
        print(status_msg)
        yield status_msg, None
        
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
            item_report["status"] = "success"
            item_report["output_file"] = qr_name
            count += 1
            yield f"✅ Success: {qr_name}", os.path.join(output_dir, qr_name)
        except Exception as e:
            error_msg = str(e)
            print(f"  - Failed: {error_msg}")
            item_report["status"] = "failed"
            item_report["error"] = error_msg
            yield f"❌ Failed: {error_msg}", None
        
        results.append(item_report)

    # Save report
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    report_file = os.path.join(output_dir, 'report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    pbar.close()
    final_msg = f"\nBatch processing finished. Total generated: {count}"
    print(final_msg)
    yield final_msg, None

def run_batch():
    # Detect if running in Docker /app or local
    base_dir = '/app' if os.path.exists('/app') and os.path.isdir('/app') else os.getcwd()
    
    input_csv = os.path.join(base_dir, 'inputs/order.csv')
    input_json = os.path.join(base_dir, 'inputs/order.json')
    assets_dir = os.path.join(base_dir, 'inputs/assets')
    output_dir = os.path.join(base_dir, 'output')

    data = []
    if os.path.exists(input_json):
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif os.path.exists(input_csv):
        import pandas as pd
        df = pd.read_csv(input_csv)
        data = df.to_dict('records')
    else:
        print(f"Error: No order.csv or order.json found!")
        return

    # Run the generator to completion for CLI
    for msg, file in process_items(data, assets_dir, output_dir):
        pass

if __name__ == '__main__':
    run_batch()
