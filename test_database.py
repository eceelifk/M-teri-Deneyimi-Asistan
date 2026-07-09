from app.database import *

create_database()

insert_chunk(
    "amazon_returns.pdf",
    "Amazon ürünleri teslimden sonra 30 gün içinde iade edilebilir."
)

rows = get_all_chunks()

print(rows)