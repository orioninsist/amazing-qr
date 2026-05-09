# 🚀 orioninsist QR: Sanatsal ve Toplu QR Kod Oluşturucu

[![GitHub-orioninsist](https://img.shields.io/badge/GitHub-orioninsist-blue?logo=github)](https://github.com/orioninsist)
[![License](https://img.shields.io/badge/license-GPLv3-yellow.svg)](https://github.com/orioninsist/amazing-qr/blob/master/LICENSE.md)

## 1. Proje Amacı ve Açıklaması
orioninsist QR, standart ve sıkıcı QR kodlarını görsel bir sanat eserine dönüştüren açık kaynaklı bir araçtır. Bu proje ile sadece veri içeren kodlar değil; arka planında resim, logo veya hareketli GIF bulunan, markanıza özel ve dikkat çekici QR kodlar oluşturabilirsiniz. Özellikle pazarlama materyalleri, kurumsal kimlik çalışmaları ve dijital içerikler için tasarlanmıştır.

## 2. Proje Süreci
Projenin geliştirme ve optimizasyon süreci aşağıdaki tarihler arasında gerçekleştirilmiştir:
- **Başlangıç:** 1 Mayıs 2024
- **Bitiş:** 9 Mayıs 2024
- **Durum:** Tamamlandı ve Optimize Edildi.

## 3. Çalışma Ortamları

### A) Yerel Kullanım (Docker)
Yerel makinenizde bağımlılık sorunlarıyla uğraşmadan çalışmanın en güvenli yolu Docker kullanmaktır.
- **Komut:** 
  ```bash
  docker run -p 7860:7860 -v $(pwd)/inputs:/app/inputs -v $(pwd)/output:/app/output orioninsist-qr
  ```
- **Erişim:** Tarayıcıdan `http://localhost:7860` adresine giderek modern Gradio arayüzünü kullanabilirsiniz.

### B) Bulut Kullanımı (Google Colab)
Herhangi bir kurulum yapmadan, doğrudan tarayıcı üzerinden çalışmak için Colab notebook'u tercih edebilirsiniz.
- **Mantık:** GitHub deposu klonlanır, kütüphaneler kurulur ve interaktif hücreler üzerinden işlemler yapılır.
- **Link:** [Google Colab Üzerinde Çalıştır](amazing_qr_colab.ipynb)

## 4. Varlık Senkronizasyonu (`sync_assets.sh`)
Toplu (Batch) QR kod üretim sürecini hızlandırmak ve otomatize etmek için bu betiği kullanabilirsiniz. Özellikle çok sayıda görselle çalışırken büyük kolaylık sağlar.
- **İşlevi:** `inputs/assets` klasörü içindeki tüm resim ve GIF dosyalarını tarar ve bunları otomatik olarak `inputs/order.csv` listesine ekler.
- **Kullanımı:**
  ```bash
  bash sync_assets.sh
  ```
- **Avantajı:** Manuel CSV düzenleme ihtiyacını ortadan kaldırır ve hata payını düşürür.

## 5. Parametre Detayları

| Parametre | Açıklama | Değer Aralığı / Örnek |
| :--- | :--- | :--- |
| `Words` | QR koda gömülecek veri. | URL veya Metin |
| `-v` | QR kod boyutu (Versiyon). | 1 - 40 |
| `-l` | Hata düzeltme seviyesi. | L, M, Q, H (Varsayılan: H) |
| `-n` | Çıktı dosyasının adı. | `isim.png`, `isim.gif` vb. |
| `-d` | Çıktının kaydedileceği klasör. | `/yol/to/klasor` |
| `-p` | Arka plana yerleştirilecek resim/GIF. | `dosya.jpg`, `dosya.gif` |
| `-c` | Çıktıyı renklendirmek için kullanılır. | (Sadece bayrak) |
| `-con` | Görselin kontrastını ayarlar. | Varsayılan 1.0 |
| `-bri` | Görselin parlaklığını ayarlar. | Varsayılan 1.0 |

## 6. Sonuç ve Çıktılar
İşlem tamamlandığında projenin `output/` klasöründe şu sonuçlar elde edilir:
- **Sanatsal QR Kodlar:** Belirlediğiniz resimle bütünleşmiş yüksek kaliteli `.png` veya `.jpg` dosyaları.
- **Hareketli QR Kodlar:** GIF arka planlı, dinamik ve okunaklı `.gif` dosyaları.
- **Analiz Raporu:** Toplu işlemlerde üretilen kodların okunabilirlik durumunu gösteren `report.json`.

## 7. Proje Analizi
Proje, görüntü işleme kütüphaneleri (Pillow ve OpenCV) ile QR kod üretim standartlarını birleştirir. Yapılan analizler sonucunda:
- **Okunabilirlik:** En yüksek hata düzeltme seviyesi (H) kullanılarak karmaşık görsellerde dahi %99 başarı oranı yakalanmıştır.
- **Performans:** Toplu işlem (Batch Processing) motoru sayesinde yüzlerce QR kod saniyeler içinde üretilebilmektedir.
- **Kullanılabilirlik:** Docker izolasyonu sayesinde "bağımlılık hatası" riski sıfıra indirilmiştir.

## 8. Credits
This project is based on the [amzqr](https://github.com/x-python/amazing-qr) library. Specialized and optimized by [orioninsist](https://github.com/orioninsist).

---
**Geliştirici:** [orioninsist](https://github.com/orioninsist)
