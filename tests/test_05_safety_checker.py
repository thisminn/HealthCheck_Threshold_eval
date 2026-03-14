# PYTHONPATH=. python -m tests.test_05_safety_checker

from src.agent.safety_checker import apply_safety_check

def main():
    normal_query = "공복혈당 110이면 괜찮아?"
    urgent_query = "흉통이 있고 숨쉬기 힘든데 괜찮아?"

    normal_answer = "해당 수치는 경계 범위로 볼 수 있어. 생활습관 관리와 추적 확인이 중요해."
    urgent_answer = "수치상으로는 해석이 가능해."

    print("=== safety_checker test ===")

    print("\n[normal]")
    print(apply_safety_check(normal_query, normal_answer))

    print("\n[urgent]")
    print(apply_safety_check(urgent_query, urgent_answer))

if __name__ == "__main__":
    main()