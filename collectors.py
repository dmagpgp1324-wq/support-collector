# collectors.py
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import SOURCES, HEADERS
from filters import filter_items


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


def looks_like_notice_title(title: str, keywords: list[str], min_len: int = 8) -> bool:
    title = clean_text(title)
    if not title or len(title) < min_len:
        return False
    return any(k in title for k in keywords)


def fetch_kstartup():
    items = []
    seen = set()

    url = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    res = safe_get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    lines = [clean_text(x) for x in text.split("\n") if clean_text(x)]

    buffer = []
    for line in lines:
        if "모집" in line or "공고" in line:
            if buffer:
                full = " ".join(buffer)
                start_date, end_date = extract_dates(full)

                item = build_item(
                    source="K-스타트업",
                    title=buffer[0],
                    summary="지원사업",
                    content=full,
                    region=buffer[0],
                    agency="",
                    category="지원사업",
                    url=url,
                    start_date=start_date,
                    end_date=end_date
                )

                key = item["title"]
                if key not in seen:
                    seen.add(key)
                    items.append(item)

                buffer = []

        buffer.append(line)

    if buffer:
        full = " ".join(buffer)
        start_date, end_date = extract_dates(full)
        item = build_item(
            source="K-스타트업",
            title=buffer[0],
            summary="지원사업",
            content=full,
            region=buffer[0],
            agency="",
            category="지원사업",
            url=url,
            start_date=start_date,
            end_date=end_date
        )
        key = item["title"]
        if key not in seen:
            seen.add(key)
            items.append(item)

    return items


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

        if not title:
            continue

        full_url = urljoin(url, href)

        # 기업마당은 상세공고 링크만 우선 수집
        if "bizinfo.go.kr" in full_url:
            if not any(x in full_url for x in ["selectSI", "selectSIA", "selectBIZ"]):
                continue

        parent_text = clean_text(a.parent.get_text(" ", strip=True)) if a.parent else title
        start_date, end_date = extract_dates(parent_text + " " + title)

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
        items.append(item)

    return items


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

            if not looks_like_notice_title(
                title,
                ["공고", "모집", "지원", "창업", "스타트업", "사업", "프로그램"]
            ):
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
            items.append(item)

    return items


def fetch_smallbiz():
    # 소상공인24는 구조 변동이 잦아 우선 비활성 안정형으로 둠
    return []


def fetch_mss():
    items = []
    seen = set()

    url = SOURCES["mss"]["list_url"]
    res = safe_get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    page_text = soup.get_text("\n", strip=True)
    links = soup.find_all("a", href=True)

    for a in links:
        title = clean_text(a.get_text(" ", strip=True))
        href = a["href"].strip()

        if not looks_like_notice_title(
            title,
            ["공고", "모집", "지원사업", "지원", "사업화", "바우처", "패키지"]
        ):
            continue

        full_url = urljoin(url, href)
        parent_text = clean_text(a.parent.get_text(" ", strip=True)) if a.parent else title
        start_date, end_date = extract_dates(parent_text + " " + page_text[:1000])

        item = build_item(
            source="중소벤처기업부",
            title=title,
            summary="중소벤처기업부 사업공고",
            content=parent_text,
            region=title,
            agency="중소벤처기업부",
            category="지원사업",
            url=full_url,
            start_date=start_date,
            end_date=end_date,
        )

        key = (item["title"], item["url"])
        if key in seen:
            continue
        seen.add(key)
        items.append(item)

    return items


def fetch_ccei():
    # 창조경제혁신센터는 센터별 구조 차이가 커서 우선 비활성 안정형으로 둠
    return []


def dedupe_items(items):
    seen = set()
    results = []

    for item in items:
        key = (
            item.get("source", ""),
            item.get("title", ""),
            item.get("url", "")
        )
        if key in seen:
            continue
        seen.add(key)
        results.append(item)

    return results


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

    if SOURCES.get("smallbiz", {}).get("enabled"):
        try:
            all_items.extend(fetch_smallbiz())
        except Exception as e:
            print(f"[오류] 소상공인24 수집 실패: {e}")

    if SOURCES.get("mss", {}).get("enabled"):
        try:
            all_items.extend(fetch_mss())
        except Exception as e:
            print(f"[오류] 중소벤처기업부 수집 실패: {e}")

    if SOURCES.get("ccei", {}).get("enabled"):
        try:
            all_items.extend(fetch_ccei())
        except Exception as e:
            print(f"[오류] 창조경제혁신센터 수집 실패: {e}")

    results = dedupe_items(all_items)
    results = filter_items(results)
    results.sort(key=lambda x: (x.get("source", ""), x.get("title", "")))
    return results