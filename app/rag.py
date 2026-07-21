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

    # SSS (FAQ) veritabanında ASIN bilgisi olmadığı için, FAQ aramasında ASIN filtresini temizle
    if filter_type != "review":
        detected_asin = ""

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
    
    # Kapsam sınırını aşmamak için bağlamı kırp (Yaklaşık 300 kelime / 1500 karakter)
    if len(context) > 1500:
        context = context[:1500] + "\n... [Bağlam Kırpıldı]"

    from app.memory import get_memory_text
    memory_context = get_memory_text()
    if len(memory_context) > 1000:
        memory_context = "... [Geçmiş Kırpıldı]\n" + memory_context[-1000:]

    # ASIN is already extracted above as detected_asin

    if filter_type == "review":
        system_instruction = f"""Sen Amazon'un Müşteri Deneyimi Danışmanısın.
GÖREVİN: Kullanıcının sorusunu SADECE verilen İngilizce BELGE BAĞLAMI'na dayanarak TÜRKÇE yanıtlamak. Doğrudan cevaba başla.

KURALLAR:
1. Cevabını madde işareti veya liste kullanmadan, düz bir paragraf (düz metin) halinde yaz.
2. SADECE bağlamdaki bilgileri kullan.
3. Kendi kendine düşünmen gerekirse (<think> etiketleri), bunu ÇOK KISA tut (maksimum 1-2 cümle)."""
        
        asin_info = f"\n\nSorgudaki Ürün Kodu (ASIN): {detected_asin}" if detected_asin else ""
        user_prompt = f"Bağlam:\n{context}{asin_info}\n\nMüşteri: {question_tr}"
    else:
        system_instruction = f"""Sen Amazon'un Müşteri Danışmanısın.
GÖREVİN: Kullanıcının sorusunu SADECE verilen İngilizce BELGE BAĞLAMI'na dayanarak TAMAMEN TÜRKÇE yanıtlamak. Doğrudan cevaba başla.

KURALLAR:
1. Cevabını madde işareti veya liste kullanmadan, düz bir paragraf (düz metin) halinde yaz.
2. SADECE bağlamdaki bilgileri kullan. Doğrudan cevaba başla.
3. Cevabın MUTLAKA %100 TÜRKÇE olmalıdır. İngilizce kelimeleri (örneğin 'undamaged', 'condition') mutlaka Türkçeye çevir (örneğin 'hasarsız', 'durum').
4. Kendi kendine düşünmen gerekirse (<think> etiketleri), bunu ÇOK KISA tut (maksimum 1-2 cümle)."""
        user_prompt = f"Bağlam:\n{context}\n\nGeçmiş Sohbet:\n{memory_context}\n\nMüşteri: {question_tr}"

    sources = list(dict.fromkeys(doc["source"] for doc in docs))

    try:
        def realtime_stream():
            visible_answer = ""
            buffer = ""
            in_think = False
            loop_detected = False
            yielded_anything = False

            for chunk in ask_llm(system_instruction, user_prompt):
                buffer += chunk
                
                if not in_think:
                    if "<think>" in buffer:
                        in_think = True
                        pre_think = buffer.split("<think>")[0]
                        if pre_think:
                            yield pre_think.replace("<", "&lt;").replace(">", "&gt;")
                            visible_answer += pre_think
                        buffer = buffer[buffer.find("<think>") + 7:]
                    else:
                        if "<" in buffer and len(buffer) < 15:
                            continue
                        
                        yield buffer.replace("<", "&lt;").replace(">", "&gt;")
                        visible_answer += buffer
                        buffer = ""
                else:
                    if "</think>" in buffer:
                        in_think = False
                        post_think = buffer.split("</think>")[1]
                        buffer = post_think
                    else:
                        if len(buffer) > 20:
                            buffer = buffer[-15:]
                
                if len(visible_answer) > 100:
                    import re
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
            
            if filter_type == "review" and detected_asin:
                footer = f"\n\n---\n[👉 Ürünü Amazon'da İncele](https://www.amazon.com.tr/dp/{detected_asin})"
                visible_answer += footer
                yield footer
                yielded_anything = True

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