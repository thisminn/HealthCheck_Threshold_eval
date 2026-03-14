import re
from typing import List, Optional, Tuple
from .schemas import SelectedEvidence, ThresholdInterpretation


def extract_first_number(query: str):
    m = re.search(r"(\d+(\.\d+)?)", query)
    if not m:
        return None
    return float(m.group(1))


def has_blood_pressure_pair_pattern(text: str) -> bool:
    slash_pattern = re.search(r"(?<!\d)\d{2,3}\s*/\s*\d{2,3}(?!\d)", text)
    e_pattern = re.search(r"(?<!\d)\d{2,3}\s*에\s*\d{2,3}(?!\d)", text)
    named_pattern = (
        re.search(r"수축기\s*\d{2,3}", text) and re.search(r"이완기\s*\d{2,3}", text)
    ) or (
        re.search(r"최고혈압\s*\d{2,3}", text) and re.search(r"최저혈압\s*\d{2,3}", text)
    )
    return bool(slash_pattern or e_pattern or named_pattern)


def is_fasting_glucose_query(q: str) -> bool:
    return ("공복혈당" in q) or ("혈당" in q)


def is_blood_pressure_query(q: str) -> bool:
    bp_terms = ["혈압", "수축기", "이완기", "최고혈압", "최저혈압"]
    return any(term in q for term in bp_terms) or has_blood_pressure_pair_pattern(q)


def extract_blood_pressure_values(query: str) -> Optional[Tuple[int, int]]:
    patterns = [
        r"수축기\s*(\d{2,3})\D+이완기\s*(\d{2,3})",
        r"최고혈압\s*(\d{2,3})\D+최저혈압\s*(\d{2,3})",
        r"(\d{2,3})\s*/\s*(\d{2,3})",
        r"(\d{2,3})\s*에\s*(\d{2,3})",
    ]

    for pattern in patterns:
        m = re.search(pattern, query)
        if m:
            systolic = int(m.group(1))
            diastolic = int(m.group(2))
            return systolic, diastolic

    return None


def interpret_blood_pressure(systolic: int, diastolic: int) -> ThresholdInterpretation:
    if systolic >= 140 or diastolic >= 90:
        return ThresholdInterpretation(
            status="high_risk",
            matched_rule="혈압은 수축기 140 이상 또는 이완기 90 이상이면 높은 범주",
            confidence="high"
        )

    if 120 <= systolic <= 139 or 80 <= diastolic <= 89:
        return ThresholdInterpretation(
            status="borderline",
            matched_rule="혈압은 수축기 120~139 또는 이완기 80~89이면 경계 범주",
            confidence="high"
        )

    if systolic < 120 and diastolic < 80:
        return ThresholdInterpretation(
            status="normal",
            matched_rule="혈압은 수축기 120 미만 그리고 이완기 80 미만이면 정상 범주",
            confidence="high"
        )

    return ThresholdInterpretation(
        status="needs_llm_interpretation",
        matched_rule="혈압 기준 해석이 필요함",
        confidence="medium"
    )


def interpret_threshold(query: str, evidence: List[SelectedEvidence]) -> ThresholdInterpretation:
    q = query.strip()

    if is_blood_pressure_query(q):
        bp_values = extract_blood_pressure_values(q)
        if bp_values is None:
            return ThresholdInterpretation(
                status="insufficient",
                matched_rule=None,
                confidence="low",
                missing_fields=["systolic", "diastolic"]
            )

        systolic, diastolic = bp_values
        return interpret_blood_pressure(systolic, diastolic)

    if is_fasting_glucose_query(q):
        value = extract_first_number(q)
        if value is None:
            return ThresholdInterpretation(
                status="insufficient",
                matched_rule=None,
                confidence="low",
                missing_fields=["numeric_value"]
            )

        if value < 100:
            return ThresholdInterpretation(
                status="normal",
                matched_rule="공복혈당 100 미만은 정상 범주",
                confidence="high"
            )
        elif 100 <= value <= 125:
            return ThresholdInterpretation(
                status="borderline",
                matched_rule="공복혈당 100~125는 공복혈당장애 범주",
                confidence="high"
            )
        else:
            return ThresholdInterpretation(
                status="high_risk",
                matched_rule="공복혈당 126 이상은 당뇨병 의심 범주",
                confidence="high"
            )

    return ThresholdInterpretation(
        status="needs_llm_interpretation",
        matched_rule=evidence[0].text[:120] if evidence else None,
        confidence="medium"
    )