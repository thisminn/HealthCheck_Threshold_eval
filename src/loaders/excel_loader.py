from pathlib import Path
import pandas as pd

from src.schemas import QuestionItem, RuleChunk


def load_questions_from_excel(excel_path: str, sheet_name: str = "gold_qa_table") -> list[QuestionItem]:
    path = Path(excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    df = pd.read_excel(path, sheet_name=sheet_name)

    required_cols = ["question_id", "question_text"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in sheet '{sheet_name}': {missing}")

    questions: list[QuestionItem] = []
    for _, row in df.iterrows():
        question = QuestionItem(
            question_id=str(row["question_id"]).strip(),
            question_text=str(row["question_text"]).strip(),
            domain=None if pd.isna(row.get("domain")) else str(row.get("domain")).strip(),
            input_value=None if pd.isna(row.get("input_value")) else str(row.get("input_value")).strip(),
            rule_ref=None if pd.isna(row.get("rule_ref")) else str(row.get("rule_ref")).strip(),
            response_mode=None if pd.isna(row.get("response_mode")) else str(row.get("response_mode")).strip(),
            final_priority_action=None
            if pd.isna(row.get("final_priority_action"))
            else str(row.get("final_priority_action")).strip(),
        )
        questions.append(question)

    return questions


def load_rule_chunks_from_excel(excel_path: str, sheet_name: str = "rule_catalog") -> list[RuleChunk]:
    path = Path(excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    df = pd.read_excel(path, sheet_name=sheet_name)

    if "rule_id" not in df.columns:
        raise ValueError(f"'rule_id' column is required in sheet '{sheet_name}'")

    chunks: list[RuleChunk] = []

    for idx, row in df.iterrows():
        rule_id = str(row["rule_id"]).strip()

        domain = None if pd.isna(row.get("domain")) else str(row.get("domain")).strip()
        source_doc = None if pd.isna(row.get("source_doc")) else str(row.get("source_doc")).strip()
        source_page = None if pd.isna(row.get("source_page")) else str(row.get("source_page")).strip()

        preferred_cols = [
            "domain",
            "class_label",
            "action_label",
            "definition",
            "threshold_text",
            "criteria",
            "guidance",
            "follow_up",
        ]

        text_parts: list[str] = []
        for col in preferred_cols:
            if col in df.columns and not pd.isna(row.get(col)):
                text_parts.append(f"{col}: {str(row.get(col)).strip()}")

        # preferred 컬럼이 부족한 경우, 비어있지 않은 나머지 컬럼까지 안전하게 합침
        if not text_parts:
            for col, value in row.items():
                if col in {"source_doc", "source_page"}:
                    continue
                if pd.isna(value):
                    continue
                text_parts.append(f"{col}: {str(value).strip()}")

        chunk_text = "\n".join(text_parts)

        chunks.append(
            RuleChunk(
                chunk_id=f"rule_chunk_{idx+1:03d}",
                rule_id=rule_id,
                domain=domain,
                text=chunk_text,
                source_doc=source_doc,
                source_page=source_page,
            )
        )

    return chunks