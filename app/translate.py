from deep_translator import GoogleTranslator

def tr_to_en(text):
    """Kullanıcının Türkçe sorusunu arama yapmak için İngilizceye çevirir."""
    if not text:
        return ""
    
    try:
        return GoogleTranslator(source='tr', target='en').translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        # Hata olursa orijinal metni döndür (RAG şansını dener)
        return text
