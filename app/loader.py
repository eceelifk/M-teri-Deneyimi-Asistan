import os
import csv
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


def load_documents():
    docs = []

    if not os.path.exists(DATA_DIR):
        print("Data folder not found:", DATA_DIR)
        return docs

    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            path = os.path.join(root, file)
            lower_file = file.lower()

            if lower_file.endswith(".pdf"):
                docs.extend(load_pdf(path))

            elif lower_file.endswith(".txt"):
                docs.extend(load_txt(path))

            elif lower_file.endswith(".csv"):
                docs.extend(load_csv(path))

    return docs