from sqlalchemy import inspect, text
from app.db.database import get_engine
import logging

from app.logger import setup_logger
logger = setup_logger(__name__)

def load_database_schema():
    """
    Reads all tables, extracts columns and data types,
    and returns structured schema metadata.
    """
    engine = get_engine()
    inspector = inspect(engine)
    
    schema_metadata = []
    
    table_names = inspector.get_table_names()
    for table_name in table_names:
        columns_info = []
        columns = inspector.get_columns(table_name)
        for col in columns:
            columns_info.append({
                "name": col["name"],
                "type": str(col["type"]).lower()
            })
            
        schema_metadata.append({
            "table": table_name,
            "columns": columns_info
        })
        
    return schema_metadata

def get_table_data(table_name: str, limit: int = 50) -> list:
    """
    Retrieves actual data rows for a given table to provide contextual examples to the LLM.
    """
    engine = get_engine()
    try:
        with engine.connect() as connection:
            # table_name is sourced directly from inspector/schema, so f-string interpolation is safe
            result = connection.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
            rows = result.fetchall()
            
            if not rows:
                return []
                
            keys = result.keys()
            # Convert row objects into structured dictionaries
            return [dict(zip(keys, row)) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching data from table {table_name}: {e}")
        return []

