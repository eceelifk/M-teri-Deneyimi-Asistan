import sqlite3
import sqlite_vec
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "rag.db")

print("Bağlanılıyor...")
conn = sqlite3.connect(DB_PATH)
conn.enable_load_extension(True)
sqlite_vec.load(conn)
conn.enable_load_extension(False)

cursor = conn.cursor()

print("vec_documents tablosu oluşturuluyor...")
cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS vec_documents USING vec0(
        embedding float[1024]
    );
""")

print("Eski veriler okunuyor...")
cursor.execute("SELECT id, embedding FROM documents")
rows = cursor.fetchall()

print(f"Toplam {len(rows)} veri dönüştürülüyor...")
# Önce tabloyu temizleyelim (aynı işlemi 2 kere çalıştırırsak çakışmasın)
cursor.execute("DELETE FROM vec_documents")

for row_id, embedding_str in rows:
    try:
        embedding = json.loads(embedding_str)
        # Binary Blob'a çevir
        blob = sqlite_vec.serialize_float32(embedding)
        
        # Virtual table'a ekle (rowid, orjinal tablodaki id ile eşleşmeli)
        cursor.execute(
            "INSERT INTO vec_documents(rowid, embedding) VALUES (?, ?)",
            (row_id, blob)
        )
    except Exception as e:
        print(f"Hata: id {row_id} çevrilemedi: {e}")

conn.commit()
conn.close()

print("\nBaşarılı! Tüm vektörler sqlite-vec formatına dönüştürüldü.")
