from app.retrieve import retrieve
from app.llm import ask_llm
from app.translate import en_to_tr

def clean_answer(text):
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    return text.strip().strip('"')

def is_small_talk(question):
    q = question.lower().strip()
    greetings = ["merhaba", "selam", "hello", "hi", "naber", "nasılsın"]
    return any(g == q or g in q for g in greetings)

def ask(question_tr):
    if is_small_talk(question_tr):
        return {
            "answer_en": "Hello! I am your Amazon Customer Experience and FAQ Assistant. How can I help you?",
            "answer_tr": "Merhaba! Ben Amazon müşteri deneyimi ve SSS asistanıyım. Size nasıl yardımcı olabilirim?",
            "sources": []
        }

    docs = retrieve(question_tr, top_k=3)

    if len(docs) == 0:
        return {
            "answer_en": "I couldn't find the exact information, but I recommend contacting Amazon customer service or checking the Help pages for more details.",
            "answer_tr": "Belgelerimde buna dair kesin bir bilgi bulamadım ancak en doğru destek için Amazon Müşteri Hizmetleri ile iletişime geçmenizi önerebilirim.",
            "sources": []
        }

    context = "\n\n".join(doc["chunk"][:700] for doc in docs)

    prompt = f"""
You are an Amazon Customer Experience Assistant.

Use ONLY the CONTEXT below.
The context may be Turkish.
First answer in English.

If the exact answer to the user's question is not directly available in the context, do NOT say "not found in documents". Instead, provide the closest helpful recommendation or related information from the context. Always try to be helpful and guiding.
Do not use your own knowledge outside of general customer service etiquette.
Do not show reasoning.
Do not use <think>.
Keep the answer short and customer-service friendly.

CONTEXT:
{context}

USER QUESTION:
{question_tr}

ENGLISH ANSWER:
"""

    try:
        answer_en = clean_answer(ask_llm(prompt))
    except Exception as e:
        print("LLM error:", e)
        answer_en = "I couldn't find this information in the provided documents."

    try:
        answer_tr = clean_answer(en_to_tr(answer_en))
    except Exception as e:
        print("Translate error:", e)
        answer_tr = "Bu bilgi verilen belgelerde bulunamadı."

    return {
        "answer_en": answer_en,
        "answer_tr": answer_tr,
        "sources": list(set(doc["source"] for doc in docs))
    }