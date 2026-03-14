from typing import Any, Optional
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    question_id: str
    question_text: str
    domain: Optional[str] = None
    input_value: Optional[str] = None
    rule_ref: Optional[str] = None
    response_mode: Optional[str] = None
    final_priority_action: Optional[str] = None


class RuleChunk(BaseModel):
    chunk_id: str
    rule_id: str
    domain: Optional[str] = None
    text: str
    source_doc: Optional[str] = None
    source_page: Optional[str] = None


class CorpusChunk(BaseModel):
    chunk_id: str
    rule_id: str
    domain: Optional[str] = None
    text: str
    source_doc: Optional[str] = None
    source_page: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)


class RetrievedDoc(BaseModel):
    chunk_id: str
    rule_id: str
    text: str
    score: float
    domain: Optional[str] = None
    source_doc: Optional[str] = None
    source_page: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)


class LLMOutput(BaseModel):
    predicted_bp_class: Optional[str] = None
    predicted_glu_class: Optional[str] = None
    predicted_action: Optional[str] = None
    answer: str
    notes: Optional[str] = None


class PipelineResult(BaseModel):
    system_name: str
    question_id: str
    question_text: str
    retrieved_context: list[dict] = Field(default_factory=list)
    reranked_context: list[dict] = Field(default_factory=list)
    predicted_bp_class: Optional[str] = None
    predicted_glu_class: Optional[str] = None
    predicted_action: Optional[str] = None
    answer: str
    notes: Optional[str] = None