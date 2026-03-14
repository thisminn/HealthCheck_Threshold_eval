import argparse
import json
from pathlib import Path

# 지금 평가 범위에서 유지할 최소 청크 ID
KEEP_IDS = {
    "healthcheck:0001:1",  # 전체 판정 개요
    "healthcheck:0001:2",  # 정상A 정의
    "healthcheck:0001:3",  # 정상B(경계) 정의
    "healthcheck:0001:5",  # 고혈압·당뇨병 이상지질혈증 질환의심 정의
    "healthcheck:0004",    # 혈압 threshold
    "healthcheck:0008",    # 공복 혈당 threshold
}


def should_keep(obj: dict) -> bool:
    chunk_id = str(obj.get("id", "")).strip()
    text = str(obj.get("text", "")).strip()
    meta = obj.get("meta") or {}

    # 1) 가장 안전한 기준: 정확한 ID 유지
    if chunk_id in KEEP_IDS:
        return True

    # 2) ID가 달라진 버전에도 대비하는 보조 규칙
    rule_kind = str(meta.get("rule_kind", "")).strip().lower()
    scope = str(meta.get("scope", "")).strip().lower()
    rule_type = str(meta.get("rule_type", "")).strip().lower()
    target_disease = str(meta.get("target_disease", "")).strip()
    test_item = str(meta.get("test_item", "")).strip()

    # 전체 판정 정의 중 필요한 것만
    if rule_kind == "global" and scope == "overall":
        if any(keyword in text for keyword in [
            "정상A",
            "정상B(경계)",
            "고혈압·당뇨병 이상지질혈증 질환의심",
        ]):
            return True

    # 혈압 numeric threshold
    if (
        rule_type == "numeric_threshold"
        and target_disease == "고혈압"
        and "혈압" in test_item
    ):
        return True

    # 공복 혈당 numeric threshold
    if (
        rule_type == "numeric_threshold"
        and target_disease == "당뇨병"
        and "공복 혈당" in test_item
    ):
        return True

    return False


def build_subset(input_path: str, output_path: str) -> None:
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    kept = []
    total = 0

    with input_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            total += 1
            obj = json.loads(line)

            if should_keep(obj):
                kept.append(obj)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        for obj in kept:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Total chunks : {total}")
    print(f"Kept chunks  : {len(kept)}")
    print(f"Output path  : {output_file}")
    print("Kept IDs:")
    for obj in kept:
        meta = obj.get("meta") or {}
        print(
            f"- {obj.get('id')} | "
            f"rule_kind={meta.get('rule_kind')} | "
            f"rule_type={meta.get('rule_type')} | "
            f"target_disease={meta.get('target_disease')} | "
            f"test_item={meta.get('test_item')}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/corpus/chunks_healthcheck.jsonl",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/corpus/chunks_healthcheck_bp_glu.jsonl",
    )
    args = parser.parse_args()

    build_subset(args.input, args.output)


if __name__ == "__main__":
    main()