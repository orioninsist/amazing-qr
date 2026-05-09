import json

notebook_path = 'amazing_qr_colab.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update Step 1 (usually cells[2])
# Finding the setup cell
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'os.path.exists(\'amzqr\')' in ''.join(cell['source']):
        cell['source'] = [
            "import os\n",
            "import shutil\n",
            "import pandas as pd\n",
            "import ipywidgets as widgets\n",
            "from IPython.display import display, HTML, clear_output\n",
            "from google.colab import files\n",
            "\n",
            "# 1. Projeyi GitHub'dan çek (Veya güncelle)\n",
            "repo_name = \"amazing-qr\"\n",
            "if not os.path.exists(repo_name):\n",
            "    print(\"🚀 Proje indiriliyor...\")\n",
            "    !git clone https://github.com/orioninsist/amazing-qr.git\n",
            "    %cd {repo_name}\n",
            "else:\n",
            "    %cd {repo_name}\n",
            "    !git pull\n",
            "\n",
            "# 2. Sistem Bağımlılıklarını Kur (ZBar)\n",
            "!apt-get install -y -qq libzbar0\n",
            "\n",
            "# 3. Python Paketlerini Kur (SABİT VERSİYONLAR)\n",
            "print(\"📦 Paketler yükleniyor (requirements.txt baz alınıyor)...\")\n",
            "!pip install -q -r requirements.txt\n",
            "!pip install -q -e .\n",
            "\n",
            "# 4. WeChat QR Modellerini Otomatik Kur\n",
            "if os.path.exists('setup_models.py'):\n",
            "    print(\"🧠 Yapay Zeka modelleri kontrol ediliyor...\")\n",
            "    !python3 setup_models.py\n",
            "\n",
            "# Klasör yapısını hazırla\n",
            "!mkdir -p inputs/assets\n",
            "!mkdir -p output\n",
            "\n",
            "print(\"✅ Kurulum ve Modeller tamamlandı.\")"
        ]
        break

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("✅ amazing_qr_colab.ipynb başarıyla güncellendi.")
