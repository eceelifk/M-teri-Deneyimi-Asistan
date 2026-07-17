# Microsoft Staj Programı - Aşama 1: Yerel RAG Asistanı

Bu proje, Microsoft 40 Günlük Proje Tabanlı Staj Programının **Aşama 1 (Gün 1-20)** görevi kapsamında geliştirilmiştir. Amacı, internet bağlantısına ihtiyaç duymadan, yerel belgeleri kaynak olarak kullanarak soruları yanıtlayan bir Retrieval-Augmented Generation (RAG) Soru-Cevap (Q&A) asistanı oluşturmaktır.

## 🚀 Proje Hakkında
Bu uygulamada, örnek senaryo olarak bir "Amazon Müşteri Deneyimi ve SSS Asistanı" tasarlanmıştır. Asistan, müşteri hizmetleri politikalarını ve ürün yorumlarını (PDF belgelerinden okuyarak) analiz edip soruları yanıtlar. Tamamen çevrimdışı ve gizlilik odaklı çalışır.

### Temel Teknolojiler ve Sistem Mimarisi
Proje, staj yönergesindeki gereksinimlere birebir uyacak şekilde aşağıdaki mimariyle tasarlanmıştır:
* **Microsoft Foundry Local:** Hem yerel LLM (Büyük Dil Modeli) çıkarımı hem de metinlerin sayısal vektörlere dönüştürülmesi (embedding) işlemleri için ana motor olarak kullanılmıştır. Bulut API'si gerektirmez.
* **RAG (Retrieval-Augmented Generation):** Kullanıcı sorularına cevap üretilirken halüsinasyonu (yanlış bilgi uydurmayı) engellemek için kullanılır. Soru geldiğinde önce yerel veritabanındaki PDF parçaları bulunur, modele "Sadece bu metinlere dayanarak cevap ver" denir.
* **SQLite:** Vektör veritabanı çözümü olarak kullanılmıştır. Dokümanlardan ayrıştırılan her bir parça (chunk) ve bu parçanın Foundry Local ile çıkarılan embedding vektörü, sunucusuz ve hafif bir dosya (`rag.db`) içerisinde yerel olarak saklanmaktadır.
* **Streamlit:** Proje yönergesindeki "Seçenek B (Orta Düzey Web Arayüzü)" kapsamını karşılamak üzere kullanıcı dostu, Amazon temalı bir sohbet arayüzü olarak kodlanmıştır.

## ⚙️ Kurulum ve Çalıştırma Adımları

1. Gerekli Python bağımlılıklarını yükleyin:
```bash
pip install -r requirements.txt
```

2. Microsoft Foundry Local altyapısının bilgisayarınızda kurulu ve çalışır durumda olduğundan emin olun.

3. Belgeleri işlemek, vektörlere çevirmek ve SQLite veritabanına kaydetmek için (Doküman Alımı Hattı):
```bash
python ingest.py
```
*(Not: Çok büyük dokümanlarda kesinti yaşanırsa işleme kaldığı yerden devam etmek için `python resume_ingest.py` kullanılabilir.)*

4. Hazır olan asistan arayüzünü ayağa kaldırmak için:
```bash
streamlit run streamlit_app.py
```

## 🧠 İstem Mühendisliği ve Sınırlandırmalar
Projedeki yapay zeka modeli (LLM), özel istem tasarımıyla (prompt engineering) kısıtlanmıştır:
- Modelin dış dünyadaki kendi genel bilgisini kullanması yasaklanmış, yalnızca getirilen (retrieved) doküman bağlamına sadık kalması sağlanmıştır.
- Kaynak dokümanlarda bulunmayan veya alakasız sorularda modelin zorlanıp yalan bilgi üretmesini engellemek için **"Bunun hakkında bir bilgi bulunamadı."** (veya İngilizce karşılığı) cevabını verme şartı koşulmuştur. (Staj yönergesindeki test kriterini tam karşılar).
