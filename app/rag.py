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
        chunk = doc["chunk"][:400]

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

    from app.embedding import unload_embedding
    
    try:
        # Doğrudan Türkçe soru ile vektör araması yapıyoruz
        import time
        docs = retrieve(question=question_tr, top_k=TOP_K, minimum_similarity=MINIMUM_SIMILARITY, filter_type=filter_type)
        unload_embedding()
        time.sleep(1.5) # VRAM'in boşaltılmasına zaman tanıyoruz
    except Exception as error:
        print("Retrieval error:", error)
        docs = []

    if not docs:
        return {
            "answer_en": NOT_FOUND_EN,
            "answer_tr": NOT_FOUND_TR,
            "sources": []
        }

    # 3. Bulunan bağlam (context) hazırlanır.
    context_tr = build_turkish_context(docs)

    prompt = f"""
Sen Amazon Müşteri Deneyimi ve SSS Asistanısın.

GÖREVİN:
Kullanıcının sorusunu SADECE aşağıdaki BELGE BAĞLAMI'nda (DOCUMENT CONTEXT) yer alan bilgilere dayanarak cevaplamaktır.

KURALLAR:
1. Sadece Türkçe cevap ver.
2. Kibar, net ve müşteri hizmetleri diline uygun ol.
3. KESİNLİKLE kendi genel bilgini kullanma, sadece metinde geçen bilgileri kullanarak cevapla.
4. Eğer sorunun cevabı metinde HİÇ YOKSA, uydurmaya çalışma ve sadece şu cümleyi yaz: "{NOT_FOUND_TR}"
5. Kısa ve öz cevap ver, gereksiz tekrarlardan kaçın.

BELGE BAĞLAMI:
{context_tr}

MÜŞTERİ SORUSU:
{question_tr}

CEVAP:
"""

    try:
        # 5. Modelden doğrudan Türkçe cevap üretilir.
        answer_tr = clean_answer(ask_llm(prompt))

        if not answer_tr:
            answer_tr = NOT_FOUND_TR

    except Exception as error:
        print("LLM error:", error)
        answer_tr = f"LLM Hatası: {error}"

    # Aynı kaynakları tekrar etmeden sırasını korur.
    sources = list(
        dict.fromkeys(doc["source"] for doc in docs)
    )

    add_to_memory(question_tr, answer_tr)

    return {
        "question_en": "",
        "answer_en": "",
        "answer_tr": answer_tr,
        "sources": sources,
        "retrieved_documents": docs
    }