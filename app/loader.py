import os
import csv
import json
import fitz

from app.document import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_txt(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    return [
        Document(
            page_content=text,
            metadata={
                "source": os.path.basename(path),
                "type": "txt"
            }
        )
    ]


def load_pdf(path):
    docs = []

    pdf = fitz.open(path)

    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text().strip()

        if text:
            docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": os.path.basename(path),
                        "type": "pdf",
                        "page": page_number
                    }
                )
            )

    pdf.close()
    return docs


def load_csv(path):
    docs = []

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            review = row.get("Review Content", "").strip()

            if len(review) < 30:
                continue

            text = f"""
Brand: {row.get("Brand", "")}
Category: {row.get("Category", "")}
Rating: {row.get("Review Rating", "")}
Title: {row.get("Review Title", "")}

Review:
{review}
"""

            docs.append(
                Document(
                    page_content=text.strip(),
                    metadata={
                        "source": os.path.basename(path),
                        "type": "review"
                    }
                )
            )

    return docs


def load_jsonl(path):
    docs = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            review = row.get("sentence", "").strip()
            title = row.get("product_title", "").strip()
            
            if not review or not title:
                continue

            text = f"Product: {title}\n"
            
            asin = row.get("asin")
            if asin:
                text += f"ASIN: {asin}\n"
                
            image_url = row.get("main_image_url")
            if image_url:
                text += f"Image URL: {image_url}\n"
                
            helpful = row.get("helpful")
            if helpful:
                text += f"Helpful Score: {helpful}\n"
                
            text += f"\nReview:\n{review}"

            docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": os.path.basename(path),
                        "type": "review"
                    }
                )
            )

    return docs


def load_documents():
    docs = []

    if not os.path.exists(DATA_DIR):
        print("Data folder not found:", DATA_DIR)
        return docs

    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            path = os.path.join(root, file)
            lower_file = file.lower()

            # Determine doc_type based on the path
            doc_type = "faq" # Default to faq
            if "review" in path.lower():
                doc_type = "review"

            new_docs = []
            if lower_file.endswith(".pdf"):
                new_docs = load_pdf(path)
            elif lower_file.endswith(".txt"):
                new_docs = load_txt(path)
            elif lower_file.endswith(".csv"):
                new_docs = load_csv(path)
            elif lower_file.endswith(".jsonl"):
                new_docs = load_jsonl(path)
                
            # Override metadata type
            for doc in new_docs:
                doc.metadata["type"] = doc_type
                
            docs.extend(new_docs)

    return docs