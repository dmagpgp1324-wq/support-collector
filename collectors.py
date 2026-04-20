# collectors.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import SOURCES, HEADERS
from filters import is_target_item


def safe_get(url, timeout=20):
    res = requests.get(url, headers=HEADERS, timeout=timeout)
    res.raise_for_status()
    return res


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
        "source": source,
        "title": title.strip(),
        "summary": summary.strip(),
        "content": content.strip(),
        "region": region.strip(),
        "agency": agency.strip(),
        "category": category.strip(),
        "url": url.strip(),
        "start_date": start_date.strip(),
        "end_date": end_date.strip(),
    }


# ---------------------------
# 1. K-스타트업
# ---------------------------
def fetch_kstartup():
    items = []
    seen = set()

    url = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    res = safe_get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    text = soup.get_text("\n", strip=True)
    links = soup.find_all("a", href=True)

    for a in links:
        title = a.get_text(" ", strip=True)
        href = a["href"].strip()

        if not title or len(title) < 5:
            continue

        full_url = urljoin(url, href)

        key = (title, full_url)
        if key in seen:
            continue
        seen.add(key)

        item = build_item(
            source="K-스타트업",
            title=title,
            summary="",
            content=text[:2000],
            region=title,
            agency="",
            category="지원사업",
            url=full_url,
            start_date="",
            end_date="",
        )

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
        title = a.get_text(" ", strip=True)
        href = a["href"].strip()

        if not title:
            continue

        # 너무 짧은 텍스트 제거
        if len(title) < 5:
            continue

        full_url = urljoin(url, href)

        if full_url in seen:
            continue
        seen.add(full_url)

        item = build_item(
            source="기업마당",
            title=title,
            summary="",
            content="",
            region=title,     # 제목에 지역이 들어가는 경우 대비
            agency="",
            category="지원사업",
            url=full_url,
        )

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
            title = a.get_text(" ", strip=True)
            href = a["href"].strip()

            if not title:
                continue

            if len(title) < 4:
                continue

            full_url = urljoin(SOURCES["modoo"]["base_url"], href)

            if full_url in seen:
                continue
            seen.add(full_url)

            item = build_item(
                source="모두의 창업",
                title=title,
                summary="",
                content="",
                region=title,
                agency="",
                category="창업지원",
                url=full_url,
            )

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

    # URL 기준 중복 제거
    dedup = {}
    for item in all_items:
        key = item.get("url") or f"{item.get('source')}::{item.get('title')}"
        dedup[key] = item

    results = list(dedup.values())

    # 제목 기준 정렬
    results.sort(key=lambda x: (x.get("source", ""), x.get("title", "")))

    return results