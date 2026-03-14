from typing import List
from .schemas import QueryClassification, SelectedEvidence, ThresholdInterpretation

import re

def has_number(text: str) -> bool:
    return bool(re.search(r"\d+(\.\d+)?", text))

def looks_like_interpret_request_without_number(query: str) -> bool:
    q = query.strip()
    interpret_terms = ["해석", "판정", "괜찮아", "어떤 상태", "정상", "경계", "위험", "수치"]
    return (not has_number(q)) and any(term in q for term in interpret_terms)


def generate_answer(query, classification, evidence, interpretation) -> str:
    if classification.safety_flag:
        return "지금 증상은 일반 정보로 넘기기보다 빠르게 진료가 필요한 상황일 수 있어. 가까운 의료기관에서 확인받는 게 안전해."

    if classification.query_type == "general_info":
        if looks_like_interpret_request_without_number(query):
            return "수치 해석을 하려면 실제 검사 수치가 필요해. 공복혈당 값을 같이 알려주면 기준에 맞춰 다시 볼 수 있어."

        if evidence and evidence[0].score > 0.4 and "관련 정보를 찾지 못했다" not in evidence[0].text:
            return evidence[0].text

        return "지금 가진 근거만으로는 해당 항목을 설명할 정보를 충분히 찾지 못했어."

    if classification.query_type == "comparison":
        return "지금 버전은 비교형 질문보다는 개별 검사 수치 해석에 맞춰져 있어. 각각의 수치나 항목을 따로 보면 더 정확하게 해석할 수 있어."

    if classification.query_type == "followup_action" and interpretation.status == "not_applicable":
        if evidence and evidence[0].score > 0.4 and "관련 정보를 찾지 못했다" not in evidence[0].text:
            return "관련 근거를 보면 후속 확인이나 관리 방향을 함께 보는 게 좋아."
        return "지금 정보만으로는 바로 행동을 단정하기 어렵고, 증상이나 검사 결과를 조금 더 구체적으로 봐야 해."

    if interpretation.status == "insufficient":
        return "지금 정보만으로는 정확히 해석하기 어려워. 수치나 검사 항목을 같이 알려주면 기준에 맞춰 다시 볼 수 있어."

    if interpretation.status == "normal":
        return "해당 수치는 현재 기준상 정상 범위로 볼 수 있어. 다만 한 번의 결과만으로 단정하기보다는 전체 검사 맥락과 함께 보는 게 좋아."

    if interpretation.status == "borderline":
        return "해당 수치는 정상보다 높은 경계 범위로 볼 수 있어. 기준표에서는 이 구간을 주의가 필요한 범주로 해석할 수 있어서 생활습관 관리와 추적 확인이 중요해."

    if interpretation.status == "high_risk":
        return "해당 수치는 기준상 높은 범주에 해당할 수 있어. 정확한 판단은 의료진 확인이 필요하고, 추가 검사나 진료 상담이 권장될 수 있어."

    return "관련 근거를 찾았지만 자동 해석은 아직 제한적이야. 질문한 항목의 기준과 권고를 함께 확인하는 게 좋아."