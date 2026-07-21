from app.llm import ask_llm

def tr_to_en(text):
    """Kullanıcının Türkçe sorusunu arama yapmak için İngilizceye çevirir."""
    if not text:
        return ""
    
    system_instruction = "You are a direct translator. Translate the given Turkish text to English. Output ONLY the English translation, no other text."
    user_prompt = f"Turkish Text: {text}\nEnglish Translation:"
    
    response_stream = ask_llm(system_instruction, user_prompt)
    
    full_en = ""
    for token in response_stream:
        # Think tag filtering logic (if model is phi-3 or reasoning model)
        if "<think>" in token or "</think>" in token:
            continue
        full_en += token
        
    return full_en.strip()
