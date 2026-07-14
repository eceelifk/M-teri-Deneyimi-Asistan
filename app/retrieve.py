import json

from app.database import get_all_chunks
from app.embedding import create_embedding, cosine_similarity

def retrieve(question, top_k=3, minimum_similarity=0.1, filter_type="all"):
    """
    Kullanıcının sorusunu vektöre çevirir ve veritabanındaki 
    belge vektörleriyle karşılaştırıp (Cosine Similarity) en benzerlerini getirir.
    """
    # 1. Kullanıcının sorusunu embedding vektörüne çevir
    query_vector = create_embedding(question)
    
    # 2. Veritabanındaki tüm chunk'ları çek
    rows = get_all_chunks()

    scored = []

    for source, doc_type, chunk, embedding_str in rows:
        try:
            # DB'de JSON text olarak kayıtlı vektörü listeye çeviriyoruz
            chunk_vector = json.loads(embedding_str)
        except Exception:
            continue
            
        # UI üzerinden gelen tipe göre filtrele ("all", "faq", "review")
        if filter_type != "all" and doc_type != filter_type:
            continue

        # 3. İki vektörün anlamsal benzerlik skorunu hesapla
        score = cosine_similarity(query_vector, chunk_vector)

        # Eğer hem SSS hem yorumlarda arama yapıyorsak (all), yorumları daha az öncelikli yap
        if filter_type == "all" and doc_type == "review":
            score -= 0.05 

        # Belli bir benzerlik eşiğinin (örn: minimum_similarity) üzerindeki belgeleri alalım
        if score > minimum_similarity:
            scored.append({
                "score": float(score),
                "source": source,
                "type": doc_type,
                "chunk": chunk
            })

    # En yüksek skora sahip olanları en üste alacak şekilde sırala
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:top_k]