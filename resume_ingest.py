from app.loader import load_documents
from app.chunk import split_documents
from app.embedding import create_embedding
from app.database import create_database, insert_chunk, get_all_chunks
import sqlite3
import json

def main():
    print("Loading documents...")
    documents = load_documents()
    print("Documents:", len(documents))

    print("Creating chunks...")
    chunks = split_documents(documents)
    print("Chunks:", len(chunks))

    create_database()
    
    existing_rows = get_all_chunks()
    existing_texts = set(row[2] for row in existing_rows)
    print(f"Found {len(existing_texts)} existing chunks. Skipping them...")

    print("Generating embeddings...")
    added = 0
    for chunk in chunks:
        if chunk.page_content in existing_texts:
            continue
            
        embedding = create_embedding(chunk.page_content)
        insert_chunk(
            chunk.metadata["source"],
            chunk.metadata["type"],
            chunk.page_content,
            embedding
        )
        added += 1
        
        if added % 10 == 0:
            print(f"Added {added} new chunks...")
            
    print("\nDatabase Ready")

if __name__ == "__main__":
    main()
