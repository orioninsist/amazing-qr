import json
import os

with open('amazing_qr_colab.ipynb', 'r') as f:
    nb = json.load(f)

# Block 7 (QC)
block_7_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
     "qc_html = \"<table border='1' style='border-collapse: collapse; width: 100%;'>\"\n",
     "qc_html += \"<tr style='background: #2c3e50; color: white;'><th>Dosya</th><th>Durum</th><th>İçerik</th></tr>\"\n",
     "for r in process_reports:\n",
     "    status = r.get('scannable', 'Unknown')\n",
     "    color = \"#27ae60\" if \"✅\" in status else (\"#e74c3c\" if \"❌\" in status else \"#f39c12\")\n",
     "    scanned_data = r.get('scanned_data', '-')\n",
     "    qc_html += f\"<tr><td>{r['output_file']}</td><td style='color: {color}; font-weight: bold;'>{status}</td><td>{scanned_data}</td></tr>\"\n",
     "qc_html += \"</table>\"\n",
     "display(HTML(qc_html))"
    ]
}

# Block 9 (Opsiyonel - Cleanup/Improve)
block_9_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
     "## 🔄 9. Hızlı Onarım (Optional)\n",
     "Eğer bazı QR kodlar okunamıyorsa, parametreleri 3. bloktan güncelleyip 5. bloğu tekrar çalıştırabilirsiniz."
    ]
}
block_9_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
     "display(HTML(\"<div style='padding: 15px; border: 1px solid #3498db; border-radius: 5px;'>💡 <b>İpucu:</b> Genellikle <b>Contrast</b> değerini 1.5 - 2.0 arasına çekmek ve <b>Brightness</b> değerini 1.0 yapmak çoğu sorunu çözer.</div>\"))"
    ]
}

# Find indices and replace
# Block 7 code is at index 14 in the NEW structure (after insertion of 2 cells)
# Let's find them by markdown source to be safe
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        src = "".join(cell['source'])
        if "7. Kalite Kontrol" in src:
            nb['cells'][i+1] = block_7_code
        elif "9. (Opsiyonel) Yeniden Kontrol" in src:
            nb['cells'][i] = block_9_md
            nb['cells'][i+1] = block_9_code

with open('amazing_qr_colab.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
