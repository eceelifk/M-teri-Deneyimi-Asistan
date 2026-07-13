import sqlite3

def check_db():
    conn = sqlite3.connect('database/rag.db')
    c = conn.cursor()
    c.execute("SELECT source, count(*) FROM documents GROUP BY source")
    rows = c.fetchall()
    for row in rows:
        print(f"{row[0]}: {row[1]}")
    
    c.execute("SELECT count(*) FROM documents")
    total = c.fetchone()[0]
    print(f"Total chunks in DB: {total}")

if __name__ == '__main__':
    check_db()
