from foundry_local_sdk import Configuration, FoundryLocalManager

from app.config import APP_NAME, MODEL_NAME


print("Initializing Foundry Local...")

config = Configuration(
    app_name=APP_NAME,
    additional_settings={"ExecutionProvider": "GPU"}
)

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


def ask_llm(system_prompt: str, user_prompt: str):
    if not user_prompt or not user_prompt.strip():
        raise ValueError("LLM prompt boş olamaz.")
    
    # Lazy loading: Sadece çağrıldığında yükle
    if not model.is_loaded:
        if not model.is_cached:
            print("Yapay zekâ modeli indiriliyor...")
            model.download()
        model.load()
        
    messages = [
        {
            "role": "system",
            "content": system_prompt.strip()
        },
        {
            "role": "user",
            "content": user_prompt.strip()
        }
    ]

    try:
        response_stream = client.complete_streaming_chat(messages)
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        if model.is_loaded:
            model.unload()
        raise e

    # RAM'i sıradaki embedding araması için boşalt
    if model.is_loaded:
        model.unload()
        import time
        time.sleep(1.5) # VRAM'in temizlenmesini bekle