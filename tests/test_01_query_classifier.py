# PYTHONPATH=. python -m tests.test_01_query_classifier

from src.agent.query_classifier import classify_query

def main():
    queries = [
        "공복혈당 110이면 괜찮아?",
        "이거 병원 가야 해?",
        "중성지방이 뭐야?",
        "혈압이랑 공복혈당 중 뭐가 더 위험해?",
        "흉통이 있는데 괜찮아?"
    ]

    print("=== query_classifier test ===")
    for q in queries:
        result = classify_query(q)
        print(f"\n[Q] {q}")
        print(result.model_dump())

if __name__ == "__main__":
    main()