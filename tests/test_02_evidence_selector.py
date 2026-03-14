# PYTHONPATH=. python -m tests.test_02_evidence_selector

from src.agent.evidence_selector import select_evidence
from src.agent.schemas import RetrievedChunk

def main():
    query = "공복혈당 110이면 괜찮아?"

    chunks = [
        RetrievedChunk(
            chunk_id="doc_001",
            text="공복혈당은 혈액 내 포도당 농도를 의미한다.",
            score=0.84,
            metadata={"source": "general_info"}
        ),
        RetrievedChunk(
            chunk_id="rule_001",
            text="공복혈당 100~125는 공복혈당장애 범주로 본다.",
            score=0.80,
            metadata={"source": "healthcheck_rule", "rule_kind": "threshold"}
        ),
        RetrievedChunk(
            chunk_id="rule_002",
            text="공복혈당이 높으면 생활습관 조절과 추적 확인이 필요할 수 있다.",
            score=0.78,
            metadata={"source": "healthcheck_rule", "rule_kind": "guidance"}
        ),
    ]

    selected = select_evidence(query, chunks, top_n=2)

    print("=== evidence_selector test ===")
    for i, ev in enumerate(selected, start=1):
        print(f"\n[selected #{i}]")
        print(ev.model_dump())

if __name__ == "__main__":
    main()