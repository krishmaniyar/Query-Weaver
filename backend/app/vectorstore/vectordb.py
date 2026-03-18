import os
import re
import json
import chromadb
from chromadb.utils import embedding_functions

# Define path for persistent ChromaDB storage
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_data")

# Initialize ChromaDB persistent client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Initialize sentence-transformers embedding function
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Get or create persistent collections
schema_collection = client.get_or_create_collection(
    name="schema_collection",
    embedding_function=sentence_transformer_ef
)

chat_collection = client.get_or_create_collection(
    name="chat_history_collection",
    embedding_function=sentence_transformer_ef
)

def store_schema_embeddings(schema_metadata: list):
    """
    Stores schema metadata as text embeddings in ChromaDB.
    Expected schema_metadata format:
    [
        {
            "table": "users",
            "columns": [{"name": "id", "type": "integer"}, ...]
        }
    ]
    """
    if not schema_metadata:
        return
        
    documents = []
    metadatas = []
    ids = []
    
    for table_info in schema_metadata:
        table_name = table_info["table"]
        columns = table_info["columns"]
        
        # Generate text description: "Table users has columns: id, email, created_at"
        col_names = [col["name"] for col in columns]
        doc_text = f"Table {table_name} has columns: {', '.join(col_names)}"
        
        documents.append(doc_text)
        
        # Store metadata (ChromaDB metadata values must be primitive types, so we serialize 'columns')
        metadatas.append({
            "table": table_name,
            "columns": json.dumps(columns)
        })
        
        ids.append(table_name)
        
    # Upsert allows inserting new or updating existing IDs
    schema_collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def search_schema(query: str, k: int = 3):
    """
    Searches the schema vector store for the closest matching tables
    given the user query text.
    Returns metadata reconstructing the original schema format.
    """
    # Perform similarity search
    results = schema_collection.query(
        query_texts=[query],
        n_results=k
    )
    
    extracted_tables = []
    
    if results and results.get("metadatas") and len(results["metadatas"]) > 0:
        for metadata in results["metadatas"][0]:
            table_name = metadata["table"]
            columns = json.loads(metadata["columns"])
            
            extracted_tables.append({
                "table": table_name,
                "columns": columns
            })
            
    return extracted_tables

from datetime import datetime
import uuid

def store_chat_message(question: str, sql: str):
    """
    Stores conversational history in ChromaDB as embeddings of the user's question.
    """
    timestamp = datetime.utcnow().isoformat()
    doc_id = str(uuid.uuid4())
    
    chat_collection.add(
        documents=[question],
        metadatas=[{
            "question": question,
            "generated_sql": sql,
            "timestamp": timestamp
        }],
        ids=[doc_id]
    )

def retrieve_relevant_history(question: str, k: int = 3):
    """
    Searches past chat messages for similar questions and returns their context.
    """
    # Wait to query based on collection size if empty to avoid errors
    if chat_collection.count() == 0:
        return []
        
    results = chat_collection.query(
        query_texts=[question],
        n_results=min(k, chat_collection.count())
    )
    
    history_context = []
    if results and results.get("metadatas") and len(results["metadatas"]) > 0:
        for metadata in results["metadatas"][0]:
            history_context.append({
                "question": metadata["question"],
                "generated_sql": metadata["generated_sql"],
                "timestamp": metadata["timestamp"]
            })
            
    return history_context


def extract_table_names_from_sql(sql: str) -> list:
    """
    Attempts to extract table names created/altered by a DDL statement.
    Handles CREATE TABLE, CREATE TABLE IF NOT EXISTS, ALTER TABLE.
    Returns an empty list if no match is found.
    """
    pattern = re.compile(
        r"\b(?:CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?|ALTER\s+TABLE)\s+['\"`]?(\w+)['\"`]?",
        re.IGNORECASE,
    )
    return list(dict.fromkeys(pattern.findall(sql)))  # preserve order, deduplicate


def sync_tables_to_schema(table_names=None) -> int:
    """
    Reads the live SQLite schema for the given table_names (or all tables
    if table_names is None) and upserts their embeddings into ChromaDB.

    Returns the number of tables synced.
    """
    from sqlalchemy import inspect
    from app.db.database import get_engine

    engine = get_engine()
    inspector = inspect(engine)

    if table_names:
        # Only sync the specified tables (filter to those that actually exist)
        existing = set(inspector.get_table_names())
        targets = [t for t in table_names if t in existing]
    else:
        targets = inspector.get_table_names()

    if not targets:
        return 0

    schema_metadata = []
    for table_name in targets:
        columns_info = [
            {"name": col["name"], "type": str(col["type"]).lower()}
            for col in inspector.get_columns(table_name)
        ]
        schema_metadata.append({"table": table_name, "columns": columns_info})

    store_schema_embeddings(schema_metadata)
    return len(schema_metadata)
