from pydantic import BaseModel
from typing import List, Dict

class ResearchPayload(BaseModel):
    query: str

class Source(BaseModel):
    title: str
    url: str

class ResearchResponse(BaseModel):
    query: str
    final_summary: str
    sources: List[Source]