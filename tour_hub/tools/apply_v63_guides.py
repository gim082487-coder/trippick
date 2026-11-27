#!/usr/bin/env python3
"""v63: 신규 가이드 3편 메타데이터(guides.json·guide_extra.json)·상호 링크.

    python3 tools/apply_v63_guides.py

값은 2026-11-27 확인분이다.
- 도쿄: 게이세이 본선 1,060엔·82분(1회 환승), 하네다 게이큐 330엔·11분,
  지하철 24/48/72시간 800/1,200/1,500엔, 스카이트리 1,800·3,000엔(현장 +500엔),
  시부야 스카이 온라인 2,700·3,400엔(현장 3,000·3,700엔), 도쿄타워 1,500엔, 도쿄도청 무료,
  디즈니 1데이 8,900엔~ / 애프터3 7,900엔~ / 애프터5 5,400엔~
- 무비자: 외교부 해외안전여행 사증면제 목록(2026.11) — 일본·대만·홍콩·마카오·말레이시아·태국 90,
  몽골 90(한시 ~2026-12-31), 베트남 45(2028-03-14까지), 괌 45(관광), 중국 30(한시 ~2026-12-31),
  필리핀·라오스 30, 인도네시아는 VOA 500,000루피아
- 동남아 렌터카: 태국 IDP+한국면허, 베트남 IDP 상호인정(2023-07-23 발효·입국일부터 1년),
  필리핀 90일, 말레이시아 IDP(12개월 미만), 발리(인도네시아)는 한국 IDP 불인정(발리 분관 안전공지)
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
        "slug": "tokyo-3n4d-course-budget",
        "category": "일본",
        "navTitle": "도쿄 3박4일 — 지하철 72시간 1,500엔·전망대 4곳",
        "h1": "도쿄 3박4일, <em>전망대 하나</em>와 <em>동네 두 곳</em>만 정하면 됩니다",
        "seoTitle": "도쿄 3박4일 코스·경비 — 지하철 72시간 1,500엔·전망대 비교 | 트립픽",
        "dek": ("나리타 게이세이 본선 1,060엔·82분, 지하철 72시간권 1,500엔(하루 2.7회면 본전), "
                "스카이트리 1,800엔~·시부야 스카이 2,700엔~. 3박4일 동선과 2인 경비 7만 3,619원을 계산했습니다."),
        "desc": ("도쿄 3박4일 코스·경비. 지하철 72시간권 1,500엔, 게이세이 본선 1,060엔(82분), 하네다 게이큐 330엔, "
                 "스카이트리 1,800엔~·시부야 스카이 2,700엔~·도쿄타워 1,500엔·도청 무료, 디즈니 8,900엔~, "
                 "2인 교통·입장료 7만 3,619원. 2026-11 확인."),
        "keywords": ("도쿄 3박4일, 도쿄 3박4일 경비, 도쿄 지하철 72시간권, 도쿄메트로 패스 1500엔, "
                     "나리타 게이세이 1060엔, 하네다 게이큐 330엔, 스카이트리 입장료, 시부야 스카이 2700엔, "
                     "도쿄 전망대 비교, 도쿄 디즈니 1일권, 아사쿠사 숙소, 도쿄 여행 코스"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v63/tokyo-3n4d-course-budget.jpg",
        "ogImage": "images/og/v63-tokyo-og.jpg",
        "imageAlt": "도쿄 지하철 개찰구에서 IC카드로 통과하는 사람들",
        "imageCredit": "사진: Pexels (Imani Williams)",
        "tours": [],
        "essentials": ["jp-esim-lingsim-1d", "cp-powerbank-spidy"],
        "related": ["tokyo-food-route", "tokyo-subway-ticket", "tokyo-disney-parks",
                    "narita-haneda-transfer", "japan-ic-card", "tokyo-fuji-tour"],
        "ctaTitle": "도쿄 3박4일 계산",
        "ctaText": "날짜와 인원을 넣으면 도쿄 숙소와 항공을 같은 기준으로 비교합니다.",
        "fxNote": "1엔 8.4426원 · 2026-11-25 고시 기준",
        "read": 12,
        "faq": [
            ["도쿄 3박4일 2인 경비는 얼마인가요?",
             "항공·숙소·식사를 빼고 교통·입장료만 7만 3,619원입니다. 나리타↔우에노 게이세이 왕복 2인 17,898원, 지하철 72시간권 2인 25,328원, 스카이트리 덴보데크 2인 30,394원으로 계산했습니다. 시부야 스카이를 더하면 11만 9,209원이 됩니다."],
            ["지하철 72시간권이 이득인가요?",
             "하루 3회 이상 지하철을 타는 날이 이틀 이상이면 이득입니다. 72시간권은 1,500엔, 24시간권 3장은 2,400엔이라 900엔(7,598원) 차이입니다. 단 JR(야마노테선)과 스카이라이너·나리타 익스프레스·게이큐는 포함되지 않습니다."],
            ["나리타와 하네다 중 어디로 들어오는 게 좋나요?",
             "숙소가 아사쿠사·우에노 쪽이면 나리타 게이세이 본선이 1,060엔·82분으로 가장 쌉니다. 하네다로 들어오면 게이큐로 시나가와까지 330엔·11분이라 시내 진입이 훨씬 짧습니다. 항공권을 볼 때 도착 공항을 같은 줄에서 확인하세요."],
            ["전망대는 하나만 가도 되나요?",
             "3박4일이면 유료 전망대 한 곳과 무료 전망대 한 곳 조합이 총액에 유리합니다. 스카이트리 덴보데크 1,800엔~, 시부야 스카이 온라인 2,700엔(15시 전), 도쿄타워 메인덱 1,500엔, 도쿄도청은 무료입니다. 스카이트리는 창구에서 사면 1장당 500엔이 더 붙습니다."],
            ["숙소는 어디에 잡는 게 좋나요?",
             "나리타로 오가고 센소지·스카이트리를 보려면 아사쿠사·우에노가 동선이 가장 짧습니다. 같은 권역에서도 1박 2인 20만 5,235원부터 49만 5,526원까지 차이가 났습니다(2026-11-19 조회). 밤 늘어지는 쇼핑이 목적이면 신주쿠·시부야, 긴자·롯폰기를 걸어서 쓰려면 아카사카입니다."],
        ],
    },
    {
        "slug": "visa-free-stay-duration-guide",
        "category": "준비물·경비",
        "navTitle": "무비자 체류기간 — 일본·태국 90일, 베트남 45일, 필리핀 30일",
        "h1": "무비자 체류기간, <em>90일·45일·30일</em>은 협정이 갈랐습니다",
        "seoTitle": "무비자 체류기간 총정리 — 일본·태국 90일, 베트남 45일 (2026) | 트립픽",
        "dek": ("일본·태국·말레이시아는 90일, 베트남은 45일, 필리핀은 30일, 인도네시아는 무비자가 아니라 "
                "도착비자 500,000루피아입니다. 협정과 일방조치의 차이, 여권 6개월 기준, 연장·도과 처리까지 정리했습니다."),
        "desc": ("목적지별 무비자 체류기간(2026-11). 일본·대만·홍콩·마카오·태국·말레이시아 90일, 베트남 45일, "
                 "괌 45일, 중국 30일(~2026-12-31), 필리핀 30일(29일 연장), 인도네시아 VOA 500,000루피아. "
                 "여권 6개월·귀국항공권·긴급여권 제한까지."),
        "keywords": ("무비자 체류기간, 베트남 무비자 45일, 태국 무비자 90일, 필리핀 무비자 30일, "
                     "일본 무비자 90일, 중국 무비자 30일 2026, 인도네시아 도착비자 500000루피아, "
                     "싱가포르 무비자 90일, 말레이시아 무비자 90일, 체류기간 연장, 여권 6개월, 무비자 입국 서류"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v63/visa-free-stay-duration-guide.jpg",
        "ogImage": "images/og/v63-visa-og.jpg",
        "imageAlt": "여권 스탬프가 찍힌 여권 면을 손에 든 모습",
        "imageCredit": "사진: Ekaterina Belinskaya / Pexels",
        "tours": [],
        "essentials": ["cp-passport-reindeer", "th-esim-usimsa-1d"],
        "related": ["entry-immigration-guide", "passport-application-guide", "esim-roaming-insurance-guide",
                    "passport-phone-lost-emergency", "travel-insurance-guide", "airport-checkin-customs-guide"],
        "ctaTitle": "목적지 항공·숙소 비교",
        "ctaText": "무비자 기간 안에서 날짜를 정하고, 항공과 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "1루피아 0.0736원 · 결제 시점 환율 확인",
        "read": 11,
        "faq": [
            ["태국은 30일로 줄었다는데 90일인가요?",
             "한국은 90일입니다. 태국은 2026년 9월 15일부터 93개국 60일 제도를 30일(60개국)·15일·도착비자·협정으로 개편했지만, 한국은 1981년 비자면제협정(90일)에 해당해 협정이 우선 적용됩니다(주태국 대사관 2026-09-09 공지). 육로 입국 횟수 제한도 적용되지 않습니다."],
            ["베트남 무비자는 며칠인가요?",
             "45일입니다. 2023년 8월 15일부터 45일로 늘었고, 2025년 3월 결의안(44/NQ-CP)으로 2028년 3월 14일까지 연장됐습니다. 여권은 6개월 이상 남아야 하고, 긴급여권으로는 무비자 입국이 되지 않습니다. 45일이 짧으면 전자비자(90일 이내)를 쓰세요."],
            ["여권 유효기간은 얼마나 남아야 하나요?",
             "대부분 6개월 이상이지만 기준일이 다릅니다. 필리핀은 입국일이 아니라 계획한 체류가 끝난 뒤 6개월을 세고, 싱가포르는 입국일 기준 6개월입니다. 베트남·말레이시아·인도네시아도 6개월 이상을 요구합니다."],
            ["인도네시아도 무비자인가요?",
             "아닙니다. 한국은 인도네시아 무비자 대상국이 아니어서 도착비자(VOA·e-VOA)를 사야 합니다. 30일 500,000루피아(약 3만 6,800원)이고 1회에 한해 30일 연장할 수 있습니다. 긴급여권으로는 입국할 수 없습니다."],
            ["무비자로 일해도 되나요?",
             "안 됩니다. 무비자는 관광·친지 방문·단기 회의 목적이고, 현지에서 돈을 버는 활동은 목적에 맞는 비자가 필요합니다. 말레이시아는 2026년 2월 공지에서 무사증 입국은 비영리 목적에 한정된다고 다시 강조했고, 적발되면 추방·입국금지로 이어집니다."],
        ],
    },
    {
        "slug": "southeast-asia-rental-car-license-guide",
        "category": "준비물·경비",
        "navTitle": "동남아 렌터카 — 태국은 되고 발리는 안 되는 국제면허",
        "h1": "동남아 렌터카, <em>같은 국제면허</em>로 태국은 되고 발리는 안 됩니다",
        "seoTitle": "동남아 렌터카·국제운전면허 — 태국·베트남·필리핀·발리 (2026) | 트립픽",
        "dek": ("국제운전면허증 9,000원·1년으로 태국·베트남·필리핀·말레이시아는 운전할 수 있지만, "
                "인도네시아(발리)는 한국 국제면허를 인정하지 않습니다. 보증금·면책금·추가 운전자 조건까지 정리했습니다."),
        "desc": ("동남아 렌터카·국제운전면허(2026-11). 태국 IDP+한국면허, 베트남 상호인정(입국일부터 1년), "
                 "필리핀 90일, 말레이시아 12개월 미만 IDP, 발리는 한국 IDP 불인정(대사관 발리 분관). "
                 "발급 9,000원·보증금·면책금 확인 5가지."),
        "keywords": ("동남아 렌터카, 국제운전면허증, 베트남 렌터카 국제면허, 태국 렌터카 IDP, "
                     "발리 렌터카 국제면허 인정, 필리핀 운전면허 90일, 말레이시아 국제면허, "
                     "국제운전면허증 발급 9000원, 렌터카 보증금 면책금, 좌측통행 운전"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v63/southeast-asia-rental-car-license-guide.jpg",
        "ogImage": "images/og/v63-rental-og.jpg",
        "imageAlt": "렌터카 차 안에서 본 내비게이션과 도로 풍경",
        "imageCredit": "사진: Pexels (Faheem Ahamad)",
        "tours": [],
        "essentials": ["cp-passport-reindeer", "cp-powerbank-spidy"],
        "related": ["japan-rental-car-etc-guide", "sea-grab-taxi-scam-guide", "bangkok-3n4d-course",
                    "danang-hoian-3n5d", "bali-ubud-seminyak-3n4d-course", "travel-card-fees-comparison"],
        "ctaTitle": "렌터카 대신 기사 포함 차량 비교",
        "ctaText": "날짜와 인원을 넣으면 항공·숙소와 함께 기사 포함 차량·투어를 같은 기준으로 봅니다.",
        "fxNote": "1밧 39.4773원 · 1달러 1,344.09원 · 2026-11-25 고시 기준",
        "read": 11,
        "faq": [
            ["국제운전면허증만 있으면 동남아 어디서나 운전할 수 있나요?",
             "아닙니다. 태국·베트남·필리핀·말레이시아는 인정되지만 인도네시아(발리)는 한국이 발급한 국제면허를 운전 자격으로 인정하지 않습니다. 주인도네시아 대사관 발리 분관은 안전공지에서 발리에서는 국제면허로 운전할 수 없다고 명시합니다."],
            ["베트남에서 정말 렌터카를 빌릴 수 있나요?",
             "제도상 가능합니다. 2023년 7월 23일 발효한 한-베 국제운전면허 상호인정 협정으로 입국일부터 1년간(국제면허 유효기간 내) 운전할 수 있고, 국제면허·한국면허 원본·여권을 함께 지참합니다. 다만 업체가 외국인 자가운전을 거절하거나 보증금 1,000달러 안팎을 요구하는 사례가 있어, 기사 포함 차량이 더 현실적일 때가 많습니다."],
            ["태국에서 면허를 안 보여주면 차를 못 빌리나요?",
             "업체가 차를 넘기지 않는 경우가 많고, 넘겨줘도 사고 시 보험이 거절될 수 있습니다. 태국은 국제면허와 한국면허를 함께 제시해야 하며, 여권까지 세 가지 원본을 확인합니다. 추가 운전자는 계약서에 이름을 올려야 보험이 적용됩니다."],
            ["발리에서는 어떻게 이동하나요?",
             "기사 포함 차량이나 그랩·Gojek를 쓰세요. 한국 면허·국제면허로는 운전 자격이 없어 무면허 운전이 되고, 사고 시 여행자보험 청구도 거절될 수 있습니다. 렌터카 업체가 열쇠를 넘겨줘도 법적 자격이 생기지는 않습니다."],
            ["보증금과 면책금은 얼마나 봐야 하나요?",
             "일일 요금보다 보증금·면책금이 총액을 좌우합니다. 보증금은 카드 홀드인지 현금인지, 면책금은 사고 시 내가 무는 최대 금액인지, 타이어·유리가 보험에서 빠지는지를 계약 전에 확인하세요. 여권을 보증금 대신 맡기는 일은 피해야 합니다."],
        ],
    },
]

EXTRA = {
    "tokyo-3n4d-course-budget": {
        "hub": "tokyo",
        "regions": ["jp"],
        "tags": ["숙소", "교통패스", "가성비"],
        "stayRegions": ["tokyo"],
        "takeaway": "도쿄 3박4일은 권역을 하루 단위로 끊고, 지하철 72시간권(1,500엔)과 유료 전망대 한 곳만 쓰면 2인 교통·입장료가 7만 3,619원입니다. 숙소는 나리타 기준 아사쿠사·우에노가 공항 이동을 두 번 줄입니다.",
        "facts": [["지하철 72시간권", "1,500엔(24시간권 3장보다 900엔↓)"], ["나리타→우에노", "게이세이 1,060엔·82분"]],
    },
    "visa-free-stay-duration-guide": {
        "hub": None,
        "regions": ["etc"],
        "tags": ["시즌·서류", "가성비"],
        "takeaway": "무비자 기간은 협정(90일)과 일방조치(30~45일)로 갈립니다. 일본·태국·말레이시아 90일, 베트남 45일, 필리핀 30일, 인도네시아는 도착비자 500,000루피아입니다. 입국 도장의 마지막 체류일을 그 자리에서 확인하세요.",
        "facts": [["태국·일본·말레이시아", "90일"], ["베트남 45일 · 필리핀 30일", "인도네시아는 VOA"]],
    },
    "southeast-asia-rental-car-license-guide": {
        "hub": None,
        "regions": ["th", "vn", "id", "etc"],
        "tags": ["시즌·서류", "교통패스"],
        "takeaway": "국제운전면허증(9,000원·1년)으로 태국·베트남·필리핀·말레이시아는 운전할 수 있지만 발리는 인정되지 않습니다. 태국은 IDP+한국면허+여권 세 가지, 베트남은 입국일부터 1년, 필리핀은 90일입니다.",
        "facts": [["국제운전면허증", "9,000원 · 1년"], ["발리(인도네시아)", "한국 IDP 불인정"]],
    },
}

REVERSE = {
    "tokyo-subway-ticket": "tokyo-3n4d-course-budget",
    "tokyo-food-route": "tokyo-3n4d-course-budget",
    "tokyo-disney-parks": "tokyo-3n4d-course-budget",
    "narita-haneda-transfer": "tokyo-3n4d-course-budget",
    "japan-ic-card": "tokyo-3n4d-course-budget",
    "entry-immigration-guide": "visa-free-stay-duration-guide",
    "passport-application-guide": "visa-free-stay-duration-guide",
    "esim-roaming-insurance-guide": "visa-free-stay-duration-guide",
    "japan-rental-car-etc-guide": "southeast-asia-rental-car-license-guide",
    "sea-grab-taxi-scam-guide": "southeast-asia-rental-car-license-guide",
    "bangkok-3n4d-course": "southeast-asia-rental-car-license-guide",
    "bali-ubud-seminyak-3n4d-course": "southeast-asia-rental-car-license-guide",
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

    for item in NEW:
        print(f"  · {item['slug']} seoTitle {len(item['seoTitle'])}자 · desc {len(item['desc'])}자 · FAQ {len(item['faq'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
