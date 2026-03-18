import json
import logging
from cerebras.cloud.sdk import Cerebras
from app.config import config

from app.logger import setup_logger

logger = setup_logger(__name__)

class LLMService:
    def __init__(self):
        # Initialize Cerebras client using the API key from config
        self.client = Cerebras(api_key=config.CEREBRAS_API_KEY)
        self.model_name = "gpt-oss-120b"

    def generate_sql(self, question: str, schema_context: list, history: list = None) -> str:
        """
        Generates a SQL query based on the user's question, database schema, and conversational history.
        """
        schema_context_str = json.dumps(schema_context, indent=2)
        history_str = json.dumps(history, indent=2) if history else "[]"
        
        prompt = f"""You are a SQLite SQL expert.

Generate a valid SQLite-compatible SQL query based on the user's question.

Use ONLY the provided tables and columns.

IMPORTANT — SQLite-specific rules (strictly follow these):
- Date arithmetic: use date('now', '-N days/months/years') instead of CURRENT_DATE - INTERVAL 'N unit'
  Example: date('now', '-6 months')  NOT  CURRENT_DATE - INTERVAL '6 months'
- Do NOT use INTERVAL keyword — SQLite does not support it.
- Do NOT use ILIKE — use LIKE instead (SQLite LIKE is case-insensitive for ASCII by default).
- Do NOT use date_trunc(), to_char(), or extract() — use strftime() instead.
  Example: strftime('%Y-%m', order_date)  instead of  date_trunc('month', order_date)
- Do NOT use :: for type casting — use CAST(x AS TYPE) instead.
- Do NOT use RETURNING clause.
- For INSERT statements, always use INSERT OR IGNORE INTO instead of INSERT INTO.
  This safely skips rows that would violate a UNIQUE or PRIMARY KEY constraint.
- Use standard aggregation, JOINs, subqueries, and CTEs — those are all supported.

Context from previous queries:
{history_str}

Schema:
{schema_context_str}

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
            temperature=0.2
        )
        
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
            
        return sql_query.strip()

