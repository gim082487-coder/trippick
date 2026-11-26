#!/usr/bin/env python3
"""v56: 신규 가이드 3편 메타데이터(guides.json·guide_extra.json)·내부 링크·제목 차별화.

    python3 tools/apply_v56_guides.py

값은 전부 v56 조사(2026-11-26)에서 확인한 것이다.
- 오키나와: 츄라우미 공식 2,180엔, 유이레일 290엔·1,000엔, 렌터카 6,600~8,910엔, 나하 12월 평년값 19.0/21.5/16.8도
- 동남아 주사제: Thai FDA 30일·IC-2, 베트남 시행령 163/2025 30일·200달러, 필리핀 Joint Circular No.1
- 방콕 3박4일: 사찰 1,000밧, 공항철도 45밧, 파타야 버스 144밧, 숙소는 data/stays.json
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
        "slug": "okinawa-3n4d-course",
        "category": "일정·경비",
        "navTitle": "오키나와 3박4일 코스·렌터카·숙소",
        "h1": "오키나와 3박4일, <em>나하 3박 vs 나하 2박+온나 1박</em>",
        "seoTitle": "오키나와 3박4일 코스 & 렌터카·숙소 — 츄라우미 2,180엔·유이레일 290엔 | 트립픽",
        "dek": ("3박4일에서 숙소를 한 번 옮기면 반나절이 사라집니다. 나하 3박과 나하 2박+온나 1박을 숙소 6곳 값으로 비교하고, "
                "렌터카 3일 비용·ETC 할인·츄라우미 입장료·12월 날씨까지 계산했습니다."),
        "desc": ("오키나와 3박4일 코스. 숙소 6곳 1박 6만 6,400원~22만 2,461원(2인), 렌터카 3일 16만 7,092~22만 5,574원, "
                 "츄라우미 2,180엔, 유이레일 공항→국제거리 290엔·13분, 2인 현지 경비 66만~119만 원(항공 제외). 2026-11 확인."),
        "keywords": ("오키나와 3박4일, 오키나와 렌터카, 츄라우미 수족관 입장료, 유이레일 요금, 나하 숙소, 온나 리조트, "
                     "오키나와 여행 경비, 만좌모, 오키나와 ETC"),
        "published": "2026-11-26",
        "updated": "2026-11-26",
        "image": "images/v56/okinawa-3n4d-course.jpg",
        "ogImage": "images/og/v56-okinawa-og.jpg",
        "imageAlt": "오키나와 나하 해변의 파도와 산호초",
        "imageCredit": "사진: Pexels",
        "tours": [],
        "essentials": ["jp-esim-trip-37658069"],
        "related": ["japan-rental-car-etc-guide", "japan-esim", "airport-arrival-city-transfer-guide",
                    "overseas-roaming-esim-install-troubleshooting", "travel-insurance-guide"],
        "ctaTitle": "오키나와 3박4일, 숙소·렌터카 넣고 총액 계산",
        "ctaText": "인원과 여행 날짜를 넣으면 숙소·항공·투어를 같은 기준으로 계산합니다.",
        "fxNote": "1엔 8.439원 · 2026-11-25 고시 기준",
        "faq": [
            ["오키나와 3박4일은 나하와 온나 중 어디에 묵나요?",
             "첫 여행이면 나하 3박이 실패가 적습니다. 나하는 공항에서 모노레일 290엔·13분이고 국제거리·슈리성이 한 줄로 이어집니다. 두 번째 이상이거나 리조트에서 쉬는 게 목적이면 나하 2박 + 온나 1박이 낫고, 온나로 옮기는 날 오전에 렌터카를 받아 만좌모·푸른동굴을 들르면 이동이 일정에 녹습니다."],
            ["렌터카 없이 3박4일이 가능한가요?",
             "가능합니다. 나하 시내·국제거리·슈리성·오모로마치 쇼핑은 유이레일과 버스로 충분합니다. 다만 츄라우미 수족관·만좌모·고우리섬은 대중교통으로 하루에 묶기 어려워, 북부를 넣으려면 렌터카나 당일 버스투어가 필요합니다."],
            ["츄라우미 수족관 입장료와 할인은 얼마인가요?",
             "성인 2,180엔(1만 8,397원), 고등학생 1,440엔, 초중학생 710엔, 6세 미만은 무료입니다. 연간 패스포트가 4,360엔으로 성인 2회 값과 같고, 도로의 역 許田에서 파는 할인권은 2,000엔(현금만)입니다. 같은 날 재입장이 됩니다."],
            ["공항에서 시내까지 얼마이고 몇 분 걸리나요?",
             "유이레일로 겐초마에(현청앞)까지 290엔·13분, 마키시 320엔·14분입니다. 첫차 6:00·막차 23:30이고, 1일권은 1,000엔·2일권 1,800엔입니다. 카드 터치 결제는 2025년 3월부터 하루 800엔 상한이라 1일권보다 먼저 계산해 보세요."],
            ["2인 경비는 얼마나 드나요?",
             "항공을 제외한 현지 경비가 2인 66만 3,727원~119만 392원입니다. 숙소 등급(나하 3박 19만 9,200원 vs 하얏트 3박 66만 7,383원)과 렌터카 요금에서 갈리고, 식비는 1끼 1,200엔 가정입니다."],
        ],
    },
    {
        "slug": "southeast-asia-injection-guide",
        "category": "준비물·경비",
        "navTitle": "동남아 자가주사제 반입 — 태국 30일·베트남 30일·필리핀 처방량",
        "h1": "동남아에 마운자로 들고 가기, <em>태국·베트남·필리핀</em> 기준",
        "seoTitle": "마운자로·위고비 동남아 반입 규정 — 태국 30일·베트남 200달러·필리핀 처방량 | 트립픽",
        "dek": ("태국은 30일분까지 처방전과 원래 용기, 베트남은 처방전 사본에 200달러·연 3회 기준이 붙고, 필리핀은 처방전에 적힌 수량이 한도입니다. "
                "기내·보관·현지 구매·귀국 반입까지 2026년 11월 기준으로 정리했습니다."),
        "desc": ("마운자로·위고비 동남아 반입 2026. 태국 30일분·향정 30일(31~90일 IC-2), 베트남 30일·200달러·연 3회·처방전 사본, "
                 "필리핀 처방전 수량·PRC 면허번호. 기내 주사기 허용, 30℃ 21일, 방콕 클리닉 마운자로 8,999밧부터, 귀국 12펜."),
        "keywords": ("마운자로 동남아 반입, 위고비 반입 규정, 태국 처방약 반입 30일, 베트남 의약품 반입 규정, 필리핀 처방약 반입, "
                     "IC-2 허가, 자가주사제 기내 반입, 마운자로 보관 온도, 방콕 마운자로 가격, GLP-1 반입 12개"),
        "published": "2026-11-26",
        "updated": "2026-11-26",
        "image": "images/v56/southeast-asia-injection-guide.jpg",
        "ogImage": "images/og/v56-injection-og.jpg",
        "imageAlt": "인슐린 펜과 줄자 — 여행 자가주사제 준비",
        "imageCredit": "사진: Pexels (Mikhail Nilov)",
        "tours": [],
        "essentials": ["cp-washbag-bromi"],
        "related": ["japan-mounjaro-injection-guide", "travel-medication-rules-guide",
                    "airport-checkin-customs-guide", "entry-immigration-guide",
                    "overseas-sick-hospital-insurance-claim"],
        "ctaTitle": "여행 일수에 맞는 약 수량 계산",
        "ctaText": "여행 일수와 주사 횟수를 넣으면 30일 기준과 보관 일수를 같은 표로 확인할 수 있습니다.",
        "fxNote": "태국 FDA·주베트남 대사관·필리핀 FDA 2026.11 기준",
        "faq": [
            ["태국에 마운자로 한 달분을 들고 갈 수 있나요?",
             "네. 태국 마약법 제13조(4)에 따라 개인 치료용 완제 의약품은 30일분까지 허가 없이 반입됩니다. 원래 용기와 라벨을 유지하고 처방전을 함께 소지하세요. GLP-1 계열은 마약류·향정신성 목록에 없어 IC-2 허가 대상이 아닙니다."],
            ["베트남은 30일분이면 서류가 끝나나요?",
             "수량은 처방전 용법 기준 30일분까지이고, 여기에 1회 반입 약값 200달러 이하·연 3회라는 기준이 붙습니다. 공증받았거나 본인이 서명한 처방전 사본(또는 외래진료기록 사본)을 약과 함께 두세요. 마약류는 7일, 향정신성은 10일까지만 처방전 용법 안에서 허용됩니다."],
            ["필리핀은 30일 제한이 있나요?",
             "일반 처방약에는 30일 고정 한도가 없습니다. 개인 사용 목적이면 처방전에 적힌 수량·용량을 넘지 않으면 사전 FDA 허가가 필요 없고, 처방전에 의사의 PRC 면허번호(외국 처방이면 그 나라 등록번호)가 있어야 합니다. 통제 성분은 30일분까지 별도 규정이 적용됩니다."],
            ["기내에 주사펜과 바늘을 가져갈 수 있나요?",
             "인천공항은 주사기·침류 등 의료용 물품을 기내와 위탁 모두 반입할 수 있다고 안내합니다. 마운자로 펜은 1자루 0.5mL라 액체 100mL 기준에 걸리지 않지만 위탁 화물칸 냉기로 얼 수 있어 기내 가방이 안전합니다. 처방전을 함께 두세요."],
            ["동남아 더위에서 보관은 어떻게 하나요?",
             "마운자로는 2~8℃ 냉장이 원칙이고, 부득이하면 30℃를 넘지 않는 곳에서 최대 21일입니다. 얼리면 안 됩니다. 공항에서 호텔까지는 보냉백과 젤 아이스팩(용기 100mL·1인 1L 지퍼백)을 쓰고, 호텔에서는 미니바 가운데 칸에 상자째 넣으세요. 냉동실에 붙은 칸은 과냉이 됩니다."],
        ],
    },
    {
        "slug": "bangkok-3n4d-course",
        "category": "일정·경비",
        "navTitle": "방콕 3박4일 코스·예산 — 파타야 당일치기 넣을까",
        "h1": "방콕 3박4일, <em>파타야를 넣으면 시내가 하루</em>로 줄어듭니다",
        "seoTitle": "방콕 3박4일 코스·2인 경비 — 파타야 버스 144밧 vs 그랩 3,000밧 | 트립픽",
        "dek": ("3박4일은 실제 관광이 2일 반입니다. 파타야 당일치기를 버스 576밧과 그랩 2,000~3,000밧으로 비교하고, "
                "왕궁·왓포·왓아룬 1,000밧 코스와 숙소 4곳 값으로 2인 경비 128만~188만 원을 계산했습니다."),
        "desc": ("방콕 3박4일 코스·예산. 사원 3곳 1,000밧, 공항철도 45밧, BTS 1일권 150밧, 파타야 버스 144밧·그랩 왕복 2,000~3,000밧, "
                 "숙소 3만 8,837~20만 7,399원. 2인 128만~188만 원, 12월 비 1.0일. 2026-11 확인."),
        "keywords": ("방콕 3박4일, 방콕 여행 경비, 파타야 당일치기, 방콕 사원 입장료, 왕궁 500밧, 공항철도 45밧, "
                     "BTS 1일권 150밧, 방콕 숙소 추천, 짜뚜짝 주말시장"),
        "published": "2026-11-26",
        "updated": "2026-11-26",
        "image": "images/v56/bangkok-3n4d-course.jpg",
        "ogImage": "images/og/v56-bangkok-og.jpg",
        "imageAlt": "방콕 왓아룬 사원과 짜오프라야강",
        "imageCredit": "사진: Pexels (Meaw Zara)",
        "tours": [],
        "essentials": ["th-esim-trip-46275998"],
        "related": ["bangkok-pattaya-3n5d-course-budget", "bangkok-airport", "bangkok-3-packages",
                    "sea-grab-taxi-scam-guide", "thailand-souvenir-list"],
        "ctaTitle": "방콕 3박4일, 내 날짜로 총액 계산",
        "ctaText": "인원과 날짜를 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 계산합니다.",
        "fxNote": "1밧 39.582원 · 2026-11-25 고시 기준",
        "faq": [
            ["방콕 3박4일에 파타야를 넣을 수 있나요?",
             "넣을 수 있지만 방콕 시내가 하루로 줄어듭니다. 에까마이에서 파타야까지 버스 144밧·2시간이라 왕복 4시간이 이동입니다. 그랩이면 1시간 30분으로 줄지만 왕복 2,000~3,000밧입니다. 첫 방콕이면 빼고, 재방문이면 3박 중 1박을 파타야로 옮기는 쪽이 낫습니다."],
            ["사원 입장료는 모두 얼마인가요?",
             "왕궁 500밧, 왓포 300밧, 왓아룬 100밧으로 3곳 합 1,000밧(1인 3만 9,582원)입니다. 왕궁은 8:30 개장이고 어깨·무릎을 가리는 복장이 필요합니다. 왓포에서 왓아룬은 배로 4밧에 건너갑니다."],
            ["공항에서 시내까지 가장 싼 방법은?",
             "수완나품공항에서 공항철도(ARL) 45밧으로 빠야타이까지 26분입니다. 2인이면 3,562원이고, 짐이 많거나 3~4인이면 택시·그랩이 500밧 안팎에 공항 요금 50밧과 통행료가 붙습니다."],
            ["방콕 3박4일 2인 경비는 얼마인가요?",
             "항공 2인 70만~100만 원을 포함해 128만 5,184원~188만 1,548원입니다. 숙소를 바이욕 스카이(3박 32만 5,833원)로 잡느냐 밀레니엄 힐튼(62만 2,197원)으로 잡느냐가 가장 큰 차이입니다. 파타야 당일치기는 버스 2만 2,799원이 더 붙습니다."],
            ["12월 방콕 날씨는 어떤가요?",
             "12월 평년값은 평균 27.3도, 강수량 11.6mm·비 온 날 1.0일로 연중 가장 건조합니다. 다만 낮 기온이 30도를 넘어 사원 관광은 오전에 몰고 오후에는 실내로 피하는 편이 낫습니다. 12월 중순부터 연말은 성수기라 숙소·항공이 함께 오릅니다."],
        ],
    },
]

EXTRA = {
    "okinawa-3n4d-course": {
        "hub": "okinawa",
        "regions": ["jp"],
        "tags": ["숙소", "교통패스", "eSIM", "가성비"],
        "stayRegions": ["okinawa"],
        "takeaway": "3박4일은 나하 3박이 실패가 적고, 리조트를 넣으려면 나하 2박+온나 1박(54만 8,069원)이 하얏트 3박(66만 7,383원)보다 11만 9,314원 쌉니다. 렌터카 3일은 16만 7,092원부터, 츄라우미는 성인 2,180엔입니다.",
        "facts": [["츄라우미 성인", "2,180엔"], ["유이레일 공항→국제거리", "290엔·13분"]],
    },
    "southeast-asia-injection-guide": {
        "hub": None,
        "regions": ["th", "vn", "etc"],
        "tags": ["시즌·서류"],
        "takeaway": "태국 30일분(처방전·원래 용기), 베트남 30일분(처방전 사본·200달러·연 3회), 필리핀은 처방전에 적힌 수량입니다. GLP-1은 세 나라 모두 마약·향정신성 목록에 없어 IC-2 같은 사전 허가 대상이 아닙니다.",
        "facts": [["태국", "30일분"], ["베트남 처방전 사본", "30일·200달러"]],
    },
    "bangkok-3n4d-course": {
        "hub": "bangkok",
        "regions": ["th"],
        "tags": ["숙소", "가성비", "교통패스", "eSIM"],
        "stayRegions": ["bangkok"],
        "takeaway": "3박4일은 실관광 2일 반이라 파타야 당일치기를 넣으면 시내가 하루로 줄어듭니다. 사원 3곳 1,000밧·공항철도 45밧으로 2인 128만~188만 원(항공 포함)입니다.",
        "facts": [["사원 3곳", "1,000밧"], ["파타야 버스", "144밧"]],
    },
}

REVERSE = {
    "japan-rental-car-etc-guide": "okinawa-3n4d-course",
    "japan-esim": "okinawa-3n4d-course",
    "airport-arrival-city-transfer-guide": "okinawa-3n4d-course",
    "japan-mounjaro-injection-guide": "southeast-asia-injection-guide",
    "travel-medication-rules-guide": "southeast-asia-injection-guide",
    "entry-immigration-guide": "southeast-asia-injection-guide",
    "airport-checkin-customs-guide": "southeast-asia-injection-guide",
    "overseas-sick-hospital-insurance-claim": "southeast-asia-injection-guide",
    "bangkok-pattaya-3n5d-course-budget": "bangkok-3n4d-course",
    "bangkok-airport": "bangkok-3n4d-course",
    "bangkok-3-packages": "bangkok-3n4d-course",
    "sea-grab-taxi-scam-guide": "bangkok-3n4d-course",
    "thailand-souvenir-list": "bangkok-3n4d-course",
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
    print(f"guides.json +{added} → {len(g['guides'])}편")

    # 제목 유사도(0.43) 낮추기 — 환전·짐싸기 글의 <title>에서 카드 브랜드 나열을 뺀다
    for x in g["guides"]:
        if x["slug"] == "travel-card-packing-guide":
            x["seoTitle"] = "환전 수수료 37,520원 vs 1,460원 — 공항·시내·앱 환전과 짐싸기 체크리스트 (2026) | 트립픽"
        if x["slug"] == "travel-card-fees-comparison":
            x["seoTitle"] = "트래블월렛·트래블로그·토스뱅크 수수료·ATM 비교 — 3만엔 인출 6,568원 차이 (2026) | 트립픽"

    for src, dst in REVERSE.items():
        row = next((x for x in g["guides"] if x["slug"] == src), None)
        if not row:
            print("  ! 없는 가이드", src)
            continue
        rel = row.setdefault("related", [])
        if dst not in rel:
            rel.append(dst)
    save("guides.json", g)

    ex = load("guide_extra.json")
    for slug, row in EXTRA.items():
        ex["guides"][slug] = row
    save("guide_extra.json", ex)
    print(f"guide_extra +{len(EXTRA)} → {len(ex['guides'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
