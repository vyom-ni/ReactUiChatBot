from typing import Optional,List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]
    session_id: str
    timestamp: str