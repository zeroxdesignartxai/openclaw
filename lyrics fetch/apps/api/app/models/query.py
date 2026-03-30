from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from uuid import UUID


class QueryRequest(BaseModel):
    input: str = Field(..., description="User input string")
    category: Optional[str] = None
    user_data: Optional[Any] = None


class QueryResponse(BaseModel):
    query_id: UUID
    answer: str
    meta: Dict[str, Any] = {}


class StoredQuery(BaseModel):
    id: UUID
    answer: str
    meta: Dict[str, Any]
