# filters.py
from config import KEYWORDS_INCLUDE, KEYWORDS_EXCLUDE
from region_filter import is_allowed_by_region

def norm(value):
    return (value or "").strip()

def is_support_project(item: dict) -> bool:
    title = norm(item.get("title"))
    summary = norm(item.get("summary"))
    content = norm(item.get("content"))
    category = norm(item.get("category"))
    agency = norm(item.get("agency"))

    full_text = " ".join([title, summary, content, category, agency])

    if not full_text:
        return False

    if any(x in full_text for x in KEYWORDS_EXCLUDE):
        return False

    if not any(x in full_text for x in KEYWORDS_INCLUDE):
        return False

    return True

def is_target_item(item: dict) -> bool:
    if not is_support_project(item):
        return False

    return is_allowed_by_region(
        title=item.get("title", ""),
        region=item.get("region", ""),
        agency=item.get("agency", ""),
        summary=item.get("summary", ""),
        content=item.get("content", ""),
    )