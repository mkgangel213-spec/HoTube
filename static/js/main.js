document.addEventListener('DOMContentLoaded', () => {
    const downloadForm = document.getElementById('download-form');
    const urlInput = document.getElementById('url-input');
    const downloadBtn = document.getElementById('download-btn');
    const loadingState = document.getElementById('loading-state');
    const messageBox = document.getElementById('message-box');
    const messageText = document.getElementById('message-text');
    const messageIcon = document.getElementById('message-icon');
    const closeMsgBtn = document.getElementById('close-msg-btn');

    // Hata veya bilgi mesajı gösteren fonksiyon
    function showMessage(message, type = 'error') {
        messageText.textContent = message;
        messageBox.classList.remove('hidden', 'success');
        
        if (type === 'success') {
            messageBox.classList.add('success');
            messageIcon.textContent = '✅';
        } else {
            messageIcon.textContent = '⚠️';
        }
    }

    // Mesaj kutusunu kapatma
    closeMsgBtn.addEventListener('click', () => {
        messageBox.classList.add('hidden');
    });

    // Form Gönderimi
    downloadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Önceki mesajı temizle
        messageBox.classList.add('hidden');

        const url = urlInput.value.trim();
        const selectedFormatEl = document.querySelector('input[name="format"]:checked');
        const format = selectedFormatEl ? selectedFormatEl.value : 'mp4';

        if (!url) {
            showMessage('Lütfen geçerli bir YouTube bağlantısı girin.');
            return;
        }

        // Arayüz durumunu güncelle (Formu gizle, loader'ı göster)
        downloadForm.style.opacity = '0.3';
        downloadForm.style.pointerEvents = 'none';
        downloadBtn.disabled = true;
        loadingState.classList.remove('hidden');

        try {
            // Sunucuya indirme isteği gönder
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, format }),
            });

            // Yanıt başarılı değilse hatayı yakala
            if (!response.ok) {
                let errorMessage = 'İndirme veya dönüştürme sırasında bir hata oluştu.';
                try {
                    const errorJson = await response.json();
                    if (errorJson && errorJson.error) {
                        errorMessage = errorJson.error;
                    }
                } catch (e) {
                    // Yanıt JSON değilse (örneğin düz metin hatası)
                }
                throw new Error(errorMessage);
            }

            // Dosya indirme başlığını oku
            const disposition = response.headers.get('content-disposition');
            let filename = `hotube_download_${Date.now()}.${format}`;
            
            if (disposition && disposition.indexOf('attachment') !== -1) {
                // UTF-8 kodlanmış dosya adını al (Türkçe karakterler için)
                const filenameRegex = /filename\*=UTF-8''([^;'\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) { 
                    filename = decodeURIComponent(matches[1]);
                } else {
                    // Fallback
                    const fallbackRegex = /filename="?([^;_\n"]*)"?/;
                    const fallbackMatches = fallbackRegex.exec(disposition);
                    if (fallbackMatches != null && fallbackMatches[1]) {
                        filename = fallbackMatches[1];
                    }
                }
            }

            // Dosyayı Blob olarak al ve indirmeyi başlat
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            
            // Temizlik işlemleri
            window.URL.revokeObjectURL(downloadUrl);
            a.remove();

            // Başarılı durumu arayüzde göster
            showMessage('Dönüştürme tamamlandı ve indirme başlatıldı!', 'success');
            urlInput.value = ''; // Link alanını temizle

        } catch (error) {
            console.error(error);
            showMessage(error.message || 'Bir hata oluştu. Lütfen bağlantıyı ve internetinizi kontrol edip tekrar deneyin.');
        } finally {
            // Arayüz durumunu eski haline getir
            downloadForm.style.opacity = '1';
            downloadForm.style.pointerEvents = 'auto';
            downloadBtn.disabled = false;
            loadingState.classList.add('hidden');
        }
    });
});
