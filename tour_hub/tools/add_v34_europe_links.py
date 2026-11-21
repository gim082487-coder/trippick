#!/usr/bin/env python3
"""v34 — 유럽 4도시(파리·런던·로마·바르셀로나) 트립닷컴 제휴 링크를 data/tripcom.json 에 병합.

발급·검증 방법
- 파트너스 콘솔(partners.trip.com)은 이 작업 환경에서 접속이 막혀(ERR_TUNNEL_CONNECTION_FAILED)
  새 trip_sub3 를 발급하지 못했다. 대신 이미 발급·검증된 두 서브ID를 그대로 쓴다
  (항공·호텔 D21275837 / 투어·공항픽업 D21285812, Allianceid 11407530 · SID 336341874).
- 링크 모양은 기존 8개 도시에서 쓰던 검증된 패턴 그대로다.
  · 항공  https://kr.trip.com/flights/Seoul-to-<City>/tickets-SEL-<IATA>?flighttype=S&dcity=SEL&acity=<IATA>
  · 호텔  https://kr.trip.com/hotels/list?city=<cityId>&display=…
  · 투어  https://kr.trip.com/things-to-do/list?searchkey=<cityId>&searchtype=1
  · 픽업  https://kr.trip.com/airport-transfers/airport-<iata>/
- 2026-11-21 실제 브라우저(관리 브라우저, 한국 IP)로 열어 제목·도시·요금을 확인했다.
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
AID = "11407530"
SID = "336341874"
SUB_FLIGHT = "D21275837"
SUB_TOUR = "D21285812"

CITIES = [
    # id, 이름, 국가, 국기, IATA, cityId, 영문 슬러그, 호텔 표시명, 호텔 note, 픽업 요금, 항공 비고
    ("paris", "파리", "프랑스", "fr", "CDG", 192, "Paris", "PAR",
     "파리", "에펠탑·루브르·몽파르나스 · 파리 3박", "스탠다드 62,154원~ (미니밴 83,114원)",
     "샤를드골(CDG) · 직항 14시간 30분"),
    ("london", "런던", "영국", "gb", "LHR", 338, "London", "LON",
     "런던", "블룸즈버리·빅토리아 · 히드로 15분", "스탠다드 71,041원~ (중형 87,044원)",
     "히스로(LHR) · 직항 14시간 40분"),
    ("rome", "로마", "이탈리아", "it", "FCO", 343, "Rome", "ROM",
     "로마", "테르미니·바티칸 · 피우미치노 32분", "스탠다드 75,428원~ (프리미엄 85,453원)",
     "피우미치노(FCO) · 직항 13시간 30분"),
    ("barcelona", "바르셀로나", "스페인", "es", "BCN", 40795, "Barcelona", "BCN",
     "바르셀로나", "카탈루냐 광장·사그라다 · 엘프라트 20분", "스탠다드 55,448원~ (미니 55,293원)",
     "엘프라트(BCN) · 경유 16시간~"),
]


def flight_url(slug: str, iata: str, sub1: str) -> str:
    return (f"https://kr.trip.com/flights/Seoul-to-{slug}/tickets-SEL-{iata}"
            f"?flighttype=S&dcity=SEL&acity={iata}&Allianceid={AID}&SID={SID}"
            f"&trip_sub1={sub1}&trip_sub3={SUB_FLIGHT}")


def hotel_url(city_id: int, name: str, sub1: str) -> str:
    from urllib.parse import quote
    q = quote(name)
    return (f"https://kr.trip.com/hotels/list?city={city_id}&display={q}&optionId={city_id}"
            f"&optionType=City&optionName={q}&Allianceid={AID}&SID={SID}"
            f"&trip_sub1={sub1}&trip_sub3={SUB_FLIGHT}")


def ticket_url(city_id: int, sub1: str) -> str:
    return (f"https://kr.trip.com/things-to-do/list?searchkey={city_id}&searchtype=1"
            f"&Allianceid={AID}&SID={SID}&trip_sub1={sub1}&trip_sub3={SUB_TOUR}")


def transfer_url(iata: str, sub1: str) -> str:
    return (f"https://kr.trip.com/airport-transfers/airport-{iata.lower()}/"
            f"?Allianceid={AID}&SID={SID}&trip_sub1={sub1}&trip_sub3={SUB_TOUR}")


def main() -> None:
    path = DATA / "tripcom.json"
    d = json.loads(path.read_text(encoding="utf-8"))

    have_f = {f["route"] for f in d["flights"]}
    have_h = {h["cityId"] for h in d["hotels"]}
    have_t = {t["id"] for t in d["tickets"]}
    have_x = {t["id"] for t in d["transfers"]}

    for cid, name, country, flag, iata, city_id, slug, fcity, hotel_name, hotel_note, pickup, flight_note in CITIES:
        route = f"서울 → {name}"
        if route not in have_f:
            d["flights"].append({
                "route": route,
                "sub": flight_note,
                "url": flight_url(slug, fcity, f"flight_sel_{fcity.lower()}"),
                "tags": ["flight", "europe"],
            })
        if cid not in have_h:
            d["hotels"].append({
                "city": hotel_name,
                "flag": flag,
                "sub": hotel_note,
                "note": f"{name} 시내·공항 이동 기준",
                "url": hotel_url(city_id, name, f"hotel_{cid}"),
                "cityId": cid,
                "tags": ["europe"],
            })
        tid = f"ticket_{cid}"
        if tid not in have_t:
            d["tickets"].append({
                "id": tid,
                "city": name,
                "cityId": cid,
                "country": country,
                "flag": flag,
                "category": "ticket",
                "label": "입장권·액티비티",
                "title": f"{name} 입장권·액티비티",
                "highlight": {"paris": "루브르·오르세·센강 크루즈·베르사유",
                              "london": "대영박물관·런던아이·해리포터 스튜디오",
                              "rome": "콜로세움·바티칸·보르게세",
                              "barcelona": "사그라다 파밀리아·구엘공원·카사바트요"}[cid],
                "summary": f"트립닷컴 '{name} 액티비티' 목록(2026-11-21 브라우저 확인). 입장권·가이드투어·패스를 같은 페이지에서 비교한다.",
                "url": ticket_url(city_id, f"ticket_{cid}"),
                "status": "verified_200_ko" if cid == "paris" else "verified_pattern_200_ko",
            })
        xid = f"transfer_{iata.lower()}"
        if xid not in have_x:
            d["transfers"].append({
                "id": xid,
                "city": name,
                "cityId": cid,
                "country": country,
                "flag": flag,
                "category": "transfer",
                "label": "공항픽업",
                "title": {"CDG": "샤를드골공항(CDG) 공항픽업", "LHR": "히스로공항(LHR) 공항픽업",
                          "FCO": "피우미치노공항(FCO) 공항픽업", "BCN": "엘프라트공항(BCN) 공항픽업"}[iata],
                "highlight": f"{pickup} · 차종별 예약",
                "summary": f"{pickup}. 공항→{name} 시내 호텔 구간, 차종(스탠다드·미니밴·프리미엄)별 요금과 무료 대기 조건을 같은 페이지에서 비교한다.",
                "url": transfer_url(iata, f"transfer_{iata.lower()}"),
                "status": "verified_200_ko",
            })

    d["source"]["checked"] = "2026-11-21"
    d["source"]["method"] += (
        " v34: 유럽 4도시(파리 CDG·런던 LHR·로마 FCO·바르셀로나 BCN) 항공권 4건·공항픽업 4건·호텔 목록 4건·"
        "투어 목록 4건을 기존 검증 패턴(Allianceid 11407530/SID 336341874, trip_sub3 D21275837·D21285812)으로 "
        "추가하고 관리 브라우저로 제목·도시·요금을 확인했다(파트너스 콘솔은 이 환경에서 접속 차단)."
    )
    path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("flights", len(d["flights"]), "hotels", len(d["hotels"]),
          "tickets", len(d["tickets"]), "transfers", len(d["transfers"]))


if __name__ == "__main__":
    main()
