import gradio as gr
import pandas as pd
import os
import shutil
import time
import cv2
from datetime import datetime
from batch_process import process_items

# Directories
BASE_DIR = os.getcwd()
INPUTS_DIR = os.path.join(BASE_DIR, "inputs")
ASSETS_DIR = os.path.join(INPUTS_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure directories exist
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def prepare_data(csv_file):
    if csv_file is None:
        return pd.DataFrame(columns=['words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name'])
    
    df = pd.read_csv(csv_file.name)
    
    # Fill defaults
    cols = ['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name']
    for col in cols:
        if col not in df.columns:
            if col == 'selected':
                df[col] = True
            else:
                df[col] = ""
    
    # Simple smart defaults for the UI
    for i, row in df.iterrows():
        if not str(row.get('version')).strip() or str(row.get('version')) == 'nan': df.at[i, 'version'] = 1
        if not str(row.get('level')).strip() or str(row.get('level')) == 'nan': df.at[i, 'level'] = 'H'
        if not str(row.get('contrast')).strip() or str(row.get('contrast')) == 'nan': df.at[i, 'contrast'] = 1.0
        if not str(row.get('brightness')).strip() or str(row.get('brightness')) == 'nan': df.at[i, 'brightness'] = 1.0
        if not str(row.get('colorized')).strip() or str(row.get('colorized')) == 'nan':
            df.at[i, 'colorized'] = True if str(row.get('picture')).strip() else False
        if pd.isna(row.get('selected')):
            df.at[i, 'selected'] = True
        
    return df[cols]

def handle_upload(files):
    if files:
        for file in files:
            dest = os.path.join(ASSETS_DIR, os.path.basename(file.name))
            shutil.copy(file.name, dest)
    return f"✅ {len(files) if files else 0} assets uploaded to inputs/assets/"

def test_qr_scannability(img_path):
    if not img_path or not os.path.exists(img_path):
        return "❌ Missing"
    if img_path.lower().endswith('.gif'):
        return "⏳ GIF (Manual Test)"
    
    try:
        img = cv2.imread(img_path)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        return "✅ Working" if data else "❌ Failed"
    except:
        return "⚠️ Error"

def generate_qrs(df_data):
    # Clear previous output
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Filter only selected rows
    df_selected = df_data[df_data['selected'] == True]
    
    if df_selected.empty:
        yield "⚠️ Error: No items selected for processing. Please check the 'selected' column.", [], None
        return

    data = df_selected.to_dict('records')
    images = []
    logs = "🚀 Batch processing started...\n"
    
    yield logs, [], None

    for status, img_path in process_items(data, ASSETS_DIR, OUTPUT_DIR):
        test_res = ""
        if img_path and os.path.exists(img_path):
            images.append(img_path)
            test_res = f" | Scan: {test_qr_scannability(img_path)}"
        
        logs += f"{status}{test_res}\n"
        yield logs, images, None

    # Create ZIP
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"amazing_qr_results_{now}"
    zip_path = os.path.join(BASE_DIR, zip_name)
    shutil.make_archive(zip_path, 'zip', OUTPUT_DIR)
    
    logs += f"\n✅ All done! {len(images)} QR codes generated.\n📦 ZIP archive created: {zip_name}.zip"
    yield logs, images, f"{zip_path}.zip"

# Premium CSS
custom_css = """
.container { max-width: 1200px; margin: auto; }
.header { text-align: center; margin-bottom: 2rem; }
.footer { text-align: center; margin-top: 2rem; color: #666; }
.gradio-container { background-color: #fdfdfd !important; }
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="slate"), css=custom_css, title="Amazing QR - Premium Batch") as demo:
    with gr.Div(elem_classes="container"):
        gr.Markdown("""
        <div class="header">
            <h1>🚀 Amazing QR: Premium Batch Generator</h1>
            <p>Upload your order CSV and assets, review parameters, and generate high-quality QR codes.</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                csv_input = gr.File(label="1. Upload Order CSV", file_types=[".csv"])
                asset_input = gr.File(label="2. Upload Assets (Logos/GIFs)", file_count="multiple")
                upload_status = gr.Markdown("ℹ️ *No assets uploaded yet.*")
                asset_input.change(handle_upload, inputs=asset_input, outputs=upload_status)
                
            with gr.Column(scale=2):
                gr.Markdown("### ✍️ 3. Review & Edit Parameters")
                data_editor = gr.Dataframe(
                    headers=['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name'],
                    datatype=["bool", "str", "number", "str", "str", "bool", "number", "number", "str"],
                    interactive=True,
                    label="Order List",
                    type="pandas"
                )
                csv_input.change(prepare_data, inputs=csv_input, outputs=data_editor)
        
        process_btn = gr.Button("🔥 Start Batch Generation", variant="primary", size="lg")
        
        with gr.Row():
            with gr.Column(scale=1):
                log_output = gr.Textbox(label="Process Logs & Testing", lines=12, interactive=False)
            with gr.Column(scale=2):
                gallery_output = gr.Gallery(label="✨ Preview Results", columns=4, height="auto", preview=True)
                zip_output = gr.File(label="📥 Download All Results (ZIP)")

        process_btn.click(
            generate_qrs, 
            inputs=data_editor, 
            outputs=[log_output, gallery_output, zip_output]
        )
        
        gr.Markdown("""
        <div class="footer">
            <p>© 2026 Amazing QR - Powered by OrionInsist</p>
        </div>
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
