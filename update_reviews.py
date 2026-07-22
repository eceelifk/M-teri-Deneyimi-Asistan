import os
import sys
import json
import sqlite3
import sqlite_vec
import concurrent.futures
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import app.llm
from app.database import DB_PATH
from app.loader import load_amazon_reviews_txt
from app.chunk import split_documents
from app.embedding import create_embedding

def update_reviews():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()
    
    print("Deleting old reviews from documents table...")
    cursor.execute("DELETE FROM documents WHERE type = 'review'")
    conn.commit()
    
    print("Loading review documents...")
    path = os.path.join(BASE_DIR, "data", "reviews", "amazon_grouped_reviews.txt")
    if not os.path.exists(path):
        print("Review file not found!")
        return
        
    docs = load_amazon_reviews_txt(path)
    print(f"Total {len(docs)} review documents found.")
    
    print("Splitting reviews into chunks...")
    chunks = split_documents(docs)
    print(f"Total {len(chunks)} review chunks created.")
    
    def get_embedding_for_chunk(chunk):
        text = chunk.page_content
        source = chunk.metadata.get("source", "unknown")
        doc_type = chunk.metadata.get("type", "review")
        embedding = create_embedding(text)
        return source, doc_type, text, embedding

    print("Generating embeddings for reviews... (using max_workers=2 to prevent Memory Errors and speed up)")
    
    # We use a lower max_workers to avoid OOM, but it's still multithreaded
    batch_size = 50
    valid_results = []
    
    for i in tqdm(range(0, len(chunks), batch_size), desc="Processing Batches"):
        batch_chunks = chunks[i:i+batch_size]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for source, doc_type, text, embedding in executor.map(get_embedding_for_chunk, batch_chunks):
                if embedding and len(embedding) > 0:
                    cursor.execute(
                        "INSERT INTO documents(source, type, chunk, embedding) VALUES (?, ?, ?, ?)",
                        (source, doc_type, text, json.dumps(embedding))
                    )
        conn.commit()

    print("Rebuilding vec_documents virtual table...")
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
    print("Review update complete! Vector database rebuilt successfully.")

if __name__ == "__main__":
    update_reviews()
