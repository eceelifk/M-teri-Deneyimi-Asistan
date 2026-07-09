from foundry_local_sdk import Configuration, FoundryLocalManager

SYSTEM_PROMPT = """
You are an Amazon Customer Experience & FAQ Assistant.

Rules:

- Always answer in English.
- Use ONLY the provided CONTEXT.
- Never use your own knowledge.
- If the answer cannot be found in the context,
  reply:

"I couldn't find this information in the provided documents."

- Keep answers short.
- Be polite.
"""
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

model.load()

client = model.get_chat_client()

print("LLM Ready")


def ask_llm(question: str):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = client.complete_chat(messages)
    return response.choices[0].message.content