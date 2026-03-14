# PYTHONPATH=. python -m tests.test_04_answer_generator

from src.agent.answer_generator import generate_answer
from src.agent.schemas import (
    QueryClassification,
    SelectedEvidence,
    ThresholdInterpretation,
)

def run_case(status: str):
    classification = QueryClassification(
        query_type="threshold_check",
        needs_numeric_interpretation=True,
        needs_action_guidance=True,
        safety_flag=False
    )

    evidence = [
        SelectedEvidence(
            chunk_id="rule_001",
            text="공복혈당 100~125는 공복혈당장애 범주",
            score=0.88,
            reason="직접 기준 포함",
            metadata={"source": "healthcheck_rule"}
        )
    ]

    interpretation = ThresholdInterpretation(
        status=status,
        matched_rule="공복혈당 100~125는 공복혈당장애 범주" if status != "insufficient" else None,
        confidence="high" if status != "insufficient" else "low",
        missing_fields=[] if status != "insufficient" else ["numeric_value"]
    )

    answer = generate_answer(
        query="공복혈당 110이면 괜찮아?",
        classification=classification,
        evidence=evidence,
        interpretation=interpretation,
    )

    print(f"\n[status] {status}")
    print(answer)

def main():
    print("=== answer_generator test ===")
    for status in ["normal", "borderline", "high_risk", "insufficient", "needs_llm_interpretation"]:
        run_case(status)

if __name__ == "__main__":
    main()