# HoTube - Video & Audio Downloader

HoTube, YouTube videolarını MP4, MP3 (sadece ses) veya AVI formatlarında kolayca indirmenizi sağlayan modern, hızlı ve şık bir web uygulamasıdır. Koyu tema (Dark Mode) ve Glassmorphism (buzlu cam efekti) ile zenginleştirilmiş premium bir arayüze sahiptir.

## Klasör Yapısı

```text
hotube/
├── app.py                   # Flask Sunucu ve İndirme Mantığı
├── requirements.txt         # Gerekli Python Kütüphaneleri
├── .gitignore               # Versiyon Kontrolü Hariç Tutma Listesi
├── README.md                # Kurulum ve Çalıştırma Kılavuzu
├── templates/
│   └── index.html           # Arayüz Şablonu
└── static/
    ├── css/
    │   └── style.css        # Glassmorphic Stil Dosyası
    └── js/
        └── main.js          # Arayüz ve İndirme İstekleri Logic Dosyası
```

## Gereksinimler

1. **Python**: Bilgisayarınızda Python 3.8 veya üzeri bir sürümün kurulu olduğundan emin olun.
2. **FFmpeg**: MP3 ses dönüştürme ve AVI formatında indirme yapabilmek için sisteminizde **FFmpeg** yüklü olmalı ve sistem `PATH` değişkenine eklenmiş olmalıdır.

### FFmpeg Nasıl Kurulur? (Windows)

1. [ffmpeg.org](https://ffmpeg.org/download.html) adresinden Windows için derlenmiş zip dosyasını indirin.
2. Zip içerisindeki klasörleri `C:\ffmpeg` gibi kolay bir konuma çıkartın.
3. `C:\ffmpeg\bin` klasör yolunu Windows **Ortam Değişkenleri (Environment Variables) -> PATH** değişkenine ekleyin.
4. Kurulumu doğrulamak için PowerShell veya Komut İstemi'ni açıp şu komutu çalıştırın:
   ```bash
   ffmpeg -version
   ```
   Eğer sürüm bilgileri ekrana geliyorsa kurulum başarıyla tamamlanmıştır.

---

## Kurulum ve Çalıştırma

### 1. Sanal Ortam Oluşturma ve Aktifleştirme

Proje klasörünün içine girin ve bir sanal ortam oluşturun:

```bash
# Sanal Ortam Oluşturma
python -m venv venv

# Sanal Ortamı Aktifleştirme (PowerShell)
.\venv\Scripts\Activate.ps1

# Sanal Ortamı Aktifleştirme (CMD / Komut İstemi)
.\venv\Scripts\activate.bat
```

### 2. Bağımlılıkları Yükleme

Gerekli olan Flask ve yt-dlp kütüphanelerini yükleyin:

```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Başlatma

Flask sunucusunu ayağa kaldırın:

```bash
python app.py
```

Uygulama varsayılan olarak **`http://127.0.0.1:5000`** adresinde çalışmaya başlayacaktır. Tarayıcınızdan bu adrese giderek HoTube'u kullanmaya başlayabilirsiniz!

## Önemli Notlar

- İndirilen dosyalar geçici olarak `downloads/` klasöründe tutulur ve kullanıcıya iletildikten hemen sonra otomatik olarak silinir.
- Sunucu her istekte veya başlangıçta 5 dakikadan eski kalmış olabilecek geçici dosyaları otomatik olarak tarar ve temizler.
- FFmpeg kurulu olmasa dahi **MP4** formatında video indirme işlemi başarıyla çalışacaktır.
