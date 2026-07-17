from foundry_local_sdk import Configuration, FoundryLocalManager

from app.config import APP_NAME, MODEL_NAME


print("Initializing Foundry Local...")

config = Configuration(app_name=APP_NAME)

try:
    FoundryLocalManager.initialize(config)
except Exception:
    # SDK zaten başlatılmış olabilir.
    pass

manager = FoundryLocalManager.instance

print("Loading model...")

model = manager.catalog.get_model(MODEL_NAME)

if model is None:
    model = manager.catalog.get_model("qwen3-1.7b")
    if model is None:
        raise ValueError("Kritik Hata: LLM modeli bulunamadı!")

client = model.get_chat_client()
if client is None:
    raise ValueError("Chat client alınamadı!")

print("LLM Initialized (Lazy Loading Ready)")


def ask_llm(prompt_text: str) -> str:
    if not prompt_text or not prompt_text.strip():
        raise ValueError("LLM prompt boş olamaz.")

    from app.config import SYSTEM_PROMPT
    
    # Lazy loading: Sadece çağrıldığında yükle
    if not model.is_loaded:
        if not model.is_cached:
            print("Yapay zekâ modeli indiriliyor...")
            model.download()
        model.load()
        
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.strip()
        },
        {
            "role": "user",
            "content": prompt_text.strip()
        }
    ]

    try:
        response_stream = client.complete_streaming_chat(messages)
        content = ""
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
    except Exception as e:
        if model.is_loaded:
            model.unload()
        raise e

    if not content:
        raise RuntimeError("Model boş cevap üretti.")

    # RAM'i sıradaki embedding araması için boşalt
    if model.is_loaded:
        model.unload()
        import time
        time.sleep(1.5) # VRAM'in temizlenmesini bekle

    return content