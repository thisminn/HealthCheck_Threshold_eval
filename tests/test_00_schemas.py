# PYTHONPATH=. python -m tests.test_00_schemas

from src.agent.schemas import (
    RetrievedChunk,
    QueryClassification,
    SelectedEvidence,
    ThresholdInterpretation,
    AgentOutput,
)

def main():
    chunk = RetrievedChunk(
        chunk_id="rule_001",
        text="공복혈당 100~125는 공복혈당장애 범주",
        score=0.81,
        metadata={"source": "healthcheck_rule"}
    )

    classification = QueryClassification(
        query_type="threshold_check",
        needs_numeric_interpretation=True,
        needs_action_guidance=True,
        safety_flag=False
    )

    evidence = SelectedEvidence(
        chunk_id="rule_001",
        text="공복혈당 100~125는 공복혈당장애 범주",
        score=0.89,
        reason="질문과 직접 관련된 기준 정보",
        metadata={"source": "healthcheck_rule"}
    )

    interpretation = ThresholdInterpretation(
        status="borderline",
        matched_rule="공복혈당 100~125는 공복혈당장애 범주",
        confidence="high",
        missing_fields=[]
    )

    output = AgentOutput(
        answer="공복혈당 110이면 정상보다 높은 경계 범위로 볼 수 있어.",
        action_type="recheck",
        classification=classification,
        selected_evidence=[evidence],
        interpretation=interpretation
    )

    print("=== schemas test ===")
    print(chunk.model_dump())
    print(output.model_dump())
    print("PASS")

if __name__ == "__main__":
    main()