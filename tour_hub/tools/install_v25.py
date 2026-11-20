#!/usr/bin/env python3
"""v25 데이터 병합 — 신규 도시 허브 6곳 + 가이드·숙소 연결.

    python3 tools/install_v25.py --dry-run
    python3 tools/install_v25.py

바꾸는 파일
-----------
- data/city_hubs.json   : 7곳 → 13곳 (서울·부산·강릉·여수·경주·나트랑 추가), index 문구 갱신
- data/guide_extra.json : 신규 가이드 6편의 hub 값을 새 허브 slug 로 연결
- data/stays.json       : 신규 6개 지역의 hub 값을 새 허브 slug 로 연결,
                          서울·여수·경주 지역에 연결 가이드 추가

여러 번 실행해도 같은 결과가 나오도록(멱등) slug 기준으로 덮어씁니다.
백업은 *.bak-v25 로 한 번만 남깁니다.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NEW_HUBS = [
    {
        "slug": "seoul",
        "name": "서울",
        "nav": "서울",
        "cityIds": ["seoul"],
        "country": "kr",
        "flag": "kr",
        "kicker": "SEOUL",
        "seoTitle": "서울 여행 코스·맛집·숙소 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "서울 성수·을지로·북촌·광장시장 맛집 4곳(카페 5,500원·냉면 18,000원·육회 200g 23,000원), 서울 숙소 5곳(레이크 호텔 1박 132,294원부터), 성수·북촌 1일 동선 가이드, 트립닷컴 서울 숙소 목록을 한 페이지에. 2026년 11월 확인 기준입니다.",
        "keywords": "서울 여행, 서울 맛집, 성수 카페, 어니언 성수, 우래옥 냉면, 북촌 만두, 광장시장 육회, 서울 1일 코스, 서울 숙소, 서울 호텔 추천",
        "h1": "서울 여행, <em>맛집·숙소·1일 동선</em>을 한 페이지에",
        "intro": "서울은 지하철 2호선 하나로 성수·을지로4가·북촌·광장시장이 이어져, 하루 네 끼를 4만 4,000원에 채울 수 있는 도시입니다. 아침은 성수 카페 아메리카노 5,500원, 점심은 우래옥 평양냉면 18,000원, 오후엔 북촌손만두 만둣국 9,500원, 저녁은 부촌육회 200g 23,000원이 같은 날에 들어갑니다. 숙소는 레이크 호텔 1박 132,294원부터 명동·공덕·동대문 5곳을 평점과 리뷰 수로 골랐고, 같은 등급도 주말과 평일 값이 크게 갈립니다.",
        "tourNote": "트립픽이 확인한 서울 단독 투어·패키지 상품은 아직 없습니다. 대신 성수·북촌 1일 동선 가이드와 서울 숙소 5곳, 트립닷컴 서울 숙소 목록으로 연결했습니다. 서울에서 출발하는 해외 상품은 홈의 지역 섹션에 있습니다.",
        "restaurants": "seoul",
        "giftCountry": None,
        "hotels": [],
        "flight": None,
        "image": "images/v24/seoul-seongsu-bukchon.jpg",
        "imageAlt": "북촌한옥마을 골목과 기와지붕, 뒤로 도시 빌딩",
        "guides": ["seoul-seongsu-bukchon-1d", "gyeongju-hwangridangil-2d", "busan-haeundae-gwangalli-2d"],
        "imageCredit": "사진: Pexels (거열 박)",
    },
    {
        "slug": "busan",
        "name": "부산",
        "nav": "부산",
        "cityIds": ["busan"],
        "country": "kr",
        "flag": "kr",
        "kicker": "BUSAN",
        "seoTitle": "부산 여행 코스·맛집·숙소 총정리 — 요트·국밥·해운대 (2026년 11월) | 트립픽",
        "metaDesc": "부산 요트·리버크루즈 4개(합승 17,000원·크루즈 8,000원·단독 249,000원), 해운대·광안리·서면 맛집 4곳(돼지국밥 10,500원·복국 15,000원), 부산 숙소 5곳(더퍼스트오션 송정 1박 63,150원부터), 해운대·광안리 1박2일과 요트 시간대 가이드 2편을 한 페이지에. 2026년 11월 확인 기준입니다.",
        "keywords": "부산 여행, 부산 1박2일, 부산 요트투어, 광안리 요트, 해운대 리버크루즈, 부산 돼지국밥, 금수복국, 고래사어묵, 해운대 숙소, 광안리 숙소, 부산 호텔",
        "h1": "부산 여행, <em>요트·국밥·숙소</em>를 한 페이지에",
        "intro": "부산은 광안리 요트 합승 17,000원, 해운대 리버크루즈 8,000원으로 바다 위에서 하루를 마무리하고, 서면·해운대·광안리 국밥집 세 곳이 24시간이라 도착 시간이 늦어도 한 끼는 남습니다. 밀양순대돼지국밥 10,500원, 금수복국 은복국 15,000원, 고래사어묵 어묵김밥 5,000원이면 1박2일 식비·액티비티가 6만 8,500원입니다. 숙소는 송정 더퍼스트오션 1박 63,150원부터 시그니엘 827,640원(2인)까지 5곳을 평점으로 골랐습니다.",
        "restaurants": "busan",
        "giftCountry": None,
        "hotels": ["busan"],
        "flight": None,
        "image": "images/n_busan_withyacht.jpg",
        "imageAlt": "광안리 앞바다를 달리는 요트와 광안대교",
        "guides": ["busan-haeundae-gwangalli-2d", "busan-yacht", "gyeongju-hwangridangil-2d", "yeosu-night-sea-2d"],
        "imageCredit": "사진: Pexels",
    },
    {
        "slug": "gangneung",
        "name": "강릉·평창",
        "nav": "강릉",
        "cityIds": ["gangneung", "gangwon"],
        "country": "kr",
        "flag": "kr",
        "kicker": "GANGNEUNG · PYEONGCHANG",
        "seoTitle": "강릉·평창 여행 — 겨울 바다·스키·맛집·숙소 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "강릉 겨울 바다·평창 스키 상품 5개(비발디 리프트 54,000원·강원 버스투어 39,500원), 초당·포남·교동·안목 맛집 4곳(순두부 15,000원·짬뽕 12,000원·꼬막 37,000원), 강릉 숙소 4곳(레스티아 1박 52,000원부터), 강릉 1박2일·강원 스키 가이드 4편을 한 페이지에. 2026년 11월 확인 기준입니다.",
        "keywords": "강릉 여행, 강릉 1박2일, 강릉 겨울 바다, 정동진, 경포 숙소, 초당순두부, 동화가든, 안목 카페, 강원 스키, 비발디파크 리프트, 평창 숙소",
        "h1": "강릉·평창 여행, <em>겨울 바다·스키·맛집</em>을 한 페이지에",
        "intro": "강릉은 KTX로 서울에서 두 시간이면 닿고, 초당 순두부 15,000원·교동 짬뽕 12,000원·포남 꼬막 37,000원(2~3인)·안목 커피 6,000원이 버스 한 번씩으로 이어집니다. 수요일만 피하면 되고, 같은 강원 동선에서 평창 스키를 붙이려면 비발디파크 리프트권 54,000원이나 스키장 왕복 셔틀 54,000원이 강릉 버스투어 39,500원과 함께 선택지가 됩니다. 숙소는 강릉역 레스티아 52,000원부터 경포·정동진 5성 4곳을 평점으로 골랐습니다.",
        "restaurants": "gangneung",
        "giftCountry": None,
        "hotels": [],
        "tripcomCity": "pyeongchang",
        "flight": None,
        "image": "images/v24/gangwon-gangneung-winter.jpg",
        "imageAlt": "강릉 해변의 소나무 숲과 겨울 바다",
        "guides": [
            "gangwon-gangneung-winter-sea-2d",
            "gangwon-ski",
            "gangwon-bustour",
            "ulleung-2n3d",
        ],
        "imageCredit": "사진: Pexels (정규송 Nui MALAMA)",
    },
    {
        "slug": "yeosu",
        "name": "여수",
        "nav": "여수",
        "cityIds": ["yeosu"],
        "country": "kr",
        "flag": "kr",
        "kicker": "YEOSU",
        "seoTitle": "여수 여행 — 게장·밤바다·숙소 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "여수 게장 맛집 4곳(돌게장 정식 13,000원·꽃게장 정식 33,000원·서대회비빔밥 13,000원), 여수 숙소 3곳(베네치아호텔 1박 111,112원부터), 해상케이블카 17,000원과 1박2일 77,600원 계산, 여수 밤바다 가이드까지 한 페이지에. 2026년 11월 확인 기준입니다.",
        "keywords": "여수 여행, 여수 1박2일, 여수 게장, 돌게장, 순이네 밥상, 여수 해상케이블카, 여수 밤바다, 낭만포차, 여수 숙소, 여수 호텔",
        "h1": "여수 여행, <em>게장·밤바다·숙소</em>를 한 페이지에",
        "intro": "여수는 게장 한 상이 여행의 중심입니다. 시내 순이네 밥상 돌게장+양념게장 정식 13,000원으로 점심을 먹고, 해상케이블카 일반 왕복 17,000원으로 돌산에 건너가 꽃게장 정식 33,000원까지 먹으면 1박2일 1인 77,600원이 나옵니다. 다만 게장 정식은 2인 이상 주문이 대부분이고 수요일 휴무인 집이 있어, 날짜를 먼저 확인하는 편이 좋습니다. 숙소는 엑스포역 신라스테이·베네치아 111,112원부터, 케이블카 자산정류장 소노캄까지 3곳을 평점으로 골랐습니다.",
        "tourNote": "트립픽이 확인한 여수 단독 투어·패키지 상품은 아직 없습니다. 대신 여수 밤바다 1박2일 가이드의 게장·케이블카 값과 동선, 여수 숙소 3곳, 트립닷컴 여수 숙소 목록으로 연결했습니다.",
        "restaurants": "yeosu",
        "giftCountry": None,
        "hotels": [],
        "flight": None,
        "image": "images/v24/yeosu-night-sea.jpg",
        "imageAlt": "여수 바다와 해안 건물의 옥상",
        "guides": ["yeosu-night-sea-2d", "busan-haeundae-gwangalli-2d", "gyeongju-hwangridangil-2d"],
        "imageCredit": "사진: Pexels (John One)",
    },
    {
        "slug": "gyeongju",
        "name": "경주",
        "nav": "경주",
        "cityIds": ["gyeongju"],
        "country": "kr",
        "flag": "kr",
        "kicker": "GYEONGJU",
        "seoTitle": "경주 여행 — 황리단길·야경·맛집·숙소 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "경주 황리단길·첨성대 맛집 4곳(한우국밥 12,000원·꼬막무침비빔밥 2인 31,000원·콩국 8,000원), 경주 숙소 3곳(경주 호텔 공간 1박 91,980원부터), 동궁과월지 3,000원 야경과 황리단길 1박2일 가이드까지 한 페이지에. 2026년 11월 확인 기준입니다.",
        "keywords": "경주 여행, 경주 1박2일, 황리단길 맛집, 경주 한우국밥, 향화정 꼬막, 동궁과월지 입장료, 경주 야경, 첨성대, 보문 숙소, 경주 호텔",
        "h1": "경주 여행, <em>황리단길·야경·숙소</em>를 한 페이지에",
        "intro": "경주는 황리단길 안에서 하루가 끝나는 도시입니다. 향화정 꼬막무침비빔밥 31,000원(2인)으로 점심, 고유한우국밥 한우국밥 12,000원으로 저녁, 동궁과월지 3,000원으로 밤을 채우면 이동은 도보로 충분합니다. 아침은 07:30에 여는 한우국밥집이나 16:30에 닫는 콩국집 시간을 맞춰야 하고, 불국사는 입장료가 없습니다. 숙소는 황리단길 경주 호텔 공간 91,980원부터 보문관광단지 코모도·더케이까지 3곳을 평점으로 골랐습니다.",
        "tourNote": "트립픽이 확인한 경주 단독 투어·패키지 상품은 아직 없습니다. 대신 경주 황리단길 1박2일 가이드의 식비·입장료·이동 시간, 경주 숙소 3곳, 트립닷컴 경주 숙소 목록으로 연결했습니다.",
        "restaurants": "gyeongju",
        "giftCountry": None,
        "hotels": [],
        "flight": None,
        "image": "images/v24/gyeongju-hwangridangil.jpg",
        "imageAlt": "경주 전통 누각과 노을",
        "guides": ["gyeongju-hwangridangil-2d", "busan-haeundae-gwangalli-2d", "yeosu-night-sea-2d", "seoul-seongsu-bukchon-1d"],
        "imageCredit": "사진: Pexels (WON JONG LEE)",
    },
    {
        "slug": "nhatrang",
        "name": "나트랑·달랏",
        "nav": "나트랑",
        "cityIds": ["nhatrang"],
        "country": "vn",
        "flag": "vn",
        "kicker": "NHA TRANG · DALAT",
        "seoTitle": "나트랑·달랏 여행 — 반미·리조트·숙소 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "나트랑·달랏 상품 3개(달랏 1일 투어 52,155원·인천 자유여행 732,350원·부산 출발 5일 687,730원), 반미 1,300원·분까 2,340원·해산물 1인 10,400원부터, 나트랑 숙소 3곳(파나마 1박 55,113원부터), 3박4일 맛집·리조트 가이드 2편과 베트남 eSIM·기념품까지 한 페이지에. 2026년 11월 확인 기준입니다.",
        "keywords": "나트랑 여행, 나트랑 3박4일, 나트랑 맛집, 반미 판, 분까, 나트랑 숙소, 나트랑 리조트, 파나마 나트랑, 인터컨티넨탈 나트랑, 나트랑 달랏 투어, 깜라인공항",
        "h1": "나트랑·달랏 여행, <em>투어·맛집·숙소</em>를 한 페이지에",
        "intro": "나트랑은 반미 한 개 1,300원, 국수 한 그릇 2,300~3,100원인 도시라 식비가 거의 들지 않고, 그 돈을 숙소에 쓰는 쪽이 만족도가 높습니다. 파나마 나트랑 1박 55,113원, 인터컨티넨탈 217,367원, 아미아나 261,873원(2인·세금 포함) 중 어디를 잡느냐에 따라 3박 값이 16만원과 65만원으로 갈립니다. 달랏 1일 투어 52,155원, 인천 자유여행 5일 732,350원, 부산 출발 687,730원을 같은 표에 놓았고, 깜라인공항에서 시내까지는 차로 49분입니다.",
        "restaurants": "nhatrang",
        "giftCountry": "vn",
        "hotels": ["nhatrang"],
        "flight": None,
        "image": "images/courses/nhatrang.jpg",
        "imageAlt": "나트랑 해변과 리조트",
        "guides": [
            "nhatrang-3n4d-food-resort",
            "nhatrang-dalat-tour-vs-free",
            "vietnam-esim",
            "vietnam-souvenir-list",
        ],
        "imageCredit": "사진: Pexels",
    },
]

INDEX = {
    "indexTitle": "도시별 여행 페이지 13곳 — 투어·맛집·선물·숙소 한 번에 | 트립픽",
    "indexDesc": "오사카·교토, 도쿄, 후쿠오카·규슈, 다낭·호이안, 나트랑·달랏, 방콕, 타이베이, 제주, 서울, 부산, 강릉·평창, 여수, 경주 13곳. 도시마다 실제 판매 중인 투어·패키지, 검증한 현지 맛집, 대표 선물 가격, 트립닷컴 숙소·항공권, 관련 가이드를 한 페이지에 모았습니다.",
    "indexIntro": "여행을 검색할 때 사람들이 실제로 치는 말은 도시 이름입니다. 그래서 도시마다 한 페이지에 <b>투어·패키지, 현지 맛집, 대표 선물, 숙소·항공권, 관련 가이드</b>를 같은 기준으로 모았습니다. 해외 7곳에 이어 국내 6곳(서울·부산·강릉·여수·경주·제주)까지 13곳이고, 가격·영업시간·취소 규정은 각 페이지에 확인 날짜를 적었고 링크는 모두 실제 판매·예약 페이지로 이어집니다.",
}

# 신규 가이드 6편 → 새 도시 허브
GUIDE_HUB = {
    "seoul-seongsu-bukchon-1d": "seoul",
    "busan-haeundae-gwangalli-2d": "busan",
    "gangwon-gangneung-winter-sea-2d": "gangneung",
    "yeosu-night-sea-2d": "yeosu",
    "gyeongju-hwangridangil-2d": "gyeongju",
    "nhatrang-3n4d-food-resort": "nhatrang",
}

STAY_SCOPE = {"jeju": "kr"}   # 국내 숙소인데 intl 로 분류돼 있던 것 수정

# stays.json 지역 → 허브 / 연결 가이드(비어 있던 곳만)
STAY_HUB = {
    "seoul": {"hub": "seoul", "guides": [{"slug": "seoul-seongsu-bukchon-1d", "label": "서울 성수·북촌 1일"}]},
    "busan": {"hub": "busan", "guides": None},
    "gangneung": {"hub": "gangneung", "guides": None},
    "yeosu": {"hub": "yeosu", "guides": [{"slug": "yeosu-night-sea-2d", "label": "여수 밤바다 1박2일"}]},
    "gyeongju": {"hub": "gyeongju", "guides": [{"slug": "gyeongju-hwangridangil-2d", "label": "경주 황리단길 1박2일"}]},
    "nhatrang": {"hub": "nhatrang", "guides": [{"slug": "nhatrang-3n4d-food-resort", "label": "나트랑 3박4일 맛집·리조트"}]},
}


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def dump(name: str, obj, dry: bool):
    text = json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
    path = DATA / name
    bak = path.with_suffix(path.suffix + ".bak-v25")
    if not dry and not bak.exists():
        shutil.copy2(path, bak)
    if not dry:
        path.write_text(text, encoding="utf-8")
    print(f"  · {name}: {'(dry-run) ' if dry else ''}{len(text)} bytes")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run

    # 1) city_hubs.json
    hubs = load("city_hubs.json")
    have = {h["slug"]: h for h in hubs["cities"]}
    added = []
    for spec in NEW_HUBS:
        if spec["slug"] in have:
            have[spec["slug"]].update(spec)
        else:
            hubs["cities"].append(spec)
            added.append(spec["slug"])
    for hub in hubs["cities"]:
        if hub["slug"] in {s["slug"] for s in NEW_HUBS}:
            hub["stayCards"] = True
    hubs.update(INDEX)
    hubs["updated"] = "2026-11-20"
    dump("city_hubs.json", hubs, dry)
    print(f"    도시 허브 {len(hubs['cities'])}곳 (신규 {len(added)}: {', '.join(added) or '없음'})")

    # 2) guide_extra.json
    extra = load("guide_extra.json")
    fixed = []
    for slug, hub in GUIDE_HUB.items():
        g = (extra.get("guides") or {}).get(slug)
        if g is None:
            raise SystemExit(f"guide_extra.json 에 {slug} 가 없습니다.")
        if g.get("hub") != hub:
            g["hub"] = hub
            fixed.append(slug)
    dump("guide_extra.json", extra, dry)
    print(f"    guide_extra hub 연결 {len(fixed)}편: {', '.join(fixed) or '이미 연결됨'}")

    # 3) stays.json
    stays = load("stays.json")
    for r in stays["regions"]:
        spec = STAY_HUB.get(r["id"])
        if not spec:
            continue
        r["hub"] = spec["hub"]
        if spec["guides"] is not None and not r.get("guides"):
            r["guides"] = spec["guides"]
    # 제주는 국내 숙소인데 scope 가 intl 로 들어가 국내/해외 집계가 20·30 으로 어긋나 있었다.
    # 국내 24(서울5·부산5·강릉4·여수3·경주3·제주4) · 해외 26 으로 바로잡는다.
    for r in stays["regions"]:
        if r["id"] in STAY_SCOPE:
            r["scope"] = STAY_SCOPE[r["id"]]
    kr = sum(len([h for h in stays["hotels"] if h["region"] == r["id"]]) for r in stays["regions"] if r.get("scope") == "kr")
    total = len(stays["hotels"])
    dump("stays.json", stays, dry)
    print("    stays.json 지역 hub 연결: " + ", ".join(sorted(STAY_HUB)))
    print(f"    stays.json 국내 {kr}곳 · 해외 {total - kr}곳 (총 {total}곳)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
