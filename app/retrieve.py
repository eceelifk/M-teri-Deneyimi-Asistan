import json

from app.database import get_all_chunks
from app.embedding import create_embedding, cosine_similarity

def retrieve(question, top_k=3):
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

        # 3. İki vektörün anlamsal benzerlik skorunu hesapla
        score = cosine_similarity(query_vector, chunk_vector)

        # Review türündeki dökümanları (kullanıcı yorumlarını) bir tık daha az öncelikli yapabiliriz
        if doc_type == "review":
            score -= 0.05 

        # Belli bir benzerlik eşiğinin (örn: %10) üzerindeki belgeleri alalım
        if score > 0.1:
            scored.append({
                "score": float(score),
                "source": source,
                "type": doc_type,
                "chunk": chunk
            })

    # En yüksek skora sahip olanları en üste alacak şekilde sırala
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:top_k]