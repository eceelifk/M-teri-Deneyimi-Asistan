from app.document import Document


def split_documents(documents, chunk_size=700, overlap=150):
    chunks = []

    for doc in documents:
        text = doc.page_content

        if not text or not text.strip():
            continue

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata=doc.metadata
                    )
                )

            start += chunk_size - overlap

    return chunks