from app.db.schema_loader import load_database_schema
from app.vectorstore.vectordb import store_schema_embeddings

print("Loading schema from app.db...")
schema = load_database_schema()
print("Storing schema embeddings into ChromaDB...")
store_schema_embeddings(schema)
print("Synchronization complete!")
