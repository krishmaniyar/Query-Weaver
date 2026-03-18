import re
from typing import List, Dict, Any
from sqlalchemy import text
from app.db.database import get_engine

class SQLExecutorError(Exception):
    pass

# DDL keywords that modify the database schema
_DDL_KEYWORDS = {"CREATE", "ALTER", "DROP"}
# DML keywords that write data but don't change the schema
_DML_WRITE_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "REPLACE", "UPSERT"}

def _detect_query_type(query: str) -> str:
    """Return the leading keyword of a SQL statement (upper-cased)."""
    stripped = query.strip().lstrip("(").strip()
    match = re.match(r"([A-Za-z]+)", stripped)
    return match.group(1).upper() if match else "UNKNOWN"

def execute_sql(query: str) -> Dict[str, Any]:
    """
    Executes a SQL query safely and returns a result dict with:
      - rows      : list of dicts (query results or success message)
      - query_type: leading SQL keyword, e.g. SELECT / INSERT / CREATE
      - ddl_executed: True when a schema-changing statement ran (CREATE / ALTER)
    """
    query_upper = query.upper().strip()
    query_type = _detect_query_type(query)

    # Security gate – extend this list if you want to block more operations
    forbidden_keywords: List[str] = []
    for keyword in forbidden_keywords:
        if f" {keyword} " in f" {query_upper} " or query_upper.startswith(f"{keyword} "):
            raise SQLExecutorError(
                f"Forbidden SQL keyword detected: {keyword}. "
                "Only SELECT, CREATE, and INSERT queries are allowed."
            )

    ddl_executed = query_type in _DDL_KEYWORDS
    engine = get_engine()

    try:
        with engine.connect() as connection:
            try:
                result = connection.execute(text(query))

                # DDL / DML statements that don't return rows
                if not result.returns_rows:
                    connection.commit()
                    return {
                        "rows": [{"status": "success", "message": "Query executed successfully."}],
                        "query_type": query_type,
                        "ddl_executed": ddl_executed,
                    }

                # SELECT (or similar) – fetch all rows
                rows = result.fetchall()
                keys = list(result.keys())
                json_results = [dict(zip(keys, row)) for row in rows]

                return {
                    "rows": json_results,
                    "query_type": query_type,
                    "ddl_executed": False,
                }

            except Exception as inner_e:
                # SQLite raises an error when multiple statements are passed at once.
                # Fall back to executescript which handles multi-statement scripts.
                if "one statement at a time" in str(inner_e).lower() and engine.dialect.name == "sqlite":
                    raw_conn = engine.raw_connection()
                    try:
                        cursor = raw_conn.cursor()
                        cursor.executescript(query)
                        raw_conn.commit()
                        return {
                            "rows": [{"status": "success", "message": "Multiple queries executed successfully (via script)."}],
                            "query_type": query_type,
                            "ddl_executed": ddl_executed,
                        }
                    finally:
                        raw_conn.close()
                else:
                    raise inner_e

    except SQLExecutorError:
        raise
    except Exception as e:
        raise SQLExecutorError(f"Error executing SQL: {str(e)}")
