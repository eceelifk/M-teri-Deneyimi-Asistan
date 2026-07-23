import os
import sys
import json
import sqlite3
import sqlite_vec
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from app.database import DB_PATH
from app.embedding import create_embedding

def finalize():
    print("Rebuilding vec_documents virtual table to save progress...")
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()

    dummy_emb = create_embedding("test")
    dim = len(dummy_emb)
    
    cursor.execute("DROP TABLE IF EXISTS vec_documents")
    cursor.execute(f"CREATE VIRTUAL TABLE vec_documents USING vec0(embedding float[{dim}])")
    
    cursor.execute("SELECT id, embedding FROM documents")
    rows = cursor.fetchall()
    
    print("Inserting all vectors into vec_documents...")
    for rowid, emb_json in tqdm(rows, desc="Vector indexing"):
        try:
            emb_list = json.loads(emb_json)
            if emb_list and len(emb_list) == dim:
                emb_blob = sqlite_vec.serialize_float32(emb_list)
                cursor.execute(
                    "INSERT INTO vec_documents(rowid, embedding) VALUES (?, ?)",
                    (rowid, emb_blob)
                )
        except Exception as e:
            pass
            
    conn.commit()
    conn.close()
    print("Database finalized successfully! Ready to shut down.")

if __name__ == "__main__":
    finalize()
