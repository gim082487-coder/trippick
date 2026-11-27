#!/usr/bin/env python3
"""v65: 트립닷컴 제휴 상품 보강 — 뉴욕·나고야·삿포로·시드니·런던 개트윅.

    python3 tools/apply_v65_products.py

2026-11-27 플레이라이트 크로미움으로 직접 열어 HTTP 200 + 한국어 제목 + 파트너스 코드를 확인한 URL만 넣는다.
(항공권 페이지는 같은 날 432로 차단돼 신규 노선을 추가하지 않았다.)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
AID = "Allianceid=11407530&SID=336341874"
CHECKED = "2026-11-27"


def tc(kind: str, cid: str) -> str:
    return f"{AID}&trip_sub1={kind}_{cid}&trip_sub3=D21285812"


TICKETS = [
    {"id": "ticket_newyork", "city": "뉴욕", "cityId": "newyork", "country": "미국", "flag": "us",
     "category": "ticket", "label": "입장권·액티비티", "title": "뉴욕 입장권·액티비티",
     "highlight": "자유의 여신상·엠파이어스테이트·메트",
     "summary": "자유의 여신상, 엠파이어스테이트 빌딩, 톱 오브 더 록, 메트로폴리탄 미술관 등 뉴욕 입장권·투어 목록. 페이지 제목 '뉴욕 최저가 예약 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/things-to-do/list?searchkey=633&searchtype=1&" + tc("ticket", "newyork"),
     "status": "verified_200_ko"},
    {"id": "ticket_nagoya", "city": "나고야", "cityId": "nagoya", "country": "일본", "flag": "jp",
     "category": "ticket", "label": "입장권·액티비티", "title": "나고야 입장권·액티비티",
     "highlight": "지브리파크·레고랜드·나고야성",
     "summary": "지브리파크, 레고랜드 재팬, 나고야성, 아츠타신궁 등 나고야 입장권·투어 목록. 페이지 제목 '나고야 최저가 예약 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/things-to-do/list?searchkey=360&searchtype=1&" + tc("ticket", "nagoya"),
     "status": "verified_200_ko"},
    {"id": "ticket_sapporo", "city": "삿포로", "cityId": "sapporo", "country": "일본", "flag": "jp",
     "category": "ticket", "label": "입장권·액티비티", "title": "삿포로 입장권·액티비티",
     "highlight": "삿포로·홋카이도 당일투어",
     "summary": "삿포로 시내와 비에이·후라노·오타루 당일투어, 홋카이도 액티비티 목록. 페이지 제목 '삿포로 최저가 예약 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/things-to-do/list?searchkey=641&searchtype=1&" + tc("ticket", "sapporo"),
     "status": "verified_200_ko"},
    {"id": "ticket_sydney", "city": "시드니", "cityId": "sydney", "country": "호주", "flag": "au",
     "category": "ticket", "label": "입장권·액티비티", "title": "시드니 입장권·액티비티",
     "highlight": "오페라하우스·블루마운틴·타롱가",
     "summary": "시드니 오페라하우스, 블루마운틴, 타롱가 동물원, 하버 크루즈 등 시드니 입장권·투어 목록. 페이지 제목 '시드니 최저가 예약 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/things-to-do/list?searchkey=501&searchtype=1&" + tc("ticket", "sydney"),
     "status": "verified_200_ko"},
]

TRANSFERS = [
    {"id": "transfer_jfk", "city": "뉴욕", "cityId": "newyork", "country": "미국", "flag": "us",
     "category": "transfer", "label": "공항픽업", "title": "JFK 공항픽업",
     "highlight": "맨해튼·브루클린 · 차종별 예약",
     "summary": "존 F. 케네디 국제공항(JFK) 도착 후 맨해튼·브루클린 숙소까지 차종별 픽업 요금. 페이지 제목 '존 F. 케네디 국제공항 공항 픽업/샌딩 | 트립닷컴' 확인(2026-11-27). 요금은 날짜·차종에 따라 달라진다.",
     "url": "https://kr.trip.com/airport-transfers/airport-jfk/?" + tc("transfer", "jfk"),
     "status": "verified_200_ko"},
    {"id": "transfer_ewr", "city": "뉴욕", "cityId": "newyork", "country": "미국", "flag": "us",
     "category": "transfer", "label": "공항픽업", "title": "뉴어크(EWR) 공항픽업",
     "highlight": "맨해튼 · 뉴저지 호텔",
     "summary": "뉴어크 리버티 국제공항(EWR)에서 맨해튼·뉴저지 숙소까지 픽업. 페이지 제목 '뉴어크 리버티 국제공항 공항 픽업/샌딩 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/airport-transfers/airport-ewr/?" + tc("transfer", "ewr"),
     "status": "verified_200_ko"},
    {"id": "transfer_ngo", "city": "나고야", "cityId": "nagoya", "country": "일본", "flag": "jp",
     "category": "transfer", "label": "공항픽업", "title": "중부국제공항(NGO) 공항픽업",
     "highlight": "나고야역·사카에 · 차종별",
     "summary": "중부국제공항(NGO)에서 나고야역·사카에 숙소까지 픽업. 페이지 제목 '츄부국제공항 공항 픽업/샌딩 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/airport-transfers/airport-ngo/?" + tc("transfer", "ngo"),
     "status": "verified_200_ko"},
    {"id": "transfer_cts", "city": "삿포로", "cityId": "sapporo", "country": "일본", "flag": "jp",
     "category": "transfer", "label": "공항픽업", "title": "신치토세공항(CTS) 공항픽업",
     "highlight": "삿포로 시내·조잔케이 · 짐 많을 때",
     "summary": "신치토세공항(CTS)에서 삿포로 시내·조잔케이 온천 숙소까지 픽업. 페이지 제목 '신치토세 공항 공항 픽업/샌딩 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/airport-transfers/airport-cts/?" + tc("transfer", "cts"),
     "status": "verified_200_ko"},
    {"id": "transfer_lgw", "city": "런던", "cityId": "london", "country": "영국", "flag": "gb",
     "category": "transfer", "label": "공항픽업", "title": "개트윅(LGW) 공항픽업",
     "highlight": "런던 시내 · 3인 이상",
     "summary": "런던 개트윅 공항(LGW)에서 시내 숙소까지 픽업. 히드로(LHR) 픽업은 별도 상품으로 이미 등록돼 있다. 페이지 제목 '런던 개트윅 공항 공항 픽업/샌딩 | 트립닷컴' 확인(2026-11-27).",
     "url": "https://kr.trip.com/airport-transfers/airport-lgw/?" + tc("transfer", "lgw"),
     "status": "verified_200_ko"},
]

ESIMS = [
    {"id": "esim_nagoya", "city": "나고야", "cityId": "nagoya", "country": "일본", "flag": "jp",
     "category": "esim", "label": "eSIM·유심", "title": "나고야 유심·eSIM",
     "highlight": "나고야 eSIM·유심 목록",
     "summary": "나고야 도착 전에 설치하는 eSIM·유심 목록. 페이지 제목 '나고야 여행 유심 및 이심(eSIM) 추천, 예약 | 트립닷컴' 확인(2026-11-27). 상품 수·최저가는 페이지에서 날짜별로 달라 이 글에 숫자로 적지 않는다.",
     "url": "https://kr.trip.com/things-to-do/experiences/nagoya-simcard/?" + tc("esim", "nagoya").replace("D21285812", "D21303312"),
     "status": "verified_200_ko"},
]


def main() -> int:
    p = D / "tripcom.json"
    t = json.loads(p.read_text(encoding="utf-8"))
    for key, rows in (("tickets", TICKETS), ("transfers", TRANSFERS), ("esims", ESIMS)):
        have = {x["id"] for x in (t.get(key) or [])}
        for r in rows:
            if r["id"] in have:
                continue
            r = dict(r)
            r["checked"] = CHECKED
            t.setdefault(key, []).append(r)
    src = t.get("activitySource")
    if isinstance(src, dict):
        src["v65"] = {
            "checked": CHECKED,
            "method": "플레이라이트 크로미움으로 직접 열어 HTTP 200 + 한국어 제목 확인",
            "added": "입장권 4건(뉴욕·나고야·삿포로·시드니) · 공항픽업 5건(JFK·EWR·NGO·CTS·LGW) · eSIM 1건(나고야)",
            "rejected": "신규 항공권 페이지는 같은 날 HTTP 432(차단)로 확인하지 못해 등록하지 않았습니다. 뉴욕 eSIM(new-york-simcard)은 제목이 비어 있고, usa-simcard는 '우사 시'로 표시돼 제외했습니다.",
        }
    p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v65] tickets {len(t['tickets'])} · transfers {len(t['transfers'])} · esims {len(t['esims'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
