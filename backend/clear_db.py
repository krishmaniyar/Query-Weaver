"""
Utility script: clears ALL tables from the SQLite database and wipes
both ChromaDB collections (schema + chat history).
Run with:  conda run -n computer_vision python clear_db.py
"""
import sys
import os

# Make sure app packages are importable
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import inspect, text
from app.db.database import get_engine
from app.vectorstore.vectordb import schema_collection, chat_collection

# ── 1. Drop all SQLite tables ─────────────────────────────────────────────────
engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()

if tables:
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS [{table}]"))
            print(f"  ✓ Dropped table: {table}")
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()
    print(f"\nSQLite: dropped {len(tables)} table(s).\n")
else:
    print("SQLite: no tables found — nothing to drop.\n")

# ── 2. Clear ChromaDB schema collection ───────────────────────────────────────
schema_ids = schema_collection.get()["ids"]
if schema_ids:
    schema_collection.delete(ids=schema_ids)
    print(f"ChromaDB schema_collection: deleted {len(schema_ids)} entry(ies).")
else:
    print("ChromaDB schema_collection: already empty.")

# ── 3. Clear ChromaDB chat-history collection ─────────────────────────────────
chat_ids = chat_collection.get()["ids"]
if chat_ids:
    chat_collection.delete(ids=chat_ids)
    print(f"ChromaDB chat_history_collection: deleted {len(chat_ids)} entry(ies).")
else:
    print("ChromaDB chat_history_collection: already empty.")

print("\n✅ All databases cleared successfully.")
