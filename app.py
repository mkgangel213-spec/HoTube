import os
import time
import uuid
import shutil
import logging
from urllib.parse import quote
from flask import Flask, render_template, request, jsonify, Response
import yt_dlp

# Flask Uygulaması Yapılandırması
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# İndirme Klasörü Yolu
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def clean_old_downloads():
    """Downloads klasöründeki 5 dakikadan eski geçici dosyaları temizler."""
    if not os.path.exists(DOWNLOAD_DIR):
        return
    now = time.time()
    deleted_count = 0
    for filename in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        try:
            # 5 dakikadan (300 saniye) eski dosyaları sil
            if os.path.isfile(file_path) and (now - os.path.getmtime(file_path) > 300):
                os.remove(file_path)
                deleted_count += 1
        except Exception as e:
            logger.error(f"Eski dosya silinirken hata olustu ({filename}): {e}")
    if deleted_count > 0:
        logger.info(f"{deleted_count} adet eski dosya temizlendi.")

def generate_and_cleanup(file_path):
    """Dosyayı parça parça okuyup gönderdikten sonra otomatik silen generator."""
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Gecici dosya silindi: {file_path}")
        except Exception as e:
            logger.error(f"Gecici dosya silinirken hata olustu ({file_path}): {e}")

@app.route('/')
def index():
    # Her ana sayfa yüklenmesinde eski dosyaları temizle
    clean_old_downloads()
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    # Eski dosyaları temizle
    clean_old_downloads()

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Lütfen geçerli bir YouTube bağlantısı girin.'}), 400

    url = data.get('url').strip()
    format_pref = data.get('format', 'mp4').strip().lower()

    if not url:
        return jsonify({'error': 'Bağlantı alanı boş olamaz.'}), 400

    if format_pref not in ['mp4', 'mp3', 'avi']:
        return jsonify({'error': 'Desteklenmeyen format seçimi.'}), 400

    # FFmpeg kontrolü
    ffmpeg_available = shutil.which("ffmpeg") is not None

    if not ffmpeg_available and format_pref in ['mp3', 'avi']:
        return jsonify({
            'error': f'Sunucuda FFmpeg kurulu olmadığı için {format_pref.upper()} dönüştürme işlemi gerçekleştirilemiyor. '
                     'Lütfen MP4 formatını deneyin veya sunucuya FFmpeg kurun.'
        }), 400

    # Benzersiz dosya adı öneki için UUID
    file_uuid = uuid.uuid4()
    
    # yt-dlp seçenekleri
   # İndirme ayarları
    ydl_opts = {
        'format': 'bestaudio/best' if format_pref == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}] if format_pref == 'mp3' else []
    }

    # Formata göre yt-dlp ayarlarını özelleştirme
    if format_pref == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif format_pref == 'avi':
        ydl_opts.update({
            'format': 'best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'avi',
            }],
        })
    else:  # MP4
        if ffmpeg_available:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })
        else:
            # FFmpeg yoksa, sadece hazır birleşik mp4 formatını indir
            ydl_opts.update({
                'format': 'best[ext=mp4]/best',
            })

    try:
        logger.info(f"Indirme baslatiliyor: URL={url}, Format={format_pref}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video bilgilerini al ve indir
            info_dict = ydl.extract_info(url, download=True)
            
            # Gerçek dosya yolunu belirle
            file_path = None
            if 'requested_downloads' in info_dict and len(info_dict['requested_downloads']) > 0:
                file_path = info_dict['requested_downloads'][0]['filepath']
            else:
                file_path = ydl.prepare_filename(info_dict)
                # Dönüşüm sonrası uzantı değişimini kontrol et
                if format_pref == 'mp3':
                    base, _ = os.path.splitext(file_path)
                    file_path = base + '.mp3'
                elif format_pref == 'avi':
                    base, _ = os.path.splitext(file_path)
                    file_path = base + '.avi'

            # Windows ve yt-dlp uyumluluğu için dosya yolunu doğrula
            if not os.path.exists(file_path):
                # UUID ile eşleşen dosyayı klasörde ara (postprocessor dosya adını değiştirdiyse)
                found = False
                for filename in os.listdir(DOWNLOAD_DIR):
                    if filename.startswith(str(file_uuid)):
                        file_path = os.path.join(DOWNLOAD_DIR, filename)
                        found = True
                        break
                if not found:
                    raise FileNotFoundError("İndirilen dosya sistemde bulunamadı.")

            logger.info(f"Indirme basarili: {file_path}")

            # Dosya adını temizleme (kullanıcıya gönderilecek ad)
            original_filename = os.path.basename(file_path)
            parts = original_filename.split('_', 1)
            clean_filename = parts[1] if len(parts) > 1 else original_filename

            # MIME type belirle
            mimetypes = {
                'mp3': 'audio/mpeg',
                'mp4': 'video/mp4',
                'avi': 'video/x-msvideo'
            }
            mimetype = mimetypes.get(format_pref, 'application/octet-stream')

            # UTF-8 dosya adı kodlaması (Türkçe karakterlerin bozulmaması için)
            encoded_filename = quote(clean_filename)

            # Dosyayı stream et ve bittiğinde sil
            response = Response(generate_and_cleanup(file_path), mimetype=mimetype)
            response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
            # Dosya boyutunu header olarak ekle
            try:
                response.headers["Content-Length"] = os.path.getsize(file_path)
            except:
                pass
            return response

    except Exception as e:
        logger.error(f"Indirme sirasinda hata olustu: {e}")
        # Hata durumunda oluşmuş olabilecek geçici dosyaları temizle
        try:
            for filename in os.listdir(DOWNLOAD_DIR):
                if filename.startswith(str(file_uuid)):
                    os.remove(os.path.join(DOWNLOAD_DIR, filename))
        except:
            pass
        return jsonify({'error': f'İndirme veya dönüştürme başarısız oldu: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
