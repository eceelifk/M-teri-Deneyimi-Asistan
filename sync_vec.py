import sqlite3
import sqlite_vec
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "rag.db")

def sync():
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, embedding FROM documents WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()
    
    print(f"Syncing {len(rows)} embeddings to vec_documents...")
    for row_id, emb_str in rows:
        emb_list = json.loads(emb_str)
        emb_blob = sqlite_vec.serialize_float32(emb_list)
        cursor.execute("UPDATE vec_documents SET embedding = ? WHERE rowid = ?", (emb_blob, row_id))
        
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    sync()
