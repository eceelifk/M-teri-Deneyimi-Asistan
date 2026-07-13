import os
import json
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def process_pdfs():
    files_to_process = [
        "raw_pdfs/amazon.pdf",
        "raw_pdfs/amazonyorum.pdf"
    ]
    
    products = {}
    
    for file_path in files_to_process:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"Extracting text from {file_path}...")
        text = extract_text_from_pdf(file_path)
        
        # Use regex to find all JSON-like structures that start with {"asin": and end with }
        import re
        
        # The text might have newlines in the middle of JSON objects due to PDF formatting.
        # We replace newlines with space to make regex matching easier, or just match across newlines.
        clean_text = text.replace('\n', ' ')
        
        # Find all JSON objects
        matches = re.findall(r'\{"asin":".*?\}', clean_text)
        
        for match in matches:
            try:
                obj = json.loads(match)
                asin = obj.get('asin')
                if not asin:
                    continue
                    
                if asin not in products:
                    products[asin] = {
                        "asin": asin,
                        "product_title": obj.get("product_title", ""),
                        "main_image_url": obj.get("main_image_url", ""),
                        "reviews": []
                    }
                
                products[asin]["reviews"].append({
                    "sentence": obj.get("sentence", ""),
                    "helpful": obj.get("helpful", 0)
                })
            except Exception:
                pass
                
    print(f"Found {len(products)} unique products.")
    
    # Save the consolidated JSON
    output_json = "amazon_grouped_reviews.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(list(products.values()), f, ensure_ascii=False, indent=2)
    print(f"Saved JSON to {output_json}")
    
    # Also generate a clean TXT file for the RAG system to ingest
    os.makedirs("data/reviews", exist_ok=True)
    rag_txt = "data/reviews/amazon_grouped_reviews.txt"
    with open(rag_txt, "w", encoding="utf-8") as f:
        for p in products.values():
            f.write(f"Ürün Kodu (ASIN): {p['asin']}\n")
            f.write(f"Ürün Adı: {p['product_title']}\n")
            f.write(f"Ürün Görseli: {p['main_image_url']}\n")
            f.write("Müşteri Yorumları:\n")
            for r in p['reviews']:
                f.write(f"- {r['sentence']} (Faydalılık: {r['helpful']})\n")
            f.write("\n\n") # Double newline to ensure clean chunking
            
    print(f"Saved RAG-friendly text format to {rag_txt}")
    
    # Move PDFs out of data folder so they aren't ingested again
    os.makedirs("raw_pdfs", exist_ok=True)
    for file_path in files_to_process:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            os.rename(file_path, f"raw_pdfs/{filename}")
            print(f"Moved {file_path} to raw_pdfs/{filename}")

if __name__ == "__main__":
    process_pdfs()
