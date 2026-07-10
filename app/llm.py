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

if not model.is_loaded:
    if not model.is_cached:
        print(
            f"Yapay zekâ modeli indiriliyor: {MODEL_NAME}. "
            "Bu işlem biraz sürebilir..."
        )
        model.download()

    model.load()

client = model.get_chat_client()

print("LLM Ready")


def ask_llm(prompt_text: str) -> str:
    if not prompt_text or not prompt_text.strip():
        raise ValueError("LLM prompt boş olamaz.")

    messages = [
        {
            "role": "user",
            "content": prompt_text.strip()
        }
    ]

    response = client.complete_chat(messages)

    if not response.choices:
        raise RuntimeError("Model herhangi bir cevap üretmedi.")

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Model boş cevap üretti.")

    return content