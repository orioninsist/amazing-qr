# Amazing-QR Kullanım Kılavuzu

Amazing-QR (amzqr), Python ile yazılmış, hem sanatsal (artistic) hem de hareketli (animated) QR kodları oluşturmanıza olanak tanıyan güçlü bir araçtır. Bu kılavuz, projenin tüm özelliklerini ve kullanım şekillerini eksiksiz bir şekilde açıklamaktadır.

---

## 1. Genel Bakış
Amazing-QR ile üç ana tipte QR kod oluşturabilirsiniz:
1.  **Standart QR Kodlar:** Sadece veri içeren klasik görünümlü kodlar.
2.  **Sanatsal QR Kodlar:** Bir görsel (arka plan) ile birleştirilmiş, siyah-beyaz veya renkli kodlar.
3.  **Hareketli QR Kodlar:** Bir GIF dosyası ile birleştirilmiş, dinamik ve dikkat çekici kodlar.

---

## 2. Kurulum

### Pip ile Kurulum
Sisteminize doğrudan kurmak için:
```bash
pip install amzqr
```

### Docker ile Kurulum
Projeyi izole bir ortamda çalıştırmak isterseniz:
```bash
docker build -t amazing-qr .
```

---

## 3. Kullanım Yöntemleri

### A. Terminal (Komut Satırı) Yolu
Eğer paket yüklüyse `amzqr` komutunu, yüklü değilse proje dizininde `python amzqr.py` komutunu kullanabilirsiniz.

#### Temel Kullanım (Sadece Metin/Link)
```bash
amzqr "https://github.com/orioninsist"
```
Bu komut, geçerli dizinde `qrcode.png` adında bir dosya oluşturur.

#### Sanatsal Arka Plan Ekleme (-p)
Bir resmi QR kodun arkasına yerleştirmek için:
```bash
amzqr "https://github.com" -p ornek_resim.jpg
```

#### Renklendirme (-c)
Arka plan resminin renklerini korumak için `-c` parametresini ekleyin:
```bash
amzqr "https://github.com" -p ornek_resim.jpg -c
```

#### Hareketli GIF Oluşturma
Arka plan olarak bir `.gif` dosyası verdiğinizde, çıktı otomatik olarak hareketli bir QR kod olur:
```bash
amzqr "https://github.com" -p animasyon.gif -c
```

---

### B. Python İçinden Kullanım (Import Yolu)
Kendi projelerinize entegre etmek için:

```python
from amzqr import amzqr
import os

version, level, qr_name = amzqr.run(
    words="https://github.com",
    version=1,                # 1-40 arası büyüklük
    level='H',                # Hata düzeltme düzeyi (L, M, Q, H)
    picture="resim.png",      # Arka plan resmi
    colorized=True,           # Renkli mi?
    contrast=1.0,             # Kontrast (Varsayılan 1.0)
    brightness=1.0,           # Parlaklık (Varsayılan 1.0)
    save_name="ozel_ad.png",  # Çıktı dosya adı
    save_dir=os.getcwd()      # Kayıt dizini
)
```

---

### C. Docker Üzerinden Kullanım
```bash
docker run -v $(pwd)/output:/app/output amazing-qr "https://github.com" -n test.png -d /app/output
```

---

## 4. Parametre Detayları

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

---

## 5. Önemli İpuçları ve Püf Noktaları

*   **Kare Resim Kullanın:** En iyi sonuç için arka plan resminiz kareye yakın olmalıdır. Dikdörtgen resimler otomatik olarak kareleştirilir.
*   **Versiyon Ayarı:** Eğer arka plan resminiz çok detaylı veya büyükse, `-v` değerini artırarak (örneğin 10 veya üzeri) QR kodun okunabilirliğini artırabilirsiniz.
*   **Şeffaflık (Transparency):** Şeffaf arka planlı resimler bazen okuma sorunlarına yol açabilir. Bu tür resimlerin arka planını beyaza çevirmek daha temiz bir sonuç verir.
*   **GIF Çıktısı:** Hareketli bir GIF kullanıyorsanız, çıktı dosya adını (`-n`) mutlaka `.gif` uzantısıyla bitirin.

---

## 6. Desteklenen Karakterler
QR kodun içine yazabileceğiniz karakterler:
*   Rakamlar: `0~9`
*   Harfler: `a~z, A~Z`
*   Semboller: `· , . : ; + - * / \ ~ ! @ # $ % ^ & ' = < > [ ] ( ) ? _ { } |` ve `boşluk`.

---

## 7. Çıktı ve Kayıt
Oluşturulan tüm QR kodlar, belirttiğiniz dizine (varsayılan olarak komutu çalıştırdığınız dizin) kaydedilir. Proje içinde bir `output/` klasörü varsa, Docker kullanımında çıktıları buraya yönlendirmeniz önerilir.

---

## 8. Proje Yapısı ve Çalışma Mantığı
Geliştiriciler için projenin iç yapısı şu şekildedir:

*   **`amzqr/`**: Ana paket dizini.
    *   `amzqr.py`: Çekirdek mantık, resim işleme ve QR birleştirme burada gerçekleşir.
    *   `terminal.py`: Komut satırı argümanlarını işleyen kısım.
    *   **`mylibs/`**: QR kodun temelini oluşturan alt kütüphaneler.
        *   `matrix.py`: QR matrisinin hesaplanması.
        *   `data.py`: Verinin kodlanması.
        *   `ECC.py`: Hata düzeltme (Error Correction) hesaplamaları.

### Nasıl Çalışır?
1.  **Veri Analizi:** Girdiğiniz metin analiz edilir ve uygun QR versiyonu seçilir.
2.  **Matris Oluşturma:** Metin, QR standartlarına göre bir bit matrisine dönüştürülür.
3.  **Resim İşleme:** Eğer bir arka plan resmi (`-p`) verdiyseniz, Pillow kütüphanesi kullanılarak resim boyutlandırılır ve kontrast/parlaklık ayarları uygulanır.
4.  **Birleştirme:** QR matrisi ile işlenen resim pikselleri birleştirilerek nihai sanatsal çıktı oluşturulur.

---

## 9. Sıkça Sorulan Sorular (SSS)

**S: Neden QR kodum okunmuyor?**
C: Arka plan resmi çok koyu veya çok karmaşık olabilir. `-con` ve `-bri` parametreleriyle oynayarak kontrastı artırmayı veya daha yüksek bir versiyon (`-v`) kullanmayı deneyin.

**S: Türkçe karakter desteği var mı?**
C: Standart QR karakter seti (alfanümerik) desteklenmektedir. Özel karakterler için çıktıları test etmeniz önerilir.

---
**Hazırlayan:** Antigravity (Yapay Zeka Asistanı)
