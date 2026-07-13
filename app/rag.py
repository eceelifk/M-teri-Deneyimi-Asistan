from app.llm import ask_llm
from app.retrieve import retrieve
from app.translate import tr_to_en, en_to_tr
from app.memory import add_to_memory
from app.config import TOP_K, MINIMUM_SIMILARITY


NOT_FOUND_EN = "No information was found about this."
NOT_FOUND_TR = "Bunun hakkında bir bilgi bulunamadı."


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

    try:
        # 1. Soruyu hemen İngilizceye çeviriyoruz (İngilizce yorumları bulabilmek için)
        question_en = tr_to_en(question_tr)
    except Exception as error:
        print("Translation to English error:", error)
        question_en = question_tr

    # 2. Hem Türkçe hem İngilizce soruyla vektör araması yapıyoruz
    # Türkçe soru Türkçe SSS'leri (FAQ), İngilizce soru İngilizce CSV yorumlarını bulacak.
    docs_tr = retrieve(question=question_tr, top_k=TOP_K, minimum_similarity=MINIMUM_SIMILARITY)
    docs_en = retrieve(question=question_en, top_k=TOP_K, minimum_similarity=MINIMUM_SIMILARITY)

    # İki dildeki sonuçları birleştir (aynı olanları filtrele)
    seen = set()
    docs = []
    for d in docs_tr + docs_en:
        if d["chunk"] not in seen:
            seen.add(d["chunk"])
            docs.append(d)

    if not docs:
        return {
            "answer_en": NOT_FOUND_EN,
            "answer_tr": NOT_FOUND_TR,
            "sources": []
        }

    # 3. Bulunan karışık bağlam (context) hazırlanır.
    context_mixed = build_turkish_context(docs)

    try:
        # 4. Tüm bağlam LLM'in anlaması için İngilizceye çevrilir (Zaten İngilizce olanlar etkilenmez)
        context_en = tr_to_en(context_mixed)
    except Exception as error:
        print("Translation context error:", error)
        context_en = context_mixed

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
2. Use only information explicitly present in the DOCUMENT CONTEXT.
3. Cite the source files you used by appending the source names in parentheses at the end of your sentences (e.g., (mock_orders.txt)). You can find the source names in the [SOURCE X: source_name] tags.
4. Do not use outside knowledge.
5. Do not invent policies, dates, prices, conditions or procedures.
6. CRITICAL: If the DOCUMENT CONTEXT does not contain the answer, you MUST NOT explain what the documents contain or try to be helpful. You MUST reply with ONLY this exact phrase and nothing else:
   "{NOT_FOUND_EN}"
7. Do not show your reasoning or use <think> tags.
8. Keep the answer concise, polite and customer-service friendly.
9. If the DOCUMENT CONTEXT contains an ASIN or Image URL for a product, you MUST include a markdown image `![Product Image](Image URL)` and a link `[Buy on Amazon](https://www.amazon.com/dp/ASIN)` at the very end of your answer.

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