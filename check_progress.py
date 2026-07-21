import sqlite3

def check_progress():
    conn = sqlite3.connect('database/rag.db')
    cursor = conn.cursor()
    # Check total documents that still have English "this" or similar markers
    cursor.execute("SELECT COUNT(*) FROM documents WHERE type='review' AND chunk LIKE '%this%'")
    untranslated_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documents WHERE type='review'")
    total_count = cursor.fetchone()[0]
    
    print(f"Total reviews: {total_count}")
    print(f"Untranslated reviews (approx): {untranslated_count}")
    print(f"Translated reviews: {total_count - untranslated_count}")
    
if __name__ == "__main__":
    check_progress()
