from app.llm import ask_llm
from app.retrieve import retrieve
from app.translate import tr_to_en, en_to_tr
from app.memory import add_to_memory


NOT_FOUND_EN = "I couldn't find this information in the provided documents."
NOT_FOUND_TR = "Bu bilgi verilen belgelerde bulunamadı."


def clean_answer(text: str) -> str:
    if not text:
        return ""

    if "</think>" in text:
        text = text.split("</think>", 1)[1]

    return text.strip().strip('"')


def is_small_talk(question: str) -> bool:
    normalized_question = question.lower().strip()

    greetings = {
        "merhaba",
        "selam",
        "hello",
        "hi",
        "hey",
        "naber",
        "nasılsın"
    }

    return normalized_question in greetings


def build_turkish_context(docs: list[dict]) -> str:
    context_parts = []

    for index, doc in enumerate(docs, start=1):
        source = doc["source"]
        chunk = doc["chunk"][:1000]

        context_parts.append(
            f"[SOURCE {index}: {source}]\n{chunk}"
        )

    return "\n\n".join(context_parts)


def ask(question_tr: str) -> dict:
    question_tr = question_tr.strip()

    if is_small_talk(question_tr):
        answer_en = (
            "Hello! I am your Amazon Customer Experience and FAQ "
            "Assistant. How can I help you?"
        )

        answer_tr = (
            "Merhaba! Ben Amazon Müşteri Deneyimi ve SSS "
            "Asistanıyım. Size nasıl yardımcı olabilirim?"
        )

        return {
            "answer_en": answer_en,
            "answer_tr": answer_tr,
            "sources": []
        }

    # 1. Retrieval Türkçe soru üzerinden yapılır.
    docs = retrieve(
        question=question_tr,
        top_k=3,
        minimum_similarity=0.30
    )

    if not docs:
        return {
            "answer_en": NOT_FOUND_EN,
            "answer_tr": NOT_FOUND_TR,
            "sources": []
        }

    # 2. Bulunan Türkçe bağlam hazırlanır.
    context_tr = build_turkish_context(docs)

    try:
        # 3. Soru İngilizceye çevrilir.
        question_en = tr_to_en(question_tr)

        # 4. Sadece bulunan bağlam İngilizceye çevrilir.
        context_en = tr_to_en(context_tr)

    except Exception as error:
        print("Translation to English error:", error)

        return {
            "answer_en": NOT_FOUND_EN,
            "answer_tr": (
                "Soru işlenirken çeviri hatası oluştu. "
                "Lütfen tekrar deneyin."
            ),
            "sources": []
        }

    prompt = f"""
You are an Amazon Customer Experience and FAQ Assistant.

Your task is to answer the user's question using only the supplied
document context.

STRICT RULES:

1. Answer only in English.
2. Use only information explicitly present in the context.
3. Do not use outside knowledge.
4. Do not invent policies, dates, prices, conditions or procedures.
5. If the context does not contain enough information, return exactly:
   "{NOT_FOUND_EN}"
6. Do not show your reasoning.
7. Do not use <think> tags.
8. Keep the answer concise, polite and customer-service friendly.
9. Do not mention information from an unrelated source.
10. Do not include a source unless it supports the answer.

DOCUMENT CONTEXT:
{context_en}

USER QUESTION:
{question_en}

ENGLISH ANSWER:
"""

    try:
        # 5. İngilizce cevap üretilir.
        answer_en = clean_answer(ask_llm(prompt))

        if not answer_en:
            answer_en = NOT_FOUND_EN

    except Exception as error:
        print("LLM error:", error)
        answer_en = NOT_FOUND_EN

    try:
        # 6. İngilizce cevap Türkçeye çevrilir.
        answer_tr = clean_answer(en_to_tr(answer_en))

    except Exception as error:
        print("Translation to Turkish error:", error)
        answer_tr = NOT_FOUND_TR

    # Aynı kaynakları tekrar etmeden sırasını korur.
    sources = list(
        dict.fromkeys(doc["source"] for doc in docs)
    )

    add_to_memory(question_tr, answer_tr)

    return {
        "question_en": question_en,
        "answer_en": answer_en,
        "answer_tr": answer_tr,
        "sources": sources,
        "retrieved_documents": docs
    }