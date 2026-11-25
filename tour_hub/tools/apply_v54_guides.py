#!/usr/bin/env python3
"""v54 데이터 반영 — 신규 가이드 3편(마운자로·괌·하와이)을 guides.json·guide_extra·photo_credits에 넣고
기존 가이드·도시 허브의 양방향 링크를 채운다.

    python3 tools/apply_v54_guides.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NEW = [
    {
        "slug": "japan-mounjaro-injection-guide",
        "category": "준비물·경비",
        "navTitle": "마운자로·자가주사제 일본 여행 반입·기내 휴대·보관",
        "h1": "마운자로 들고 일본 가기, <em>1개월분·기내·보관</em> 기준",
        "seoTitle": "마운자로 일본 여행 반입 규정 — 1개월분·기내 휴대·보관 | 트립픽",
        "dek": "마운자로 같은 자가주사제를 일본에 들고 갈 때 필요한 건 효능 정보가 아니라 서류와 온도입니다. 일본은 처방약·자가주사제 1개월분(마운자로 4펜)까지 서류 없이 통관되고, 넘으면 수입확인증이 필요합니다. 기내 반입, 보냉, 귀국 6병·3개월 한도까지 2026년 11월 기준으로 정리했습니다.",
        "desc": "마운자로 일본 반입 2026. 처방약·자가주사 1개월분(4펜) 서류 면제, 초과 시 수입확인증, 기내 주사기 허용·젤 아이스팩 100mL, 2~8℃ 보관·30℃ 이하 21일, 귀국 6병·3개월·GLP-1 12개.",
        "keywords": "마운자로 일본 여행, 자가주사제 반입 규정, 처방약 일본 반입, 유뉴카쿠닌쇼, 수입확인증, 마운자로 기내 반입, 마운자로 보관 온도, GLP-1 반입 12개, 주사침 기내 반입, 의약품 세관 신고",
        "published": "2026-11-25",
        "updated": "2026-11-25",
        "read": 9,
        "image": "images/v54/japan-mounjaro-injection-guide.jpg",
        "ogImage": "images/og/v54-mounjaro-og.jpg",
        "imageAlt": "주사펜과 주사기, 의료용품이 놓인 흰 배경 — 여행 자가주사제 준비",
        "imageCredit": "사진: Pexels (Artem Podrez)",
        "tours": [],
        "essentials": ["cp-washbag-bromi"],
        "related": [
            "travel-medication-rules-guide",
            "entry-immigration-guide",
            "airport-checkin-customs-guide",
            "overseas-sick-hospital-insurance-claim",
            "flight-delay-card-lost-emergency",
        ],
        "ctaTitle": "내 일정에 맞는 약 수량을 계산하면?",
        "ctaText": "여행 일수와 주사 횟수를 넣으면 1개월분 기준과 보관 일수를 같은 표로 확인할 수 있습니다.",
        "fxNote": "후생노동성·식약처 2026.11 기준",
        "faq": [
            ["마운자로 한 상자를 일본에 들고 갈 수 있나요?",
             "네. 마운자로 1회용 펜은 한 상자에 4펜이고 1자루가 1주분이라 1상자가 1개월분입니다. 일본은 처방약과 자가주사제(프리필드펜·자가주사 키트) 1개월분까지 수입확인증 없이 세관 확인만으로 통관됩니다. 2상자(8펜)부터는 출발 전에 수입확인증을 받아야 합니다."],
            ["수입확인증은 어디서 신청하나요?",
             "2025년 7월 1일부터 후생노동성 '의약품 등 수입확인 정보 시스템' 온라인 신청이 원칙입니다. 도착 공항을 관할하는 세관에 따라 창구가 갈리는데, 나리타·하네다·신치토세는 간토신에쓰 후생국(048-740-0800), 간사이·후쿠오카·나하는 긴키 후생국(06-6942-4096)입니다."],
            ["기내에 주사펜과 바늘을 가져갈 수 있나요?",
             "인천공항은 주사기·침류 등 의료용 물품을 기내와 위탁 모두 반입할 수 있다고 안내합니다. 마운자로 펜은 1자루 0.5mL로 액체 100mL 기준에는 걸리지 않지만, 수하물 칸의 저온으로 얼 수 있어 기내 가방에 넣는 편이 안전합니다. 처방전을 함께 두세요."],
            ["여행 중 냉장이 안 되면 어떻게 하나요?",
             "국내 허가사항 기준 30℃를 넘지 않는 곳에서 최대 21일까지 보관할 수 있습니다. 얼리면 안 되고 얼었던 펜은 녹여도 쓰지 않습니다. 호텔 미니바 냉장고는 냉동실에 붙은 칸이나 냉기 출구 쪽이 과냉이 될 수 있어 가운데 칸에 원래 상자째 넣으세요."],
            ["한국으로 돌아올 때 몇 개까지 가져올 수 있나요?",
             "2026년 11월 12일부터 자가치료용 의약품은 총 6병 또는 3개월 복용량까지 반입됩니다. 주 1회 투여 GLP-1 계열 비만치료제는 최대 12개까지 허용돼 마운자로 펜 3상자가 상한입니다. 세관이 처방전이나 구매 영수증을 요구할 수 있고, 타인에게 팔거나 넘기면 약사법 위반입니다."],
        ],
    },
    {
        "slug": "guam-4n5d-course",
        "category": "대만·괌",
        "navTitle": "괌 4박5일 코스 — 투몬 4박·렌터카·2인 경비",
        "h1": "괌 4박5일, <em>투몬 4박 + 남부 드라이브</em> 2인 161만 원",
        "seoTitle": "괌 4박5일 코스 — 투몬·렌터카·공항 택시·2인 경비 (2026) | 트립픽",
        "dek": "괌은 인천에서 4시간 15분, 시차 +1시간이라 4박5일이면 리조트와 섬을 반씩 나눌 수 있습니다. 공항에서 투몬까지 법정 택시 7~11달러, 레드 셔틀 1일권 15달러, 렌터카 45달러, 피시아이 돌고래 66달러, 숙소 4박 53만~190만 원까지 실제 조회값으로 계산했습니다.",
        "desc": "괌 4박5일 2026. 무료 G-CNMI ETA 45일·ESTA 40.62달러, 공항→투몬 택시 7.20달러+짐, GRTA 1.50달러·레드 셔틀 15달러, 렌터카 28달러+CDW17달러, 사랑의 절벽 3달러·피시아이 16달러, 숙소 4박 536,184원~, 2인 1,608,617원.",
        "keywords": "괌 4박5일, 괌 자유여행 코스, 괌 렌터카, 괌 공항 택시, 괌 레드 셔틀, 피시아이 돌고래, 괌 숙소 가격, G-CNMI ETA, 괌 전자세관신고서, 괌 남부 드라이브",
        "published": "2026-11-25",
        "updated": "2026-11-25",
        "read": 10,
        "image": "images/v54/guam-4n5d-course.jpg",
        "ogImage": "images/og/v54-guam-og.jpg",
        "imageAlt": "투몬 베이 리조트 수영장과 바다 — 괌 4박5일",
        "imageCredit": "사진: Pexels (Ran Hua)",
        "tours": ["gu_p2", "gu_p1", "gu_p3"],
        "essentials": ["gu-esim-trip-101949204"],
        "related": [
            "guam-resorts",
            "guam-vs-saipan-comparison",
            "entry-immigration-guide",
            "incheon-airport-smartpass-lounge",
            "travel-insurance-guide",
        ],
        "ctaTitle": "내 날짜로 괌 경비를 다시 계산하면?",
        "ctaText": "출발일과 인원을 넣으면 항공·숙소·투어·eSIM을 같은 기준으로 계산해 3안으로 보여줍니다.",
        "fxNote": "1달러 = 1,342원 · 2026-11-25 고시",
        "faq": [
            ["괌만 갈 때 ESTA가 필요한가요?",
             "괌과 북마리아나제도만 방문한다면 무료 G-CNMI ETA로 최대 45일 체류가 가능해 ESTA가 필요 없습니다. 이미 유효한 ESTA가 있으면 그대로 쓰면 되고, 하와이나 미국 본토로 이어 가는 일정이라면 ESTA(1인 40.62달러)를 받아야 합니다."],
            ["공항에서 투몬까지 얼마인가요?",
             "공항에서 투몬 호텔가까지는 2마일입니다. 괌 법정 택시요금은 기본 2.40달러, 첫 1마일 4.00달러, 이후 0.25마일마다 0.80달러, 짐 1개 1달러라 2인 짐 2개면 9~11달러 선입니다. GRTA 블루라인 1은 1인 1.50달러지만 하루 4번만 서고 일요일은 운행하지 않습니다."],
            ["렌터카 없이 괌을 돌 수 있나요?",
             "투몬 안은 레드 셔틀(1회 7달러·1일 15달러)로 충분하지만, 남부 드라이브와 리티디안은 차가 없으면 사실상 어렵습니다. 5인승 렌터카는 1일 28달러에 차량 손상 보상(CDW) 17달러가 붙어 하루 45달러 선이고, 한국 운전면허로 도착일부터 30일까지 운전할 수 있습니다."],
            ["괌에서 꼭 예약해야 하는 게 있나요?",
             "피시아이 돌고래 크루즈는 3일 전까지 예약하면 전망대 요금이 2달러 싸고, 차모로 빌리지 야시장은 수요일에만 섭니다. 리티디안 보호구역은 수~일만 열고 월·화요일은 닫습니다. 아쿠아리움 오브 괌은 공사 휴관 보도가 있어 방문 전에 확인하세요."],
            ["4박5일 2인 경비는 얼마인가요?",
             "숙소를 괌 플라자 리조트(4박 536,184원)로 잡고 렌터카 2일, 피시아이 돌고래 2인, 식비 4일을 넣으면 2인 1,608,617원(1인 804,309원)입니다. 항공과 ESTA는 별도이고, 숙소를 두짓타니로 바꾸면 2인 279만 원까지 올라갑니다."],
        ],
    },
    {
        "slug": "hawaii-oahu-5n7d-course",
        "category": "유럽·장거리",
        "navTitle": "하와이 오아후 5박7일 코스 — 와이키키·예약 3곳·2인 경비",
        "h1": "하와이 오아후 5박7일, <em>예약 3곳</em>과 2인 288만 원",
        "seoTitle": "하와이 오아후 5박7일 코스 — 와이키키·예약·경비 (2026) | 트립픽",
        "dek": "인천에서 8시간 50분, 시차 -19시간이라 오아후는 5박7일이 기준입니다. 다이아몬드헤드 5달러·하나우마베이 25달러·USS 애리조나 1달러 예약, 공항 택시 정액 38달러, HOLO 7일권 45달러, 숙소 5박 161만~355만 원을 실제 조회값으로 정리했습니다.",
        "desc": "하와이 오아후 5박7일 2026. ESTA 40.62달러, 공항→와이키키 택시 38달러·TheBus 3.25달러, HOLO 7일 45달러, 다이아몬드헤드 5달러+주차10달러, 하나우마 25달러(월·화 휴무), 숙소 5박 1,613,192원~, 2인 2,881,836원.",
        "keywords": "하와이 5박7일, 오아후 여행 코스, 와이키키 숙소, 다이아몬드헤드 예약, 하나우마베이 예약, 진주만 USS애리조나, 호놀룰루 공항 택시, HOLO 카드, 하와이 ESTA, 하와이 2인 경비",
        "published": "2026-11-25",
        "updated": "2026-11-25",
        "read": 10,
        "image": "images/v54/hawaii-oahu-5n7d-course.jpg",
        "ogImage": "images/og/v54-hawaii-og.jpg",
        "imageAlt": "와이키키 해변과 다이아몬드헤드 — 하와이 오아후 5박7일",
        "imageCredit": "사진: Pexels (Aleksandr Poklad)",
        "tours": ["hi_sheraton7", "hi_hyatt8"],
        "essentials": ["cp-neckpillow-rango"],
        "related": [
            "hawaii-hyatt-vs-sheraton",
            "entry-immigration-guide",
            "luggage-size-weight-airline-guide",
            "travel-insurance-guide",
            "airport-checkin-customs-guide",
        ],
        "ctaTitle": "내 날짜로 하와이 경비를 다시 계산하면?",
        "ctaText": "출발일과 인원을 넣으면 항공·숙소·렌터카·투어를 같은 기준으로 계산해 3안으로 보여줍니다.",
        "fxNote": "1달러 = 1,342원 · 2026-11-25 고시",
        "faq": [
            ["하와이는 3박4일로는 부족한가요?",
             "인천–호놀룰루 직항이 8시간 50분이고 시차가 -19시간이라, 3박4일이면 실제로 움직일 수 있는 낮이 두 번뿐입니다. 5박7일이면 다이아몬드헤드·진주만·노스쇼어·하나우마베이를 하루에 하나씩 배치할 수 있습니다."],
            ["다이아몬드헤드와 하나우마베이는 예약이 꼭 필요한가요?",
             "비거주자는 두 곳 모두 예약이 필수입니다. 다이아몬드헤드는 입장 5달러·주차 10달러로 30일 전부터 예약하고, 하나우마베이는 25달러에 온라인 수수료 2.35%가 붙고 방문 2일 전 오전 7시(하와이 시간)에 예약이 열립니다. 하나우마베이는 월·화요일 휴무입니다."],
            ["공항에서 와이키키까지 어떻게 가나요?",
             "택시 정액이 38달러 선이고, 공유 셔틀은 1인 16~20달러입니다. 짐이 적으면 TheBus W 노선이 현금 3.25달러로 가장 싸지만, 큰 캐리어 1개와 기내 가방 1개까지만 탈 수 있습니다."],
            ["버스 요금은 얼마인가요?",
             "2026년 7월 1일부터 현금 1회 3.25달러입니다. HOLO 카드를 쓰면 2시간 3달러, 하루 7.50달러 상한, 3일 20달러, 7일 45달러입니다. 카드 발급비는 2달러이고 공항 스카이라인 역에서 살 수 있습니다."],
            ["리조트피와 주차비는 요금에 포함되나요?",
             "트립닷컴 표시 요금은 세금·봉사료 포함이지만 리조트피와 주차비는 호텔별로 따로 붙습니다. 와이키키 호텔 주차는 하루 30~50달러 선이므로, 렌터카를 빌린다면 예약 전에 주차 요금을 확인하세요."],
        ],
    },
]

EXTRA = {
    "japan-mounjaro-injection-guide": {
        "hub": None,
        "regions": ["jp", "etc"],
        "tags": ["시즌·서류"],
        "takeaway": "일본은 마운자로 4펜(1상자)까지 서류 없이 통관되고, 넘으면 수입확인증이 필요합니다. 펜은 기내 가방에 넣고 30℃ 이하 21일 규칙을 확인하세요.",
        "facts": [["서류 없는 한도", "4펜(1개월분)"], ["귀국 한도", "12펜(3개월)"]],
    },
    "guam-4n5d-course": {
        "hub": None,
        "regions": ["gu"],
        "tags": ["숙소", "가성비"],
        "takeaway": "투몬 4박에 남부 드라이브 하루, 피시아이 반나절이면 괌 4박5일이 채워집니다. 2인 현지 경비는 숙소를 플라자로 잡으면 161만 원입니다.",
        "facts": [["공항→투몬 택시", "7.20달러 + 짐 1달러"], ["렌터카 1일", "45달러(CDW 포함)"]],
    },
    "hawaii-oahu-5n7d-course": {
        "hub": None,
        "regions": ["long"],
        "tags": ["숙소", "교통패스"],
        "takeaway": "오아후는 5박7일이 기준입니다. 다이아몬드헤드·하나우마베이·USS 애리조나 세 곳을 먼저 예약하고, 시내는 HOLO 7일권으로 묶으세요.",
        "facts": [["예약 3곳", "다이아몬드헤드·하나우마·USS애리조나"], ["HOLO 7일권", "45달러"]],
    },
}

BACKLINKS = {
    "travel-medication-rules-guide": "japan-mounjaro-injection-guide",
    "entry-immigration-guide": ["japan-mounjaro-injection-guide", "guam-4n5d-course", "hawaii-oahu-5n7d-course"],
    "airport-checkin-customs-guide": ["japan-mounjaro-injection-guide", "hawaii-oahu-5n7d-course"],
    "overseas-sick-hospital-insurance-claim": "japan-mounjaro-injection-guide",
    "flight-delay-card-lost-emergency": "japan-mounjaro-injection-guide",
    "guam-resorts": "guam-4n5d-course",
    "guam-vs-saipan-comparison": "guam-4n5d-course",
    "incheon-airport-smartpass-lounge": "guam-4n5d-course",
    "travel-insurance-guide": ["guam-4n5d-course", "hawaii-oahu-5n7d-course"],
    "hawaii-hyatt-vs-sheraton": "hawaii-oahu-5n7d-course",
    "luggage-size-weight-airline-guide": "hawaii-oahu-5n7d-course",
}

CREDITS = {
    "japan-mounjaro-injection-guide": {"pexels_id": 6823742, "photographer": "Artem Podrez", "url": "https://www.pexels.com/photo/6823742/"},
    "guam-4n5d-course": {"pexels_id": 24033245, "photographer": "Ran Hua", "url": "https://www.pexels.com/photo/24033245/"},
    "hawaii-oahu-5n7d-course": {"pexels_id": 36072131, "photographer": "Aleksandr Poklad", "url": "https://www.pexels.com/photo/36072131/"},
}


def main() -> int:
    gp = DATA / "guides.json"
    gspec = json.loads(gp.read_text(encoding="utf-8"))
    guides = gspec["guides"]
    have = {g["slug"] for g in guides}
    added = 0
    for g in NEW:
        if g["slug"] not in have:
            guides.append(g)
            added += 1
    by = {g["slug"]: g for g in guides}

    for src, targets in BACKLINKS.items():
        tgt = targets if isinstance(targets, list) else [targets]
        rel = by[src].setdefault("related", [])
        for t in tgt:
            if t not in rel:
                rel.append(t)

    # 허브(도쿄·오사카·후쿠오카)에 일본 자가주사제 가이드 연결
    hp = DATA / "city_hubs.json"
    hubs = json.loads(hp.read_text(encoding="utf-8"))
    for c in hubs["cities"]:
        if c["slug"] in ("tokyo", "osaka", "fukuoka"):
            if "japan-mounjaro-injection-guide" not in c["guides"]:
                c["guides"].append("japan-mounjaro-injection-guide")
            md = c.get("metaDesc") or ""
            import re
            md2 = re.sub(r"관련 가이드 \d+편", f"관련 가이드 {len(c['guides'])}편", md)
            c["metaDesc"] = md2
    hp.write_text(json.dumps(hubs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 괌 숙소 지역의 가이드 목록에도 새 코스 연결
    sp = DATA / "stays.json"
    stays = json.loads(sp.read_text(encoding="utf-8"))
    for r in stays["regions"]:
        if r["id"] == "guam":
            gl = r.setdefault("guides", [])
            if not any(x.get("slug") == "guam-4n5d-course" for x in gl):
                gl.append({"slug": "guam-4n5d-course", "label": "괌 4박5일 코스"})

    ep = DATA / "guide_extra.json"
    extra = json.loads(ep.read_text(encoding="utf-8"))
    for k, v in EXTRA.items():
        extra["guides"][k] = v

    cp = DATA / "photo_credits.json"
    credits = json.loads(cp.read_text(encoding="utf-8"))
    for k, v in CREDITS.items():
        credits["photos"][k] = v

    gp.write_text(json.dumps(gspec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(extra, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cp.write_text(json.dumps(credits, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sp.write_text(json.dumps(stays, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"가이드 {len(guides)}편 (신규 {added}) · guide_extra {len(extra['guides'])} · credits {len(credits['photos'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
