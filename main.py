# main.py
import json
import os
from collectors import collect_all

SEEN_FILE = "seen_urls.json"


def load_seen_urls():
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception:
        return set()


def save_seen_urls(urls):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(urls)), f, ensure_ascii=False, indent=2)


def main():
    items = collect_all()
    seen_urls = load_seen_urls()

    new_items = []
    all_urls = set(seen_urls)

    for item in items:
        url = item.get("url", "").strip()
        if not url:
            continue

        if url not in seen_urls:
            new_items.append(item)

        all_urls.add(url)

    print("=" * 80)
    print(f"전체 수집 건수: {len(items)}")
    print(f"신규 공고 건수: {len(new_items)}")
    print("=" * 80)

    for i, item in enumerate(new_items, 1):
        print(f"[{i}] [{item['source']}] {item['title']}")
        print(f"    URL: {item['url']}")
        if item.get("region"):
            print(f"    지역: {item['region']}")
        if item.get("agency"):
            print(f"    기관: {item['agency']}")
        print()

    save_seen_urls(all_urls)


if __name__ == "__main__":
    main()