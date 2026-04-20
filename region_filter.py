# region_filter.py
import re
from config import TARGET_REGIONS, EXCLUDED_REGIONS, INCLUDE_NATIONWIDE_IF_NO_REGION

NATIONWIDE_PATTERNS = [
    "전국",
    "전국단위",
    "전 지역",
    "전지역",
    "지역 제한 없음",
    "지역무관",
    "전국 공모",
    "전국 모집",
    "전국 대상",
]

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()

def contains_any(text: str, keywords: list[str]) -> bool:
    text = normalize_text(text)
    return any(k in text for k in keywords)

def detect_target_region(text: str) -> bool:
    return contains_any(text, TARGET_REGIONS)

def detect_excluded_region(text: str) -> bool:
    return contains_any(text, EXCLUDED_REGIONS)

def detect_nationwide(text: str) -> bool:
    return contains_any(text, NATIONWIDE_PATTERNS)

def is_allowed_by_region(title="", region="", agency="", summary="", content="") -> bool:
    joined = " | ".join([
        normalize_text(title),
        normalize_text(region),
        normalize_text(agency),
        normalize_text(summary),
        normalize_text(content),
    ])

    has_target = detect_target_region(joined)
    has_excluded = detect_excluded_region(joined)
    is_nationwide = detect_nationwide(joined)

    if has_target:
        return True

    if has_excluded and not has_target:
        return False

    if INCLUDE_NATIONWIDE_IF_NO_REGION and is_nationwide:
        return True

    if INCLUDE_NATIONWIDE_IF_NO_REGION and not has_target and not has_excluded:
        return True

    return False