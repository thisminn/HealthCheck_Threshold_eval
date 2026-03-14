import json
from pathlib import Path

from src.config import (
    CORPUS_SOURCE,
    DEFAULT_CORPUS_JSONL_PATH,
    EMBED_MODEL,
    ENABLE_DOMAIN_PREFILTER,
    INCLUDE_GLOBAL_RULES,
    RERANK_MODEL,
    RERANK_TOP_N,
    RULE_SHEET_NAME,
    TOP_K,
    USE_RERANKER,
)
from src.generator.client import LLMClient
from src.loaders.corpus_loader import load_corpus_chunks_from_jsonl
from src.loaders.excel_loader import load_questions_from_excel, load_rule_chunks_from_excel
from src.retriever.embedder import TextEmbedder
from src.retriever.reranker import OptionalReranker
from src.retriever.search import retrieve_top_k
from src.schemas import PipelineResult, QuestionItem


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def _norm(value) -> str:
    return "" if value is None else str(value).strip()


def _detect_topics(q: QuestionItem) -> set[str]:
    """
    반환 예시:
    - {"bp", "global"}
    - {"glu", "global"}
    - {"bp", "glu", "global"}   # mixed
    - {"global"}                # overall only
    """
    joined = " ".join([
        _norm(q.question_text),
        _norm(q.domain),
        _norm(q.rule_ref),
        _norm(q.input_value),
    ]).lower()

    topics: set[str] = set()

    domain = _norm(q.domain).lower()

    if domain == "blood_pressure":
        topics.update({"bp", "global"})
    elif domain == "fasting_glucose":
        topics.update({"glu", "global"})
    elif domain == "mixed":
        topics.update({"bp", "glu", "global"})
    elif domain == "overall":
        topics.update({"global"})

    if "혈압" in joined or "blood_pressure" in joined or "bp_" in joined:
        topics.update({"bp", "global"})

    if (
        "공복혈당" in joined
        or "공복 혈당" in joined
        or "혈당" in joined
        or "당뇨" in joined
        or "fasting_glucose" in joined
        or "glu_" in joined
    ):
        topics.update({"glu", "global"})

    if not topics:
        topics.add("global")

    return topics


def _is_bp_chunk(chunk) -> bool:
    meta = getattr(chunk, "meta", {}) or {}
    target_disease = _norm(meta.get("target_disease"))
    test_item = _norm(meta.get("test_item"))
    text = _norm(getattr(chunk, "text", ""))

    return (
        target_disease == "고혈압"
        or "혈압" in test_item
        or "혈압" in text
    )


def _is_glu_chunk(chunk) -> bool:
    meta = getattr(chunk, "meta", {}) or {}
    target_disease = _norm(meta.get("target_disease"))
    test_item = _norm(meta.get("test_item"))
    text = _norm(getattr(chunk, "text", ""))

    return (
        target_disease == "당뇨병"
        or "공복 혈당" in test_item
        or "공복혈당" in text
        or "혈당" in text
    )


def _is_overall_global_chunk(chunk) -> bool:
    meta = getattr(chunk, "meta", {}) or {}
    rule_kind = _norm(meta.get("rule_kind")).lower()
    scope = _norm(meta.get("scope")).lower()

    return rule_kind == "global" and scope == "overall"


def _filter_chunks_for_question(q: QuestionItem, corpus_chunks: list):
    if not ENABLE_DOMAIN_PREFILTER:
        return corpus_chunks

    topics = _detect_topics(q)

    kept = []
    for chunk in corpus_chunks:
        if "global" in topics and INCLUDE_GLOBAL_RULES and _is_overall_global_chunk(chunk):
            kept.append(chunk)
            continue

        if "bp" in topics and _is_bp_chunk(chunk):
            kept.append(chunk)
            continue

        if "glu" in topics and _is_glu_chunk(chunk):
            kept.append(chunk)
            continue

    return kept if kept else corpus_chunks


def _slim_meta(meta: dict | None) -> dict:
    meta = meta or {}
    keep_keys = [
        "rule_kind",
        "rule_type",
        "rule_role",
        "scope",
        "target_disease",
        "test_item",
        "unit",
        "title",
    ]
    return {k: meta[k] for k in keep_keys if k in meta and meta[k] is not None}


def _compact_retrieved_docs(docs: list) -> list[dict]:
    """
    디버깅용 최소 정보만 저장.
    text / full meta는 제외해서 JSON 길이를 줄인다.
    """
    compact = []
    for doc in docs:
        compact.append(
            {
                "chunk_id": doc.chunk_id,
                "rule_id": doc.rule_id,
                "score": round(float(doc.score), 4),
                "source_doc": doc.source_doc,
                "source_page": doc.source_page,
            }
        )
    return compact


def _compact_final_context(docs: list) -> list[dict]:
    """
    실제 LLM이 본 최종 context만 저장.
    retrieved_context 전체 text 중복을 줄이기 위해 final context만 full-ish하게 보관.
    """
    compact = []
    for doc in docs:
        compact.append(
            {
                "chunk_id": doc.chunk_id,
                "rule_id": doc.rule_id,
                "text": doc.text,
                "score": round(float(doc.score), 4),
                "domain": doc.domain,
                "source_doc": doc.source_doc,
                "source_page": doc.source_page,
                "meta": _slim_meta(getattr(doc, "meta", {}) or {}),
            }
        )
    return compact


def build_rag_user_input(question: QuestionItem, context_docs: list[dict]) -> str:
    context_str_parts = []
    for i, doc in enumerate(context_docs, start=1):
        context_str_parts.append(
            f"[{i}] rule_id={doc['rule_id']} | "
            f"source_doc={doc.get('source_doc')} | "
            f"source_page={doc.get('source_page')} | "
            f"score={doc['score']:.4f}\n"
            f"{doc['text']}"
        )

    context_str = "\n\n".join(context_str_parts)

    return (
        f"Question Meta:\n"
        f"- question_id: {question.question_id}\n"
        f"- domain: {question.domain}\n"
        f"- input_value: {question.input_value}\n"
        f"- rule_ref: {question.rule_ref}\n\n"
        f"Retrieved Context:\n{context_str}\n\n"
        f"User Question:\n{question.question_text}"
    )


def run_rag_pipeline(
    excel_path: str,
    question_sheet_name: str,
    prompt_path: str,
    output_path: str,
    limit: int = 5,
    question_ids: list[str] | None = None,
    domains: list[str] | None = None,
) -> list[dict]:
    questions = load_questions_from_excel(excel_path, sheet_name=question_sheet_name)

    if question_ids:
        question_id_set = {q.strip() for q in question_ids if q.strip()}
        questions = [q for q in questions if q.question_id in question_id_set]

    if domains:
        domain_set = {d.strip() for d in domains if d.strip()}
        questions = [q for q in questions if (q.domain or "") in domain_set]

    questions = questions[:limit]

    if CORPUS_SOURCE == "jsonl":
        corpus_chunks = load_corpus_chunks_from_jsonl(DEFAULT_CORPUS_JSONL_PATH)
    else:
        corpus_chunks = load_rule_chunks_from_excel(excel_path, sheet_name=RULE_SHEET_NAME)

    embedder = TextEmbedder(EMBED_MODEL)

    reranker = OptionalReranker(
        model_name=RERANK_MODEL,
        enabled=USE_RERANKER,
    )

    system_prompt = load_prompt(prompt_path)
    client = LLMClient()

    results: list[dict] = []

    for q in questions:
        candidate_chunks = _filter_chunks_for_question(q, corpus_chunks)
        candidate_texts = [chunk.text for chunk in candidate_chunks]
        candidate_embeddings = embedder.encode_texts(candidate_texts)

        query_embedding = embedder.encode_query(q.question_text)

        retrieved_docs = retrieve_top_k(
            query_embedding=query_embedding,
            corpus_embeddings=candidate_embeddings,
            corpus_chunks=candidate_chunks,
            top_k=TOP_K,
        )

        reranked_docs = reranker.rerank(
            query=q.question_text,
            docs=retrieved_docs,
            top_n=RERANK_TOP_N,
        )

        final_context_docs = reranked_docs if reranked_docs else retrieved_docs[:RERANK_TOP_N]
        final_context_dicts = [doc.model_dump() for doc in final_context_docs]

        user_input = build_rag_user_input(
            question=q,
            context_docs=final_context_dicts,
        )

        llm_out = client.generate_structured_answer(
            system_prompt=system_prompt,
            user_question=user_input,
        )

        result = PipelineResult(
            system_name="plain_rag",
            question_id=q.question_id,
            question_text=q.question_text,

            # 길이 줄이기: retrieved는 최소 정보만 저장
            retrieved_context=_compact_retrieved_docs(retrieved_docs),

            # 길이 줄이기: 실제 최종 context만 저장
            reranked_context=_compact_final_context(final_context_docs),

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