from fastapi import APIRouter, HTTPException
from app.models.request_models import QueryRequest, QueryResponse
from app.vectorstore.vectordb import (
    search_schema,
    retrieve_relevant_history,
    store_chat_message,
    sync_tables_to_schema,
    extract_table_names_from_sql,
)
from app.services.llm_service import LLMService
from app.services.sql_executor import execute_sql, SQLExecutorError
from app import sse_broadcaster
import logging
import time
import json

from app.logger import setup_logger
from app.db.schema_loader import get_table_data, load_database_schema

logger = setup_logger(__name__)
router = APIRouter(prefix="/query", tags=["query"])

llm_service = LLMService()

@router.post("/", response_model=QueryResponse)
def process_query(request: QueryRequest):
    start_time = time.time()
    try:
        logger.info(f"Received question: {request.question}")
        logger.info(f"Selected tables from UI: {request.selected_tables}")
        
        # 1. Retrieve the appropriate schema
        logger.info("\n=== STEP 1: RETRIEVING SCHEMA ===")
        schema_context = []
        
        # Determine the retrieval strategy based on selected_tables
        if not request.selected_tables or "Auto" in request.selected_tables:
            logger.info("Strategy: Auto (Vector Search)")
            schema_context = search_schema(request.question, k=3)
        elif "All" in request.selected_tables or "All Tables" in request.selected_tables:
            logger.info("Strategy: All Tables")
            schema_context = load_database_schema()
        else:
            logger.info(f"Strategy: Specific Tables ({request.selected_tables})")
            full_schema = load_database_schema()
            schema_context = [t for t in full_schema if t["table"] in request.selected_tables]
            
        retrieved_tables = [table_info["table"] for table_info in schema_context]
        logger.info(f"Retrieved tables: {retrieved_tables}")
        
        # 1.2 Fetch actual table data and inject it into the LLM context
        for table_info in schema_context:
            table_name = table_info["table"]
            table_data = get_table_data(table_name, limit=5)
            table_info["rows"] = table_data
            
        logger.info(f"Schema and Data Details:\n{json.dumps(schema_context, indent=2, default=str)}")
        
        # 1.5 Retrieve relevant chat history context
        logger.info("\n=== STEP 1.5: RETRIEVING HISTORY ===")
        history = retrieve_relevant_history(request.question, k=3)
        logger.info(f"History context:\n{json.dumps(history, indent=2)}")
        
        # 2. Generate SQL using LLM (with history)
        logger.info("\n=== STEP 2: GENERATING SQL VIA LLM ===")
        generated_sql = llm_service.generate_sql(request.question, schema_context, history=history)
        logger.info(f"Generated SQL:\n{generated_sql}")
        
        # 3. Execute SQL
        logger.info("\n=== STEP 3: EXECUTING SQL ON DATABASE ===")
        sql_exec_start = time.time()
        exec_result = execute_sql(generated_sql)
        sql_exec_time = time.time() - sql_exec_start
        logger.info(f"SQL execution time: {sql_exec_time:.4f}s | type: {exec_result['query_type']}")

        results = exec_result["rows"]
        row_count = len(results) if isinstance(results, list) else 1
        logger.info(f"Query returned {row_count} row(s).")
        logger.info(f"Results sample (first 2 rows):\n{json.dumps(results[:2] if isinstance(results, list) else results, indent=2, default=str)}\n")

        # 3.5 — If a DDL statement ran (CREATE TABLE / ALTER TABLE), sync new schema into ChromaDB
        if exec_result.get("ddl_executed"):
            logger.info("\n=== STEP 3.5: SYNCING SCHEMA TO VECTOR STORE ===")
            new_tables = extract_table_names_from_sql(generated_sql)
            logger.info(f"Tables detected in DDL: {new_tables or 'unknown — syncing all'}")
            synced = sync_tables_to_schema(new_tables if new_tables else None)
            logger.info(f"Schema sync complete. {synced} table(s) upserted into ChromaDB.")
            # Notify all SSE clients that the schema has changed
            sse_broadcaster.notify_schema_changed()
            logger.info("Schema change event broadcast to SSE clients.")


        # 3.6 Store the successful chat message
        store_chat_message(request.question, generated_sql)
        
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.4f}s")
        
        # 4. Return results
        return {
            "sql": generated_sql,
            "results": results
        }
    except SQLExecutorError as sqle:
        logger.error(f"SQL execution error: {str(sqle)}")
        raise HTTPException(status_code=400, detail={"error": "SQL Error", "message": str(sqle)})
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Internal Error", "message": str(e)})

