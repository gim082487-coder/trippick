#!/usr/bin/env python3
"""v35 — 유럽 4도시 eSIM·유심 제휴 링크 + 유럽 전역 eSIM 상품 1건을 data/tripcom.json 에 병합하고,
data/season.json 의 유럽 4도시 `affiliateTodo`(eSIM) 를 해소한다.

발급·검증 방법 (2026-11-21)
- 파트너스 콘솔(partners.trip.com)은 이 작업 환경에서 접속이 막혀 새 trip_sub3 를 발급하지 못한다.
  그래서 v15~v34 에서 이미 쓴 검증된 서브ID(tour/activity D21303312, Allianceid 11407530 · SID 336341874)를
  그대로 쓰고, 링크 모양도 기존 eSIM 5개 도시와 똑같이 맞췄다.
    · 도시 목록  https://kr.trip.com/things-to-do/experiences/<city>-simcard/
    · 상품 상세  https://kr.trip.com/things-to-do/detail/<상품번호>/
- curl(iPhone Safari UA) 로 5개 URL 모두 HTTP 200 + 한국어 <title> 을 확인했고,
  상품 수·최저가·평점은 각 페이지의 JSON-LD(ItemList.numberOfItems, Offer.price)와 FAQ 문장에서 읽었다.
    파리 30개 · 런던 34개 · 로마 27개 · 바르셀로나 28개
    유럽 전역 상품(53369178): 4.6점·리뷰 13,487 · 109원(1일 500MB)~77,895원(총 50GB·90일)

    python3 tools/add_v35_europe_esim.py
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
AID = "11407530"
SID = "336341874"
SUB_TOUR = "D21303312"

CITIES = [
    # id, 이름, 국가, 국기, cityId, 슬러그, 상품 수, 최저가(원), 강조, 요약
    ("paris", "파리", "프랑스", "fr", 192, "paris", 30, 109,
     "유럽 eSIM 30개 상품 · 1일 500MB 109원부터",
     "파리 도착 전에 설치하는 유럽·프랑스 eSIM 30개 상품. 유럽 45개국 공용 상품이 1일 500MB 109원부터이고, "
     "프랑스 번호·통화가 되는 Orange 상품은 24시간 단위 3,154원(31일 총량형 20,771원)입니다. "
     "가장 많이 팔린 유럽 전역 상품은 4.6점·리뷰 13,487건입니다."),
    ("london", "런던", "영국", "gb", 338, "london", 34, 109,
     "영국 eSIM 34개 상품 · 1일 500MB 109원부터",
     "런던 도착 전에 설치하는 영국·유럽 eSIM 34개 상품. 유럽 공용 1일권이 109원부터, 영국 전용 1일권이 138원부터이고, "
     "영국 번호·통화가 되는 CMLINK UK 40GB/80GB는 9,386원(4.9점·리뷰 124건), Lyca 30GB는 14,044원입니다."),
    ("rome", "로마", "이탈리아", "it", 343, "rome", 27, 109,
     "이탈리아 eSIM 27개 상품 · 1일 500MB 102원부터",
     "로마 도착 전에 설치하는 이탈리아·유럽 eSIM 27개 상품. 이탈리아 전용 1일권이 102원(4.5점·리뷰 365건)으로 "
     "유럽 공용 1일권(109원)보다 쌉니다. 3~60일 총량형과 24시간 단위 요금제가 함께 있습니다."),
    ("barcelona", "바르셀로나", "스페인", "es", 40795, "barcelona", 28, 109,
     "스페인 eSIM 28개 상품 · 1일 500MB 109원부터",
     "바르셀로나 도착 전에 설치하는 스페인·유럽 eSIM 28개 상품. 스페인 전용 1일권이 109원부터이고, "
     "보다폰 5G 유심(데이터+통화)은 공항 T1·T2 수령 5,343원(4.9점·리뷰 21건)입니다. "
     "유럽 공용 상품은 1일 500MB부터 총 50GB까지 있습니다."),
]

EUROPE = {
    "id": "esim_europe",
    "city": "유럽",
    "cityId": "europe",
    "country": "유럽",
    "flag": "eu",
    "category": "esim",
    "label": "eSIM·유심",
    "title": "유럽 전역 eSIM (45개국·1~90일)",
    "highlight": "4.6점·리뷰 13,487 · 1일 500MB 109원부터",
    "summary": "여러 나라를 한 장으로 도는 유럽 전역 eSIM. 1일 500MB부터 총 50GB·90일까지 요금제가 있고, "
               "최저 109원·최고 77,895원(2026-11-21 기준)입니다. 파리·런던·로마·바르셀로나를 잇는 일정이면 "
               "나라별 상품을 네 번 사는 대신 이 상품 하나로 커버할 수 있습니다.",
    "url": (f"https://kr.trip.com/things-to-do/detail/53369178/?Allianceid={AID}&SID={SID}"
            f"&trip_sub1=esim_europe&trip_sub3={SUB_TOUR}"),
    "status": "verified_200_ko",
}


def city_url(slug: str, sub1: str) -> str:
    return (f"https://kr.trip.com/things-to-do/experiences/{slug}-simcard/"
            f"?Allianceid={AID}&SID={SID}&trip_sub1={sub1}&trip_sub3={SUB_TOUR}")


def main() -> None:
    tc_path = DATA / "tripcom.json"
    tc = json.loads(tc_path.read_text(encoding="utf-8"))
    have = {e["id"] for e in tc["esims"]}

    added = []
    for cid, name, country, flag, city_id, slug, n, low, highlight, summary in CITIES:
        eid = f"esim_{cid}"
        if eid in have:
            continue
        tc["esims"].append({
            "id": eid,
            "city": name,
            "cityId": cid,
            "cityNo": city_id,
            "country": country,
            "flag": flag,
            "category": "esim",
            "label": "eSIM·유심",
            "title": f"{name} 유심·eSIM",
            "highlight": highlight,
            "summary": summary,
            "products": n,
            "fromPrice": low,
            "url": city_url(slug, eid),
            "status": "verified_200_ko",
            "checked": "2026-11-21",
        })
        added.append(eid)

    if EUROPE["id"] not in have:
        tc["esims"].append(dict(EUROPE, checked="2026-11-21"))
        added.append(EUROPE["id"])

    tc["source"]["checked"] = "2026-11-21"
    note = (" v35: 유럽 4도시(파리 192·런던 338·로마 343·바르셀로나 40795) eSIM·유심 목록 4건과 "
            "유럽 전역 eSIM 상품 1건(53369178)을 기존 검증 패턴(Allianceid 11407530/SID 336341874, "
            "trip_sub3 D21303312)으로 추가했다. 5개 URL 모두 curl(iPhone UA) HTTP 200 + 한국어 title, "
            "상품 수·최저가는 JSON-LD(ItemList.numberOfItems·Offer.price), 평점은 페이지 구조화 데이터에서 확인했다.")
    if "v35:" not in tc["source"]["method"]:
        tc["source"]["method"] += note
    tc_path.write_text(json.dumps(tc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # season.json — 유럽 4도시 eSIM 제휴 활성 + affiliateTodo 해소
    season_path = DATA / "season.json"
    season = json.loads(season_path.read_text(encoding="utf-8"))
    cleared = []
    for c in season["cities"]:
        if c["id"] in {x[0] for x in CITIES}:
            c.setdefault("affiliate", {})["esim"] = True
            before = list(c.get("affiliateTodo") or [])
            after = [t for t in before if not t.startswith("esim:")]
            c["affiliateTodo"] = after
            if len(after) != len(before):
                cleared.append((c["id"], before, after))
    season["version"] = "v35"
    season["updated"] = "2026-11-21"
    season_path.write_text(json.dumps(season, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("tripcom esims", len(tc["esims"]), "added", added)
    for cid, before, after in cleared:
        print("cleared", cid, before, "->", after)


if __name__ == "__main__":
    main()
