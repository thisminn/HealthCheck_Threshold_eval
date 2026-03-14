from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_path(path_str: str) -> str:
    path = Path(path_str)
    if path.is_absolute():
        return str(path)
    return str((BASE_DIR / path).resolve())


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

DEFAULT_EXCEL_PATH = _resolve_path(
    os.getenv(
        "DEFAULT_EXCEL_PATH",
        "data/raw/rules/healthcheck_rule_v1.xlsx",
    )
)

DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "gold_qa_table")
RULE_SHEET_NAME = os.getenv("RULE_SHEET_NAME", "rule_catalog")

CORPUS_SOURCE = os.getenv("CORPUS_SOURCE", "jsonl").lower()
DEFAULT_CORPUS_JSONL_PATH = _resolve_path(
    os.getenv(
        "DEFAULT_CORPUS_JSONL_PATH",
        "data/raw/corpus/chunks_healthcheck_bp_glu.jsonl",
    )
)

ENABLE_DOMAIN_PREFILTER = os.getenv("ENABLE_DOMAIN_PREFILTER", "true").lower() == "true"
INCLUDE_GLOBAL_RULES = os.getenv("INCLUDE_GLOBAL_RULES", "true").lower() == "true"

LLM_OUTPUT_DIR = str((BASE_DIR / "outputs" / "llm_only").resolve())
RAG_OUTPUT_DIR = str((BASE_DIR / "outputs" / "rag").resolve())

MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "5"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "Qwen/Qwen3-Embedding-0.6B")
RERANK_MODEL = os.getenv("RERANK_MODEL", "Qwen/Qwen3-Reranker-0.6B")

TOP_K = int(os.getenv("TOP_K", "3"))
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "3"))

USE_RERANKER = os.getenv("USE_RERANKER", "false").lower() == "true"