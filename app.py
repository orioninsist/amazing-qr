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
.header { text-align: center; margin-bottom: 2rem; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.step-box { border: 1px solid #eee; padding: 20px; border-radius: 12px; margin-bottom: 20px; background: #f8f9fa; }
.status-green { color: #27ae60; font-weight: bold; }
.status-orange { color: #f39c12; font-weight: bold; }
.bulk-panel { background: #f1f3f5; padding: 15px; border-radius: 8px; border-left: 5px solid #ff922b; margin-bottom: 15px; }
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"), css=custom_css, title="Amazing QR - Professional Workflow") as demo:
    with gr.Div(elem_classes="container"):
        gr.Markdown("""
        <div class="header">
            <h1>🚀 Amazing QR: Profesyonel İş Akışı</h1>
            <p>Modern ve Tam Kontrollü QR Kod Üretim Merkezi</p>
        </div>
        """)
        
        with gr.Tabs() as tabs:
            with gr.TabItem("📁 ADIM 1-2.5: Hazırlık & Yükleme"):
                with gr.Row():
                    with gr.Column(elem_classes="step-box"):
                        gr.Markdown("### 1-2. Liste Yükle")
                        csv_input = gr.File(label="order.csv Yükle (Zorunlu)", file_types=[".csv"])
                        csv_status = gr.Markdown("ℹ️ *Lütfen CSV yükleyin.*")
                    with gr.Column(elem_classes="step-box"):
                        gr.Markdown("### 2.5. Assetleri Yükle")
                        asset_input = gr.File(label="Görselleri Yükle (Logos/GIFs)", file_count="multiple")
                        asset_status = gr.Markdown("ℹ️ *Henüz asset yüklenmedi.*")
                
            with gr.TabItem("✍️ ADIM 3-4: Düzenleme & Kontrol"):
                with gr.Accordion("🛠️ Toplu Düzenleme Paneli", open=False):
                    with gr.Row(elem_classes="bulk-panel"):
                        with gr.Column():
                            v_check = gr.Checkbox(label="Versiyon Uygula")
                            v_val = gr.Slider(1, 40, 1, label="Versiyon")
                        with gr.Column():
                            l_check = gr.Checkbox(label="Hata Seviyesi Uygula")
                            l_val = gr.Dropdown(['L', 'M', 'Q', 'H'], value='H', label="Seviye")
                        with gr.Column():
                            p_check = gr.Checkbox(label="Görsel Uygula")
                            p_val = gr.Textbox(placeholder="resim.png", label="Asset Adı")
                        with gr.Column():
                            c_check = gr.Checkbox(label="Renk Uygula")
                            c_val = gr.Checkbox(value=True, label="Renklendir")
                        with gr.Column():
                            con_check = gr.Checkbox(label="Kontrast Uygula")
                            con_val = gr.Slider(0.1, 3.0, 1.5, step=0.1, label="Kontrast")
                        with gr.Column():
                            bri_check = gr.Checkbox(label="Parlaklık Uygula")
                            bri_val = gr.Slider(0.1, 3.0, 1.0, step=0.1, label="Parlaklık")
                    
                    bulk_apply_btn = gr.Button("⚡ Seçili Ayarları Tümüne Uygula", variant="secondary")

                gr.Markdown("### 3. Sipariş Detaylarını Düzenle")
                with gr.Row():
                    sel_all_btn = gr.Button("✅ Tümünü Seç", size="sm")
                    sel_none_btn = gr.Button("⬜ Seçimi Kaldır", size="sm")
                data_editor = gr.Dataframe(
                    headers=['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name'],
                    datatype=["bool", "str", "number", "str", "str", "bool", "number", "number", "str"],
                    interactive=True,
                    label="Düzenleme Tablosu (order.csv)",
                    type="pandas"
                )
                
                gr.Markdown("### 4. İşlem Öncesi Son Kontrol")
                final_preview = gr.Dataframe(interactive=False, label="Sadece İşlenecek Olanlar (Selected=True)")
                
                def update_previews(df):
                    return get_final_preview(df)
                
                data_editor.change(update_previews, inputs=data_editor, outputs=final_preview)
                
                bulk_apply_btn.click(
                    apply_bulk_edit, 
                    inputs=[data_editor, v_check, v_val, l_check, l_val, p_check, p_val, c_check, c_val, con_check, con_val, bri_check, bri_val], 
                    outputs=data_editor
                )
                
                sel_all_btn.click(lambda df: select_all_rows(df, True), inputs=data_editor, outputs=data_editor)
                sel_none_btn.click(lambda df: select_all_rows(df, False), inputs=data_editor, outputs=data_editor)

            with gr.TabItem("⚙️ ADIM 5-10: İşlem & Kalite Kontrol"):
                process_btn = gr.Button("🔥 Üretimi Başlat (Start Batch Process)", variant="primary", size="lg")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        log_output = gr.Textbox(label="5-8. Süreç Raporu", lines=15, interactive=False)
                        final_status_display = gr.Markdown("### Durum: Hazır", elem_id="status_display")
                    with gr.Column(scale=2):
                        gallery_output = gr.Gallery(label="6. QR Önizleme Galerisi", columns=4, height="auto")
                
            with gr.TabItem("📥 ADIM 11: Paketle & İndir"):
                gr.Markdown("### 11. Final Paketini İndir")
                gr.Markdown("İşlem tamamlandığında aşağıda beliren ZIP dosyasını indirebilirsiniz.")
                zip_output = gr.File(label="ZIP Dosyasını İndir")

        # Event Bindings
        csv_input.change(handle_csv_upload, inputs=csv_input, outputs=[data_editor, csv_status])
        asset_input.change(handle_asset_upload, inputs=asset_input, outputs=asset_status)
        
        process_btn.click(
            run_batch_ui, 
            inputs=data_editor, 
            outputs=[log_output, gallery_output, zip_output, final_status_display]
        )

        gr.Markdown("""
        <div style="text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 0.9em; border-top: 1px solid #eee; padding-top: 20px;">
            <p>© 2026 Amazing QR Workflow Engine | OrionInsist Solutions</p>
            <p><i>Güvenli, Hızlı ve Profesyonel QR Çözümleri</i></p>
        </div>
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
