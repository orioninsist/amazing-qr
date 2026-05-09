import gradio as gr
import pandas as pd
import os
import shutil
import time
import cv2
from datetime import datetime
from batch_process import process_items, slugify

# Directories
BASE_DIR = os.getcwd()
INPUTS_DIR = os.path.join(BASE_DIR, "inputs")
ASSETS_DIR = os.path.join(INPUTS_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure directories exist
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def handle_csv_upload(file):
    if file is None:
        return None, "❌ Lütfen bir CSV dosyası seçin."
    
    dest = os.path.join(INPUTS_DIR, "order.csv")
    shutil.copy(file.name, dest)
    
    df = pd.read_csv(dest)
    # Fill defaults if missing
    cols = ['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name']
    for col in cols:
        if col not in df.columns:
            if col == 'selected': df[col] = True
            elif col in ['contrast', 'brightness']: df[col] = 1.0
            elif col == 'version': df[col] = 1
            elif col == 'level': df[col] = 'H'
            elif col == 'colorized': df[col] = True
            else: df[col] = ""
    
    df.to_csv(dest, index=False)
    return df[cols], f"✅ {os.path.basename(file.name)} yüklendi ve inputs/order.csv olarak kaydedildi."

def handle_asset_upload(files):
    if files:
        for file in files:
            dest = os.path.join(ASSETS_DIR, os.path.basename(file.name))
            shutil.copy(file.name, dest)
    return f"✅ {len(files) if files else 0} asset yüklendi."

def get_final_preview(df):
    if df is None or df.empty:
        return pd.DataFrame()
    return df[df['selected'] == True]

def run_batch_ui(df_data):
    if df_data is None or df_data.empty:
        yield "❌ Hata: Veri bulunamadı.", [], None, "❌ İşlem Başlatılamadı"
        return

    # Save current state to order.csv
    dest = os.path.join(INPUTS_DIR, "order.csv")
    df_data.to_csv(dest, index=False)

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    selected_rows = df_data[df_data['selected'] == True].to_dict('records')
    if not selected_rows:
        yield "⚠️ Uyarı: Hiçbir satır seçilmedi.", [], None, "⚠️ Seçim Yok"
        return

    logs = "🚀 İşlem başlatıldı...\n"
    images = []
    qc_reports = []
    
    for status, img_path, report in process_items(selected_rows, ASSETS_DIR, OUTPUT_DIR):
        if status:
            logs += f"{status}\n"
        if img_path:
            images.append(img_path)
        if report:
            qc_reports.append(report)
        
        yield logs, images, None, "⏳ İşleniyor..."

    # Create ZIP
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"amazing_qr_results_{now}"
    zip_path = os.path.join(BASE_DIR, zip_name)
    shutil.make_archive(zip_path, 'zip', OUTPUT_DIR)
    
    final_csv = os.path.join(OUTPUT_DIR, "order-updated.csv")
    
    logs += f"\n✅ Tamamlandı! {len(images)} QR üretildi.\n📦 ZIP oluşturuldu: {zip_name}.zip"
    
    # Check for overall status
    failed_count = len([r for r in qc_reports if "❌" in r.get('scannable', '')])
    final_status = "🟢 TAMAMLANDI" if failed_count == 0 else f"🟠 {failed_count} SORUNLU"
    
    yield logs, images, f"{zip_path}.zip", final_status

# Premium CSS
custom_css = """
.container { max-width: 1200px; margin: auto; }
.header { text-align: center; margin-bottom: 2rem; background: #2c3e50; color: white; padding: 20px; border-radius: 10px; }
.step-box { border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-bottom: 15px; background: white; }
.status-green { color: #27ae60; font-weight: bold; font-size: 20px; text-align: center; }
.status-orange { color: #f39c12; font-weight: bold; font-size: 20px; text-align: center; }
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"), css=custom_css, title="Amazing QR - 11 Step Workflow") as demo:
    with gr.Div(elem_classes="container"):
        gr.Markdown("""
        <div class="header">
            <h1>🚀 Amazing QR: Profesyonel İş Akışı</h1>
            <p>11 Adımda Tam Kontrollü QR Kod Üretimi</p>
        </div>
        """)
        
        with gr.Tabs() as tabs:
            with gr.TabItem("📁 ADIM 1-2: Hazırlık"):
                with gr.Row():
                    with gr.Column():
                        csv_input = gr.File(label="1. order.csv Yükle (Zorunlu)", file_types=[".csv"])
                        csv_status = gr.Markdown("ℹ️ *Lütfen CSV yükleyin.*")
                    with gr.Column():
                        asset_input = gr.File(label="2. Assetleri Yükle (Logos/GIFs)", file_count="multiple")
                        asset_status = gr.Markdown("ℹ️ *Henüz asset yüklenmedi.*")
                
            with gr.TabItem("✍️ ADIM 3-4: Düzenleme"):
                gr.Markdown("### 3. Siparişleri Düzenle")
                data_editor = gr.Dataframe(
                    headers=['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name'],
                    datatype=["bool", "str", "number", "str", "str", "bool", "number", "number", "str"],
                    interactive=True,
                    label="Düzenleme Tablosu",
                    type="pandas"
                )
                gr.Markdown("### 4. İşlem Öncesi Son Kontrol (Seçililer)")
                final_preview = gr.Dataframe(interactive=False, label="İşleme Alınacaklar")
                
                def update_previews(df):
                    return get_final_preview(df)
                
                data_editor.change(update_previews, inputs=data_editor, outputs=final_preview)

            with gr.TabItem("⚙️ ADIM 5-10: İşlem & QC"):
                process_btn = gr.Button("🔥 Üretimi Başlat (Process)", variant="primary", size="lg")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        log_output = gr.Textbox(label="5-8. İşlem Günlüğü & QC Raporu", lines=15, interactive=False)
                        final_status_display = gr.Markdown("### Durum: Bekleniyor", elem_id="status_display")
                    with gr.Column(scale=2):
                        gallery_output = gr.Gallery(label="6. Sonuç Önizleme", columns=4, height="auto")
                
            with gr.TabItem("📥 ADIM 11: İndir"):
                gr.Markdown("### 11. Final Paketini İndir")
                zip_output = gr.File(label="ZIP Dosyasını İndir (QRlar + order-updated.csv)")

        # Event Bindings
        csv_input.change(handle_csv_upload, inputs=csv_input, outputs=[data_editor, csv_status])
        asset_input.change(handle_asset_upload, inputs=asset_input, outputs=asset_status)
        
        process_btn.click(
            run_batch_ui, 
            inputs=data_editor, 
            outputs=[log_output, gallery_output, zip_output, final_status_display]
        )

        gr.Markdown("""
        <div style="text-align: center; margin-top: 20px; color: #666;">
            <p>© 2026 Amazing QR - Powered by OrionInsist | 11-Step Workflow Engine</p>
        </div>
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
