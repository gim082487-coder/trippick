#!/usr/bin/env python3
"""v68: 찐숙소 지역 2곳(푸껫·고베) + 숙소 11곳(stays.json).

    python3 tools/apply_v68_data.py

목록 값은 2026-11-28 트립닷컴 호텔 목록(2026-12-10~11 · 성인 2명 · KRW · 세금&서비스비용 포함)에서
그대로 옮겼고, 성급·주소·한국어명은 각 호텔 상세 페이지(HTTP 200)에서 확인했다.
료칸 2곳(아리마 온센 겟코엔 코로칸·고베 미나토 온센 렌)은 목록에 세금 포함 표기가 없어 넣지 않았다.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
AID = "Allianceid=11407530&SID=336341874"
BASIS = "2026-12-10~11 · 1박 · 2인 · 세금·봉사료 포함 최저가"


def load(n):
    return json.loads((D / n).read_text(encoding="utf-8"))


def save(n, o):
    (D / n).write_text(json.dumps(o, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


REGIONS = [
    {
        "id": "phuket",
        "name": "푸껫",
        "country": "태국",
        "note": "빠통·카론·카타 세 해변과 푸켓 타운. 공항에서 스마트버스가 어디서나 100밧이라 차 없이도 해변을 옮겨 다닐 수 있습니다.",
        "count": 6,
        "top": "호텔 미드타운 라트사다",
        "cityId": "725",
        "scope": "intl",
        "hub": "",
        "guides": [
            {"slug": "phuket-3n4d-budget", "label": "푸껫 3박4일 경비"},
            {"slug": "thailand-cities-comparison-guide", "label": "태국 4도시 비교"},
        ],
    },
    {
        "id": "kobe",
        "name": "고베",
        "country": "일본",
        "note": "산노미야·모토마치·하버랜드가 한 줄로 이어집니다. 오사카 우메다에서 한큐 330엔·28분이라 오사카 숙소를 두고 당일치기로도 닿습니다.",
        "count": 5,
        "top": "더 로열 파크 캔버스 고베 산노미야",
        "cityId": "423",
        "scope": "intl",
        "hub": "osaka",
        "guides": [
            {"slug": "osaka-kobe-nara-daytrip-guide", "label": "고베·나라 당일치기"},
            {"slug": "osaka-kyoto-3n4d", "label": "오사카·교토 3박4일"},
        ],
    },
]

# region, id, name, en, star, typeLabel, score, reviews, zone, access, reason, price, themes, pointTags
HOTELS = [
    ("phuket", "702258", "다라 호텔", "Dara Hotel", 4, "호텔", 8.9, 2046,
     "푸켓 타운", "차오파 로드 · 시내 중심, 푸켓 타운 버스터미널 도보권",
     "리뷰 2,046개·8.9 — 이 도시 조회분 12곳 중 1박 6만 1,611원으로 가장 낮습니다. 푸켓 타운이라 야시장·올드타운이 도보권이고, 해변은 스마트버스로 나갑니다.",
     61611, ["value"], ["야시장", "올드타운"]),
    ("phuket", "703557", "호텔 미드타운 라트사다", "Hotel Midtown Ratsada", 4, "호텔", 9.3, 642,
     "푸켓 타운", "랏사다 로드 · 푸켓 타운 버스터미널 인근",
     "리뷰 642개·9.3 — 위치 9.7·청결 9.4로 이 도시 조회분 중 평점이 가장 높습니다. 버스터미널이 가까워 공항버스·섬 이동 출발점으로 쓰기 좋고 1박 7만 8,697원입니다.",
     78697, ["value", "station"], ["평점 최고", "버스터미널"]),
    ("phuket", "702180", "더 로얄 파라다이스 호텔 & 스파", "The Royal Paradise Hotel & Spa", 4, "호텔", 8.7, 1413,
     "빠통 비치", "랏우팃 200피 로드 · 정실론 쇼핑센터 도보권",
     "리뷰 1,413개·8.7 — 빠통 한가운데라 방라 로드·정실론·해변이 모두 도보권입니다. 야간 이동이 편한 대신 해변까지 도보 10분 안팎, 1박 14만 7,775원입니다.",
     147775, ["pool", "station"], ["빠통 중심", "쇼핑"]),
    ("phuket", "21847079", "아우리코 카타 리조트 & 스파", "Aurico Kata Resort & Spa", 4, "리조트", 8.6, 1160,
     "카타 비치", "타이나 로드 · 카론 해변 방면, 카타 비치 도보권",
     "리뷰 1,160개·8.6 — 카타·카론 사이에 있어 두 해변을 걸어서 오갑니다. 가족 단위 객실이 많고 1박 15만 3,775원입니다.",
     153775, ["pool", "villa"], ["카타", "가족"]),
    ("phuket", "83988303", "판와부리 비치프런트 리조트", "Panwaburi Beachfront Resort", 5, "호텔", 8.8, 1418,
     "케이프 판와", "아오욘 해변 · 케이프 판와 남쪽",
     "리뷰 1,418개·8.8 — 청결 9.1·서비스 9.0의 5성급인데 위치 평가는 8.1입니다. 시내와 떨어져 조용하고, 1박 16만 8,295원으로 5성급 중 낮은 편입니다.",
     168295, ["pool", "ocean"], ["5성급", "한적"]),
    ("phuket", "998415", "만다라바 리조트 앤 스파 카론 비치", "Mandarava Resort and Spa Phuket", 5, "리조트", 9.1, 611,
     "카론 비치", "파탁 로드 · 카론 해변 언덕",
     "리뷰 611개·9.1 — 청결 9.3·서비스 9.2로 카론 조회분 중 가장 높습니다. 언덕 위 리조트라 해변까지 셔틀을 타고, 1박 30만 1,937원입니다.",
     301937, ["pool", "ocean", "onsen"], ["리조트", "스파"]),
    ("kobe", "54594014", "고베 플라자 호텔 웨스트", "Kobe Plaza Hotel West", 3, "호텔", 9.2, 440,
     "모토마치", "모토마치도리 3-4-7 · 모토마치역·난킨마치(차이나타운) 도보권",
     "리뷰 440개·9.2 — 청결·서비스가 모두 9.3인 3성급입니다. 차이나타운과 모토마치 쇼핑가가 도보권이고 1박 7만 3,253원으로 이 도시 조회분 최저가입니다.",
     73253, ["value", "station"], ["모토마치", "차이나타운"]),
    ("kobe", "704939", "호텔 몬테 에르마나 고베 아마리", "Hotel Monte Hermana Kobe Amalie", 4, "호텔", 9.0, 1227,
     "산노미야", "나카야마테도리 2-2-28 · 산노미야역 도보 7분",
     "리뷰 1,227개·9.0 — 산노미야역 도보 7분, 이쿠타 신사·기타노 이진칸이 가깝습니다. 조식 뷔페 평가가 좋고 1박 8만 1,570원입니다.",
     81570, ["station", "value"], ["산노미야", "조식"]),
    ("kobe", "55210543", "호텔 몬토레 고베", "Hotel Monterey Kobe", 4, "호텔", 9.1, 1447,
     "산노미야", "시모야마테도리 2-11-13 · 산노미야 시 지하철역 인근",
     "리뷰 1,447개·9.1 — 산노미야 지하철역이 가까워 오사카·교토 이동이 편합니다. 고베 시내 관광의 중심에 있고 1박 14만 1,761원입니다.",
     141761, ["station"], ["지하철", "시내 중심"]),
    ("kobe", "63372661", "더 로열 파크 캔버스 고베 산노미야", "The Royal Park Canvas - Kobe Sannomiya", 4, "호텔", 9.3, 1799,
     "산노미야", "시모야마테도리 2-3-1 · 산노미야 시 지하철역 인근",
     "리뷰 1,799개·9.3 — 청결 9.4로 이 도시 조회분 중 평점이 가장 높습니다. 쇼핑가·이쿠타 신사·하버랜드가 모두 도보권이고 1박 15만 7,634원입니다.",
     157634, ["station"], ["평점 최고", "쇼핑가"]),
    ("kobe", "1465318", "고베 메리켄 파크 오리엔탈 호텔", "Kobe Meriken Park Oriental Hotel", 5, "호텔", 9.0, 1595,
     "하버랜드", "하토바초 5-6 · 메리켄 공원·포트 타워 인근",
     "리뷰 1,595개·9.0 — 메리켄 공원과 포트 타워 사이의 5성급으로 위치 9.2입니다. 발코니 오션뷰와 조식 평가가 높고 1박 15만 3,930원입니다.",
     153930, ["ocean", "station"], ["오션뷰", "메리켄공원"]),
]


def list_url(city: str, name: str, sub: str) -> str:
    q = quote(name)
    return (f"https://kr.trip.com/hotels/list?city={city}&display={q}&optionId={city}"
            f"&optionType=City&optionName={q}&{AID}&trip_sub1={sub}&trip_sub3=D21372570")


def main() -> int:
    stays = load("stays.json")
    have_regions = {r["id"] for r in stays["regions"]}
    have_hotels = {h["id"] for h in stays["hotels"]}
    added_regions = added_hotels = 0
    for r in REGIONS:
        if r["id"] in have_regions:
            continue
        row = dict(r)
        row["listUrl"] = list_url(r["cityId"], r["name"], f"hotel_{r['id']}")
        stays["regions"].append(row)
        added_regions += 1
    for (region, hid, name, en, star, type_label, score, reviews, zone, access,
         reason, price, themes, point_tags) in HOTELS:
        if hid in have_hotels:
            continue
        stays["hotels"].append({
            "region": region,
            "id": hid,
            "name": name,
            "en": en,
            "star": star,
            "type": "hotel" if type_label == "호텔" else "resort",
            "typeLabel": type_label,
            "score": score,
            "reviews": reviews,
            "sub": {},
            "zone": zone,
            "access": access,
            "reason": reason,
            "price": price,
            "priceBasis": BASIS,
            "img": f"images/stays/{region}-{hid}.jpg",
            "url": (f"https://kr.trip.com/hotels/detail/?cityId="
                    f"{'725' if region == 'phuket' else '423'}&hotelId={hid}&curr=KRW"
                    f"&{AID}&trip_sub1=stays_{region}_{hid}&trip_sub3=D21372570"),
            "themes": themes,
            "pointTags": point_tags,
        })
        added_hotels += 1

    # 세부 점수는 목록 응답 값 그대로 채운다(상세 페이지 재확인은 v68_stays.py에서 HTTP 200 확인)
    scraped = json.loads(Path("/workspace/v68_list_phuket.json").read_text(encoding="utf-8")) + \
        json.loads(Path("/workspace/v68_list_kobe.json").read_text(encoding="utf-8"))
    subs = {r["id"]: r["sub"] for r in scraped if r.get("sub")}
    for h in stays["hotels"]:
        if not h.get("sub") and h["id"] in subs:
            h["sub"] = subs[h["id"]]

    stays["source"]["v68"] = (
        "2026-11-28: 푸껫(6곳)·고베(5곳) 지역을 새로 넣었습니다. 트립닷컴 숙소 목록을 "
        "2026-12-10~11 · 성인 2명 · KRW · 세금&서비스비용 포함 조건으로 조회해 1박 최저가·평점·리뷰 수를 그대로 옮겼고, "
        "각 호텔 상세 페이지(HTTP 200)에서 한국어명·주소를 확인했습니다. 료칸 2곳(아리마 온센 겟코엔 코로칸·고베 미나토 온센 렌)은 "
        "목록에 세금 포함 표기가 없어 넣지 않았습니다.")
    stays["source"]["checked"] = "2026-11-28"
    save("stays.json", stays)

    # 가이드 → 숙소 지역 연결
    ex = load("guide_extra.json")
    ex["guides"].setdefault("phuket-3n4d-budget", {})["stayRegions"] = ["phuket"]
    kobe = ex["guides"].setdefault("osaka-kobe-nara-daytrip-guide", {})
    kobe["stayRegions"] = ["osaka", "kobe"]
    save("guide_extra.json", ex)

    print(f"[v68] 지역 +{added_regions} → {len(stays['regions'])} · 숙소 +{added_hotels} → {len(stays['hotels'])}")
    for r in stays["regions"][-2:]:
        print("  ·", r["id"], r["name"], sum(1 for h in stays["hotels"] if h["region"] == r["id"]), "곳")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
