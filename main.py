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

    if question == "":
        continue

    print("\nİşleniyor...")

    result = ask(question)

    print("\nAsistan:")
    print(result["answer_tr"])

    if result["sources"]:
        print("\nKaynaklar:")
        for source in result["sources"]:
            print("-", source)

    # SELF-LEARNING (Kendi Kendine Öğrenme) Mekanizması
    if "bulamadım" in result["answer_tr"].lower() or "bilgi yok" in result["answer_tr"].lower() or "bulunmamaktadır" in result["answer_tr"].lower():
        print("\n[Sistem Önerisi]: Görünüşe göre asistanımız bu sorunun cevabını veritabanında bulamadı.")
        ogret = input("👉 Bu sorunun doğru cevabını sisteme öğretmek ister misin? (E/H): ").strip().lower()
        if ogret == 'e':
            yeni_cevap = input("Lütfen doğru cevabı yazın: ").strip()
            if yeni_cevap:
                print("Öğreniliyor (Vektörlere çevriliyor)...")
                
                # 1. Metni faq.txt dosyasına kalıcı olarak ekle
                with open("data/faq/faq.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n\nQ: {question}\nA: {yeni_cevap}\n")
                
                # 2. Anında embedding (vektör) oluştur ve SQLite veritabanına kaydet
                from app.embedding import create_embedding
                from app.database import insert_chunk
                
                yeni_chunk = f"Q: {question}\nA: {yeni_cevap}"
                yeni_vektor = create_embedding(yeni_chunk)
                insert_chunk("faq.txt (Kullanıcı Öğretti)", "faq", yeni_chunk, yeni_vektor)
                
                print("✅ Harika! Asistan bu bilgiyi öğrendi. Bir sonraki soruşunda doğru cevap verecek!")

    print("\n" + "-" * 60)