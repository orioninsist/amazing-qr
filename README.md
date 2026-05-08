# 🚀 Amazing-QR: Sanatsal ve Toplu QR Kod Oluşturucu

[![GitHub-orioninsist](https://img.shields.io/badge/GitHub-orioninsist-blue?logo=github)](https://github.com/orioninsist)
[![License](https://img.shields.io/badge/license-GPLv3-yellow.svg)](https://github.com/orioninsist/amazing-qr/blob/master/LICENSE.md)
[![Python-Version](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)

Amazing-QR (amzqr), standart QR kodlarının ötesine geçerek; sanatsal, renkli ve hareketli (GIF) QR kodları oluşturmanıza olanak tanıyan güçlü bir araçtır. Bu sürüm, özellikle **toplu üretim (batch processing)** için optimize edilmiştir.

---

## 🌟 Öne Çıkan Özellikler

- **Sanatsal QR:** İstediğiniz bir görseli (JPG, PNG, BMP) QR kodun arka planı olarak kullanın.
- **Hareketli QR:** GIF desteği ile göz alıcı, hareketli QR kodları oluşturun.
- **Toplu İşlem:** Tek bir CSV veya JSON dosyası ile yüzlerce QR kodunu saniyeler içinde üretin.
- **Türkçe Karakter Desteği:** Linklerinizde veya metinlerinizde Türkçe karakterleri (ç, ğ, ı, ö, ş, ü) güvenle kullanın.
- **Otomatik Optimizasyon:** Görselleriniz otomatik olarak kare boyutuna getirilir ve keskinleştirilir.

---

## 🛠️ Kurulum ve Kullanım

### 1. Docker ile Yerel Kullanım (Kesin Kural: Sadece Docker)
Yerel bilgisayarınızda Python veya kütüphane kurulumu yapmanıza gerek yoktur. Her şey Docker konteyneri içinde çalışır.

**Tekil QR Üretimi:**
```bash
docker run -v $(pwd)/output:/app/output amazing-qr "https://github.com/orioninsist" -n my_qr.png
```

**Toplu (Batch) QR Üretimi:**
`inputs/order.csv` veya `order.json` dosyanızı hazırlayın ve şu komutu çalıştırın:
```bash
docker run --entrypoint python -v $(pwd)/inputs:/app/inputs -v $(pwd)/output:/app/output amazing-qr batch_process.py
```

### 2. Google Colab ile Kullanım (Bulut Üzerinde)
Google Colab üzerinde Docker kullanılmaz. Notebook, projeyi doğrudan GitHub'dan klonlayarak çalıştırır.

👉 **[Amazing-QR Google Colab Notebook](amazing_qr_colab.ipynb)**

Notebook adımları:
1. `git clone https://github.com/orioninsist/amazing-qr.git` komutu ile projeyi indirir.
2. Gerekli kütüphaneleri yükler.
3. Form üzerinden tekil veya `batch_process.py` ile toplu üretim yapar.

---

## 📊 Müşteri Veri Formatı (Toplu Sipariş)

Toplu üretim için `inputs/order.csv` dosyasını hazırlamak artık çok daha kolay. Teknik detaylarla uğraşmanıza gerek yok, sistemimiz en iyi ayarları (Premium) otomatik seçer.

| Sütun (Key) | Açıklama | Örnek |
| :--- | :--- | :--- |
| **words** | QR kodun içeriği (URL veya Metin) | `https://google.com` |
| **picture** | Logo veya GIF dosya adı (Opsiyonel) | `logo.png` veya `animasyon.gif` |

### Örnek CSV içeriği:
```csv
words,picture
https://site1.com,logo.png
https://site2.com,dance.gif
https://site3.com,
```

> [!TIP]
> **Akıllı Sistem:** Eğer bir görsel (`picture`) eklerseniz, sistem otomatik olarak renklendirme (`colorized=True`) yapar ve en yüksek kalite seviyesini (`Level=H`) seçer. Dosya isimleri de içeriğe göre otomatik oluşturulur.

---

## 📁 Klasör Yapısı

Sistemin doğru çalışması için dosyalarınızı şu yapıda tutun:

```text
amazing-qr/
├── inputs/
│   ├── order.csv       <-- Sipariş listesi (CSV veya JSON)
│   └── assets/         <-- Görseller ve GIF'ler (logo.png vb.)
└── output/             <-- Üretilen QR kodları ve report.json buraya gelir
```

---

## 🔍 Teknik Detaylar

- **Hata Düzeltme Seviyesi (Level):** Varsayılan olarak **H** (En yüksek) kullanılır.
- **Kontrast ve Parlaklık:** `-con` (kontrast) ve `-bri` (parlaklık) parametreleri ile arka plan görsellerini optimize edebilirsiniz.
- **Raporlama:** Toplu işlem bittiğinde `output/report.json` dosyasında hangi QR'ın başarıyla üretildiğini görebilirsiniz.

---

## 👨‍💻 Geliştirici
**Murat** tarafından geliştirilmektedir.
[GitHub Profilim](https://github.com/orioninsist)

---

## 📜 Lisans
Bu proje **GPLv3** lisansı ile korunmaktadır.
