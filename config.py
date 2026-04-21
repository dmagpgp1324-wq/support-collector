# config.py

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

SOURCES = {
    "kstartup": {
        "enabled": True
    },
    "bizinfo": {
        "enabled": True,
        "list_url": "https://www.bizinfo.go.kr"
    },
    "modoo": {
        "enabled": True,
        "base_url": "https://www.modoo.or.kr",
        "list_urls": [
            "https://www.modoo.or.kr/notice/list",
            "https://www.modoo.or.kr/project/list"
        ]
    },

    # 다음 단계용 확장 소스 (구조만 준비)
    "smallbiz": {
        "enabled": False,
        "list_url": "https://www.sbiz24.kr/#/pbanc"
    },
    "mss": {
        "enabled": False,
        "list_url": "https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=310"
    },
    "ccei": {
        "enabled": False,
        "list_urls": [
            "https://ccei.creativekorea.or.kr/"
        ]
    }
}