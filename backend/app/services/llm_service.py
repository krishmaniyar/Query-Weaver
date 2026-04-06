import time

import json
import logging
# from cerebras.cloud.sdk import Cerebras  # Commented out — switched to Groq
from groq import Groq
from app.config import config

from app.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# MySQL-specific prompt rules
# ---------------------------------------------------------------------------
_MYSQL_RULES = """\
You are a MySQL SQL expert.

Generate a valid MySQL-compatible SQL query based on the user's question.

Use ONLY the provided tables and columns.

IMPORTANT — MySQL-specific rules (strictly follow these):
- Generate ONLY MySQL-compatible SQL. Do not use SQLite syntax.
- Date/time functions: use NOW() for current datetime, CURDATE() for current date.
- Date arithmetic: use DATE_SUB(NOW(), INTERVAL N DAY/MONTH/YEAR) for past dates.
  Example: DATE_SUB(NOW(), INTERVAL 6 MONTH)  NOT  date('now', '-6 months')
- Do NOT use INTERVAL as a standalone keyword without DATE_SUB/DATE_ADD.
- String concatenation: use CONCAT(a, b) instead of || operator.
- Case-insensitive search: use LOWER(column) LIKE LOWER('%value%').
- For INSERT statements, use INSERT IGNORE INTO instead of INSERT INTO.
  This safely skips rows that would violate a UNIQUE or PRIMARY KEY constraint.
- Use AUTO_INCREMENT for auto-incrementing primary keys, NOT AUTOINCREMENT.
- Use INT, VARCHAR, DECIMAL, DATETIME types (not TEXT, REAL, INTEGER).
- Do NOT use strftime(), date('now', ...), or any SQLite-only functions.
- Do NOT use INSERT OR IGNORE — use INSERT IGNORE (MySQL syntax).
- Do NOT use :: for type casting — use CAST(x AS TYPE) instead.
- Do NOT use RETURNING clause — MySQL does not support it.
- Do NOT use reserved words like 'rank', 'order', or 'system' as column aliases. If you must, wrap them in backticks (e.g. AS `rank`). Prefer using safe aliases like 'rnk' or 'ranking'.
- Use standard aggregation, JOINs, subqueries, and CTEs — those are all supported.
- Always end SQL statements with a semicolon.
- You may return multiple SQL statements separated by semicolons if completing the user request requires it (e.g., inserting to multiple tables).
"""

_DB_RULES = {
    "mysql": _MYSQL_RULES,
}


class LLMService:
    def __init__(self):
        # --- Cerebras (commented out) ---
        # self.client = Cerebras(api_key=config.CEREBRAS_API_KEY)
        # self.model_name = "gpt-oss-120b"

        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model_name = "llama-3.3-70b-versatile"
        # self.model_name = "openai/gpt-oss-120b"
        self.db_type = config.DB_TYPE

    def generate_sql(self, question: str, schema_context: list, history: list = None, extra_data: dict = None) -> tuple:
        """
        Generates a SQL query based on the user's question, database schema, and conversational history.
        Returns tuple of (sql_query, generation_time_seconds)
        """
        generation_start = time.time()
        
        schema_context_str = json.dumps(schema_context, indent=2)
        history_str = json.dumps(history, indent=2) if history else "[]"
        # Select the appropriate rules for the configured database type
        db_rules = _DB_RULES.get(self.db_type, _MYSQL_RULES)

        if extra_data and "column" in extra_data and "values" in extra_data:
            column_name = extra_data["column"]
            values_list = "\n".join(extra_data["values"])
            extra_data_section = f"""
Additional Data (STRICT INPUT):

The following values are retrieved directly from the database.

Column: {column_name}

Values:
{values_list}

Rules:
- The values list is COMPLETE and comes from the database
- You MUST use ALL values in your query
- Do NOT ignore any value
- Do NOT use only sample rows
- Do NOT hallucinate or invent values

If generating CASE statements:
- Include one WHEN clause for EACH value

If any value is ignored, the answer is INVALID.
"""
        else:
            extra_data_section = ""

        prompt = f"""{db_rules}

Context from previous queries:
{history_str}

Schema:
{schema_context_str}
{extra_data_section}
User question:
{question}

Return ONLY the raw SQL query, no explanation, no markdown.
"""
        logger.info("\n--- CONSTRUCTED LLM PROMPT ---")
        logger.info(prompt)
        logger.info("------------------------------")

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4096
        )
        
        generation_time = time.time() - generation_start
        logger.info(f"\n*** LLM GENERATION TIME: {generation_time:.4f}s ***")
        
        # Extract the SQL string from the response
        raw_response_content = response.choices[0].message.content.strip()
        logger.info("\n--- RAW LLM RESPONSE ---")
        logger.info(raw_response_content)
        logger.info("------------------------")
        
        sql_query = raw_response_content
        
        # Clean up common markdown block formatting if present
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        elif sql_query.startswith("```"):
            sql_query = sql_query[3:]
            
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
            
        return sql_query.strip(), generation_time
