import argparse
from pathlib import Path

from src.config import DEFAULT_EXCEL_PATH, DEFAULT_SHEET_NAME, RAG_OUTPUT_DIR, MAX_QUESTIONS
from src.pipelines.rag_pipeline import run_rag_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel_path", type=str, default=DEFAULT_EXCEL_PATH)
    parser.add_argument("--sheet_name", type=str, default=DEFAULT_SHEET_NAME)
    parser.add_argument("--prompt_path", type=str, default="prompts/rag.txt")
    parser.add_argument(
        "--output_path",
        type=str,
        default=str(Path(RAG_OUTPUT_DIR) / "sample_run_rag.json"),
    )
    parser.add_argument("--limit", type=int, default=MAX_QUESTIONS)

    # 추가
    parser.add_argument(
        "--question_ids",
        type=str,
        default="",
        help="쉼표로 구분한 question_id 목록. 예: Q016,Q017,Q018",
    )
    parser.add_argument(
        "--domains",
        type=str,
        default="",
        help="쉼표로 구분한 domain 목록. 예: fasting_glucose,blood_pressure",
    )

    args = parser.parse_args()

    question_ids = [x.strip() for x in args.question_ids.split(",") if x.strip()]
    domains = [x.strip() for x in args.domains.split(",") if x.strip()]

    results = run_rag_pipeline(
        excel_path=args.excel_path,
        question_sheet_name=args.sheet_name,
        prompt_path=args.prompt_path,
        output_path=args.output_path,
        limit=args.limit,
        question_ids=question_ids if question_ids else None,
        domains=domains if domains else None,
    )

    print(f"Saved {len(results)} results to {args.output_path}")


if __name__ == "__main__":
    main()