from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel

QueryType = Literal[
    "threshold_check",
    "followup_action",
    "general_info",
    "comparison",
    "insufficient_context"
]

ActionType = Literal[
    "self_care",
    "recheck",
    "consult_clinic",
    "urgent_care",
    "insufficient_info"
]

class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = {}

class QueryClassification(BaseModel):
    query_type: QueryType
    needs_numeric_interpretation: bool
    needs_action_guidance: bool
    safety_flag: bool

class SelectedEvidence(BaseModel):
    chunk_id: str
    text: str
    score: float
    reason: str
    metadata: Dict[str, Any] = {}

class ThresholdInterpretation(BaseModel):
    status: str
    matched_rule: Optional[str] = None
    confidence: str = "low"
    missing_fields: List[str] = []

class AgentOutput(BaseModel):
    answer: str
    action_type: ActionType
    classification: QueryClassification
    selected_evidence: List[SelectedEvidence]
    interpretation: ThresholdInterpretation