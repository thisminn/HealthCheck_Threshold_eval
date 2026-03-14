import numpy as np

from src.schemas import RetrievedDoc


def retrieve_top_k(
    query_embedding: np.ndarray,
    corpus_embeddings: np.ndarray,
    corpus_chunks: list,
    top_k: int = 5,
) -> list[RetrievedDoc]:
    scores = corpus_embeddings @ query_embedding
    top_indices = np.argsort(scores)[::-1][:top_k]

    results: list[RetrievedDoc] = []
    for idx in top_indices:
        chunk = corpus_chunks[int(idx)]

        results.append(
            RetrievedDoc(
                chunk_id=chunk.chunk_id,
                rule_id=chunk.rule_id,
                text=chunk.text,
                score=float(scores[int(idx)]),
                domain=getattr(chunk, "domain", None),
                source_doc=getattr(chunk, "source_doc", None),
                source_page=getattr(chunk, "source_page", None),
                meta=getattr(chunk, "meta", {}) or {},
            )
        )

    return results