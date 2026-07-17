import math
from foundry_local_sdk import Configuration, FoundryLocalManager

from app.config import APP_NAME, EMBEDDING_MODEL_NAME


print("Foundry Local Embedding API başlatılıyor...")

config = Configuration(app_name=APP_NAME)

try:
    FoundryLocalManager.initialize(config)
except Exception:
    # SDK daha önce başlatılmış olabilir.
    pass

manager = FoundryLocalManager.instance

model = manager.catalog.get_model(EMBEDDING_MODEL_NAME)

if model is None:
    model = manager.catalog.get_model("qwen3-embedding-0.6b")
    if model is None:
        raise ValueError("Kritik Hata: Embedding modeli bulunamadı!")

client = model.get_embedding_client()
if client is None:
    raise ValueError("Embedding client alınamadı!")


def create_embedding(text: str) -> list[float]:
    """Metin için embedding (vektör) oluşturur."""
    if not text or not text.strip():
        return []

    # Lazy loading: Sadece çağrıldığında yükle
    if not model.is_loaded:
        if not model.is_cached:
            print("Embedding modeli indiriliyor...")
            model.download()
        model.load()

    try:
        response = client.generate_embedding(text.strip())
        return response.data[0].embedding
    except Exception as e:
        print(f"Hata: {e}")
        return []


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """
    İki embedding vektörü arasındaki cosine similarity
    değerini hesaplar.
    """
    if not v1 or not v2:
        return 0.0

    if len(v1) != len(v2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2))

    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


def unload_embedding():
    """Unloads the embedding model from memory."""
    if model.is_loaded:
        model.unload()