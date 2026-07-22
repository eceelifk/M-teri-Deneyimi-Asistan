from app.llm import ask_llm
from app.retrieve import retrieve
from app.translate import tr_to_en, en_to_tr
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
    
    # SADECE VERİTABANINDA SEMANTİK OLARAK ARAYACAĞIZ (ASIN FİLTRESİ YOK)
    try:
        docs = retrieve(question=english_query, top_k=TOP_K, minimum_similarity=MINIMUM_SIMILARITY, filter_type=filter_type)
        unload_embedding()
    except Exception as error:
        print("Retrieval error:", error)
        docs = []

    if not docs:
        return {
            "answer_stream": get_simulated_stream(NOT_FOUND_TR),
            "sources": []
        }
        
    # (ASIN detection will be done after building the full context)

    if not docs:
        return {
            "answer_stream": get_simulated_stream(NOT_FOUND_TR),
            "sources": []
        }

    context = build_context(docs)
    
    # Kapsam sınırını aşmamak için bağlamı kırp (Yaklaşık 12000 karakter)
    if len(context) > 12000:
        context = context[:12000] + "\n... [Bağlam Kırpıldı]"

    from app.memory import get_memory_text
    memory_context = get_memory_text()
    
    full_text_for_asin = context + "\n\n" + memory_context
    detected_asins = []
    if filter_type == "review":
        import re
        matches = re.findall(r'\b([B0-9][A-Z0-9]{9})\b', full_text_for_asin)
        detected_asins = list(dict.fromkeys(matches))
    context = context + "\n\n" + memory_context
    
    if len(memory_context) > 1000:
        memory_context = "... [Geçmiş Kırpıldı]\n" + memory_context[-1000:]

    if filter_type == "review":
        system_instruction = f"""You are Amazon's expert Customer Advisor.
YOUR TASK: Provide a highly engaging, helpful, and direct answer based ONLY on the provided English PRODUCT REVIEWS.

RULES:
1. Answer ENTIRELY in English. Do not use Turkish.
2. DO NOT copy-paste raw reviews or lists of reviews. DO NOT mention "Helpfulness" scores.
3. Your main goal is to summarize the overall consensus based on the reviews.
4. RECOMMENDATIONS: If the user asks for a recommendation (e.g., "suggest a camera"):
   - Recommend ONE OR MORE products found in the context.
   - For EACH recommended product, you MUST use this exact format:
     
     ### [Product Name]
     - **Why I Recommend It**: [Explain why it's recommended based on the reviews]
     - **Key Features**: [List key features mentioned by customers]
5. COMPARISONS: If the user asks to compare products, DO NOT output a table. Instead, format it as a clean list. 
   - For EACH product, use this format EXACTLY, with double blank lines between every section:
   
     ### [Product Name]
     
     - **Estimated Rating**: [e.g. ⭐⭐⭐⭐½ (4.5/5)]
     
     - **Pros**: [List pros]
     
     - **Cons**: [List cons]
     
     - **Final Recommendation**: [Why you recommend it]
6. DO NOT sound like a robot. Synthesize the information naturally.
7. If the provided reviews are completely irrelevant to the user's question, DO NOT make up an answer. Simply say: "Unfortunately, I couldn't find a product in our database that matches these criteria."
8. STRUCTURE YOUR ANSWER CAREFULLY: If you use Markdown headings, YOU MUST put them on a completely new line. Always separate paragraphs and headings with a blank line.
9. Start directly with the core answer. Keep a helpful, enthusiastic tone.
10. If you need to think (<think> tags), keep it VERY SHORT."""
        
        user_prompt = f"""REVIEWS CONTEXT:
{context}

CUSTOMER QUESTION: {english_query}

IMPORTANT REMINDER: Answer the customer based ONLY on the reviews above. First, evaluate the overall sentiment for the product.

If the product has MOSTLY POSITIVE reviews, RECOMMEND IT. Your answer MUST look like this example:
### Sony Cyber-shot Camera
- **Estimated Rating**: ⭐⭐⭐⭐½ (4.5/5)
- **Why I Recommend It**: Customers love the image quality and battery life.
- **Key Features**: 20MP sensor, compact size.

If the product has MOSTLY NEGATIVE reviews, DO NOT RECOMMEND IT. Your answer MUST look like this example:
### Bad Brand Speaker
- **Estimated Rating**: ⭐½☆☆☆ (1.5/5)
- **Why I DO NOT Recommend It**: Most customers complained that it breaks after one day and has terrible sound.
- **Major Complaints**: Poor sound, breaks easily.

If the customer asks to COMPARE two or more products, YOU MUST use a Markdown table. Your answer MUST look like this example:
| Feature | Sony Camera | Bad Brand Camera |
|---|---|---|
| **Rating** | ⭐⭐⭐⭐½ | ⭐½☆☆☆ |
| **Pros** | Great image | Cheaper |
| **Cons** | Expensive | Breaks easily |

YOUR HELPFUL ANSWER (in English):"""
    else:
        system_instruction = f"""You are Amazon's Customer Advisor.
YOUR TASK: Answer the user's question based ONLY on the provided English DOCUMENT CONTEXT.

RULES:
1. Answer ENTIRELY in English. Do not use Turkish.
2. Structure your answer clearly. If the answer involves steps, use numbered lists or bullet points.
3. Start your answer directly with the information. DO NOT use introductory phrases like "The answer is" or "Based on the context".
4. If you need to think (<think> tags), keep it VERY SHORT."""
        user_prompt = f"Context:\n{context}\n\nChat History:\n{memory_context}\n\nCustomer: {english_query}"

    sources = list(dict.fromkeys(doc["source"] for doc in docs))

    try:
        def realtime_stream():
            buffer = ""
            in_think = False
            visible_answer = ""
            line_buffer = ""
            loop_detected = False
            yielded_anything = False

            for chunk in ask_llm(system_instruction, user_prompt):
                buffer += chunk
                
                if not in_think:
                    if "<think>" in buffer:
                        parts = buffer.split("<think>")
                        pre_think = parts[0]
                        if pre_think:
                            line_buffer += pre_think
                            if line_buffer.strip():
                                tr_text = en_to_tr(line_buffer)
                                yield tr_text
                                visible_answer += tr_text
                                yielded_anything = True
                            else:
                                yield line_buffer
                                visible_answer += line_buffer
                            line_buffer = ""
                        in_think = True
                        buffer = parts[1] if len(parts) > 1 else ""
                    else:
                        line_buffer += chunk
                        buffer = ""
                        
                        while "\n" in line_buffer:
                            parts = line_buffer.split("\n", 1)
                            line = parts[0]
                            line_buffer = parts[1]
                            
                            if line.strip():
                                tr_text = en_to_tr(line)
                                yield tr_text + "\n"
                                visible_answer += tr_text + "\n"
                                yielded_anything = True
                            else:
                                yield "\n"
                                visible_answer += "\n"
                else:
                    if "</think>" in buffer:
                        parts = buffer.split("</think>")
                        in_think = False
                        buffer = parts[1] if len(parts) > 1 else ""
                        if buffer:
                            line_buffer += buffer
                            buffer = ""
                        
                # Loop detection using visible_answer
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

            if line_buffer.strip():
                tr_text = en_to_tr(line_buffer)
                yield tr_text
                yielded_anything = True
            elif line_buffer:
                yield line_buffer

            if not yielded_anything:
                yield NOT_FOUND_TR

        return {
            "answer_stream": realtime_stream(),
            "sources": sources,
            "asins": detected_asins if filter_type == "review" else []
        }

    except Exception as error:
        print("LLM error:", error)
        def error_stream():
            yield f"LLM Hatası: {error}"
        return {
            "answer_stream": error_stream(),
            "sources": sources
        }