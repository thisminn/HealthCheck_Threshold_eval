import json
from pathlib import Path

from src.schemas import CorpusChunk


def load_corpus_chunks_from_jsonl(jsonl_path: str) -> list[CorpusChunk]:
    path = Path(jsonl_path)
    if not path.exists():
        raise FileNotFoundError(f"JSONL corpus not found: {jsonl_path}")

    chunks: list[CorpusChunk] = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            raw = json.loads(line)
            meta = raw.get("meta") or {}

            chunk_id = str(raw.get("id") or f"jsonl_chunk_{line_no:04d}")
            text = str(raw.get("text") or "").strip()
            if not text:
                continue

            source_doc = (
                meta.get("title")
                or meta.get("source")
                or "chunks_healthcheck.jsonl"
            )
            source_page = meta.get("source_page")

            chunks.append(
                CorpusChunk(
                    chunk_id=chunk_id,
                    rule_id=chunk_id,
                    domain=meta.get("domain"),
                    text=text,
                    source_doc=str(source_doc) if source_doc else None,
                    source_page=str(source_page) if source_page else None,
                    meta=meta,
                )
            )

    return chunks