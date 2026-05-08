# Amazing-QR Proje Dosyaları Açıklaması

Bu belge, Amazing-QR projesindeki temel Python dosyalarının işlevlerini ve projenin çalışma mantığını Türkçe olarak açıklamaktadır.

## Ana Dizin Dosyaları

### [amzqr.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr.py)
Projenin kök dizininde bulunan bu dosya, paket henüz sisteme yüklenmemişken (`pip install` ile kurulmadan önce) projenin doğrudan çalıştırılabilmesini sağlayan bir aracı (wrapper) dosyadır. `amzqr.terminal` içerisindeki `main` fonksiyonunu çağırarak terminal üzerinden komut almasını sağlar.

### [setup.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/setup.py)
Bu dosya, projenin bir Python paketi olarak kurulabilmesi için gereken yapılandırma dosyasıdır. Paket adı, versiyonu, bağımlılıkları (Pillow, imageio, numpy gibi) ve terminal komutu olarak `amzqr` isminin tanımlanması gibi bilgileri içerir.

---

## `amzqr/` Dizini (Ana Paket)

### [amzqr/__init__.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/__init__.py)
Bu dosya, `amzqr` dizininin bir Python paketi olarak tanınmasını sağlar. İçeriği boştur ancak Python'un bu klasörü modül olarak içe aktarabilmesi için gereklidir.

### [amzqr/terminal.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/terminal.py)
Kullanıcının terminal (komut satırı) üzerinden verdiği argümanları (`-v` versiyon, `-l` hata düzeltme seviyesi, `-p` resim yolu vb.) `argparse` kütüphanesi ile işleyen dosyadır. Kullanıcıdan gelen verileri temizler ve işlenmek üzere `amzqr/amzqr.py` içerisindeki `run` fonksiyonuna iletir.

### [amzqr/amzqr.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/amzqr.py)
Projenin ana mantığını barındıran dosyadır. `run` fonksiyonu burada tanımlıdır. QR kod oluşturma sürecini yönetir; eğer kullanıcı bir arka plan resmi veya GIF verdiyse, QR kodunu bu resimle birleştirme (combine) işlemini gerçekleştirir. Kontrast ve parlaklık ayarları da burada yapılır.

---

## `amzqr/mylibs/` Dizini (Kütüphane Katmanı)

Bu dizin, QR kodunun standartlara uygun olarak adım adım oluşturulmasını sağlayan alt modülleri içerir.

### [amzqr/mylibs/__init__.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/mylibs/__init__.py)
`mylibs` klasörünün bir Python alt paketi olarak kullanılmasını sağlar.

### [amzqr/mylibs/theqrmodule.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/mylibs/theqrmodule.py)
QR kod üretim sürecini koordine eden "orkestra şefi" modülüdür. Veri kodlama, hata düzeltme, matris oluşturma ve çizim adımlarını sırasıyla çağırır.

### [amzqr/mylibs/data.py](file:///mnt/sacamole/orion-backup-local/projects/amazing-qr/amzqr/mylibs/data.py)
Kullanıcının girdiği metni (URL, kelime vb.) QR standartlarına göre ikili (binary) verilere dönüştürür. Sayısal, alfanümerik veya bayt modlarından hangisinin kullanılacağına karar verir.

### [amzqr/mylibs/ECC.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/mylibs/ECC.py)
**Error Correction Coding (Hata Düzeltme Kodlaması)** işlemlerini yapar. QR kodunun bir kısmı hasar görse bile okunabilmesini sağlayan Reed-Solomon hata düzeltme baytlarını üretir.

### [amzqr/mylibs/structure.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/mylibs/structure.py)
Kodlanmış verileri ve hata düzeltme baytlarını uygun sırada birbirine ekler (interleaving işlemi) ve matris yerleşimi için son bit dizisini hazırlar.

### [amzqr/mylibs/matrix.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/mylibs/matrix.py)
QR kodunun 2 boyutlu matris (ızgara) yapısını oluşturur. İçerisinde şu özellikleri barındırır:
- Bulucu desenler (Finder Patterns - köşelerdeki büyük kareler)
- Zamanlama desenleri (Timing Patterns)
- Hizalama desenleri (Alignment Patterns)
- Veri maskeleme (okunabilirliği artırmak için uygulanan desenler)

### [amzqr/mylibs/draw.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/mylibs/draw.py)
Oluşturulan matris yapısını fiziksel bir resim dosyasına (`.png`) dönüştürür. `Pillow (PIL)` kütüphanesini kullanarak siyah-beyaz kareleri çizer.

### [amzqr/mylibs/constant.py](file:///mnt/samsung/orion-backup-local/projects/amazing-qr/amzqr/mylibs/constant.py)
QR kod standartlarına ait tüm sabit verileri (tablolar, hata düzeltme kapasiteleri, maskeleme formülleri vb.) içeren devasa bir sözlük/liste dosyasıdır. Diğer tüm modüller bu verileri referans alır.

---

## Özet Çalışma Akışı
1. **Giriş:** `terminal.py` veya `amzqr.py` üzerinden kullanıcı girdileri alınır.
2. **Kodlama:** `data.py` metni bitlere dönüştürür.
3. **Güvenlik:** `ECC.py` hata düzeltme katmanlarını ekler.
4. **Yapılandırma:** `structure.py` ve `matrix.py` bu verileri 2 boyutlu bir ızgaraya yerleştirir.
5. **Görselleştirme:** `draw.py` temel QR resmini çizer.
6. **Birleştirme:** (Opsiyonel) `amzqr/amzqr.py` bu QR kodunu kullanıcıdan gelen resim veya GIF ile harmanlar.
7. **Çıkış:** Sonuç dosyası kaydedilir.
