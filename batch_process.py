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
    if not img_path:
        return None, "❌ Error: No path provided"
        
    if not os.path.exists(img_path):
        return None, f"❌ Missing: {os.path.basename(img_path)}"
    
    # GIF handling (OpenCV detector doesn't support GIFs directly)
    if img_path.lower().endswith('.gif'):
        try:
            cap = cv2.VideoCapture(img_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                detector = cv2.QRCodeDetector()
                data, _, _ = detector.detectAndDecode(frame)
                if data:
                    return data, "✅ Success (GIF)"
                else:
                    return None, "⚠️ Manual Test Needed (GIF - Frame 1 Not Readable)"
            else:
                return None, "⚠️ Manual Test Needed (GIF - Frame Extract Error)"
        except Exception as e:
            return None, f"⚠️ Manual Test Needed (GIF Error: {str(e)})"
    
    try:
        img = cv2.imread(img_path)
        if img is None:
            return None, "❌ File Load Error (Corrupt?)"
            
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        
        # If standard detector fails, try some preprocessing
        if not data:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Try CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl1 = clahe.apply(gray)
            data, _, _ = detector.detectAndDecode(cl1)
            
        if data:
            return data, "✅ Success"
        else:
            return None, "❌ Failed (Unreadable)"
    except Exception as e:
        return None, f"⚠️ QC Error: {str(e)}"

def get_advice(row, scannable_msg):
    """Provides specific advice if scannability fails."""
    if "Success" in scannable_msg or "Manual" in scannable_msg:
        return ""
    
    advice = []
    contrast = float(row.get('contrast', 1.0))
    brightness = float(row.get('brightness', 1.0))
    version = int(row.get('version', 1))
    
    if "Missing" in scannable_msg:
        return " | Hata: Dosya oluşturulamadı. Kayıt dizinini ve yazma izinlerini kontrol edin."

    if contrast < 1.3:
        advice.append("Kontrastı artırın (Örn: 1.5 - 2.0)")
    elif contrast > 2.5:
        advice.append("Kontrast çok yüksek, düşürün (Örn: 1.5)")
        
    if brightness > 1.3:
        advice.append("Parlaklığı azaltın (Örn: 1.0)")
    elif brightness < 0.7:
        advice.append("Parlaklığı artırın (Örn: 1.0)")
        
    if version > 15:
        advice.append("Versiyonu düşürerek yoğunluğu azaltın (Örn: 10)")
    
    if not advice:
        advice.append("Görsel çok karmaşık olabilir, daha sade bir görsel seçin veya kontrastı 1.5 yapın.")
    
    return " | Tavsiye: " + ", ".join(advice)

def process_items(data, assets_dir, output_dir, auto_repair=False):
    """
    Core processing loop that can be called by CLI or Gradio.
    Yields progress info.
    """
    if not data:
        yield "Error: Input data is empty.", None, None
        return

    print(f"Starting batch process for {len(data)} items...")
    
    results = []
    pbar = tqdm(total=len(data), desc="Processing QRs")
    
    for idx, row in enumerate(data, 1):
        pbar.update(1)
        words = str(row.get('words', '')).strip()
        if not words:
            continue
        
        # --- Base Parameters ---
        initial_version = int(row.get('version', 1))
        initial_level = str(row.get('level', 'H'))
        picture_name = str(row.get('picture', '')).strip()
        picture_path = None
        if picture_name and picture_name != 'nan':
            picture_path = os.path.join(assets_dir, picture_name)
            if not os.path.exists(picture_path):
                picture_path = None

        colorized = str(row.get('colorized', 'True')).lower() == 'true'
        initial_contrast = float(row.get('contrast', 1.0))
        initial_brightness = float(row.get('brightness', 1.0))

        save_name = str(row.get('save_name', '')).strip()
        if not save_name or save_name == 'nan':
            ext = '.gif' if picture_name.lower().endswith('.gif') else '.png'
            slug = slugify(words) or f"qr_{idx}"
            save_name = f"{slug}{ext}"

        # --- Smart Repair Loop ---
        # We try up to 3 attempts if auto_repair is ON
        max_attempts = 3 if auto_repair else 1
        last_item_report = None
        
        for attempt in range(1, max_attempts + 1):
            current_contrast = initial_contrast
            current_brightness = initial_brightness
            current_level = initial_level
            current_version = initial_version

            if attempt == 2:
                # Attempt 2: Balanced improvement
                current_contrast = 1.5
                current_brightness = 1.0
                current_level = 'Q'
                yield f"🔄 [Attempt 2] Retrying with Balanced parameters for {save_name}...", None, None
            elif attempt == 3:
                # Attempt 3: High Contrast / Safe mode
                current_contrast = 2.0
                current_brightness = 1.0
                current_level = 'H'
                yield f"🔄 [Attempt 3] Retrying with Safe parameters for {save_name}...", None, None

            status_msg = f"Processing [{idx}/{len(data)}] (Attempt {attempt}): {words}"
            yield status_msg, None, None
            
            item_report = row.copy()
            item_report["process_status"] = "pending"
            item_report["output_file"] = save_name
            item_report["attempt"] = attempt
            
            try:
                # Generation
                ver, ecl, qr_full_path = amzqr.run(
                    words=words,
                    version=current_version,
                    level=current_level,
                    picture=picture_path,
                    colorized=colorized,
                    contrast=current_contrast,
                    brightness=current_brightness,
                    save_name=save_name,
                    save_dir=output_dir
                )
                
                # Verify file exists
                if not os.path.exists(qr_full_path):
                    qr_full_path = os.path.join(output_dir, save_name)
                
                # QC Test
                scanned_data, scannable_msg = test_qr_scannability(qr_full_path)
                
                advice = get_advice(item_report, scannable_msg)
                
                item_report["process_status"] = "success"
                item_report["scannable"] = scannable_msg
                item_report["advice"] = advice
                item_report["scanned_data"] = scanned_data
                item_report["contrast"] = current_contrast
                item_report["brightness"] = current_brightness
                item_report["level"] = current_level
                
                last_item_report = item_report

                # If success, break the repair loop
                if "✅" in scannable_msg or "Manual" in scannable_msg:
                    yield f"✅ {save_name} | {scannable_msg}", qr_full_path, item_report
                    break
                else:
                    if attempt == max_attempts:
                        yield f"❌ {save_name} | {scannable_msg}", qr_full_path, item_report
            
            except Exception as e:
                error_msg = str(e)
                item_report["process_status"] = "failed"
                item_report["error"] = error_msg
                item_report["scannable"] = f"❌ Error: {error_msg}"
                last_item_report = item_report
                yield f"❌ Failed: {error_msg}", None, item_report
                if attempt == max_attempts:
                    break
        
        results.append(last_item_report)

    # Save final updated CSV for internal tracking
    updated_df = pd.DataFrame(results)
    updated_csv_path = os.path.join(output_dir, 'order-updated.csv')
    updated_df.to_csv(updated_csv_path, index=False)
    
    pbar.close()
    final_msg = f"\nBatch processing finished. Total processed: {len(data)}"
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

    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    data = df.to_dict('records')
    selected_data = [item for item in data if str(item.get('selected', True)).lower() == 'true']

    if not selected_data:
        print("No items selected for processing.")
        return

    for msg, file, report in process_items(selected_data, assets_dir, output_dir, auto_repair=True):
        if msg: print(msg)

if __name__ == '__main__':
    run_batch()
