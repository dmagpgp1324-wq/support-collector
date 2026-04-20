# collectors.py
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import SOURCES, HEADERS
from filters import is_target_item


def safe_get(url, timeout=20):
    res = requests.get(url, headers=HEADERS, timeout=timeout)
    res.raise_for_status()
    return res


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def build_item(
    source,
    title="",
    summary="",
    content="",
    region="",
    agency="",
    category="",
    url="",
    start_date="",
    end_date=""
):
    return {
        "source": clean_text(source),
        "title": clean_text(title),
        "summary": clean_text(summary),
        "content": clean_text(content),
        "region": clean_text(region),
        "agency": clean_text(agency),
        "category": clean_text(category),
        "url": clean_text(url),
        "start_date": clean_text(start_date),
        "end_date": clean_text(end_date),
    }


def extract_dates(text: str):
    matches = re.findall(r"(20\d{2}[.\-/]\d{1,2}[.\-/]\d{1,2})", text or "")
    cleaned = []
    for m in matches:
        m = m.replace(".", "-").replace("/", "-")
        parts = m.split("-")
        if len(parts) == 3:
            yyyy = parts[0]
            mm = parts[1].zfill(2)
            dd = parts[2].zfill(2)
            cleaned.append(f"{yyyy}-{mm}-{dd}")
    if len(cleaned) >= 2:
        return cleaned[0], cleaned[1]
    if len(cleaned) == 1:
        return cleaned[0], cleaned[0]
    return "", ""


# ---------------------------
# 1. K-스타트업
# ---------------------------
def fetch_kstartup():
    items = []
    seen = set()

    url = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    res = safe_get(url)
    html = res.text

    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text("\n", strip=True)

    blocks = html.split("<li")
    for block in blocks:
        # 모집중 표시 위주로 추출
        if "D-" not in block and "마감일자" not in block:
            continue

        title_match = re.search(r'class="tit"[^>]*>([\s\S]*?)</a>', block, re.I)
        if not title_match:
            title_match = re.search(r"<a[^>]*>([\s\S]*?)</a>", block, re.I)
        if not title_match:
            continue

        title = clean_text(re.sub(r"<[^>]+>", " ", title_match.group(1)))
        if not title or len(title) < 5:
            continue

        href_match = re.search(r'<a[^>]+href="([^"]+)"', block, re.I)
        href = href_match.group(1).strip() if href_match else url
        full_url = urljoin(url, href)

        category_match = re.search(r'<span[^>]*class="[^"]*badge[^"]*"[^>]*>([\s\S]*?)</span>', block, re.I)
        category = clean_text(re.sub(r"<[^>]+>", " ", category_match.group(1))) if category_match else "지원사업"

        start_date, end_date = extract_dates(block)

        # 날짜가 없으면 D-day 기준으로라도 수집 허용
        item = build_item(
            source="K-스타트업",
            title=title,
            summary=category,
            content=page_text[:3000],
            region=title,
            agency="",
            category=category,
            url=full_url,
            start_date=start_date,
            end_date=end_date,
        )

        key = (item["title"], item["url"])
        if key in seen:
            continue
        seen.add(key)

        if is_target_item(item):
            items.append(item)

    return items


# ---------------------------
# 2. 기업마당
# ---------------------------
def fetch_bizinfo():
    items = []
    seen = set()

    url = SOURCES["bizinfo"]["list_url"]
    res = safe_get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    links = soup.find_all("a", href=True)

    for a in links:
        title = clean_text(a.get_text(" ", strip=True))
        href = a["href"].strip()

        if not title or len(title) < 5:
            continue

        full_url = urljoin(url, href)
        parent_text = clean_text(a.parent.get_text(" ", strip=True)) if a.parent else title
        start_date, end_date = extract_dates(parent_text)

        item = build_item(
            source="기업마당",
            title=title,
            summary="기업마당 공고",
            content=parent_text,
            region=title,
            agency="",
            category="지원사업",
            url=full_url,
            start_date=start_date,
            end_date=end_date,
        )

        key = (item["title"], item["url"])
        if key in seen:
            continue
        seen.add(key)

        if is_target_item(item):
            items.append(item)

    return items


# ---------------------------
# 3. 모두의 창업
# ---------------------------
def fetch_modoo():
    items = []
    seen = set()

    for list_url in SOURCES["modoo"]["list_urls"]:
        try:
            res = safe_get(list_url)
        except Exception:
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a", href=True)

        for a in links:
            title = clean_text(a.get_text(" ", strip=True))
            href = a["href"].strip()

            if not title or len(title) < 4:
                continue

            full_url = urljoin(SOURCES["modoo"]["base_url"], href)
            parent_text = clean_text(a.parent.get_text(" ", strip=True)) if a.parent else title
            start_date, end_date = extract_dates(parent_text + " " + title)

            item = build_item(
                source="모두의 창업",
                title=title,
                summary="창업지원",
                content=parent_text,
                region=title,
                agency="",
                category="창업지원",
                url=full_url,
                start_date=start_date,
                end_date=end_date,
            )

            key = (item["title"], item["url"])
            if key in seen:
                continue
            seen.add(key)

            if is_target_item(item):
                items.append(item)

    return items


# ---------------------------
# 4. 전체 통합
# ---------------------------
def collect_all():
    all_items = []

    if SOURCES["kstartup"]["enabled"]:
        try:
            all_items.extend(fetch_kstartup())
        except Exception as e:
            print(f"[오류] K-스타트업 수집 실패: {e}")

    if SOURCES["bizinfo"]["enabled"]:
        try:
            all_items.extend(fetch_bizinfo())
        except Exception as e:
            print(f"[오류] 기업마당 수집 실패: {e}")

    if SOURCES["modoo"]["enabled"]:
        try:
            all_items.extend(fetch_modoo())
        except Exception as e:
            print(f"[오류] 모두의 창업 수집 실패: {e}")

    dedup = {}
    for item in all_items:
        key = item.get("url") or f"{item.get('source')}::{item.get('title')}"
        dedup[key] = item

    results = list(dedup.values())
    results.sort(key=lambda x: (x.get("source", ""), x.get("title", "")))
    return results