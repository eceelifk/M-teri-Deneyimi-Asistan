import math
from foundry_local_sdk import Configuration, FoundryLocalManager

print("Foundry Local Embedding API başlatılıyor...")

config = Configuration(app_name="AmazonCustomerSupportAI")
try:
    FoundryLocalManager.initialize(config)
except Exception:
    pass
manager = FoundryLocalManager.instance

# Hocanın istediği gibi yerel Foundry Local SDK'nın modelini alıyoruz
model = manager.catalog.get_model("qwen3-embedding-0.6b")

if not model.is_loaded:
    if not model.is_cached:
        print("Embedding modeli indiriliyor (ilk sefere mahsus, işlem 1-2 dakika sürebilir)...")
        model.download()
    model.load()

client = model.get_embedding_client()

def create_embedding(text):
    """
    Metni Foundry Local SDK ile sayısal bir vektöre çevirir.
    """
    response = client.generate_embedding(text)
    # OpenAI standart formatında döndüğü için embedding'i bu şekilde alıyoruz:
    return response.data[0].embedding

def cosine_similarity(v1, v2):
    """
    İki vektör arasındaki anlamsal benzerliği hesaplar (Kosinüs Benzerliği).
    Numpy gerektirmeden standart Python ile çalışır.
    """
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)