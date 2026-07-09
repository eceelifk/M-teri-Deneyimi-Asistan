from foundry_local_sdk import Configuration, FoundryLocalManager

print("Initializing Foundry Local...")

config = Configuration(
    app_name="AmazonCustomerSupportAI"
)

try:
    FoundryLocalManager.initialize(config)
except Exception:
    pass

manager = FoundryLocalManager.instance

print("Loading model...")

MODEL_NAME = "qwen3-1.7b"
model = manager.catalog.get_model(MODEL_NAME)

if not model.is_loaded:
    if not model.is_cached:
        print("Yapay Zeka Modeli indiriliyor (1.7B, bu islem biraz surebilir)...")
        model.download()
    model.load()

client = model.get_chat_client()

print("LLM Ready")


def ask_llm(prompt_text: str):
    messages = [
        {
            "role": "user",
            "content": prompt_text
        }
    ]

    response = client.complete_chat(messages)
    return response.choices[0].message.content