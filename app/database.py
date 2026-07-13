import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "rag.db")


def create_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            type TEXT,
            chunk TEXT,
            embedding TEXT
        )
    """)

    conn.commit()
    conn.close()


def clear_database():
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM documents")

    conn.commit()
    conn.close()


def insert_chunk(source, doc_type, chunk, embedding):
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents(source, type, chunk, embedding)
        VALUES (?, ?, ?, ?)
        """,
        (
            source,
            doc_type,
            chunk,
            json.dumps(embedding)
        )
    )

    conn.commit()
    conn.close()


def get_all_chunks():
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT source, type, chunk, embedding
        FROM documents
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows