#!/usr/bin/env python3
"""v34 — 도시별 「한 번에 예약·준비 묶음」 링크 묶음을 만든다.

data/tripcom.json(트립닷컴 파트너스) · data/stays.json(찐숙소) · data/essentials.json(쿠팡·네이버)
· data/season.json(도시 이름) 만 읽어서 실제로 존재하는 링크만 담는다. 새 URL 을 지어내지 않는다.

    python3 tools/build_bundles.py      # data/bundles.json 생성

출력 구조
{
 "checked": "2026-11-21",
 "cities": { "<cityId>": {"name": "파리", "items": {"flight": {…}, "hotel": {…}, …}} },
 "alias":  { "italy": "rome", "eu_west": "paris", … },      # 계획서 도시 → 묶음 도시
 "currencyCity": { "JPY": "osaka", … }                      # /exchange 통화 → 도시
}
item = {"label": "서울 → 파리 항공권", "note": "최저가 검색", "url": "https://…", "external": true}
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

PLANNER_ONLY = {
    "gangwon": ("강원", "gangwon"),
    "sapporo": ("삿포로", "sapporo"),
    "guam": ("괌", "guam"),
    "hawaii": ("하와이", "hawaii"),
    "ulleung": ("울릉도", "ulleung"),
}
ALIAS = {
    "italy": "rome",
    "eu_west": "paris",
    "eu_iberia": "barcelona",
    "gangwon": "gangwon",
    "sapporo": "sapporo",
    "guam": "guam",
    "hawaii": "hawaii",
}
CURRENCY_CITY = {
    "JPY": "osaka", "VND": "danang", "THB": "bangkok", "TWD": "taipei",
    "EUR": "paris", "GBP": "london", "SGD": "singapore", "HKD": "hongkong",
    "USD": "guam",
}
ESS_ESIM = {
    "jp": ("jp-esim-usimsa-3d", "일본 eSIM 3일 무제한"),
    "vn": ("vn-esim-usimsa-3d", "베트남 eSIM 3일 무제한"),
    "th": ("th-esim-usimsa-3d", "태국 eSIM 3일 무제한"),
    "tw": ("tw-esim-usimsa-3d", "대만 eSIM 3일 무제한"),
}
# 도시별로 어울리는 쿠팡 필수품(모두 실제 제휴 링크)
ESS_GOODS = {
    "default": ("cp-adapter-nemotab", "멀티어댑터 PD35W", "해외 콘센트 대비"),
    "kr": ("cp-bostonbag-mongddang", "접이식 보스턴백", "기내 반입 보조가방"),
}
EU_GOODS = ("cp-adapter-nemotab", "유럽 멀티어댑터", "C·G형 콘센트 대비")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    tc = load("tripcom.json")
    stays = load("stays.json")
    ess = {e["id"]: e for e in load("essentials.json")["products"]}
    season = load("season.json")
    stay_count = {}
    for h in stays["hotels"]:
        stay_count[h["region"]] = stay_count.get(h["region"], 0) + 1

    cities: dict[str, dict] = {}
    for c in season["cities"]:
        cid, name = c["id"], c["name"]
        items: dict[str, dict] = {}
        short = name.split("·")[0]

        f = next((x for x in tc.get("flights") or [] if short in x["route"]), None)
        if f:
            items["flight"] = {"label": f"{f['route']} 항공권", "note": "최저가 검색",
                               "url": f["url"], "external": True}

        h = next((x for x in tc.get("hotels") or [] if x.get("cityId") == cid), None)
        if h:
            items["hotel"] = {"label": f"{name} 숙소 검색", "note": "이 달 요금",
                              "url": h["url"], "external": True}

        t = next((x for x in tc.get("tickets") or [] if x.get("cityId") == cid), None)
        if not t:
            r = next((x for x in tc.get("resorts") or [] if x.get("cityId") == cid), None)
            if r and (r.get("ticket") or {}).get("url"):
                t = {"title": r["ticket"].get("title") or f"{name} 입장권·액티비티", "url": r["ticket"]["url"]}
        if t:
            items["ticket"] = {"label": t["title"], "note": "입장권·투어",
                               "url": t["url"], "external": True}

        x = next((y for y in tc.get("transfers") or [] if y.get("cityId") == cid), None)
        if not x:
            r = next((y for y in tc.get("resorts") or [] if y.get("cityId") == cid), None)
            if r and (r.get("transfer") or {}).get("url"):
                x = {"title": r["transfer"].get("title") or "공항픽업", "url": r["transfer"]["url"]}
        if x:
            items["transfer"] = {"label": x.get("title") or "공항픽업", "note": "공항→숙소",
                                 "url": x["url"], "external": True}

        if stay_count.get(cid):
            items["stays"] = {"label": f"찐숙소 {stay_count[cid]}곳 비교", "note": "평점·1박 최저가",
                              "url": f"/stays#{cid}", "external": False}

        e = next((z for z in tc.get("esims") or [] if z.get("cityId") == cid), None)
        if e:
            note = (f"{e['fromPrice']:,}원~ · 도착 전 설치" if e.get("fromPrice")
                    else "도착 전 설치")
            items["esim"] = {"label": e["title"], "note": note, "url": e["url"], "external": True}
        elif c["flag"] in ESS_ESIM:
            eid, label = ESS_ESIM[c["flag"]]
            if eid in ess:
                items["esim"] = {"label": label, "note": f"{ess[eid]['price']:,}원~",
                                 "url": ess[eid].get("url") or ess[eid]["naverMe"], "external": True}

        gi = ESS_GOODS["kr" if c["region"] == "kr" else "default"]
        if cid in ("paris", "london", "rome", "barcelona"):
            gi = EU_GOODS
        if gi[0] in ess:
            items["goods"] = {"label": gi[1], "note": f"{ess[gi[0]]['price']:,}원 · 쿠팡",
                              "url": ess[gi[0]].get("url") or ess[gi[0]]["naverMe"], "external": True}

        cities[cid] = {"name": name, "items": items}

    # 계획서에만 있는 도시 — 실제 자산(호텔 목록·숙소)이 있으면 별도 묶음으로 넣는다
    for cid, (name, stay_id) in PLANNER_ONLY.items():
        items: dict[str, dict] = {}
        h = next((x for x in tc.get("hotels") or [] if x.get("cityId") == cid), None)
        if h:
            items["hotel"] = {"label": f"{name} 숙소 검색", "note": "이 달 요금",
                              "url": h["url"], "external": True}
        if stay_count.get(stay_id):
            items["stays"] = {"label": f"찐숙소 {stay_count[stay_id]}곳 비교", "note": "평점·1박 최저가",
                              "url": f"/stays#{stay_id}", "external": False}
        f = next((x for x in tc.get("flights") or [] if name in x["route"]), None)
        if f:
            items["flight"] = {"label": f"{f['route']} 항공권", "note": "최저가 검색",
                               "url": f["url"], "external": True}
        gi = ESS_GOODS["default"]
        if gi[0] in ess:
            items["goods"] = {"label": gi[1], "note": f"{ess[gi[0]]['price']:,}원 · 쿠팡",
                              "url": ess[gi[0]].get("url") or ess[gi[0]]["naverMe"], "external": True}
        if items:
            cities[cid] = {"name": name, "items": items}

    out = {
        "version": "v35",
        "checked": "2026-11-21",
        "note": "각 링크는 data/tripcom.json·data/stays.json·data/essentials.json 에 실제로 있는 제휴 링크만 옮긴 것입니다.",
        "cities": cities,
        "alias": ALIAS,
        "currencyCity": CURRENCY_CITY,
    }
    (DATA / "bundles.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("cities", len(cities), "items", sum(len(c["items"]) for c in cities.values()))
    for cid in ("paris", "london", "rome", "barcelona", "osaka", "sapporo", "guam"):
        if cid in cities:
            print(cid, sorted(cities[cid]["items"]))


if __name__ == "__main__":
    main()
