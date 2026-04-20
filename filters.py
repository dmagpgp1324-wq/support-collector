# filters.py
def is_target_item(item: dict) -> bool:
    title = str(item.get("title", "")).strip()
    return bool(title)