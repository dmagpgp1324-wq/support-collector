# filters.py
import re

TARGET_REGIONS = [
    "강원", "강원도", "강원특별자치도",
    "경기", "경기도",
    "서울", "서울특별시",
    "인천", "인천광역시",
]

EXCLUDE_REGIONS = [
    "부산", "부산광역시",
    "대구", "대구광역시",
    "광주", "광주광역시",
    "대전", "대전광역시",
    "울산", "울산광역시",
    "세종", "세종특별자치시",
    "충북", "충청북도",
    "충남", "충청남도",
    "전북", "전라북도", "전북특별자치도",
    "전남", "전라남도",
    "경북", "경상북도",
    "경남", "경상남도",
    "제주", "제주특별자치도",
]

NATIONWIDE_KEYWORDS = [
    "전국",
    "전국단위",
    "전지역",
    "전 지역",
    "지역무관",
    "지역 제한 없음",
    "전국 모집",
    "전국 공고",
    "전국 대상",
]

GOOD_KEYWORDS = [
    "지원사업",
    "지원",
    "공고",
    "모집",
    "참여기업",
    "수혜기업",
    "사업화",
    "창업",
    "스타트업",
    "실증",
    "프로그램",
    "바우처",
    "패키지",
    "액셀러레이팅",
    "데모데이",
    "투자유치",
    "IR",
    "PoC",
    "스마트시티",
    "데이터",
    "플랫폼",
    "소상공인",
    "혁신",
]

BAD_KEYWORDS = [
    "개인정보처리방침",
    "이용약관",
    "저작권",
    "고객의 소리",
    "고객센터",
    "자주하는 질문",
    "자주 묻는 질문",
    "FAQ",
    "로그인",
    "회원가입",
    "회원",
    "전체메뉴",
    "전체 메뉴",
    "메뉴",
    "바로가기",
    "대시보드",
    "설정",
    "사이트맵",
    "정책정보",
    "정책정보 개방",
    "자료이용 및 저작권보호",
    "기업업무 서식",
    "서식",
    "온라인화상회의실",
    "웹접근성점검",
    "이메일무단수집거부",
    "입법·행정예고/고시",
    "입법 행정예고 고시",
    "자료실",
    "공지사항",
    "알림마당",
    "진행중공고보기",
    "공고보기",
    "javascript",
    "void(",
    "endbsns",
    "조회",
    "신청",
    "발급",
    "증명서",
    "확인서",
    "일자리포털",
    "뉴스",
    "메일",
    "구독",
]

HARD_BLOCK_KEYWORDS = [
    "분야(",
    "분야",
    "온라인화상회의실",
    "품목별 법정의무 인증제도",
    "서남권",
]

GENERIC_BAD_TITLES = [
    "기업마당 공고",
    "사업공고",
    "지원사업",
    "공고",
]

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()

def _haystack(item: dict) -> str:
    return _clean(
        " ".join([
            item.get("source", ""),
            item.get("title", ""),
            item.get("summary", ""),
            item.get("content", ""),
            item.get("region", ""),
            item.get("agency", ""),
            item.get("category", ""),
        ])
    ).lower()

def is_noise_title(title: str) -> bool:
    title = _clean(title)

    if not title or len(title) < 10:
        return True

    if any(k in title for k in HARD_BLOCK_KEYWORDS):
        return True

    if re.match(r"^분야\(\d+\)$", title):
        return True

    if re.search(r"\d+\s*건", title):
        return True

    if title in GENERIC_BAD_TITLES:
        return True

    if any(x in title for x in [
        "전체", "현황", "정보", "안내", "소개", "목록",
        "통합", "조회", "검색", "결과", "뉴스레터"
    ]):
        return True

    return False

def is_junk_item(item: dict) -> bool:
    title = _clean(item.get("title", ""))
    url = _clean(item.get("url", ""))

    if not title or len(title) < 8:
        return True

    if not url.startswith("http"):
        return True

    if "javascript" in url.lower() or "void(" in url.lower():
        return True

    lower_title = title.lower()

    if any(k.lower() in lower_title for k in BAD_KEYWORDS):
        return True

    return False

def is_business_item(item: dict) -> bool:
    hs = _haystack(item)
    return any(k.lower() in hs for k in GOOD_KEYWORDS)

def is_real_notice(item: dict) -> bool:
    title = _clean(item.get("title", ""))

    if not any(k in title for k in ["모집", "공고", "참여기업", "지원사업"]):
        return False

    if any(k in title for k in ["조회", "신청", "발급", "증명", "포털", "뉴스"]):
        return False

    return True

def is_target_region(item: dict) -> bool:
    hs = _haystack(item)

    if any(k.lower() in hs for k in NATIONWIDE_KEYWORDS):
        return True

    if any(k.lower() in hs for k in TARGET_REGIONS):
        return True

    if any(k.lower() in hs for k in EXCLUDE_REGIONS):
        return False

    return True

def sanitize_item(item: dict) -> dict:
    return {
        "source": _clean(item.get("source", "")),
        "title": _clean(item.get("title", "")),
        "summary": _clean(item.get("summary", "")),
        "content": _clean(item.get("content", "")),
        "region": _clean(item.get("region", "")),
        "agency": _clean(item.get("agency", "")),
        "category": _clean(item.get("category", "")),
        "url": _clean(item.get("url", "")),
        "start_date": _clean(item.get("start_date", "")),
        "end_date": _clean(item.get("end_date", "")),
    }

def filter_items(items: list[dict]) -> list[dict]:
    results = []

    for item in items:
        item = sanitize_item(item)

        if is_junk_item(item):
            continue

        if is_noise_title(item.get("title", "")):
            continue

        if not is_real_notice(item):
            continue

        if not is_business_item(item):
            continue

        if not is_target_region(item):
            continue

        results.append(item)

    return results