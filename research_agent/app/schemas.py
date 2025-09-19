from datetime import datetime
from pydantic import BaseModel
from typing import List


class ResearchPayload(BaseModel):
    query: str


class Source(BaseModel):
    title: str
    url: str


class ResearchResponse(BaseModel):
    query: str
    final_summary: str
    sources: List[Source]


class ResearchRecord(BaseModel):
    query: str
    final_summary: str
    sources: List[Source]
    created_at: datetime


class ResearchHistoryResponse(BaseModel):
    items: List[ResearchRecord]
