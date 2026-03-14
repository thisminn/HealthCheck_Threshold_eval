from .query_classifier import classify_query
from .evidence_selector import select_evidence
from .threshold_interpreter import interpret_threshold
from .answer_generator import generate_answer
from .safety_checker import apply_safety_check
from .schemas import AgentOutput, RetrievedChunk, ThresholdInterpretation


import re

def has_number(text: str) -> bool:
    return bool(re.search(r"\d+(\.\d+)?", text))

def looks_like_interpret_request_without_number(query: str) -> bool:
    interpret_terms = ["해석", "판정", "괜찮아", "어떤 상태", "정상", "경계", "위험", "수치"]
    return (not has_number(query)) and any(term in query for term in interpret_terms)


class SimpleRAGAgent:
    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, query: str) -> AgentOutput:
        classification = classify_query(query)

        raw_chunks = self.retriever.search(query=query, top_k=5)
        retrieved = [RetrievedChunk(**c) if isinstance(c, dict) else c for c in raw_chunks]

        selected = select_evidence(query, retrieved, top_n=2)

        if classification.query_type == "threshold_check":
            interpretation = interpret_threshold(query, selected)
        else:
            interpretation = ThresholdInterpretation(
                status="not_applicable",
                matched_rule=None,
                confidence="low",
                missing_fields=[]
            )

        answer = generate_answer(
            query=query,
            classification=classification,
            evidence=selected,
            interpretation=interpretation,
        )
        answer = apply_safety_check(query, answer)

        action_type = "insufficient_info"
        if classification.safety_flag:
            action_type = "urgent_care"
        elif classification.query_type == "threshold_check":
            if interpretation.status == "normal":
                action_type = "self_care"
            elif interpretation.status == "borderline":
                action_type = "recheck"
            elif interpretation.status == "high_risk":
                action_type = "consult_clinic"
            else:
                action_type = "insufficient_info"
        elif classification.query_type == "general_info":
            if looks_like_interpret_request_without_number(query):
                action_type = "insufficient_info"
            elif selected and selected[0].score > 0.4 and "관련 정보를 찾지 못했다" not in selected[0].text:
                action_type = "self_care"
            else:
                action_type = "insufficient_info"
        elif classification.query_type == "followup_action":
            action_type = "consult_clinic"

        return AgentOutput(
            answer=answer,
            action_type=action_type,
            classification=classification,
            selected_evidence=selected,
            interpretation=interpretation
        )