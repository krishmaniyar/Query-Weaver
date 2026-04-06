"""
Utility script: clears ALL tables from the database and wipes
both ChromaDB collections (schema + chat history).
Run with:  python clear_db.py
"""
import sys
import os

# Make sure app packages are importable
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import inspect, text
from app.db.database import get_engine
from app.vectorstore.vectordb import schema_collection, chat_collection

# ── 1. Drop all tables ────────────────────────────────────────────────────────
engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()

if tables:
    with engine.connect() as conn:
        dialect = engine.dialect.name

        # Disable foreign-key checks so we can drop in any order
        if dialect == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
            print(f"  ✓ Dropped table: {table}")

        # Re-enable foreign-key checks
        if dialect == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        conn.commit()
    print(f"\nDatabase: dropped {len(tables)} table(s).\n")
else:
    print("Database: no tables found — nothing to drop.\n")

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
