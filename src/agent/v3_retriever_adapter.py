from types import SimpleNamespace

from src.config import (
    CORPUS_SOURCE,
    DEFAULT_CORPUS_JSONL_PATH,
    EMBED_MODEL,
    RERANK_MODEL,
    RERANK_TOP_N,
    RULE_SHEET_NAME,
    TOP_K,
    USE_RERANKER,
)
from src.loaders.corpus_loader import load_corpus_chunks_from_jsonl
from src.loaders.excel_loader import load_rule_chunks_from_excel
from src.pipelines.rag_pipeline import _filter_chunks_for_question, _slim_meta
from src.retriever.embedder import TextEmbedder
from src.retriever.reranker import OptionalReranker
from src.retriever.search import retrieve_top_k


class V3RetrieverAdapter:
    def __init__(self, excel_path: str | None = None, default_domain: str = "fasting_glucose"):
        self.default_domain = default_domain

        if CORPUS_SOURCE == "jsonl":
            self.corpus_chunks = load_corpus_chunks_from_jsonl(DEFAULT_CORPUS_JSONL_PATH)
        else:
            if not excel_path:
                raise ValueError("CORPUS_SOURCE가 excel이면 excel_path가 필요함")
            self.corpus_chunks = load_rule_chunks_from_excel(
                excel_path,
                sheet_name=RULE_SHEET_NAME,
            )

        self.embedder = TextEmbedder(EMBED_MODEL)
        self.reranker = OptionalReranker(
            model_name=RERANK_MODEL,
            enabled=USE_RERANKER,
        )

    def search(self, query: str, top_k: int = 5, domain: str | None = None) -> list[dict]:
        q = SimpleNamespace(
            question_text=query,
            domain=domain or self.default_domain,
            rule_ref="",
            input_value="",
        )

        candidate_chunks = _filter_chunks_for_question(q, self.corpus_chunks)
        candidate_texts = [chunk.text for chunk in candidate_chunks]
        candidate_embeddings = self.embedder.encode_texts(candidate_texts)

        query_embedding = self.embedder.encode_query(query)

        retrieved_docs = retrieve_top_k(
            query_embedding=query_embedding,
            corpus_embeddings=candidate_embeddings,
            corpus_chunks=candidate_chunks,
            top_k=max(top_k, TOP_K),
        )

        reranked_docs = self.reranker.rerank(
            query=query,
            docs=retrieved_docs,
            top_n=top_k,
        )

        final_docs = reranked_docs if reranked_docs else retrieved_docs[:top_k]

        results = []
        for doc in final_docs:
            results.append(
                {
                    "chunk_id": doc.chunk_id,
                    "text": doc.text,
                    "score": float(doc.score),
                    "metadata": {
                        "rule_id": doc.rule_id,
                        "domain": doc.domain,
                        "source_doc": doc.source_doc,
                        "source_page": doc.source_page,
                        **_slim_meta(getattr(doc, "meta", {}) or {}),
                    },
                }
            )
        return results