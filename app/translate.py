from deep_translator import GoogleTranslator

def en_to_tr(text):
    """İngilizce metni Türkçeye çevirir (Google Translate API)"""
    if not text:
        return ""
    try:
        # 5000 karakter sınırına karşı önlem
        text = text[:4999]
        return GoogleTranslator(source='en', target='tr').translate(text)
    except Exception as e:
        print(f"Çeviri hatası (EN->TR): {e}")
        return text # Çeviremezse orijinali döndür

def tr_to_en(text):
    """Türkçe metni İngilizceye çevirir (Google Translate API)"""
    if not text:
        return ""
    try:
        text = text[:4999]
        return GoogleTranslator(source='tr', target='en').translate(text)
    except Exception as e:
        print(f"Çeviri hatası (TR->EN): {e}")
        return text