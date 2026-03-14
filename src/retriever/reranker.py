from sentence_transformers import CrossEncoder

from src.schemas import RetrievedDoc


class OptionalReranker:
    def __init__(self, model_name: str, enabled: bool = False) -> None:
        self.enabled = enabled
        self.model = None

        if self.enabled:
            self.model = CrossEncoder(model_name, trust_remote_code=True)

    def rerank(
        self,
        query: str,
        docs: list[RetrievedDoc],
        top_n: int = 3,
    ) -> list[RetrievedDoc]:
        if not docs:
            return []

        if not self.enabled or self.model is None:
            return docs[:top_n]

        pairs = [[query, doc.text] for doc in docs]
        scores = self.model.predict(pairs)

        scored_docs = []
        for doc, score in zip(docs, scores):
            doc.score = float(score)
            scored_docs.append(doc)

        scored_docs.sort(key=lambda x: x.score, reverse=True)
        return scored_docs[:top_n]