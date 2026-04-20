# config.py

TARGET_REGIONS = [
    "강원", "강원도", "강원특별자치도",
    "경기", "경기도",
    "서울", "서울특별시",
    "인천", "인천광역시",
]

EXCLUDED_REGIONS = [
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

INCLUDE_NATIONWIDE_IF_NO_REGION = True

KEYWORDS_INCLUDE = [
    "창업", "스타트업", "벤처", "사업화", "예비창업", "초기창업",
    "도약", "재도전", "창업중심대학", "소상공인", "중소기업",
    "기업지원", "판로", "마케팅", "투자", "실증", "스마트시티",
    "디지털전환", "기술개발", "R&D", "지원사업", "공모", "모집"
]

KEYWORDS_EXCLUDE = [
    "입찰", "채용", "용역", "조달", "구매", "단순 공지", "행사 안내"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SOURCES = {
    "kstartup": {
        "enabled": True,
        "name": "K-스타트업",
        "base_url": "https://www.k-startup.go.kr",
    },
    "bizinfo": {
        "enabled": True,
        "name": "기업마당",
        "list_url": "https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do",
    },
    "modoo": {
        "enabled": True,
        "name": "모두의 창업",
        "base_url": "https://www.modoo.or.kr",
        "list_urls": [
            "https://www.modoo.or.kr/notice/list",
            "https://www.modoo.or.kr/project/list",
        ]
    }
}