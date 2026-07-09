from app.retrieve import retrieve

results = retrieve(
    "How can I return my order?"
)

for item in results:

    print("=" * 50)

    print(item["score"])

    print(item["source"])

    print(item["chunk"][:300])