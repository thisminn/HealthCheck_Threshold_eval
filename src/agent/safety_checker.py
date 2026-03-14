URGENT_TERMS = ["흉통", "호흡곤란", "실신", "의식저하"]

def apply_safety_check(query: str, answer: str) -> str:
    if any(term in query for term in URGENT_TERMS):
        return "지금 말한 증상은 일반 정보로 넘기기보다 바로 진료가 필요한 상황일 수 있어. 가까운 의료기관이나 응급 평가를 우선 고려하는 게 안전해."
    return answer