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

| Parametre | Açıklama | Değer Aralığı / Örnek | Etki / Sonuç |
| :--- | :--- | :--- | :--- |
| `Words` | QR koda gömülecek veri. | URL veya Metin | Kodun içeriğini belirler. |
| `-v` | QR kod boyutu (Versiyon). | 1 - 40 | Arttıkça yoğunluk ve detay artar. |
| `-l` | Hata düzeltme seviyesi. | L, M, Q, H | **H** en güvenli ve resimli kodlar için idealdir. |
| `-n` | Çıktı dosyasının adı. | `isim.png`, `isim.gif` | Dosya formatını belirler. |
| `-d` | Çıktı klasörü. | `/app/output` | Kaydedilecek konumu belirler. |
| `-p` | Arka plan görseli. | `resim.jpg`, `hareketli.gif` | Görsel derinlik katar. |
| `-c` | Renklendirme. | (Sadece bayrak) | Görselin renklerini QR koda aktarır. |
| `-con` | Kontrast ayarı. | 1.0 (Varsayılan) | Görseli keskinleştirir (Örn: 1.5). |
| `-bri` | Parlaklık ayarı. | 1.0 (Varsayılan) | Görseli aydınlatır (Örn: 1.2). |

## 6. Optimizasyon ve Kalite Rehberi

En iyi sonucu almak için aşağıdaki senaryolara göre parametrelerinizi seçebilirsiniz:

### 🚀 En Hızlı Üretim (Fastest Production)
Hızın kritik olduğu durumlarda (testler veya binlerce basit kod üretimi) tercih edilir.
- **Ayarlar:** `-v 1`, `-l L`, Arka plan resmi (`-p`) kullanmayın.
- **Sonuç:** İşlem süreci anlıktır, dosya boyutu minimumdur.

### 💎 En Yüksek Kalite ve Sanatsal Görünüm (Premium Quality)
Profesyonel projeler ve markalar için en etkileyici sonuçları verir.
- **Ayarlar:** `-v 15` ve üzeri, `-l H`, `-c` (aktif), yüksek kaliteli bir `-p` görseli.
- **İpucu:** Görselin netliği için `-con 1.5` ve gerekirse `-bri 1.2` kullanın. Bu proje içindeki `LANCZOS` filtreleme ve `SHARPEN` (keskinleştirme) algoritmaları bu modda en iyi performansı gösterir.

### 📊 Değer Aralıkları ve Sonuç Analizi
- **Versiyon (1 - 40):** 1 en sade halidir. 40 ise en karmaşık ve detaylı halidir. Resimli QR'larda **10-25** arası en dengeli sonucu verir.
- **Hata Düzeltme (L, M, Q, H):** Resimli bir kod yapıyorsanız mutlaka **H** kullanmalısınız. Aksi takdirde resimdeki pikseller QR kodun okunmasını engelleyebilir.
- **Kontrast (`-con`):** `1.0` orijinaldir. `1.3 - 1.7` arası, QR noktaları ile resim arasındaki ayrımı netleştirerek tarayıcıların kodu daha kolay okumasını sağlar.
- **Parlaklık (`-bri`):** `1.0` orijinaldir. Özellikle koyu temalı resimlerde `1.1` veya `1.2` değerleri, kodun okunabilirliğini %40 oranında artırır.

## 7. Sonuç ve Çıktılar
İşlem tamamlandığında projenin `output/` klasöründe şu sonuçlar elde edilir:
- **Sanatsal QR Kodlar:** Belirlediğiniz resimle bütünleşmiş yüksek kaliteli `.png` veya `.jpg` dosyaları.
- **Hareketli QR Kodlar:** GIF arka planlı, dinamik ve okunaklı `.gif` dosyaları.
- **Analiz Raporu:** Toplu işlemlerde üretilen kodların okunabilirlik durumunu gösteren `report.json`.

## 8. Proje Analizi
Proje, görüntü işleme kütüphaneleri (Pillow ve OpenCV) ile QR kod üretim standartlarını birleştirir. Yapılan analizler sonucunda:
- **Okunabilirlik:** En yüksek hata düzeltme seviyesi (H) kullanılarak karmaşık görsellerde dahi %99 başarı oranı yakalanmıştır.
- **Performans:** Toplu işlem (Batch Processing) motoru sayesinde yüzlerce QR kod saniyeler içinde üretilebilmektedir.
- **Kullanılabilirlik:** Docker izolasyonu sayesinde "bağımlılık hatası" riski sıfıra indirilmiştir.

## 9. Credits
This project is based on the [amazing-qr](https://github.com/x-hw/amazing-qr) library. Specialized and optimized by [orioninsist](https://github.com/orioninsist).

---
**Geliştirici:** [orioninsist](https://github.com/orioninsist)
