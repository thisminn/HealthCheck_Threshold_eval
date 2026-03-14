import argparse
from pathlib import Path

from src.config import DEFAULT_EXCEL_PATH, DEFAULT_SHEET_NAME, OUTPUT_DIR, MAX_QUESTIONS
from src.pipelines.llm_only_pipeline import run_llm_only_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel_path", type=str, default=DEFAULT_EXCEL_PATH)
    parser.add_argument("--sheet_name", type=str, default=DEFAULT_SHEET_NAME)
    parser.add_argument("--prompt_path", type=str, default="prompts/llm_only.txt")
    parser.add_argument(
        "--output_path",
        type=str,
        default=str(Path(OUTPUT_DIR) / "sample_run_llm.json"),
    )
    parser.add_argument("--limit", type=int, default=MAX_QUESTIONS)
    args = parser.parse_args()

    results = run_llm_only_pipeline(
        excel_path=args.excel_path,
        sheet_name=args.sheet_name,
        prompt_path=args.prompt_path,
        output_path=args.output_path,
        limit=args.limit,
    )

    print(f"Saved {len(results)} results to {args.output_path}")


if __name__ == "__main__":
    main()