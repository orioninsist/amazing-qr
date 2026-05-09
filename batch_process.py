import csv
import json
import os
import sys
import re
import cv2
import pandas as pd
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

def test_qr_scannability(img_path):
    """Checks if a QR code is scannable and returns the result."""
    if not img_path or not os.path.exists(img_path):
        return None, "Missing"
    
    # GIF handling (OpenCV detector doesn't support GIFs directly)
    if img_path.lower().endswith('.gif'):
        return None, "Manual Test Needed (GIF)"
    
    try:
        img = cv2.imread(img_path)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        if data:
            return data, "✅ Success"
        else:
            return None, "❌ Failed"
    except Exception as e:
        return None, f"⚠️ Error: {str(e)}"

def get_advice(row, scannable_msg):
    """Provides advice if scannability fails."""
    if "Success" in scannable_msg or "Manual" in scannable_msg:
        return ""
    
    advice = []
    contrast = float(row.get('contrast', 1.0))
    brightness = float(row.get('brightness', 1.0))
    version = int(row.get('version', 1))
    
    if contrast < 1.5:
        advice.append("Kontrastı artırın (Örn: 2.0)")
    if brightness > 1.2:
        advice.append("Parlaklığı azaltın (Örn: 1.0)")
    if version > 10:
        advice.append("Versiyonu düşürmeyi deneyin")
    
    if not advice:
        advice.append("Kontrast ve Parlaklık dengesini kontrol edin")
    
    return " | Tavsiye: " + ", ".join(advice)

def process_items(data, assets_dir, output_dir):
    """
    Core processing loop that can be called by CLI or Gradio.
    Yields progress info.
    """
    if not data:
        yield "Error: Input data is empty.", None, None
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
        version = int(row.get('version', 1))
        level = str(row.get('level', 'H'))
        picture_name = str(row.get('picture', '')).strip()
        picture_path = None
        if picture_name and picture_name != 'nan':
            picture_path = os.path.join(assets_dir, picture_name)
            if not os.path.exists(picture_path):
                picture_path = None

        colorized = str(row.get('colorized', 'True')).lower() == 'true'
        contrast = float(row.get('contrast', 1.0))
        brightness = float(row.get('brightness', 1.0))

        save_name = str(row.get('save_name', '')).strip()
        if not save_name or save_name == 'nan':
            ext = '.gif' if picture_name.lower().endswith('.gif') else '.png'
            slug = slugify(words) or f"qr_{idx}"
            save_name = f"{slug}{ext}"

        status_msg = f"Processing [{idx}/{len(data)}]: {words}"
        yield status_msg, None, None
        
        item_report = row.copy()
        item_report["process_status"] = "pending"
        item_report["output_file"] = save_name
        
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
            
            # QC Test
            full_path = os.path.join(output_dir, qr_name)
            scanned_data, scannable_msg = test_qr_scannability(full_path)
            advice = get_advice(row, scannable_msg)
            
            item_report["process_status"] = "success"
            item_report["scannable"] = scannable_msg
            item_report["advice"] = advice
            item_report["scanned_data"] = scanned_data
            
            count += 1
            yield f"✅ {qr_name} | {scannable_msg}{advice}", full_path, item_report
        except Exception as e:
            error_msg = str(e)
            item_report["process_status"] = "failed"
            item_report["error"] = error_msg
            yield f"❌ Failed: {error_msg}", None, item_report
        
        results.append(item_report)

    # Save final updated CSV for internal tracking
    updated_df = pd.DataFrame(results)
    updated_csv_path = os.path.join(output_dir, 'order-updated.csv')
    updated_df.to_csv(updated_csv_path, index=False)
    
    pbar.close()
    final_msg = f"\nBatch processing finished. Total generated: {count}"
    yield final_msg, None, None

def run_batch():
    # Detect if running in Docker /app or local
    base_dir = '/app' if os.path.exists('/app') and os.path.isdir('/app') else os.getcwd()
    
    input_csv = os.path.join(base_dir, 'inputs/order.csv')
    assets_dir = os.path.join(base_dir, 'inputs/assets')
    output_dir = os.path.join(base_dir, 'output')

    if not os.path.exists(input_csv):
        print(f"Error: No order.csv found!")
        return

    df = pd.read_csv(input_csv)
    data = df.to_dict('records')

    # Filter selected items
    data = [item for item in data if str(item.get('selected', True)).lower() == 'true']

    if not data:
        print("No items selected for processing.")
        return

    # Run the generator to completion for CLI
    for msg, file, report in process_items(data, assets_dir, output_dir):
        if msg: print(msg)

if __name__ == '__main__':
    run_batch()
