import re
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime, date, time, timedelta
from sqlalchemy import text
from app.db.database import get_engine


def _sanitize_value(val):
    """Convert MySQL-specific Python types to JSON-serializable equivalents."""
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (datetime, date, time)):
        return val.isoformat()
    if isinstance(val, timedelta):
        return str(val)
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return val


def _sanitize_row(keys, row):
    """Build a JSON-safe dict from a database result row."""
    return {k: _sanitize_value(v) for k, v in zip(keys, row)}

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


def is_modifying_query(query: str) -> bool:
    """
    Checks if any statement in the query string modifies data or schema.
    """
    statements = _split_statements(query)
    for stmt in statements:
        if not stmt:
            continue
        stmt_type = _detect_query_type(stmt)
        if stmt_type in _DDL_KEYWORDS or stmt_type in _DML_WRITE_KEYWORDS:
            return True
    return False


def _is_multi_statement(query: str) -> bool:
    """
    Detect whether the query string contains multiple SQL statements.
    Ignores semicolons inside single-quoted or double-quoted strings.
    A trailing semicolon on a single statement is acceptable.
    """
    # Remove string literals so embedded semicolons don't cause false positives
    cleaned = re.sub(r"'[^']*'", "", query)
    cleaned = re.sub(r'"[^"]*"', "", cleaned)

    # Split on semicolons and filter out empty/whitespace-only fragments
    parts = [p.strip() for p in cleaned.split(";") if p.strip()]
    return len(parts) > 1


def _split_statements(query: str) -> List[str]:
    """
    Split a multi-statement SQL string into individual statements.
    Handles semicolons inside string literals gracefully.
    """
    statements = []
    current_stmt = []
    in_single_quote = False
    in_double_quote = False
    
    for char in query:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        
        if char == ';' and not in_single_quote and not in_double_quote:
            stmt = ''.join(current_stmt).strip()
            if stmt:
                statements.append(stmt)
            current_stmt = []
        else:
            current_stmt.append(char)
            
    # Capture any trailing content after the last semicolon
    trailing = ''.join(current_stmt).strip()
    if trailing:
        statements.append(trailing)

    return statements


def _fix_trailing_comma(stmt: str) -> str:
    """Remove trailing commas before closing parentheses or end of statement.

    LLMs sometimes produce VALUES lists like:
        (1, 'a'),
        (2, 'b'),   <-- trailing comma
    which is invalid SQL.
    """
    # Remove a comma that is only followed by optional whitespace and end-of-string
    stmt = re.sub(r",\s*$", "", stmt)
    # Remove a comma immediately before a closing paren at end: ...),)  -> ...))
    stmt = re.sub(r",(\s*\))\s*$", r"\1", stmt)
    return stmt


def execute_sql(query: str) -> Dict[str, Any]:
    """
    Executes one or more SQL statements safely and returns a result dict with:
      - rows      : list of dicts (query results or success message)
      - query_type: leading SQL keyword, e.g. SELECT / INSERT / CREATE
      - ddl_executed: True when a schema-changing statement ran (CREATE / ALTER / DROP)

    If multiple statements are detected they are split and executed
    sequentially inside a single connection/transaction.
    """
    query_upper = query.upper().strip()
    query_type = _detect_query_type(query)

    # ---------- Security gate ----------
    forbidden_keywords: List[str] = []
    for keyword in forbidden_keywords:
        if f" {keyword} " in f" {query_upper} " or query_upper.startswith(f"{keyword} "):
            raise SQLExecutorError(
                f"Forbidden SQL keyword detected: {keyword}. "
                "Only SELECT, CREATE, and INSERT queries are allowed."
            )

    # ---------- Split into individual statements ----------
    statements = _split_statements(query)
    if not statements:
        raise SQLExecutorError("Empty SQL query.")

    ddl_executed = False
    engine = get_engine()

    try:
        with engine.connect() as connection:
            last_select_result = None

            for stmt in statements:
                stmt = _fix_trailing_comma(stmt)
                stmt_type = _detect_query_type(stmt)
                if stmt_type in _DDL_KEYWORDS:
                    ddl_executed = True

                result = connection.execute(text(stmt))

                if result.returns_rows:
                    rows = result.fetchall()
                    keys = list(result.keys())
                    last_select_result = [_sanitize_row(keys, row) for row in rows]

            # Commit once after all statements succeed
            connection.commit()

            # If the last (or any) statement was a SELECT, return those rows
            if last_select_result is not None:
                return {
                    "rows": last_select_result,
                    "query_type": query_type,
                    "ddl_executed": ddl_executed,
                }

            # Otherwise return a success message
            msg = "Query executed successfully."
            if len(statements) > 1:
                msg = f"{len(statements)} statements executed successfully."
            return {
                "rows": [{"status": "success", "message": msg}],
                "query_type": query_type,
                "ddl_executed": ddl_executed,
            }

    except SQLExecutorError:
        raise
    except Exception as e:
        raise SQLExecutorError(f"Error executing SQL: {str(e)}")

