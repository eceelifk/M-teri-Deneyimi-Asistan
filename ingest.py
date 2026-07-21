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

# Ensure Foundry SDK model is loaded
import app.llm

from app.database import create_database, clear_database, DB_PATH
from app.loader import load_documents
from app.chunk import split_documents
from app.embedding import create_embedding

def setup_vec_table():
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()
    
    # Check embedding dimension by generating a dummy embedding
    dummy_emb = create_embedding("test")
    dim = len(dummy_emb)
    
    cursor.execute("DROP TABLE IF EXISTS vec_documents")
    cursor.execute(f"CREATE VIRTUAL TABLE vec_documents USING vec0(embedding float[{dim}])")
    
    conn.commit()
    conn.close()
    return dim

def run_ingest():
    print("Creating database...")
    create_database()
    clear_database()
    dim = setup_vec_table()
    
    print("Loading documents...")
    docs = load_documents()
    print(f"Total {len(docs)} documents found.")
    
    print("Splitting documents into chunks...")
    chunks = split_documents(docs)
    print(f"Total {len(chunks)} chunks created.")
    
    print("Saving to vector database...")
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()
    
    def get_embedding_for_chunk(chunk):
        text = chunk.page_content
        source = chunk.metadata.get("source", "unknown")
        doc_type = chunk.metadata.get("type", "faq")
        embedding = create_embedding(text)
        return source, doc_type, text, embedding

    print("Generating embeddings and writing to database in batches...")
    batch_size = 100
    for i in tqdm(range(0, len(chunks), batch_size), desc="Processing Batches"):
        batch_chunks = chunks[i:i+batch_size]
        batch_results = []
        
        # Calculate embeddings for the batch using multithreading
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            for res in executor.map(get_embedding_for_chunk, batch_chunks):
                batch_results.append(res)
                
        # Write batch to database
        for source, doc_type, text, embedding in batch_results:
            cursor.execute(
                "INSERT INTO documents(source, type, chunk, embedding) VALUES (?, ?, ?, ?)",
                (source, doc_type, text, json.dumps(embedding))
            )
            rowid = cursor.lastrowid
            
            emb_blob = sqlite_vec.serialize_float32(embedding)
            cursor.execute(
                "INSERT INTO vec_documents(rowid, embedding) VALUES (?, ?)",
                (rowid, emb_blob)
            )
            
        conn.commit()

    conn.close()
    
    print("Process completed! System is ready.")

if __name__ == "__main__":
    run_ingest()
