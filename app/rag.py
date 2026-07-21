from app.llm import ask_llm
from app.retrieve import retrieve
from app.translate import tr_to_en
from app.memory import add_to_memory
from app.config import TOP_K, MINIMUM_SIMILARITY


NOT_FOUND_TR = "Bunun hakkında bir bilgi bulunamadı."


def get_simulated_stream(text):
    import time
    for char in text:
        yield char
        time.sleep(0.005)

def is_small_talk(question: str) -> bool:
    normalized_question = question.lower().strip()
    greetings = {"merhaba", "selam", "hello", "hi", "hey", "naber", "nasılsın"}
    return normalized_question in greetings


def build_context(docs: list[dict]) -> str:
    context_parts = []
    for index, doc in enumerate(docs, start=1):
        chunk = doc["chunk"]
        context_parts.append(f"[INFORMATION {index}]\n{chunk}")
    return "\n\n".join(context_parts)

def ask(question_tr: str, filter_type: str = "all") -> dict:
    question_tr = question_tr.strip()

    if is_small_talk(question_tr):
        answer_tr = "Merhaba! Ben Amazon Müşteri Deneyimi ve SSS Danışmanıyım. Size nasıl yardımcı olabilirim?"
        return {"answer_stream": get_simulated_stream(answer_tr), "sources": []}

    from app.embedding import unload_embedding
    from app.memory import chat_history
    
    # Context-aware retrieval: if we have history, prepend the last question to the search query
    # to help the vector database find the right product when user says "this product"
    search_context = ""
    if chat_history:
        last_q = chat_history[-1]["user"]
        search_context = f"{last_q} "
        
    # Translate Turkish query to English for DB search
    english_query = tr_to_en(search_context + question_tr)
    
    import re
    asin_match = re.search(r'\b([B0-9][A-Z0-9]{9})\b', search_context + question_tr)
    detected_asin = asin_match.group(1) if asin_match else ""

    try:
        docs = retrieve(question=english_query, top_k=TOP_K, minimum_similarity=MINIMUM_SIMILARITY, filter_type=filter_type, asin=detected_asin)
        unload_embedding()
    except Exception as error:
        print("Retrieval error:", error)
        docs = []

    if not docs:
        return {
            "answer_stream": get_simulated_stream(NOT_FOUND_TR),
            "sources": []
        }

    context = build_context(docs)

    from app.memory import get_memory_text
    memory_context = get_memory_text()

    # ASIN is already extracted above as detected_asin

    if filter_type == "review":
        system_instruction = f"""Sen bir Amazon Müşteri Deneyimi Danışmanısın.
GÖREVİN: Kullanıcının sorusunu SADECE verilen İngilizce BELGE BAĞLAMI'na dayanarak **TÜRKÇE** ve **ÇOK KISA** cevaplamaktır.

KURALLAR:
1. Kısa ve net ol. Asla soruyu tekrar etme, doğrudan cevaba geç. Uzun açıklamalar yapma.
2. SADECE bağlamdaki bilgileri kullan. Bağlamda yoksa uydurma.
3. Cevabın MUTLAKA TÜRKÇE olmalıdır.
4. ASIN kodu varsa veya istenirse link ekle: [Ürünü İncele](https://www.amazon.com.tr/dp/ASIN_KODU) ve ![Görsel](https://ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=ASIN_KODU&Format=_SL250_&ID=AsinImage&MarketPlace=US&ServiceVersion=20070822&WS=1)
5. Sorunun cevabı bağlamda YOKSA, uydurma. Sadece şunu yaz: "{NOT_FOUND_TR}" """
        user_prompt = f"Bağlam:\n{context}\n\nSoru: {question_tr}"
    else:
        system_instruction = f"""Sen Amazon Müşteri Danışmanısın.
Görev: Müşterinin sorusunu SADECE verilen İNGİLİZCE BELGE BAĞLAMI'nı kullanarak **TÜRKÇE** ve **ÇOK KISA** cevapla.
Kurallar:
1. Kısa ve öz ol. Doğrudan cevabı ver, soruyu veya gereksiz başlıkları ("Cevap:", "Müşteri Sorusu:" vb.) asla kullanma.
2. Asla kendi genel bilgini kullanma. Sadece belgedekileri söyle.
3. Eğer sorunun cevabı belgede geçmiyorsa sadece "{NOT_FOUND_TR}" yaz, başka bir şey ekleme."""
        user_prompt = f"Bağlam:\n{context}\n\nSoru: {question_tr}"

    sources = list(dict.fromkeys(doc["source"] for doc in docs))

    try:
        def realtime_stream():
            visible_answer = ""
            in_think = False
            loop_detected = False
            yielded_anything = False
            
            for chunk in ask_llm(system_instruction, user_prompt):
                # Think tag filtering logic
                if "<think>" in chunk or in_think:
                    if "<think>" in chunk:
                        in_think = True
                    if "</think>" in chunk:
                        in_think = False
                        # If it just exited think, don't yield the tag itself
                        chunk = chunk.split("</think>")[-1]
                        if not chunk:
                            continue
                    else:
                        continue # Skip yielding while inside think block
                        
                # Ensure we don't accidentally yield part of <think> if it was split
                if "<think" in chunk and not in_think:
                    continue # Wait for the rest of the tag
                    
                visible_answer += chunk
                
                # Loop breaker logic (improved to ignore numbers)
                if len(visible_answer) > 100:
                    import re
                    # Remove non-alphabet characters and convert to lower
                    clean_text = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ\s]', '', visible_answer.lower())
                    words = clean_text.split()
                    for i in range(4, 20):
                        if loop_detected: break
                        for j in range(max(0, len(words) - i * 3), len(words) - i * 3 + 1):
                            if words[j:j+i] == words[j+i:j+2*i] == words[j+2*i:j+3*i]:
                                loop_detected = True
                                break
                if loop_detected:
                    yield "\n\n... (Aynı cümlelerin tekrar ettiği algılandığı için otomatik olarak kesildi. Başka bir sorunuz varsa lütfen sorun.)"
                    yielded_anything = True
                    break
                    
                yielded_anything = True
                yield chunk
                
            if not yielded_anything:
                yield NOT_FOUND_TR

        return {
            "answer_stream": realtime_stream(),
            "sources": sources
        }

    except Exception as error:
        print("LLM error:", error)
        def error_stream():
            yield f"LLM Hatası: {error}"
        return {
            "answer_stream": error_stream(),
            "sources": sources
        }