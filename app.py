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

# Global state
current_reports = []

def handle_csv_upload(file):
    if file is None:
        return None, "❌ Lütfen bir CSV dosyası seçin."
    dest = os.path.join(INPUTS_DIR, "order.csv")
    shutil.copy(file.name, dest)
    df = pd.read_csv(dest)
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
    return df[cols], f"✅ {os.path.basename(file.name)} yüklendi."

def handle_asset_upload(files):
    if files:
        for file in files:
            dest = os.path.join(ASSETS_DIR, os.path.basename(file.name))
            shutil.copy(file.name, dest)
    return f"✅ {len(files) if files else 0} asset yüklendi."

def run_process(df_data, auto_repair=True):
    global current_reports
    if df_data is None or df_data.empty:
        yield "❌ Hata: Veri bulunamadı.", [], None, "❌ Hata", pd.DataFrame()
        return

    # Save current state
    df_data.to_csv(os.path.join(INPUTS_DIR, "order.csv"), index=False)

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    selected_rows = df_data[df_data['selected'] == True].to_dict('records')
    current_reports = []

    if not selected_rows:
        yield "⚠️ Hiçbir satır seçilmedi.", [], None, "⚠️ Seçim Yok", pd.DataFrame()
        return

    logs = "🚀 Üretim başlatıldı...\n"
    images = []
    
    for status, img_path, report in process_items(selected_rows, ASSETS_DIR, OUTPUT_DIR, auto_repair=auto_repair):
        if status: logs += f"{status}\n"
        if img_path:
            images = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(('.png', '.gif', '.jpg'))]
            images.sort()
        if report: current_reports.append(report)
        
        qc_df = pd.DataFrame(current_reports)
        yield logs, images, None, "⏳ İşleniyor...", qc_df

    # ZIP logic
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"amazing_qr_results_{now}.zip"
    zip_path = os.path.join(BASE_DIR, "output_zips")
    os.makedirs(zip_path, exist_ok=True)
    full_zip_path = os.path.join(zip_path, zip_name)
    shutil.make_archive(full_zip_path.replace('.zip', ''), 'zip', OUTPUT_DIR)
    
    failed_count = len([r for r in current_reports if "❌" in r.get('scannable', '')])
    final_status = "🟢 TAMAMLANDI" if failed_count == 0 else f"🟠 {failed_count} HATALI"
    
    yield logs + "\n✅ İşlem bitti.", images, full_zip_path, final_status, pd.DataFrame(current_reports)

def apply_bulk_edit(df, v_check, v_val, l_check, l_val, p_check, p_val, c_check, c_val, con_check, con_val, bri_check, bri_val):
    if df is None or df.empty: return df
    new_df = df.copy()
    for i in range(len(new_df)):
        if v_check: new_df.at[i, 'version'] = v_val
        if l_check: new_df.at[i, 'level'] = l_val
        if p_check: new_df.at[i, 'picture'] = p_val
        if c_check: new_df.at[i, 'colorized'] = c_val
        if con_check: new_df.at[i, 'contrast'] = con_val
        if bri_check: new_df.at[i, 'brightness'] = bri_val
    return new_df

# Premium CSS
custom_css = """
.container { max-width: 1200px; margin: auto; font-family: 'Inter', sans-serif; }
.header { text-align: center; background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: white; padding: 50px; border-radius: 25px; margin-bottom: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.3); }
.step-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; border-left: 5px solid #3498db; }
.main-btn { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important; color: white !important; border-radius: 10px !important; font-weight: bold !important; transition: transform 0.2s; }
.main-btn:hover { transform: scale(1.02); }
.repair-btn { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%) !important; color: white !important; }
.status-badge { padding: 10px 20px; border-radius: 30px; font-weight: bold; text-align: center; }
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue"), css=custom_css, title="Amazing QR Pro") as demo:
    with gr.Div(elem_classes="container"):
        gr.Markdown("""
        <div class="header">
            <h1>🚀 Amazing QR: Profesyonel İş Akışı v1.2</h1>
            <p>Yapay Zeka Destekli, 9 Adımlı Kusursuz QR Üretim Merkezi</p>
        </div>
        """)
        
        with gr.Tabs():
            with gr.TabItem("📁 ADIM 1-3: Giriş"):
                with gr.Row():
                    with gr.Column(elem_classes="step-card"):
                        gr.Markdown("### 1-2. Sipariş Listesi")
                        csv_input = gr.File(label="order.csv Yükle", file_types=[".csv"])
                        csv_status = gr.Markdown("ℹ️ *Bekleniyor...*")
                    with gr.Column(elem_classes="step-card"):
                        gr.Markdown("### 3. Asset Yükleme")
                        asset_input = gr.File(label="Logolar / Arka Planlar", file_count="multiple")
                        asset_status = gr.Markdown("ℹ️ *Bekleniyor...*")

            with gr.TabItem("✍️ ADIM 4-5: Düzenle"):
                with gr.Accordion("🛠️ Toplu Düzenleme Paneli", open=False):
                    with gr.Row():
                        with gr.Column():
                            v_check = gr.Checkbox(label="V"); v_val = gr.Slider(1, 40, 1, label="Versiyon")
                            l_check = gr.Checkbox(label="L"); l_val = gr.Dropdown(['L','M','Q','H'], value='H', label="Hata")
                        with gr.Column():
                            p_check = gr.Checkbox(label="Pic"); p_val = gr.Textbox(placeholder="logo.png", label="Görsel")
                            c_check = gr.Checkbox(label="Col"); c_val = gr.Checkbox(value=True, label="Renkli")
                        with gr.Column():
                            con_check = gr.Checkbox(label="Con"); con_val = gr.Slider(0.1, 3.0, 1.5, step=0.1, label="Kontrast")
                            bri_check = gr.Checkbox(label="Bri"); bri_val = gr.Slider(0.1, 3.0, 1.0, step=0.1, label="Parlaklık")
                    bulk_btn = gr.Button("⚡ Seçilenleri Güncelle", variant="secondary")
                
                gr.Markdown("### 4. order.csv Editörü")
                data_editor = gr.Dataframe(
                    headers=['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name'],
                    datatype=["bool", "str", "number", "str", "str", "bool", "number", "number", "str"],
                    interactive=True, type="pandas"
                )
                gr.Markdown("### 5. İşlem Öncesi Kontrol")
                preview_df = gr.Dataframe(interactive=False)
                data_editor.change(lambda df: df[df['selected']==True] if df is not None else None, inputs=data_editor, outputs=preview_df)
                bulk_btn.click(apply_bulk_edit, inputs=[data_editor, v_check, v_val, l_check, l_val, p_check, p_val, c_check, c_val, con_check, con_val, bri_check, bri_val], outputs=data_editor)

            with gr.TabItem("🔥 ADIM 6-8: Üretim & QC"):
                process_btn = gr.Button("🚀 Üretimi Başlat", variant="primary", elem_classes="main-btn")
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### 6-7. Çıktılar")
                        gallery = gr.Gallery(label="Önizleme", columns=4, height="auto")
                        logs = gr.Textbox(label="Süreç Logları", lines=8, interactive=False)
                    with gr.Column(scale=1):
                        gr.Markdown("### 8. Kalite Kontrol (QC)")
                        qc_table = gr.Dataframe(interactive=False)
                        status_msg = gr.Markdown("### Durum: Hazır")

            with gr.TabItem("📥 ADIM 9: Onarım & İndir"):
                gr.Markdown("### 9. Hatalı QR Onarımı ve Final Paket")
                with gr.Row():
                    repair_btn = gr.Button("🛠️ Akıllı Onarımı Başlat", variant="secondary", elem_classes="repair-btn")
                    download_btn = gr.File(label="ZIP Paketini İndir")
                gr.Markdown("""
                > **Not:** Akıllı onarım, okunamayan QR kodları otomatik olarak daha yüksek kontrast ve güvenli ayarlarla tekrar üretir.
                """)

        # Actions
        csv_input.change(handle_csv_upload, inputs=csv_input, outputs=[data_editor, csv_status])
        asset_input.change(handle_asset_upload, inputs=asset_input, outputs=asset_status)
        process_btn.click(run_process, inputs=[data_editor, gr.State(False)], outputs=[logs, gallery, download_btn, status_msg, qc_table])
        repair_btn.click(run_process, inputs=[data_editor, gr.State(True)], outputs=[logs, gallery, download_btn, status_msg, qc_table])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
