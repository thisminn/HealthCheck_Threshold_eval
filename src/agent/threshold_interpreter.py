import re
from typing import List
from .schemas import SelectedEvidence, ThresholdInterpretation

def extract_first_number(query: str):
    m = re.search(r"(\d+(\.\d+)?)", query)
    if not m:
        return None
    return float(m.group(1))

def is_fasting_glucose_query(q: str) -> bool:
    return ("공복혈당" in q) or ("혈당" in q)

def interpret_threshold(query: str, evidence: List[SelectedEvidence]) -> ThresholdInterpretation:
    value = extract_first_number(query)
    if value is None:
        return ThresholdInterpretation(
            status="insufficient",
            matched_rule=None,
            confidence="low",
            missing_fields=["numeric_value"]
        )

    q = query

    if is_fasting_glucose_query(q):
        if value < 100:
            return ThresholdInterpretation(
                status="normal",
                matched_rule="공복혈당 100 미만은 정상 범주",
                confidence="high"
            )
        elif 100 <= value <= 125:
            return ThresholdInterpretation(
                status="borderline",
                matched_rule="공복혈당 100~125는 공복혈당장애 범주",
                confidence="high"
            )
        else:
            return ThresholdInterpretation(
                status="high_risk",
                matched_rule="공복혈당 126 이상은 당뇨병 의심 범주",
                confidence="high"
            )

    return ThresholdInterpretation(
        status="needs_llm_interpretation",
        matched_rule=evidence[0].text[:120] if evidence else None,
        confidence="medium"
    )