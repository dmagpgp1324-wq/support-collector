import re
from datetime import datetime
from config import TARGET_REGION_KEYWORDS


def parse_date(text):
    if not text:
        return None

    text = text.strip()
    text = text.replace(".", "-").replace("/", "-")
    text = re.sub(r"\s+", "", text)

    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def extract_period(text):
    """
    예:
    2026-04-01 ~ 2026-04-15
    2026.04.01 ~ 2026.04.15
    같은 형식에서 시작일/종료일 추출
    """
    if not text:
        return None, None, False

    raw = text.strip()

    # 상시공고 처리
    if "상시" in raw or "수시" in raw or "예산 소진시까지" in raw:
        date_match = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", raw)
        start_date = parse_date(date_match.group(1)) if date_match else None
        return start_date, None, True

    # 기간형 추출
    match = re.search(
        r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2}).*?[~～\-].*?(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})",
        raw
    )
    if match:
        start_date = parse_date(match.group(1))
        end_date = parse_date(match.group(2))
        return start_date, end_date, False

    # 날짜 하나만 있는 경우
    one = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", raw)
    if one:
        d = parse_date(one.group(1))
        return d, None, False

    return None, None, False


def normalize_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def build_notice_search_text(notice):
    """
    SupportNotice 객체에서 지역 판단용 텍스트를 최대한 넓게 합침
    crawler별로 필드가 다를 수 있어서 getattr 사용
    """
    parts = [
        getattr(notice, "source", ""),
        getattr(notice, "source_name", ""),
        getattr(notice, "title", ""),
        getattr(notice, "url", ""),
        getattr(notice, "organization", ""),
        getattr(notice, "description", ""),
        getattr(notice, "content", ""),
        getattr(notice, "region", ""),
        getattr(notice, "target_region", ""),
    ]
    return normalize_text(" ".join([str(p) for p in parts if p]))


def detect_regions_in_notice(notice):
    text = build_notice_search_text(notice)
    matched = [kw for kw in TARGET_REGION_KEYWORDS if kw.lower() in text]
    return sorted(set(matched))


def is_target_region_notice(notice):
    return len(detect_regions_in_notice(notice)) > 0