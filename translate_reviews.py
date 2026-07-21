import os

def translate_reviews():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    reviews_file = os.path.join(base_dir, "data", "reviews", "amazon_grouped_reviews.txt")
    
    if not os.path.exists(reviews_file):
        print(f"File not found: {reviews_file}")
        return
        
    print(f"Translating metadata in {reviews_file}...")
    
    with open(reviews_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace Turkish headers with English
    content = content.replace("Ürün Kodu (ASIN):", "Product Code (ASIN):")
    content = content.replace("Ürün Adı:", "Product Name:")
    content = content.replace("Ürün Görseli:", "Product Image:")
    content = content.replace("Müşteri Yorumları:", "Customer Reviews:")
    content = content.replace("(Faydalılık:", "(Helpfulness:")
    
    # Write it back
    with open(reviews_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Done translating review metadata.")

if __name__ == "__main__":
    translate_reviews()
