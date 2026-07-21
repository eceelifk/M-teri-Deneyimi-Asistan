import json
import sqlite3
import sqlite_vec

from app.database import DB_PATH
from app.embedding import create_embedding

def retrieve(question, top_k=3, minimum_similarity=0.1, filter_type="all", asin=None):
    """
    Kullanıcının sorusunu vektöre çevirir ve veritabanındaki 
    belge vektörleriyle sqlite-vec (C Modülü) kullanarak 100 kat daha hızlı karşılaştırır.
    """
    # 1. Kullanıcının sorusunu embedding vektörüne çevir
    query_vector = create_embedding(question)
    query_blob = sqlite_vec.serialize_float32(query_vector)
    
    # 2. Veritabanına bağlan ve sqlite-vec uzantısını yükle
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    
    cursor = conn.cursor()
    
    like_clause = ""
    sql_params = [query_blob]
    
    if asin:
        like_clause = f" WHERE d.chunk LIKE ?"
        sql_params.append(f"%{asin}%")
    
    # 3. İki tabloyu (metinler ve vektörler) birleştirip C seviyesinde Cosine Distance hesapla
    sql = f"""
        SELECT d.source, d.type, d.chunk, vec_distance_cosine(v.embedding, ?) as distance
        FROM documents d
        JOIN vec_documents v ON d.id = v.rowid
        {like_clause}
    """
    cursor.execute(sql, tuple(sql_params))
    rows = cursor.fetchall()
    
    scored = []
    for source, doc_type, chunk, distance in rows:
        # Arayüzden gelen filtreyi uygula ("all", "faq", "review")
        if filter_type != "all" and doc_type != filter_type:
            continue
            
        # Cosine Distance 0'a ne kadar yakınsa o kadar benzerdir. 
        # Similarity ise 1.0'a ne kadar yakınsa o kadar benzerdir.
        score = 1.0 - distance
        
        # Eğer hem SSS hem yorumlarda arama yapıyorsak (all), yorumları daha az öncelikli yap
        if filter_type == "all" and doc_type == "review":
            score -= 0.05 

        # Belli bir benzerlik eşiğinin (örn: minimum_similarity) üzerindeki belgeleri alalım
        # Eğer ASIN eşleşmesi varsa, semantik benzerlik düşük olsa bile (vektörler alakasız kalsa da) bu satırı KESİNLİKLE al.
        if score > minimum_similarity or asin:
            # ASIN eşleşmesi varsa skorunu yapay olarak yükselt ki her zaman en üstte çıksın
            if asin:
                score += 1.0
                
            scored.append({
                "score": float(score),
                "source": source,
                "type": doc_type,
                "chunk": chunk
            })
            
    conn.close()

    # En yüksek skora sahip olanları en üste alacak şekilde sırala
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:top_k]