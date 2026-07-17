from app.loader import load_documents
from app.chunk import split_documents
from app.embedding import create_embedding
from app.database import create_database, insert_chunk, get_all_chunks
import sqlite3
import json

def main():
    print("Loading documents...", flush=True)
    documents = load_documents()
    print("Documents:", len(documents), flush=True)

    print("Creating chunks...", flush=True)
    chunks = split_documents(documents)
    print("Chunks:", len(chunks), flush=True)

    create_database()
    
    existing_rows = get_all_chunks()
    existing_texts = set(row[2] for row in existing_rows)
    print(f"Found {len(existing_texts)} existing chunks. Skipping them...", flush=True)

    print("Generating embeddings (Parallel Processing)...", flush=True)
    added = 0
    
    import concurrent.futures
    import threading
    db_lock = threading.Lock()

    def process_chunk(chunk):
        if chunk.page_content in existing_texts:
            return False
            
        embedding = create_embedding(chunk.page_content)
        if embedding:
            with db_lock:
                insert_chunk(
                    chunk.metadata["source"],
                    chunk.metadata["type"],
                    chunk.page_content,
                    embedding
                )
            return True
        return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                added += 1
                if added % 50 == 0:
                    print(f"Added {added} new chunks...", flush=True)
            
    print("\nDatabase Ready", flush=True)

if __name__ == "__main__":
    main()
