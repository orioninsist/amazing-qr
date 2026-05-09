import json
import os

with open('amazing_qr_colab.ipynb', 'r') as f:
    nb = json.load(f)

# Block 2 and 2.5
block_2_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
     "## 📁 2. Sipariş Listesini Yükle (order.csv)\n",
     "Her seferinde sıfırdan bir `order.csv` yüklenmesi zorunludur. Tablo yüklenene kadar görünmez."
    ]
}
block_2_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
     "csv_path = 'inputs/order.csv'\n",
     "\n",
     "def upload_csv(b):\n",
     "    clear_output()\n",
     "    display(HTML(\"<div style='color: #2980b9; font-weight: bold;'>📁 Lütfen order.csv dosyasını seçin...</div>\"))\n",
     "    uploaded = files.upload()\n",
     "    if uploaded:\n",
     "        filename = list(uploaded.keys())[0]\n",
     "        with open(csv_path, 'wb') as f:\n",
     "            f.write(uploaded[filename])\n",
     "        display(HTML(f\"<div style='color: #27ae60; font-weight: bold;'>✅ {filename} yüklendi ve {csv_path} olarak kaydedildi.</div>\"))\n",
     "        display(HTML(\"<p>Şimdi 2.5 Bloğa geçerek assetleri yükleyebilirsiniz.</p>\"))\n",
     "\n",
     "up_csv_btn = widgets.Button(description=\"📁 order.csv Yükle\", button_style='primary', layout={'width': '250px', 'height': '50px'})\n",
     "up_csv_btn.on_click(upload_csv)\n",
     "display(up_csv_btn)"
    ]
}
block_2_5_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
     "## 🖼️ 2.5. Assetleri Yükle (Logos, GIFs, Backgrounds)\n",
     "QR kodlarda kullanacağınız görselleri buraya yükleyin. Birden fazla dosya seçebilirsiniz."
    ]
}
block_2_5_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
     "def upload_assets(b):\n",
     "    display(HTML(\"<div style='color: #2980b9;'>🖼️ Lütfen arka plan/logo dosyalarını seçin (Çoklu seçim yapılabilir)...</div>\"))\n",
     "    uploaded = files.upload()\n",
     "    for filename in uploaded.keys():\n",
     "        dest = os.path.join('inputs/assets', filename)\n",
     "        with open(dest, 'wb') as f:\n",
     "            f.write(uploaded[filename])\n",
     "        display(HTML(f\"<div style='color: #27ae60;'>✅ {filename} yüklendi.</div>\"))\n",
     "\n",
     "up_asset_btn = widgets.Button(description=\"🖼️ Asset Yükle\", button_style='info', layout={'width': '250px', 'height': '50px'})\n",
     "up_asset_btn.on_click(upload_assets)\n",
     "display(up_asset_btn)"
    ]
}

# Block 3 Editor overhaul
block_3_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
     "import re\n",
     "\n",
     "def slugify(value):\n",
     "    value = re.sub(r'^https?://', '', str(value))\n",
     "    value = re.sub(r'[^\\w\\s-]', '_', value).strip().lower()\n",
     "    return re.sub(r'[-\\s]+', '_', value)[:50]\n",
     "\n",
     "def load_data():\n",
     "    if not os.path.exists(csv_path): return pd.DataFrame()\n",
     "    df = pd.read_csv(csv_path)\n",
     "    cols = ['selected', 'words', 'version', 'level', 'picture', 'colorized', 'contrast', 'brightness', 'save_name']\n",
     "    for c in cols:\n",
     "        if c not in df.columns:\n",
     "            if c == 'selected': df[c] = True\n",
     "            elif c == 'version': df[c] = 1\n",
     "            elif c == 'level': df[c] = 'H'\n",
     "            elif c in ['contrast', 'brightness']: df[c] = 1.0\n",
     "            elif c == 'colorized': df[c] = True\n",
     "            else: df[c] = \"\"\n",
     "    return df[cols]\n",
     "\n",
     "def save_data(df): df.to_csv(csv_path, index=False)\n",
     "\n",
     "editor_out = widgets.Output()\n",
     "\n",
     "def refresh_editor():\n",
     "    with editor_out:\n",
     "        clear_output()\n",
     "        df = load_data()\n",
     "        if df.empty: \n",
     "            display(HTML(\"❌ Tablo bulunamadı. Lütfen 2. Bloğu kullanarak bir CSV yükleyin.\"))\n",
     "            return\n",
     "        \n",
     "        display(HTML(\"<h3 style='color: #2c3e50;'>✍️ Sipariş Düzenleyici</h3>\"))\n",
     "        \n",
     "        bulk_btn = widgets.Button(description=\"🛠️ Toplu Düzenle\", button_style='warning', icon='gears')\n",
     "        bulk_btn.on_click(lambda b: show_bulk_editor())\n",
     "        refresh_btn = widgets.Button(description=\"🔄 Yenile\", button_style='info', icon='refresh')\n",
     "        refresh_btn.on_click(lambda b: refresh_editor())\n",
     "        \n",
     "        display(widgets.HBox([bulk_btn, refresh_btn]))\n",
     "        display(HTML(\"<br>\"))\n",
     "\n",
     "        header = widgets.HBox([\n",
     "            widgets.Label(\"Seç\", layout={'width': '40px'}),\n",
     "            widgets.Label(\"URL / Metin\", layout={'width': '200px'}),\n",
     "            widgets.Label(\"V\", layout={'width': '30px'}),\n",
     "            widgets.Label(\"L\", layout={'width': '30px'}),\n",
     "            widgets.Label(\"Görsel\", layout={'width': '120px'}),\n",
     "            widgets.Label(\"İşlem\", layout={'width': '80px'})\n",
     "        ])\n",
     "        display(header)\n",
     "        \n",
     "        rows = []\n",
     "        for i, row in df.iterrows():\n",
     "            sel = widgets.Checkbox(value=bool(row['selected']), layout={'width': '40px'})\n",
     "            def on_sel(change, idx=i): \n",
     "                d = load_data()\n",
     "                d.at[idx, 'selected'] = change['new']\n",
     "                save_data(d)\n",
     "            sel.observe(on_sel, 'value')\n",
     "            \n",
     "            edit = widgets.Button(description=\"Düzenle\", icon='pencil', layout={'width': '80px'}, button_style='primary')\n",
     "            edit.on_click(lambda b, idx=i: show_row_editor(idx))\n",
     "            \n",
     "            r = widgets.HBox([\n",
     "                sel, \n",
     "                widgets.Label(str(row['words'])[:25], layout={'width': '200px'}), \n",
     "                widgets.Label(str(row['version']), layout={'width': '30px'}),\n",
     "                widgets.Label(str(row['level']), layout={'width': '30px'}),\n",
     "                widgets.Label(str(row['picture']), layout={'width': '120px'}), \n",
     "                edit\n",
     "            ])\n",
     "            rows.append(r)\n",
     "        display(widgets.VBox(rows))\n",
     "\n",
     "def show_row_editor(idx):\n",
     "    with editor_out:\n",
     "        clear_output()\n",
     "        df = load_data()\n",
     "        row = df.iloc[idx]\n",
     "        display(HTML(f\"<h4>Satır {idx+1} Düzenleniyor</h4>\"))\n",
     "        \n",
     "        w_words = widgets.Text(value=str(row['words']), description='Words (URL):')\n",
     "        w_ver = widgets.IntSlider(value=int(row['version']), min=1, max=40, description='Version:')\n",
     "        w_lvl = widgets.Dropdown(options=['L', 'M', 'Q', 'H'], value=row['level'], description='Level:')\n",
     "        w_pic = widgets.Text(value=str(row['picture']), description='Picture:')\n",
     "        w_col = widgets.Checkbox(value=bool(row['colorized']), description='Colorized')\n",
     "        w_con = widgets.FloatSlider(value=float(row['contrast']), min=0.1, max=3.0, step=0.1, description='Contrast:')\n",
     "        w_bri = widgets.FloatSlider(value=float(row['brightness']), min=0.1, max=3.0, step=0.1, description='Brightness:')\n",
     "        w_name = widgets.Text(value=str(row['save_name']), description='Save Name:')\n",
     "        \n",
     "        save = widgets.Button(description=\"Kaydet\", button_style='success', icon='check')\n",
     "        cancel = widgets.Button(description=\"İptal\", button_style='danger', icon='times')\n",
     "        \n",
     "        def on_save(b):\n",
     "            df.at[idx, 'words'] = w_words.value\n",
     "            df.at[idx, 'version'] = w_ver.value\n",
     "            df.at[idx, 'level'] = w_lvl.value\n",
     "            df.at[idx, 'picture'] = w_pic.value\n",
     "            df.at[idx, 'colorized'] = w_col.value\n",
     "            df.at[idx, 'contrast'] = w_con.value\n",
     "            df.at[idx, 'brightness'] = w_bri.value\n",
     "            df.at[idx, 'save_name'] = w_name.value\n",
     "            save_data(df)\n",
     "            refresh_editor()\n",
     "            \n",
     "        save.on_click(on_save)\n",
     "        cancel.on_click(lambda b: refresh_editor())\n",
     "        display(widgets.VBox([w_words, w_ver, w_lvl, w_pic, w_col, w_con, w_bri, w_name, widgets.HBox([save, cancel])]))\n",
     "\n",
     "def show_bulk_editor():\n",
     "    with editor_out:\n",
     "        clear_output()\n",
     "        df = load_data()\n",
     "        display(HTML(\"<h4>Toplu Düzenleme Paneli</h4>\"))\n",
     "        v_check = widgets.Checkbox(description=\"Versiyon (1-40)\")\n",
     "        v_val = widgets.IntSlider(value=1, min=1, max=40)\n",
     "        l_check = widgets.Checkbox(description=\"Hata Seviyesi (L,M,Q,H)\")\n",
     "        l_val = widgets.Dropdown(options=['L', 'M', 'Q', 'H'], value='H')\n",
     "        p_check = widgets.Checkbox(description=\"Görsel (Asset Adı)\")\n",
     "        p_val = widgets.Text(placeholder=\"logo.png\")\n",
     "        c_check = widgets.Checkbox(description=\"Renklendirme (True/False)\")\n",
     "        c_val = widgets.Checkbox(value=True)\n",
     "        apply_b = widgets.Button(description=\"Tümüne Uygula\", button_style='warning', icon='bolt')\n",
     "        cancel_b = widgets.Button(description=\"Vazgeç\", icon='times')\n",
     "        \n",
     "        def on_apply(b):\n",
     "            for i in range(len(df)):\n",
     "                if v_check.value: df.at[i, 'version'] = v_val.value\n",
     "                if l_check.value: df.at[i, 'level'] = l_val.value\n",
     "                if p_check.value: df.at[i, 'picture'] = p_val.value\n",
     "                if c_check.value: df.at[i, 'colorized'] = c_val.value\n",
     "            save_data(df)\n",
     "            refresh_editor()\n",
     "            \n",
     "        apply_b.on_click(on_apply)\n",
     "        cancel_b.on_click(lambda b: refresh_editor())\n",
     "        display(widgets.VBox([\n",
     "            widgets.HBox([v_check, v_val]), \n",
     "            widgets.HBox([l_check, l_val]), \n",
     "            widgets.HBox([p_check, p_val]), \n",
     "            widgets.HBox([c_check, c_val]), \n",
     "            widgets.HBox([apply_b, cancel_b])\n",
     "        ]))\n",
     "\n",
     "refresh_editor()\n",
     "display(editor_out)"
    ]
}

# Replace cells
# Original indices: 
# 3: Block 2 MD, 4: Block 2 Code -> Replace with block_2_md, block_2_code, block_2_5_md, block_2_5_code
# 6: Block 3 Code -> Replace with block_3_code

new_cells = nb['cells'][:3] # Up to Block 1
new_cells.extend([block_2_md, block_2_code, block_2_5_md, block_2_5_code])
new_cells.append(nb['cells'][5]) # Block 3 MD
new_cells.append(block_3_code)
new_cells.extend(nb['cells'][7:]) # Rest of the blocks

nb['cells'] = new_cells

with open('amazing_qr_colab.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
