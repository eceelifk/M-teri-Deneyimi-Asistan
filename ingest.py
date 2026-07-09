from app.loader import load_documents
from app.chunk import split_documents
from app.embedding import create_embedding
from app.database import create_database, clear_database, insert_chunk


def main():
    print("Loading documents...")

    documents = load_documents()

    print("Documents:", len(documents))

    print("Creating chunks...")

    chunks = split_documents(documents)

    print("Chunks:", len(chunks))

    create_database()
    clear_database()

    print("Generating embeddings...")

    for chunk in chunks:
        embedding = create_embedding(chunk.page_content)

        insert_chunk(
            chunk.metadata["source"],
            chunk.metadata["type"],
            chunk.page_content,
            embedding
        )

    print()
    print("Database Ready")


if __name__ == "__main__":
    main()