from app.rag import ask


print("=" * 60)
print("Amazon Customer Experience & FAQ Assistant")
print("Çıkmak için 'exit' yaz.")
print("=" * 60)

while True:
    question = input("\nSen: ").strip()

    if question.lower() == "exit":
        print("\nGörüşürüz!")
        break

    if not question:
        continue

    print("\nİşleniyor...")

    try:
        result = ask(question)
    except Exception as error:
        print("\nSistem hatası:", error)
        continue

    print("\nAsistan:")
    print(result["answer_tr"])



    if result["sources"]:
        print("\nKaynaklar:")

        for source in result["sources"]:
            print("-", source)

    print("\n" + "-" * 60)