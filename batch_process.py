import csv
import json
import os
import sys
from amzqr import amzqr

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
    
    for row in data:
        words = row.get('words', '')
        if not words:
            continue
        
        # Extract parameters with defaults
        version = int(row.get('version', 1))
        level = row.get('level', 'H')
        picture_name = row.get('picture', None)
        colorized = str(row.get('colorized', 'False')).lower() == 'true'
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
        
        item_report = {
            "input": row,
            "status": "pending",
            "output_file": None,
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
            print(f"Success: Generated {qr_name}")
            item_report["status"] = "success"
            item_report["output_file"] = qr_name
            count += 1
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to generate QR for {words}: {error_msg}")
            item_report["status"] = "failed"
            item_report["error"] = error_msg
        
        results.append(item_report)

    # Save report
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\nBatch processing finished. Total generated: {count}")
    print(f"Report saved to {report_file}")

if __name__ == '__main__':
    run_batch()
