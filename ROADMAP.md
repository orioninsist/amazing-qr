# 🗺️ Amazing-QR Çalışma Yol Haritası (Roadmap)

Bu belge, projenin temiz yapısını ve çalışma prensiplerini özetler.

## 1. Klasör Yapısı ve Görevleri

Proje, karmaşayı önlemek için belirli bir hiyerarşi üzerine kuruludur:

| Klasör / Dosya | Görev | Not |
| :--- | :--- | :--- |
| `inputs/` | Ana giriş klasörü. | Git tarafından yoksayılır. |
| `inputs/assets/` | Arka plan resimlerini ve GIF'leri içerir. | Git tarafından yoksayılır. |
| `inputs/order.csv` | Üretilecek QR kodların listesini tutar. | Git tarafından yoksayılır. |
| `output/` | Üretilen QR kodlar ve raporların kaydedildiği yer. | Git tarafından yoksayılır. |
| `portfolio/` | GitHub'da sergilenecek örnek çalışmaları içerir. | **Git'e eklenir.** |
| `amzqr/` | Projenin çekirdek görüntü işleme kütüphanesi. | - |
| `app.py` | Yerel Docker arayüzü (Gradio). | - |
| `amazing_qr_colab.ipynb` | Google Colab bulut çalışma dosyası. | - |

## 2. Çalışma Akışları

### A) Yerel (Docker) Akışı
1.  `inputs/assets/` klasörüne görsellerinizi koyun.
2.  `inputs/order.csv` dosyasını hazırlayın (veya `sync_assets.sh` kullanın).
3.  Docker container'ı çalıştırın:
    ```bash
    docker run -p 7860:7860 -v $(pwd)/inputs:/app/inputs -v $(pwd)/output:/app/output amazing-qr
    ```
4.  `http://localhost:7860` üzerinden işlemi başlatın.

### B) Bulut (Google Colab) Akışı
1.  `amazing_qr_colab.ipynb` dosyasını Colab'da açın.
2.  Adımları sırasıyla takip ederek CSV ve Asset yüklemelerini yapın.
3.  Sonuçları ZIP olarak indirin.

## 3. Temizlik ve Bakım Kuralları
- **Gizlilik:** Müşteri assetleri ve sipariş listeleri asla GitHub'a pushlanmamalıdır (`.gitignore` buna göre ayarlanmıştır).
- **Redundant Dosyalar:** `outputs`, `temp`, `downloads` gibi klasörler yerine doğrudan `output/` klasörü kullanılmalıdır.
- **Yedekler:** `.bak` uzantılı dosyalar temiz tutulmalı veya `.gitignore` ile engellenmelidir.

---
*Bu yol haritası 9 Mayıs 2024 tarihinde projenin optimize edilmesiyle oluşturulmuştur.*
