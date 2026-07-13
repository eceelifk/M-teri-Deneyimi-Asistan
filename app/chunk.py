from app.document import Document


def split_documents(documents, chunk_size=700, overlap=150):
    chunks = []

    for doc in documents:
        text = doc.page_content

        if not text or not text.strip():
            continue

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        current_chunk = ""

        for paragraph in paragraphs:
            if len(paragraph) > chunk_size * 1.5:
                if current_chunk:
                    chunks.append(Document(page_content=current_chunk.strip(), metadata=doc.metadata))
                    current_chunk = ""
                
                start = 0
                while start < len(paragraph):
                    end = start + chunk_size
                    chunk_text = paragraph[start:end].strip()
                    if chunk_text:
                        chunks.append(Document(page_content=chunk_text, metadata=doc.metadata))
                    start += chunk_size - overlap
                continue
                
            if not current_chunk:
                current_chunk = paragraph
                continue
            
            if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
                current_chunk += "\n\n" + paragraph
            else:
                chunks.append(
                    Document(
                        page_content=current_chunk.strip(),
                        metadata=doc.metadata
                    )
                )
                current_chunk = paragraph

        if current_chunk:
            chunks.append(
                Document(
                    page_content=current_chunk.strip(),
                    metadata=doc.metadata
                )
            )

    return chunks