from dataclasses import dataclass
from typing import List, Optional

from src.agent.simple_rag_agent import SimpleRAGAgent
from src.agent.v3_retriever_adapter import V3RetrieverAdapter


BP_DOMAIN = "blood_pressure"  # 실제 domain 문자열이 다르면 여기만 수정


@dataclass
class EvalCase:
    case_id: int
    query: str
    expected_query_type: str
    expected_status: str
    expected_action_type: str
    expected_answer_keywords: List[str]
    expected_safety_flag: Optional[bool] = None


EVAL_CASES = [
    EvalCase(
        case_id=1,
        query="혈압 118/78이면 괜찮아?",
        expected_query_type="threshold_check",
        expected_status="normal",
        expected_action_type="self_care",
        expected_answer_keywords=["정상"],
    ),
    EvalCase(
        case_id=2,
        query="혈압 119/79면 어때?",
        expected_query_type="threshold_check",
        expected_status="normal",
        expected_action_type="self_care",
        expected_answer_keywords=["정상"],
    ),
    EvalCase(
        case_id=3,
        query="혈압 120/80이면 괜찮아?",
        expected_query_type="threshold_check",
        expected_status="borderline",
        expected_action_type="recheck",
        expected_answer_keywords=["경계", "추적"],
    ),
    EvalCase(
        case_id=4,
        query="혈압 130/85면 어떤 상태야?",
        expected_query_type="threshold_check",
        expected_status="borderline",
        expected_action_type="recheck",
        expected_answer_keywords=["경계", "관리"],
    ),
    EvalCase(
        case_id=5,
        query="혈압이 139/89야.",
        expected_query_type="threshold_check",
        expected_status="borderline",
        expected_action_type="recheck",
        expected_answer_keywords=["경계"],
    ),
    EvalCase(
        case_id=6,
        query="혈압 140/90이면 병원 가야 해?",
        expected_query_type="threshold_check",
        expected_status="high_risk",
        expected_action_type="consult_clinic",
        expected_answer_keywords=["의료진", "진료"],
    ),
    EvalCase(
        case_id=7,
        query="혈압 150/95면 위험한 편이야?",
        expected_query_type="threshold_check",
        expected_status="high_risk",
        expected_action_type="consult_clinic",
        expected_answer_keywords=["높은", "진료"],
    ),
    EvalCase(
        case_id=8,
        query="수축기 135 이완기 88이야.",
        expected_query_type="threshold_check",
        expected_status="borderline",
        expected_action_type="recheck",
        expected_answer_keywords=["경계"],
    ),
    EvalCase(
        case_id=9,
        query="최고혈압 145 최저혈압 92야.",
        expected_query_type="threshold_check",
        expected_status="high_risk",
        expected_action_type="consult_clinic",
        expected_answer_keywords=["의료진", "진료"],
    ),
    EvalCase(
        case_id=10,
        query="130/85인데 괜찮아?",
        expected_query_type="threshold_check",
        expected_status="borderline",
        expected_action_type="recheck",
        expected_answer_keywords=["경계"],
    ),
    EvalCase(
        case_id=11,
        query="혈압 118/78인데 관리 어떻게 해?",
        expected_query_type="threshold_check",
        expected_status="normal",
        expected_action_type="self_care",
        expected_answer_keywords=["정상"],
    ),
    EvalCase(
        case_id=12,
        query="혈압이랑 공복혈당 중 뭐가 더 위험해?",
        expected_query_type="comparison",
        expected_status="not_applicable",
        expected_action_type="insufficient_info",
        expected_answer_keywords=["비교", "현재 버전"],
    ),
    EvalCase(
        case_id=13,
        query="혈압 수치가 있는데 해석해줘.",
        expected_query_type="general_info",
        expected_status="not_applicable",
        expected_action_type="insufficient_info",
        expected_answer_keywords=["120/80", "기준"],
    ),
    EvalCase(
        case_id=14,
        query="혈압 130/85인데 흉통이 있어. 괜찮아?",
        expected_query_type="threshold_check",
        expected_status="borderline",
        expected_action_type="urgent_care",
        expected_answer_keywords=["바로 진료", "응급"],
        expected_safety_flag=True,
    ),
    EvalCase(
        case_id=15,
        query="혈압 140인데 괜찮아?",
        expected_query_type="threshold_check",
        expected_status="insufficient",
        expected_action_type="insufficient_info",
        expected_answer_keywords=["120/80", "수축기"],
    ),
]


def build_agent() -> SimpleRAGAgent:
    retriever = V3RetrieverAdapter(default_domain=BP_DOMAIN)
    return SimpleRAGAgent(retriever=retriever)


def contains_any_keyword(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def main():
    agent = build_agent()

    total = len(EVAL_CASES)
    query_type_correct = 0
    status_correct = 0
    action_correct = 0
    answer_direction_correct = 0
    safety_flag_correct = 0
    safety_flag_total = 0

    failed_cases = []

    print("=== BP MINI EVALSET ===")

    for case in EVAL_CASES:
        result = agent.run(case.query)

        actual_query_type = result.classification.query_type
        actual_status = result.interpretation.status
        actual_action_type = result.action_type
        actual_answer = result.answer
        actual_safety_flag = result.classification.safety_flag

        qt_ok = actual_query_type == case.expected_query_type
        st_ok = actual_status == case.expected_status
        ac_ok = actual_action_type == case.expected_action_type
        ans_ok = contains_any_keyword(actual_answer, case.expected_answer_keywords)

        if qt_ok:
            query_type_correct += 1
        if st_ok:
            status_correct += 1
        if ac_ok:
            action_correct += 1
        if ans_ok:
            answer_direction_correct += 1

        sf_ok = None
        if case.expected_safety_flag is not None:
            safety_flag_total += 1
            sf_ok = actual_safety_flag == case.expected_safety_flag
            if sf_ok:
                safety_flag_correct += 1

        case_failed = not (qt_ok and st_ok and ac_ok and ans_ok and (sf_ok is not False))
        if case_failed:
            failed_cases.append(
                {
                    "case_id": case.case_id,
                    "query": case.query,
                    "expected_query_type": case.expected_query_type,
                    "actual_query_type": actual_query_type,
                    "expected_status": case.expected_status,
                    "actual_status": actual_status,
                    "expected_action_type": case.expected_action_type,
                    "actual_action_type": actual_action_type,
                    "expected_answer_keywords": case.expected_answer_keywords,
                    "actual_answer": actual_answer,
                    "expected_safety_flag": case.expected_safety_flag,
                    "actual_safety_flag": actual_safety_flag,
                }
            )

        print(f"\n--- CASE {case.case_id} ---")
        print(f"Q: {case.query}")
        print(
            f"query_type     | expected={case.expected_query_type} actual={actual_query_type} | {'PASS' if qt_ok else 'FAIL'}"
        )
        print(
            f"status         | expected={case.expected_status} actual={actual_status} | {'PASS' if st_ok else 'FAIL'}"
        )
        print(
            f"action_type    | expected={case.expected_action_type} actual={actual_action_type} | {'PASS' if ac_ok else 'FAIL'}"
        )
        print(
            f"answer_dir     | expected_keywords={case.expected_answer_keywords} | {'PASS' if ans_ok else 'FAIL'}"
        )
        if sf_ok is not None:
            print(
                f"safety_flag    | expected={case.expected_safety_flag} actual={actual_safety_flag} | {'PASS' if sf_ok else 'FAIL'}"
            )
        print(f"answer         | {actual_answer}")

    print("\n=== SUMMARY ===")
    print(
        f"query_type accuracy      : {query_type_correct}/{total} = {query_type_correct/total:.2%}"
    )
    print(
        f"status accuracy          : {status_correct}/{total} = {status_correct/total:.2%}"
    )
    print(
        f"action_type accuracy     : {action_correct}/{total} = {action_correct/total:.2%}"
    )
    print(
        f"answer direction accuracy: {answer_direction_correct}/{total} = {answer_direction_correct/total:.2%}"
    )
    if safety_flag_total > 0:
        print(
            f"safety_flag accuracy     : {safety_flag_correct}/{safety_flag_total} = {safety_flag_correct/safety_flag_total:.2%}"
        )

    if failed_cases:
        print("\n=== FAILED CASES ===")
        for failed in failed_cases:
            print(f"\n[CASE {failed['case_id']}] {failed['query']}")
            print(
                f"- query_type   : expected={failed['expected_query_type']} / actual={failed['actual_query_type']}"
            )
            print(
                f"- status       : expected={failed['expected_status']} / actual={failed['actual_status']}"
            )
            print(
                f"- action_type  : expected={failed['expected_action_type']} / actual={failed['actual_action_type']}"
            )
            print(
                f"- answer_kw    : expected one of {failed['expected_answer_keywords']}"
            )
            if failed["expected_safety_flag"] is not None:
                print(
                    f"- safety_flag  : expected={failed['expected_safety_flag']} / actual={failed['actual_safety_flag']}"
                )
            print(f"- answer       : {failed['actual_answer']}")
    else:
        print("\nALL CASES PASSED")


if __name__ == "__main__":
    main()