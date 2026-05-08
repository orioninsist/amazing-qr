import gradio as gr
import pandas as pd
import os
import shutil
import time
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
    cols = ['words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name']
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    
    # Simple smart defaults for the UI
    for i, row in df.iterrows():
        if not str(row.get('version')).strip() or str(row.get('version')) == 'nan': df.at[i, 'version'] = 1
        if not str(row.get('level')).strip() or str(row.get('level')) == 'nan': df.at[i, 'level'] = 'H'
        if not str(row.get('contrast')).strip() or str(row.get('contrast')) == 'nan': df.at[i, 'contrast'] = 1.0
        if not str(row.get('brightness')).strip() or str(row.get('brightness')) == 'nan': df.at[i, 'brightness'] = 1.0
        
    return df[cols]

def handle_upload(files):
    if files:
        for file in files:
            dest = os.path.join(ASSETS_DIR, os.path.basename(file.name))
            shutil.copy(file.name, dest)
    return f"✅ {len(files) if files else 0} assets uploaded to inputs/assets/"

def generate_qrs(df_data):
    # Clear previous output
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    data = df_data.to_dict('records')
    images = []
    logs = ""
    
    for status, img_path in process_items(data, ASSETS_DIR, OUTPUT_DIR):
        logs += status + "\n"
        if img_path and os.path.exists(img_path):
            images.append(img_path)
        yield logs, images, None

    # Create ZIP
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(BASE_DIR, f"amazing_qr_results_{now}")
    shutil.make_archive(zip_path, 'zip', OUTPUT_DIR)
    
    yield logs + "\n✅ All done! ZIP archive created.", images, f"{zip_path}.zip"

# GUI Design
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"), title="Amazing QR - Premium Batch") as demo:
    gr.Markdown("""
    # 🚀 Amazing QR: Premium Batch Generator
    Upload your order CSV and assets, review the parameters, and generate high-quality QR codes in seconds.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            csv_input = gr.File(label="1. Upload Order CSV", file_types=[".csv"])
            asset_input = gr.File(label="2. Upload Assets (Logos/GIFs)", file_count="multiple")
            upload_status = gr.Markdown("No assets uploaded yet.")
            asset_input.change(handle_upload, inputs=asset_input, outputs=upload_status)
            
        with gr.Column(scale=2):
            gr.Markdown("### 3. Review & Edit Parameters")
            data_editor = gr.Dataframe(
                headers=['words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name'],
                datatype=["str", "number", "str", "str", "bool", "number", "number", "str"],
                interactive=True,
                label="Order List",
                type="pandas"
            )
            csv_input.change(prepare_data, inputs=csv_input, outputs=data_editor)
    
    process_btn = gr.Button("🔥 Generate QR Codes", variant="primary", size="lg")
    
    with gr.Row():
        log_output = gr.Textbox(label="Process Logs", lines=10, interactive=False)
        with gr.Column():
            gallery_output = gr.Gallery(label="Generated QR Codes", columns=4, height="auto", preview=True)
            zip_output = gr.File(label="Download Results (ZIP)")

    process_btn.click(
        generate_qrs, 
        inputs=data_editor, 
        outputs=[log_output, gallery_output, zip_output]
    )

if __name__ == "__main__":
    # Gradio 4.x uses 'server_name' and 'server_port' similarly
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
