from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import List, Literal, Optional


class ResearchPayload(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    query: str
    # Optionally override env MODEL_NAME/TEMPERATURE per-request
    model_name: Optional[Literal["grok", "llama", "deepseek", "google"]] = Field(
        default=None,
        description="Choose one of the free models: grok, llama, deepseek, google",
        validation_alias=AliasChoices("model_name", "modelName", "model"),
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 - 2.0)",
        validation_alias=AliasChoices("temperature", "temp"),
    )


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
