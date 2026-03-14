# PYTHONPATH=. python -m tests.test_03_threshold_interpreter

from src.agent.threshold_interpreter import interpret_threshold
from src.agent.schemas import SelectedEvidence

def run_case(query: str):
    evidence = [
        SelectedEvidence(
            chunk_id="rule_001",
            text="공복혈당 100 미만은 정상, 100~125는 공복혈당장애, 126 이상은 당뇨병 의심 범주",
            score=0.91,
            reason="직접 기준 포함",
            metadata={"source": "healthcheck_rule"}
        )
    ]

    result = interpret_threshold(query, evidence)
    print(f"\n[Q] {query}")
    print(result.model_dump())

def main():
    print("=== threshold_interpreter test ===")
    run_case("공복혈당 95면 괜찮아?")
    run_case("공복혈당 110이면 어떤 상태야?")
    run_case("공복혈당 126이면 병원 가야 해?")
    run_case("공복혈당 수치가 있는데 해석해줘")

if __name__ == "__main__":
    main()