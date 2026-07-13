import sys
from app.rag import ask
import json

def test():
    query = "402-7518138-6531927 siparişin durumu ne"
    res = ask(query)
    print("ANSWER EN:", res.get("answer_en"))
    print("ANSWER TR:", res.get("answer_tr"))
    print("SOURCES:", res.get("sources"))
    docs = res.get("retrieved_documents", [])
    print(f"RETRIEVED {len(docs)} DOCS:")
    for d in docs:
        print(f"[{d['source']}] Score: {d.get('score', 'N/A')}")
        print(d['chunk'][:200])
        print("---")

if __name__ == "__main__":
    test()
