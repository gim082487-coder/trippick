#!/usr/bin/env python3
"""v70: 신규 가이드 2편 메타데이터(guides.json·guide_extra.json).

    python3 tools/apply_v70_guides.py

값은 2026-11-28 확인분이다.
- 마운자로 일본 여행지: 스카이라이너 41분 2,470엔, 게이큐 330엔, 하루카 교토 2,700엔
  (2026-11-01 판매분부터)·오사카 1,900엔, 난카이 라피트 1,410/1,670엔·공항급행 970엔,
  JR 쾌속 에어포트 33분 1,230엔, 후쿠오카 지하철 5분 260엔, 규동 小盛 465엔·ミニ 420엔,
  조잔케이 료칸 694,357원 vs 시내 87,205원 + 온천 투어 57,948원
- 대부도: 달전망대 10:00~20:00 무료, 누에섬 동절기 09:00~17:00 월 휴관, 바닷길 1.2km,
  해솔길 1코스 11.5km·1-1코스 6.0km, 경기 시내버스 1,650원, 박물관 2,000원
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"


def load(n):
    return json.loads((D / n).read_text(encoding="utf-8"))


def save(n, o):
    (D / n).write_text(json.dumps(o, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


NEW = [
    {
        "slug": "japan-mounjaro-travel-destinations",
        "category": "일본",
        "navTitle": "마운자로 일본 여행지 TOP 4 — 교토·도쿄·삿포로·후쿠오카",
        "h1": "마운자로 들고 일본, <em>네 도시</em> 이동·소식·냉장 기준",
        "seoTitle": "마운자로 일본 여행지 TOP4 — 교토·도쿄·삿포로·후쿠오카 | 트립픽",
        "dek": ("마운자로를 들고 일본을 갈 때 도시 선택은 관광지가 아니라 이동과 보관으로 갈립니다. "
                "공항에서 숙소까지 도쿄 41분·삿포로 33분·후쿠오카 5분·교토 80분, "
                "숙소 1박 최저가, 규동 小盛 465엔 같은 소식 메뉴, 조잔케이 료칸 대신 시내 호텔+당일 온천까지 "
                "2026년 11월 확인값으로 정리했습니다."),
        "desc": ("마운자로 일본 여행지 4곳(2026-11). 스카이라이너 41분 2,470엔, 하루카 교토 2,700엔, "
                 "쾌속 에어포트 1,230엔, 후쿠오카 지하철 260엔, 숙소 87,205원부터, 규동 小盛 465엔."),
        "keywords": ("마운자로 일본 여행, 마운자로 여행지, 일본 여행지 추천, 자가주사제 여행, "
                     "스카이라이너 요금, 나리타 익스프레스, 하루카 교토 2700엔, 난카이 라피트 1410엔, "
                     "JR 쾌속 에어포트 1230엔, 후쿠오카 공항 하카타 260엔, 조잔케이 온천 당일 투어, "
                     "요시노야 소모리, 스키야 미니, 일본 호텔 냉장고 보관"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 11,
        "image": "images/v70/japan-mounjaro-travel-destinations.jpg",
        "ogImage": "images/og/v70-mounjaro-dest-og.jpg",
        "imageAlt": "교토 기요미즈데라의 탑과 단풍",
        "imageCredit": "사진: Pexels (Belle Co)",
        "tours": [],
        "essentials": ["cp-washbag-bromi", "cp-powerbank-spidy"],
        "related": ["japan-mounjaro-injection-guide", "kyoto-2n3d-course-budget", "tokyo-3n4d-course-budget",
                    "sapporo-hokkaido-3n4d-winter", "fukuoka-yufuin-3n4d-course",
                    "kansai-airport-osaka-kyoto-transfer"],
        "ctaTitle": "내 일정에 맞는 약 수량을 계산하면?",
        "ctaText": ("여행 일수와 주사 횟수를 넣으면 1개월분(4펜) 기준과 보관 일수를 같은 표로 확인할 수 있습니다."),
        "fxNote": "1엔 8.3748원 · 2026-11-28 고시 기준",
        "faq": [
            ["마운자로를 들고 가기 가장 편한 일본 도시는 어디인가요?",
             "공항에서 숙소까지 시간으로 보면 후쿠오카가 지하철 5분·260엔으로 가장 짧고, 삿포로 33분·1,230엔, 도쿄 41분·2,470엔, 교토 80분·2,700엔 순입니다. 어느 도시든 객실 냉장고가 있는 호텔을 고르면 2~8℃ 보관이 유지됩니다."],
            ["1개월분을 넘으면 어떻게 되나요?",
             "마운자로 1회용 펜 4개가 1상자(4주분)이고, 일본은 처방약·자가주사제 1개월분까지 서류 없이 통관됩니다. 2상자(8펜)부터는 출발 전에 후생노동성 수입확인증을 받아야 합니다."],
            ["호텔 냉장고에 그냥 넣어도 되나요?",
             "2~8℃ 냉장·차광이 원칙이고, 얼리면 폐기입니다. 냉동실이 붙은 미니바는 냉기 출구 쪽이 과냉이 되기 쉬우니 원래 상자째 가운데 칸에 넣으세요. 냉장이 어려운 경우에만 30℃ 이하에서 최대 21일입니다."],
            ["료칸과 시내 호텔 중 어디가 낫나요?",
             "삿포로 기준으로 조잔케이 료칸 1박이 694,357원(2인·세금 포함)이고, 시내 5성 호텔 87,205원에 조잔케이 온천 당일 투어 57,948원을 더하면 145,153원입니다. 온천을 당일로 즐기면 549,204원이 남습니다."],
            ["여행 중 식사량은 어떻게 조절하나요?",
             "작은 사이즈 이름을 외우면 됩니다. 요시노야 小盛 465엔, 스키야 ミニ 420엔이고, 밥은 보통으로 두고 고기만 늘리는 요시노야 アタマの大盛은 674엔입니다. 뷔페·코스보다 한 그릇 단품이 남기지 않기 쉽습니다."],
        ],
    },
    {
        "slug": "daebudo-daytrip-1n2d-course",
        "category": "국내",
        "navTitle": "대부도 당일치기·1박2일 — 물때·해솔길·탄도항 노을",
        "h1": "대부도, <em>물때</em>가 일정표입니다",
        "seoTitle": "대부도 당일치기·1박2일 코스 — 물때·해솔길·탄도항 노을 | 트립픽",
        "dek": ("대부도는 탄도항 누에섬 바닷길이 하루 두 번만 열려 물때가 일정을 정합니다. "
                "시화나래 달전망대 무료·10:00~20:00, 누에섬 동절기 09:00~17:00, "
                "해솔길 1코스 11.5km, 123번 버스 1,650원, 방아머리 바지락칼국수까지 "
                "2026년 11월 확인값으로 짰습니다."),
        "desc": ("대부도 당일·1박2일(2026-11). 달전망대 무료 10:00~20:00, 누에섬 09:00~17:00 월 휴관, "
                 "바닷길 1.2km, 간조 12/26 12:14, 해솔길 1코스 11.5km, 버스 1,650원, 2인 10,600원."),
        "keywords": ("대부도 당일치기, 대부도 1박2일, 대부도 코스, 탄도항 누에섬, 누에섬 바닷길 물때, "
                     "시화나래 달전망대, 대부해솔길 1코스, 구봉도 낙조전망대, 대부도 가는 법, "
                     "안산역 123번, 대부도 바지락칼국수, 방아머리 음식문화거리, 안산어촌민속박물관"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 12,
        "image": "images/v70/daebudo-daytrip-1n2d-course.jpg",
        "ogImage": "images/og/v70-daebudo-og.jpg",
        "imageAlt": "서해 갯벌 위로 지는 노을",
        "imageCredit": "사진: Pexels (Fu Shan Un)",
        "tours": [],
        "essentials": ["cp-umbrella-crocodile", "cp-waterproof-sinji"],
        "related": ["incheon-yeongjongdo-2d", "incheon-airport-parking-bus", "seoul-seongsu-bukchon-1d",
                    "gangwon-gangneung-winter-sea-2d", "sokcho-yangyang-2d", "busan-haeundae-gwangalli-2d"],
        "ctaTitle": "같은 날 물때와 날씨를 한 번에",
        "ctaText": "날짜를 넣으면 탄도 물때와 서해 날씨, 인근 숙소를 같은 화면에서 확인할 수 있습니다.",
        "fxNote": "무료 입장 3곳 · 2026-11-28 확인",
        "faq": [
            ["누에섬 바닷길은 아무 때나 걸을 수 있나요?",
             "아닙니다. 탄도항에서 누에섬까지 약 1.2km 갯벌 길이 하루 두 번, 썰물 때만 드러납니다. 안산시는 썰물이 시작된 뒤 30분~1시간 사이에 들어가라고 안내합니다. 예를 들어 12월 26일은 간조가 12:14라 12:40~14:00이 걷기 좋은 때입니다."],
            ["입장료는 얼마인가요?",
             "시화나래 달전망대, 누에섬 등대전망대, 대부해솔길은 모두 무료입니다. 안산어촌민속박물관만 어른 2,000원이고 월요일과 1월 1일, 설·추석에는 쉼니다."],
            ["대중교통으로 가려면?",
             "4호선 안산역에서 123번을 타고 탄도 종점까지 갑니다. 경기 일반 시내버스 기본요금은 교통카드 1,650원(현금 1,700원)이고 거리에 따라 추가될 수 있습니다. 오이도역에서는 790번이 대부동 방면으로 다닙니다."],
            ["월요일에 가면 어디가 문을 닫나요?",
             "누에섬 등대전망대와 안산어촌민속박물관, 시화나래 조력전시관이 모두 월요일에 쉽니다. 달전망대만 연중무휴(10:00~20:00, 입장 마감 19:30)라 월요일에는 전망대와 해솔길 위주로 짜야 합니다."],
            ["1박2일 숙소는 어디에 잡나요?",
             "대부도 안 숙소를 잡으면 이동이 가장 짧고, 날짜별 가격은 트립닷컴에서 조회해야 합니다. 트립픽에 값이 확인된 인근 숙소는 인천 송도 센트럴파크 호텔 160,123원, 골든 튤립 인천공항 211,437원(2026-11-20~21, 2인·세금 포함)입니다."],
        ],
    },
]

EXTRA = {
    "japan-mounjaro-travel-destinations": {
        "hub": "",
        "regions": ["jp"],
        "tags": ["숙소", "가성비"],
        "stayRegions": [],
        "takeaway": ("마운자로를 들고 일본을 간다면 공항→숙소 이동과 냉장고가 기준입니다. 후쿠오카 5분·260엔, "
                     "삿포로 33분·1,230엔, 도쿄 41분·2,470엔, 교토 80분·2,700엔이고, 조잔케이 료칸 대신 "
                     "시내 호텔+당일 온천이면 549,204원이 남습니다."),
        "facts": [["스카이라이너", "41분 · 2,470엔"], ["규동 小盛", "465엔 · 3,894원"]],
    },
    "daebudo-daytrip-1n2d-course": {
        "hub": "",
        "regions": ["kr"],
        "tags": ["일정", "가성비"],
        "stayRegions": ["incheon"],
        "takeaway": ("대부도는 탄도항 누에섬 바닷길이 하루 두 번만 열려 물때가 일정을 정합니다. "
                     "달전망대·누에섬·해솔길이 모두 무료이고, 2인 확정 지출은 버스 왕복 6,600원과 "
                     "박물관 4,000원으로 10,600원입니다."),
        "facts": [["달전망대", "무료 · 10:00~20:00"], ["바닷길", "1.2km · 하루 2회"]],
    },
}


def main() -> int:
    g = load("guides.json")
    slugs = {x["slug"] for x in g["guides"]}
    added = 0
    for item in NEW:
        if item["slug"] in slugs:
            continue
        g["guides"].append(item)
        added += 1
    save("guides.json", g)

    ex = load("guide_extra.json")
    for slug, row in EXTRA.items():
        ex["guides"][slug] = row
    save("guide_extra.json", ex)

    for item in NEW:
        print(f"  · {item['slug']} seoTitle {len(item['seoTitle'])}자 · desc {len(item['desc'])}자 · FAQ {len(item['faq'])}")
    print(f"[v70] guides {len(g['guides'])}편 (+{added}) · guide_extra {len(ex['guides'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
