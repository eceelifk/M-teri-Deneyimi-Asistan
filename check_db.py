import sqlite3
import pandas as pd

try:
    c = sqlite3.connect('database/rag.db')
    df = pd.read_sql_query("SELECT * FROM documents WHERE chunk LIKE '%B000AO3L84%'", c)
    print(f"B000AO3L84 matches: {len(df)}")
    if len(df) > 0:
        print(df.head())
except Exception as e:
    print(e)
