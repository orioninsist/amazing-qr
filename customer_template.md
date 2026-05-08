# 📋 Amazing-QR Toplu Sipariş Şablonu (Müşteri Rehberi)

Bu döküman, toplu QR kodu siparişi verirken doldurmanız gereken tabloyu açıklamaktadır. Lütfen aşağıdaki kurallara göre bir Excel veya Google Sheets dosyası hazırlayıp tarafımıza iletiniz.

## 📁 Dosya Yapısı
Siparişinizi şu şekilde teslim etmelisiniz:
1.  **Sipariş Listesi (Excel/CSV):** Linklerin ve ayarların bulunduğu tablo.
2.  **Varlıklar Klasörü (Assets):** QR kodun içinde kullanılacak logolar, fotoğraflar veya GIF'ler.

---

## 📊 Tablo Sütun Açıklamaları

| Sütun Adı | Açıklama | Örnek Değer | Zorunlu mu? |
| :--- | :--- | :--- | :--- |
| **words** | QR kodun içine gömülecek link veya metin. | `https://site.com` | **EVET** |
| **picture** | Kullanılacak görselin dosya adı (Uzantısıyla birlikte). | `logo.png` veya `dans.gif` | Hayır |
| **colorized** | QR kod renkli mi olsun? (True/False) | `True` | Hayır |
| **save_name** | Oluşturulacak dosyanın adı. | `sube_1_qr.png` | **EVET** |
| **version** | QR yoğunluğu (1-40 arası). Karmaşık linkler için 10 idealdir. | `10` | Hayır (Varsayılan: 1) |
| **level** | Hata düzeltme seviyesi (L, M, Q, H). H en yüksektir. | `H` | Hayır (Varsayılan: H) |
| **contrast** | Görselin kontrast ayarı (1.0 normaldir). | `1.2` | Hayır |
| **brightness** | Görselin parlaklık ayarı (1.0 normaldir). | `1.1` | Hayır |

---

## 💡 Önemli İpuçları
- **Görsel İsimleri:** Tablodaki `picture` sütununa yazdığınız isim ile klasöre koyduğunuz dosya ismi **birebir aynı** olmalıdır.
- **GIF Kullanımı:** Eğer hareketli bir QR istiyorsanız, `picture` kısmına `.gif` uzantılı bir dosya yazın ve `save_name` kısmını da mutlaka `.gif` ile bitirin.
- **Logo Kullanımı:** Logonun QR'ın ortasında net görünmesi için `colorized` değerini `True` yapmanızı öneririz.

---

## 🚀 Örnek Senaryo
10 farklı restoran şubesi için QR istiyorsanız, tablonuza 10 satır ekleyin ve her şube için farklı bir `save_name` (örneğin: `kadikoy.png`, `besiktas.png`) belirleyin.
