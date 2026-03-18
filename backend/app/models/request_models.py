from typing import Union, Optional, List
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    selected_tables: Optional[List[str]] = None

class QueryResponse(BaseModel):
    sql: str
    results: Union[list, dict]
