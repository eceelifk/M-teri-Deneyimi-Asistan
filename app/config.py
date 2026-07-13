APP_NAME = "AmazonCustomerSupportAI"

# Cevap üretmek için kullanılan LLM
MODEL_NAME = "qwen3-1.7b"

# Embedding üretmek için kullanılan model
EMBEDDING_MODEL_NAME = "qwen3-embedding-0.6b"


SYSTEM_PROMPT = """
You are an Amazon Customer Experience and FAQ Assistant.

Your job is to answer questions about:

- Orders
- Shipping
- Returns
- Refunds
- Payments
- Prime Membership
- Customer Service

Rules:

- Always answer in English.
- Use only the information provided in the document context.
- Be polite.
- Be concise.
- Never make up information.
- If the documents do not support the answer, say that you do not know.
"""


# Retrieval sırasında döndürülecek maksimum belge parçası
TOP_K = 6

# Embedding benzerliği için minimum kabul edilen değer
MINIMUM_SIMILARITY = 0.05


NOT_FOUND_EN = (
    "I couldn't find this information in the provided documents."
)

NOT_FOUND_TR = (
    "Bu bilgi verilen belgelerde bulunamadı."
)