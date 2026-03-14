import json
from pathlib import Path

from src.generator.client import LLMClient
from src.loaders.excel_loader import load_questions_from_excel
from src.schemas import PipelineResult


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def run_llm_only_pipeline(
    excel_path: str,
    sheet_name: str,
    prompt_path: str,
    output_path: str,
    limit: int = 5,
) -> list[dict]:
    questions = load_questions_from_excel(excel_path, sheet_name=sheet_name)
    questions = questions[:limit]

    system_prompt = load_prompt(prompt_path)
    client = LLMClient()

    results: list[dict] = []

    for q in questions:
        llm_out = client.generate_structured_answer(
            system_prompt=system_prompt,
            user_question=q.question_text,
        )

        result = PipelineResult(
            system_name="llm_only",
            question_id=q.question_id,
            question_text=q.question_text,
            retrieved_context=[],
            predicted_bp_class=llm_out.predicted_bp_class,
            predicted_glu_class=llm_out.predicted_glu_class,
            predicted_action=llm_out.predicted_action,
            answer=llm_out.answer,
            notes=llm_out.notes,
        )
        results.append(result.model_dump())

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return results