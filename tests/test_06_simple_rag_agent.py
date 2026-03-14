# PYTHONPATH=. python -m tests.test_06_simple_rag_agent

from src.agent.simple_rag_agent import SimpleRAGAgent

class FakeRetriever:
    def search(self, query: str, top_k: int = 5):
        if "공복혈당" in query:
            return [
                {
                    "chunk_id": "rule_001",
                    "text": "공복혈당 100 미만은 정상 범주, 100~125는 공복혈당장애 범주, 126 이상은 당뇨병 의심 범주로 본다.",
                    "score": 0.86,
                    "metadata": {"source": "healthcheck_rule", "rule_kind": "threshold"}
                },
                {
                    "chunk_id": "rule_002",
                    "text": "공복혈당이 경계 범위이면 생활습관 관리와 추적 확인이 필요할 수 있다.",
                    "score": 0.81,
                    "metadata": {"source": "healthcheck_rule", "rule_kind": "guidance"}
                },
                {
                    "chunk_id": "doc_001",
                    "text": "공복혈당은 일정 시간 공복 상태에서 측정한 혈당 수치다.",
                    "score": 0.79,
                    "metadata": {"source": "general_info"}
                },
            ]
        return [
            {
                "chunk_id": "doc_999",
                "text": "관련 정보를 찾지 못했다.",
                "score": 0.2,
                "metadata": {"source": "unknown"}
            }
        ]

def run_case(agent, query: str):
    result = agent.run(query)

    print(f"\n===== QUERY: {query} =====")
    print("[classification]")
    print(result.classification.model_dump())

    print("\n[selected_evidence]")
    for ev in result.selected_evidence:
        print(ev.model_dump())

    print("\n[interpretation]")
    print(result.interpretation.model_dump())

    print("\n[action_type]")
    print(result.action_type)

    print("\n[answer]")
    print(result.answer)

def main():
    agent = SimpleRAGAgent(retriever=FakeRetriever())

    print("=== simple_rag_agent E2E test ===")
    run_case(agent, "공복혈당 95면 괜찮아?")
    run_case(agent, "공복혈당 110이면 어떤 상태야?")
    run_case(agent, "공복혈당 126이면 병원 가야 해?")
    run_case(agent, "흉통이 있는데 괜찮아?")
    run_case(agent, "중성지방이 뭐야?")

if __name__ == "__main__":
    main()