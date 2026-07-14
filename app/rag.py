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

    # Remove repeated lines and 'Answer:' prefixes
    lines = text.strip().strip('"').split('\n')
    cleaned_lines = []
    seen = set()
    for line in lines:
        line_clean = line.strip()
        if line_clean.lower().startswith("answer:"):
            line_clean = line_clean[7:].strip()
        if line_clean.lower().startswith("cevap:"):
            line_clean = line_clean[6:].strip()
            
        if line_clean and line_clean not in seen:
            seen.add(line_clean)
            cleaned_lines.append(line_clean)

    return "\n".join(cleaned_lines).strip()


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
        chunk = doc["chunk"][:1000]

        context_parts.append(
            f"[INFORMATION {index}]\n{chunk}"
        )

    return "\n\n".join(context_parts)


def ask(question_tr: str, filter_type: str = "all") -> dict:
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

    # 2. Hem Türkçe hem İngilizce soruyla sektörel filtreyi kullanarak arama yapıyoruz
    docs_tr = retrieve(question=question_tr, top_k=TOP_K, minimum_similarity=MINIMUM_SIMILARITY, filter_type=filter_type)
    docs_en = retrieve(question=question_en, top_k=TOP_K, minimum_similarity=MINIMUM_SIMILARITY, filter_type=filter_type)

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
3. Do not use outside knowledge and do not invent policies, dates, prices, conditions or procedures.
4. CRITICAL: If the DOCUMENT CONTEXT does not contain the answer, you MUST NOT explain what the documents contain or try to be helpful. You MUST reply with ONLY this exact phrase and nothing else:
   "{NOT_FOUND_EN}"
5. Do not show your reasoning or use <think> tags.
6. Keep the answer concise, polite and customer-service friendly.
7. Provide ONLY the final answer text. Do not repeat the question, do not repeat yourself, and do not use prefixes like "Answer:".
8. If the DOCUMENT CONTEXT contains an ASIN or Image URL for a product, you MUST include a markdown image `![Product Image](Image URL)` and a link `[Buy on Amazon](https://www.amazon.com/dp/ASIN)` at the very end of your answer.

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