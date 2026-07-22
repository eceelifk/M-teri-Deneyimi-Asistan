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

def load_amazon_reviews_txt(path):
    docs = []
    with open(path, encoding="utf-8") as f:
        content = f.read()
    
    # "Product Code (ASIN): " kelimesine göre böl
    products_raw = content.split("Product Code (ASIN): ")
    
    for p_raw in products_raw:
        if not p_raw.strip():
            continue
            
        lines = p_raw.strip().split("\n")
        asin = lines[0].strip()
        
        product_name = ""
        product_image = ""
        reviews_start_idx = -1
        
        for i, line in enumerate(lines[1:], start=1):
            if line.startswith("Product Name: "):
                product_name = line.replace("Product Name: ", "").strip()
            elif line.startswith("Product Image: "):
                product_image = line.replace("Product Image: ", "").strip()
            elif line.startswith("Customer Reviews:"):
                reviews_start_idx = i + 1
                break
                
        if reviews_start_idx == -1:
            continue
            
        reviews_text = "\n".join(lines[reviews_start_idx:])
        # Yorumları "- " (tire ve boşluk) ile ayır
        reviews_list = [r.strip() for r in reviews_text.split("\n- ") if r.strip()]
        
        # Eğer yorumların başında da "- " varsa onu da temizle
        reviews_list = [r[2:] if r.startswith("- ") else r for r in reviews_list]
        
        header = f"Product Name: {product_name}\nASIN: {asin}\n"
        if product_image:
            header += f"Product Image: {product_image}\n"
        header += "\nReviews:\n"
        
        current_chunk = header
        
        for r in reviews_list:
            # 650 karakteri geçiyorsa yeni bir Document oluştur
            if len(current_chunk) + len(r) > 650 and len(current_chunk) > len(header):
                docs.append(
                    Document(
                        page_content=current_chunk,
                        metadata={
                            "source": os.path.basename(path),
                            "type": "review",
                            "asin": asin,
                            "product": product_name
                        }
                    )
                )
                current_chunk = header + f"- {r}\n"
            else:
                current_chunk += f"- {r}\n"
                
        if len(current_chunk) > len(header):
            docs.append(
                Document(
                    page_content=current_chunk,
                    metadata={
                        "source": os.path.basename(path),
                        "type": "review",
                        "asin": asin,
                        "product": product_name
                    }
                )
            )
            
    return docs


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
    
    # Ürünleri ASIN'e göre grupla
    products = {}

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
            asin = row.get("asin")
            
            if not review or not title or not asin:
                continue
                
            if asin not in products:
                products[asin] = {
                    "title": title,
                    "image_url": row.get("main_image_url"),
                    "helpful": row.get("helpful"),
                    "reviews": []
                }
            products[asin]["reviews"].append(review)

    for asin, data in products.items():
        header = f"Product: {data['title']}\nASIN: {asin}\n"
        if data['image_url']:
            header += f"Image URL: {data['image_url']}\n"
        header += "\nReviews:\n"
        
        current_chunk = header
        
        for r in data["reviews"]:
            # Eğer mevcut chunk limiti aşacaksa, yeni bir Document oluştur (650 karakter sınırı)
            if len(current_chunk) + len(r) > 650 and len(current_chunk) > len(header):
                docs.append(
                    Document(
                        page_content=current_chunk,
                        metadata={
                            "source": os.path.basename(path),
                            "type": "review"
                        }
                    )
                )
                current_chunk = header + f"- {r}\n"
            else:
                current_chunk += f"- {r}\n"
                
        # Kalan kısmı da ekle
        if len(current_chunk) > len(header):
            docs.append(
                Document(
                    page_content=current_chunk,
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
            if lower_file == "amazon_grouped_reviews.txt":
                new_docs = load_amazon_reviews_txt(path)
            elif lower_file.endswith(".pdf"):
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