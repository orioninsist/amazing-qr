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

# Global state for reports
current_reports = []

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

def run_batch_ui(df_data, auto_repair=False):
    global current_reports
    if df_data is None or df_data.empty:
        yield "❌ Hata: Veri bulunamadı.", [], None, "❌ İşlem Başlatılamadı", pd.DataFrame()
        return

    # Save current state to order.csv
    dest = os.path.join(INPUTS_DIR, "order.csv")
    df_data.to_csv(dest, index=False)

    if not auto_repair:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)
        selected_rows = df_data[df_data['selected'] == True].to_dict('records')
        current_reports = []
    else:
        # Repair only failed items from current_reports
        selected_rows = [r for r in current_reports if "❌" in r.get('scannable', '')]
        if not selected_rows:
            yield "✅ Onarılacak hatalı kod bulunamadı.", [], None, "✅ Sorun Yok", pd.DataFrame(current_reports)
            return

    if not selected_rows:
        yield "⚠️ Uyarı: Hiçbir satır seçilmedi.", [], None, "⚠️ Seçim Yok", pd.DataFrame()
        return

    logs = "🚀 İşlem başlatıldı...\n" if not auto_repair else "🛠️ Akıllı Onarım başlatıldı...\n"
    images = []
    
    for status, img_path, report in process_items(selected_rows, ASSETS_DIR, OUTPUT_DIR, auto_repair=auto_repair):
        if status:
            logs += f"{status}\n"
        if img_path:
            # Refresh images list
            images = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(('.png', '.gif', '.jpg'))]
            images.sort()
        if report:
            if auto_repair:
                # Update existing report
                for i, orp in enumerate(current_reports):
                    if orp['output_file'] == report['output_file']:
                        current_reports[i] = report
            else:
                current_reports.append(report)
        
        qc_df = pd.DataFrame(current_reports)
        yield logs, images, None, "⏳ İşleniyor...", qc_df

    # Create ZIP
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"amazing_qr_results_{now}.zip"
    zip_path = os.path.join(BASE_DIR, "output_zips")
    os.makedirs(zip_path, exist_ok=True)
    full_zip_path = os.path.join(zip_path, zip_name)
    
    # Remove extension from make_archive base_name
    shutil.make_archive(full_zip_path.replace('.zip', ''), 'zip', OUTPUT_DIR)
    
    logs += f"\n✅ Tamamlandı!\n📦 Paket hazır: {zip_name}"
    
    failed_count = len([r for r in current_reports if "❌" in r.get('scannable', '')])
    final_status = "🟢 TÜMÜ BAŞARILI" if failed_count == 0 else f"🟠 {failed_count} HATALI"
    
    qc_df = pd.DataFrame(current_reports)
    yield logs, images, full_zip_path, final_status, qc_df

def apply_bulk_edit(df, v_check, v_val, l_check, l_val, p_check, p_val, c_check, c_val, con_check, con_val, bri_check, bri_val):
    if df is None or df.empty:
        return df
    
    new_df = df.copy()
    for i in range(len(new_df)):
        if v_check: new_df.at[i, 'version'] = v_val
        if l_check: new_df.at[i, 'level'] = l_val
        if p_check: new_df.at[i, 'picture'] = p_val
        if c_check: new_df.at[i, 'colorized'] = c_val
        if con_check: new_df.at[i, 'contrast'] = con_val
        if bri_check: new_df.at[i, 'brightness'] = bri_val
        
    return new_df

def select_all_rows(df, status):
    if df is None or df.empty:
        return df
    new_df = df.copy()
    new_df['selected'] = status
    return new_df

# Premium CSS
custom_css = """
.container { max-width: 1200px; margin: auto; }
.header { text-align: center; margin-bottom: 2rem; background: linear-gradient(135deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%); color: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
.step-box { border: 1px solid #e0e0e0; padding: 25px; border-radius: 15px; margin-bottom: 20px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.status-card { padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; margin-top: 10px; }
.bulk-panel { background: #f8f9fa; padding: 20px; border-radius: 12px; border-left: 6px solid #4dabf7; margin-bottom: 20px; }
.repair-btn { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%) !important; color: white !important; }
"""

with gr.Blocks(theme=gr.themes.Default(primary_hue="blue", secondary_hue="slate"), css=custom_css, title="Amazing QR - Pro Workflow") as demo:
    with gr.Div(elem_classes="container"):
        gr.Markdown("""
        <div class="header">
            <h1>🚀 Amazing QR: Profesyonel İş Akışı v1.1</h1>
            <p>Yapay Zeka Destekli Akıllı QR Üretim ve Onarım Merkezi</p>
        </div>
        """)
        
        with gr.Tabs() as tabs:
            with gr.TabItem("📁 ADIM 1-2.5: Hazırlık"):
                with gr.Row():
                    with gr.Column(elem_classes="step-box"):
                        gr.Markdown("### 1-2. Sipariş Listesi (order.csv)")
                        csv_input = gr.File(label="CSV Yükle", file_types=[".csv"])
                        csv_status = gr.Markdown("ℹ️ *Lütfen CSV yükleyerek başlayın.*")
                    with gr.Column(elem_classes="step-box"):
                        gr.Markdown("### 2.5. Asset Yükleme")
                        asset_input = gr.File(label="Görseller (Logos/GIFs)", file_count="multiple")
                        asset_status = gr.Markdown("ℹ️ *Henüz asset yüklenmedi.*")
                
            with gr.TabItem("✍️ ADIM 3-4: Düzenleme"):
                with gr.Accordion("🛠️ Toplu Düzenleme Paneli", open=False):
                    with gr.Row(elem_classes="bulk-panel"):
                        with gr.Column():
                            v_check = gr.Checkbox(label="V")
                            v_val = gr.Slider(1, 40, 1, label="Versiyon")
                        with gr.Column():
                            l_check = gr.Checkbox(label="L")
                            l_val = gr.Dropdown(['L', 'M', 'Q', 'H'], value='H', label="Hata Seviyesi")
                        with gr.Column():
                            p_check = gr.Checkbox(label="Pic")
                            p_val = gr.Textbox(placeholder="logo.png", label="Görsel")
                        with gr.Column():
                            c_check = gr.Checkbox(label="Color")
                            c_val = gr.Checkbox(value=True, label="Renkli")
                        with gr.Column():
                            con_check = gr.Checkbox(label="Con")
                            con_val = gr.Slider(0.1, 3.0, 1.5, step=0.1, label="Kontrast")
                        with gr.Column():
                            bri_check = gr.Checkbox(label="Bri")
                            bri_val = gr.Slider(0.1, 3.0, 1.0, step=0.1, label="Parlaklık")
                    
                    bulk_apply_btn = gr.Button("⚡ Tümüne Uygula", variant="secondary")

                gr.Markdown("### 3. Sipariş Detayları")
                with gr.Row():
                    sel_all_btn = gr.Button("✅ Tümünü Seç", size="sm")
                    sel_none_btn = gr.Button("⬜ Seçimi Kaldır", size="sm")
                data_editor = gr.Dataframe(
                    headers=['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name'],
                    datatype=["bool", "str", "number", "str", "str", "bool", "number", "number", "str"],
                    interactive=True,
                    label="order.csv Verileri",
                    type="pandas"
                )
                
                gr.Markdown("### 4. Son Kontrol")
                final_preview = gr.Dataframe(interactive=False, label="İşlenecek Satırlar")
                
                data_editor.change(get_final_preview, inputs=data_editor, outputs=final_preview)
                bulk_apply_btn.click(apply_bulk_edit, inputs=[data_editor, v_check, v_val, l_check, l_val, p_check, p_val, c_check, c_val, con_check, con_val, bri_check, bri_val], outputs=data_editor)
                sel_all_btn.click(lambda df: select_all_rows(df, True), inputs=data_editor, outputs=data_editor)
                sel_none_btn.click(lambda df: select_all_rows(df, False), inputs=data_editor, outputs=data_editor)

            with gr.TabItem("🔥 ADIM 5-10: İşlem & QC"):
                with gr.Row():
                    process_btn = gr.Button("🚀 Üretimi Başlat", variant="primary", size="lg")
                    repair_btn = gr.Button("🛠️ Akıllı Onarımı Başlat", variant="secondary", size="lg", elem_classes="repair-btn")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 8. Kalite Kontrol (QC)")
                        qc_table = gr.Dataframe(interactive=False, label="QC Raporu")
                        final_status_display = gr.Markdown("### Durum: Hazır")
                    with gr.Column(scale=2):
                        gr.Markdown("### 6-7. Çıktılar")
                        gallery_output = gr.Gallery(label="Önizleme", columns=3, height="auto")
                        log_output = gr.Textbox(label="Süreç Logları", lines=10, interactive=False)
                
            with gr.TabItem("📥 ADIM 11: İndir"):
                gr.Markdown("### 11. Sonuç Paketini Al")
                zip_output = gr.File(label="ZIP Paketini İndir")

        # Bindings
        csv_input.change(handle_csv_upload, inputs=csv_input, outputs=[data_editor, csv_status])
        asset_input.change(handle_asset_upload, inputs=asset_input, outputs=asset_status)
        
        process_btn.click(
            run_batch_ui, 
            inputs=[data_editor, gr.State(False)], 
            outputs=[log_output, gallery_output, zip_output, final_status_display, qc_table]
        )
        
        repair_btn.click(
            run_batch_ui, 
            inputs=[data_editor, gr.State(True)], 
            outputs=[log_output, gallery_output, zip_output, final_status_display, qc_table]
        )

        gr.Markdown("""
        <div style="text-align: center; margin-top: 40px; color: #95a5a6; font-size: 0.85em; border-top: 1px solid #eee; padding-top: 20px;">
            <p>© 2026 Amazing QR Pro | AI-Powered Workflow Engine</p>
            <p><i>Design Excellence by OrionInsist Solutions</i></p>
        </div>
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
