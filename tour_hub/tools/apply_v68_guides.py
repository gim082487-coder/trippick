#!/usr/bin/env python3
"""v68: 신규 가이드 3편 메타데이터(guides.json·guide_extra.json).

    python3 tools/apply_v68_guides.py

값은 2026-11-28 확인분이다.
- 중국: 무비자 30일(~2026-12-31) · 알리페이·위챗페이 200위안 이하 수수료 0, 초과 3% · 1건 $5,000/연 $50,000
- 보라카이: 제티 1인 535페소(터미널 150·환경 300·보트 50·수수료 35) · 2인 3박4일 388,896~786,672원
- 사이판: G-CNMI ETA 무료·45일·2년 · 마나가하 1인 $63(보트 $50+환경 $10+부두 $3) · 2인 1,279,300~1,569,610원
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
        "slug": "china-visa-free-alipay-wechat-pay-guide",
        "category": "중국",
        "navTitle": "중국 무비자 30일 — 알리페이·위챗페이, 200위안 넘으면 3%",
        "h1": "중국 무비자 30일, <em>결제는 알리페이·위챗페이</em> 하나로",
        "seoTitle": "중국 무비자 입국·알리페이 결제 — 200위안 3% (2026) | 트립픽",
        "dek": ("중국은 한국 일반여권에 2026년 12월 31일까지 최장 30일 무비자를 줍니다. "
                "중국 은행 계좌 없이 알리페이·위챗페이에 해외 카드를 붙이면 QR로 결제되고, "
                "200위안 이하는 수수료가 없으며 넘으면 전액의 3%가 붙습니다. "
                "푸둥공항 자기부상 50위안과 세금 환급 9%까지 숫자로 정리했습니다."),
        "desc": ("중국 무비자 30일(~2026-12-31)과 알리페이·위챗페이 실전(2026-11). 200위안 이하 수수료 0, "
                 "초과 시 3%, 1건 $5,000·연 $50,000, 자기부상 50위안·지하철 7위안, 출국 세금 환급 11%-2%."),
        "keywords": ("중국 무비자, 중국 무비자 30일, 중국 입국 조건, 알리페이 등록, 위챗페이 등록, "
                     "알리페이 수수료 3%, 알리페이 200위안, 중국 QR 결제, 상하이 자기부상 50위안, "
                     "푸둥공항 지하철 7위안, 중국 세금 환급 11%, 중국 eSIM VPN"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 12,
        "image": "images/v68/china-visa-free-alipay-wechat-pay-guide.jpg",
        "ogImage": "images/og/v68-china-pay-og.jpg",
        "imageAlt": "네온이 켜진 상하이 거리 야경",
        "imageCredit": "사진: Pexels (Wilbur Ludlow)",
        "tours": [],
        "essentials": ["cp-adapter-nemotab", "cp-passport-reindeer"],
        "related": ["shanghai-2n3d-3n4d-course", "beijing-3n4d-course", "visa-free-stay-duration-guide",
                    "currency-payment-fees", "travel-card-fees-comparison", "airport-arrival-city-transfer-guide"],
        "ctaTitle": "중국 항공·숙소 비교",
        "ctaText": "출발일을 넣으면 상하이·베이징 항공과 2호선 역 근처 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "1위안 201.3288원 · 1달러 1,344.09원 · 2026-11-27 기준",
        "faq": [
            ["중국 무비자는 언제까지인가요?",
             "한국 일반여권 소지자는 2026년 12월 31일까지 최장 30일 무비자로 입국할 수 있습니다. 관광·친지 방문·경유·교류 방문이 대상이고, 취업·유학·취재는 해당 비자가 필요합니다."],
            ["30일은 언제부터 세나요?",
             "입국한 다음 날부터 셉니다. 1월 1일 입국이면 1월 31일이 30일째이고, 그 뒤로 더 머물려면 공안 출입국관리기관에 체류 허가를 신청해야 합니다."],
            ["알리페이 수수료는 얼마인가요?",
             "해외 카드를 붙인 결제는 200위안 이하면 플랫폼 수수료가 없고, 200위안을 넘으면 결제 금액 전액의 3%가 붙습니다. 210위안이면 6.30위안(약 1,268원)입니다."],
            ["중국 은행 계좌가 없어도 결제되나요?",
             "됩니다. 알리페이·위챗페이에 Mastercard·Visa·JCB·Diners·Discover 카드를 붙이면 계좌 없이 QR 결제가 됩니다. 1건 5,000달러·연 50,000달러 한도이고, 누적 2,000달러를 넘으면 여권 인증을 요구합니다."],
            ["푸둥공항에서 시내까지 얼마인가요?",
             "자기부상열차가 룽양루까지 8분에 50위안(당일 탑승권 제시 40위안), 지하철 2호선은 인민광장까지 7위안에 60~75분입니다. 자기부상 막차는 21:42, 2호선은 22:30입니다."],
        ],
    },
    {
        "slug": "boracay-3n4d-course-budget",
        "category": "일정·경비",
        "navTitle": "보라카이 3박4일 — 제티 500페소·호핑 750페소, 2인 39만~79만",
        "h1": "보라카이 3박4일, <em>제티 500페소</em>부터 시작합니다",
        "seoTitle": "보라카이 3박4일 코스·경비 — 제티 500페소, 2인 39만~79만 (2026) | 트립픽",
        "dek": ("보라카이는 공항·차·배 세 구간을 지나야 섬에 닿습니다. 외국인 1인 제티 요금은 "
                "터미널 150페소·환경세 300페소·배삯 50페소에 수수료 35페소를 더해 535페소이고, "
                "호핑투어는 표시가 위에 크리스털 코브 300페소·매직 아일랜드 250페소가 붙습니다. "
                "2인 3박4일 현지 경비를 숙소 3안으로 계산했습니다."),
        "desc": ("보라카이 3박4일(2026-11). 제티 1인 535페소(2인 왕복 45,066원), 칼리보 육로 38,065원, "
                 "호핑 현장 750~850페소, 숙소 1박 45,063~177,655원, 2인 현지 388,896~786,672원."),
        "keywords": ("보라카이 3박4일, 보라카이 여행 경비, 보라카이 제티 요금, 보라카이 환경세 300페소, "
                     "보라카이 터미널비, 칼리보 공항 카티클란, 보라카이 호핑투어 가격, 크리스털 코브 300페소, "
                     "보라카이 숙소 추천, 스테이션 2 호텔, 보라카이 eTravel"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 11,
        "image": "images/v68/boracay-3n4d-course-budget.jpg",
        "ogImage": "images/og/v68-boracay-og.jpg",
        "imageAlt": "보라카이 화이트 비치의 백사장과 청록색 바다",
        "imageCredit": "사진: Pexels (Jeffrey Ligan)",
        "tours": [],
        "essentials": ["ph-esim-globe-5d", "cp-adapter-nemotab"],
        "related": ["cebu-3n4d-course", "bohol-3n4d-course", "airport-arrival-city-transfer-guide",
                    "sea-grab-taxi-scam-guide", "travel-insurance-guide", "currency-payment-fees"],
        "ctaTitle": "보라카이 항공·숙소 비교",
        "ctaText": "날짜를 넣으면 칼리보 직항과 스테이션 1~3 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "1페소 21.0588원 · 1달러 1,344.09원 · 2026-11-27 기준",
        "faq": [
            ["보라카이 제티 요금은 얼마인가요?",
             "외국인 1인 편도 535페소입니다. 터미널 이용료 150페소, 환경세 300페소, 배삯 50페소에 LezzGo 수수료 35페소를 더한 값이고, 2인 왕복이면 2,140페소(45,066원)입니다."],
            ["칼리보와 카티클란 중 어디로 가야 하나요?",
             "한국 직항은 칼리보(KLO)에 내리고 제티까지 차로 1시간 30분~2시간 걸립니다. 카티클란(MPH)은 제티까지 5~10분이지만 마닐라·세부에서 국내선으로 갈아타야 합니다."],
            ["호핑투어에서 현장에 얼마를 더 내나요?",
             "크리스털 코브 300페소, 매직 아일랜드 250페소, 스노클링 100페소, 보트맨 팁 100~200페소로 1인 750~850페소(15,794~17,900원)입니다. 상품에 포함된 항목은 빼야 합니다."],
            ["보라카이 3박4일 2인 경비는?",
             "항공을 빼고 숙소에 따라 388,896원(스테이션 3)~786,672원(스테이션 1)입니다. 제티 왕복 45,066원, 칼리보 육로 38,065원, 호핑 현장 35,800원, 식비 134,776원(가정)이 공통으로 들어갑니다."],
            ["12월에 가도 되나요?",
             "12월은 건기 초입이라 비가 적습니다. 다만 태풍이 남쪽으로 지나가면 배가 끊기므로 마지막 날 오전 비행편이면 전날 카티클란 쪽으로 나오는 편이 안전합니다."],
        ],
    },
    {
        "slug": "saipan-3n4d-course-budget",
        "category": "일정·경비",
        "navTitle": "사이판 3박4일 — ETA 무료·마나가하 63달러, 2인 128만~157만",
        "h1": "사이판 3박4일, <em>ETA는 무료</em>입니다",
        "seoTitle": "사이판 3박4일 코스·경비 — G-CNMI ETA 무료, 2인 128만 (2026) | 트립픽",
        "dek": ("사이판은 ESTA 대신 G-CNMI ETA를 무료로 받고 갑니다. 출발 5일 전까지 신청하고 "
                "전자여권을 써야 하며, 체류는 45일까지입니다. 마나가하섬은 보트 50달러에 "
                "환경세 10달러·부두세 3달러가 붙고, 렌터카는 하루 50~80달러입니다. "
                "2인 3박4일 현지 경비를 숙소 3안으로 계산했습니다."),
        "desc": ("사이판 3박4일(2026-11). G-CNMI ETA 무료·45일·2년, 마나가하 1인 63달러, 그로토 투어 45~55달러, "
                 "렌터카 50~80달러, 숙소 1박 141,487~238,257원, 2인 현지 1,279,300~1,569,610원."),
        "keywords": ("사이판 3박4일, 사이판 여행 경비, G-CNMI ETA, 사이판 ETA 신청, 사이판 입국 서류, "
                     "마나가하섬 환경세, 마나가하 보트값, 그로토 스노클링, 사이판 렌터카, "
                     "사이판 숙소 추천, 가라판 호텔, 사이판 전자여권"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 11,
        "image": "images/v68/saipan-3n4d-course-budget.jpg",
        "ogImage": "images/og/v68-saipan-og.jpg",
        "imageAlt": "사이판 해변의 야자수와 노을",
        "imageCredit": "사진: Pexels (Rommell Buenaflor)",
        "tours": [],
        "essentials": ["cp-adapter-nemotab", "cp-passport-reindeer"],
        "related": ["guam-4n5d-course", "guam-vs-saipan-comparison", "us-esta-application-guide",
                    "airport-arrival-city-transfer-guide", "travel-insurance-guide", "travel-card-fees-comparison"],
        "ctaTitle": "사이판 항공·숙소 비교",
        "ctaText": "출발일을 넣으면 인천–사이판 직항과 가라판·해변 리조트를 같은 기준으로 비교합니다.",
        "fxNote": "1달러 1,344.09원 · 2026-11-27 기준",
        "faq": [
            ["사이판은 ESTA 없이 갈 수 있나요?",
             "갑니다. 대신 출발 5일 전까지 G-CNMI ETA를 무료로 받아야 하고, 유효기간은 2년, 체류는 45일까지입니다. ESTA나 미국 관광비자가 있으면 ETA는 필요 없습니다."],
            ["사이판은 전자여권이 꼭 필요한가요?",
             "외교부 주하갓냐 출장소 공지 기준으로 사이판은 전자여권이 필수입니다. 긴급여권(비전자)으로는 입국할 수 없으니 여권을 새로 만들어야 합니다."],
            ["마나가하섬 비용은 얼마인가요?",
             "보트 왕복과 입도가 35~50달러이고, 환경세 10달러와 부두세 3달러가 따로 붙습니다. 1인 63달러(84,677원)로 잡으면 2인 169,355원입니다."],
            ["사이판에서 렌터카가 필요한가요?",
             "대중교통이 없어 필요합니다. 하루 50~80달러(보험 포함)이고 주유는 갤런당 4~5달러로 섬 한 바퀴에 10달러 안팎입니다. 북부·남부를 하루에 묶을 때만 빌려도 됩니다."],
            ["사이판 3박4일 2인 경비는?",
             "항공을 빼고 숙소에 따라 1,279,300원(코럴 오션)~1,569,610원(크라운 플라자)입니다. 마나가하 169,355원, 그로토 134,409원, 공항 택시 80,645원, 렌터카·주유 94,086원, 식비 376,344원(가정)이 들어갑니다."],
        ],
    },
]

EXTRA = {
    "china-visa-free-alipay-wechat-pay-guide": {
        "hub": "",
        "regions": ["cn"],
        "tags": ["준비물", "가성비"],
        "stayRegions": ["shanghai"],
        "takeaway": ("중국은 2026년 12월 31일까지 30일 무비자이고, 결제는 알리페이·위챗페이에 해외 카드를 붙여 합니다. "
                     "200위안 이하는 수수료가 없고 넘으면 3%이므로, 큰 결제는 카드나 현금이 낫습니다."),
        "facts": [["무비자 체류", "30일 · ~2026-12-31"], ["알리페이 수수료", "200위안 초과 3%"]],
    },
    "boracay-3n4d-course-budget": {
        "hub": "",
        "regions": ["ph"],
        "tags": ["가성비", "일정"],
        "stayRegions": [],
        "takeaway": ("보라카이는 제티에서 1인 535페소(터미널 150·환경 300·보트 50·수수료 35)를 내고, "
                     "호핑투어는 표시가 위에 크리스털 코브 300페소가 붙습니다. 2인 3박4일 현지는 39만~79만 원입니다."),
        "facts": [["제티 1인", "535페소 · 11,266원"], ["호핑 현장 지출", "750~850페소"]],
    },
    "saipan-3n4d-course-budget": {
        "hub": "",
        "regions": ["gu", "etc"],
        "tags": ["가성비", "일정"],
        "stayRegions": ["saipan"],
        "takeaway": ("사이판은 G-CNMI ETA(무료·45일·2년)를 출발 5일 전까지 받고, 전자여권을 써야 합니다. "
                     "마나가하는 보트 50달러에 환경세 10달러·부두세 3달러가 붙고, 렌터카는 하루 50~80달러입니다."),
        "facts": [["G-CNMI ETA", "무료 · 45일"], ["마나가하 1인", "63달러 · 84,677원"]],
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
    print(f"[v68] guides {len(g['guides'])}편 (+{added}) · guide_extra {len(ex['guides'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
