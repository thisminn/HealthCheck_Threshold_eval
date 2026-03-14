from typing import List
from .schemas import RetrievedChunk, SelectedEvidence

PRIORITY_KEYS = [
    "rule", "criteria", "판정", "기준", "권고"
]

def select_evidence(query: str, chunks, top_n: int = 2):
    scored = []

    for ch in chunks:
        bonus = 0.0
        text = ch.text
        meta_str = " ".join([str(v) for v in ch.metadata.values()]) if ch.metadata else ""

        if any(k in text for k in PRIORITY_KEYS):
            bonus += 0.08
        if any(k in meta_str for k in ["rule", "healthcheck", "threshold"]):
            bonus += 0.08

        final_score = ch.score + bonus
        scored.append((final_score, ch))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = []

    for final_score, ch in scored[:top_n]:
        if "관련 정보를 찾지 못했다" in ch.text or final_score < 0.3:
            reason = "유의미한 근거를 찾지 못해 fallback 결과로 선택됨"
        elif "기준" in ch.text or "범주" in ch.text or ch.metadata.get("rule_kind") == "threshold":
            reason = "질문 해석에 직접 필요한 기준 정보가 포함됨"
        elif ch.metadata.get("rule_kind") == "guidance":
            reason = "후속 행동과 관리 방향에 도움이 되는 권고 정보가 포함됨"
        else:
            reason = "질문과 관련된 설명 정보를 포함함"

        selected.append(
            SelectedEvidence(
                chunk_id=ch.chunk_id,
                text=ch.text,
                score=final_score,
                reason=reason,
                metadata=ch.metadata
            )
        )

    return selected