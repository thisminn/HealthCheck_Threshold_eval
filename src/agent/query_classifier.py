# 사용자의 질문을 보고 어떤 종류의 질문인지 먼저 분류하는 역할

import re
from .schemas import QueryClassification

NUMERIC_TARGET_TERMS = [
    "공복혈당", "혈당", "혈압", "수축기", "이완기",
    "중성지방", "총콜레스테롤", "콜레스테롤", "hdl", "ldl",
    "bmi", "허리둘레", "ast", "alt", "감마지티피",
    "키", "몸무게", "체중", "수치", "기준", "판정", "정상", "경계"
]

ACTION_HINTS = [
    "병원", "진료", "재검", "검사", "관리", "조심",
    "해야", "어떻게", "권고", "주의", "괜찮아", "문제", "위험"
]

COMPARISON_HINTS = [
    "비교", "둘 중", "중 뭐", "중 어떤", "중 어느",
    "뭐가 더", "어떤 게 더", "어느 게 더"
]

SAFETY_TERMS = [
    "흉통", "호흡곤란", "실신", "의식저하", "자살", "죽고싶"
]

def classify_query(query: str) -> QueryClassification:
    q = query.strip().lower()

    has_number = bool(re.search(r"\d+(\.\d+)?", q))
    has_numeric_target = any(term in q for term in NUMERIC_TARGET_TERMS)
    has_action_hint = any(term in q for term in ACTION_HINTS)
    has_comparison_hint = any(term in q for term in COMPARISON_HINTS)
    has_pair_connector = any(term in q for term in ["이랑", "랑", "와", "과", "vs", "대비"])
    safety_flag = any(term in q for term in SAFETY_TERMS)

    if has_comparison_hint or (has_pair_connector and "더" in q):
        query_type = "comparison"
    elif has_number and has_numeric_target:
        query_type = "threshold_check"
    elif has_action_hint:
        query_type = "followup_action"
    else:
        query_type = "general_info"

    return QueryClassification(
        query_type=query_type,
        needs_numeric_interpretation=(query_type == "threshold_check"),
        needs_action_guidance=(query_type in ["threshold_check", "followup_action"]),
        safety_flag=safety_flag
    )