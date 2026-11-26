#!/usr/bin/env python3
"""v59: 신규 가이드 3편 메타데이터(guides.json·guide_extra.json)·내부 링크.

    python3 tools/apply_v59_guides.py

값은 전부 v59 조사(2026-11-26)에서 확인한 것이다.
- 푸꾸옥: 썬월드 혼똠 케이블카 850,000동(2026-01-01 적용), 빈펄 사파리 950,000동·빈원더스 1,050,000동·1일 콤보 1,500,000동, 빈버스 무료
- 세부: 오슬롭 외국인 1,000페소(2025-03-21 시행), MyBus 50페소, 택시 기본 65/115페소(2026-09-28), 필리핀 무비자 30일·eTravel 무료
- 하노이: 86번 버스 50,000동(노이바이 공항 공식), 하롱베이 관람료 250,000/550,000/750,000동(관리위원회)
- 숙소: 트립닷컴 1박·2인·세금 포함 최저가(2026-12-10~11 조회)
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
        "slug": "phu-quoc-3n4d-4n5d-course",
        "category": "일정·경비",
        "navTitle": "푸꾸옥 3박4일 — 케이블카 85만동 vs 사파리 95만동",
        "h1": "푸꾸옥 3박4일, <em>남부 케이블카</em>와 북부 사파리 중 하나",
        "seoTitle": "푸꾸옥 3박4일·4박5일 — 케이블카 85만동·사파리 95만동 | 트립픽",
        "dek": ("푸꾸옥은 남부(혼똠 케이블카·선셋타운)와 북부(사파리·빈원더스·그랜드월드)가 섬 양 끝입니다. "
                "3박4일은 한쪽만, 4박5일은 양쪽을 도는 구성이 이동을 덜 쓰고, 숙소는 1박 5만 1,978원부터 45만 5,768원까지입니다."),
        "desc": ("푸꾸옥 3박4일·4박5일 코스. 혼똠 케이블카 왕복 850,000동(아쿠아토피아 포함), 빈펄 사파리 950,000동, "
                 "빈원더스 1,050,000동, 1일 콤보 1,500,000동, 공항↔그랜드월드 무료 빈버스, 숙소 1박 5만 1,978~45만 5,768원, "
                 "2인 경비 42만~116만 원(항공 제외). 2026-11 확인."),
        "keywords": ("푸꾸옥 3박4일, 푸꾸옥 4박5일, 푸꾸옥 케이블카 가격, 혼똠 케이블카 85만동, 빈원더스 푸꾸옥 입장권, "
                     "빈펄 사파리 푸꾸옥, 그랜드월드 푸꾸옥, 푸꾸옥 숙소, 푸꾸옥 무비자 45일"),
        "published": "2026-11-26",
        "updated": "2026-11-26",
        "image": "images/v59/phu-quoc-3n4d-4n5d-course.jpg",
        "ogImage": "images/og/v59-phu-quoc-og.jpg",
        "imageAlt": "푸꾸옥 롱비치의 야자수와 백사장",
        "imageCredit": "사진: Pexels (Quang Nguyen Vinh)",
        "tours": [],
        "essentials": ["vn-esim-usimsa-3d-phuquoc", "cp-waterproof-sinji", "cp-powerbank-spidy"],
        "related": ["chiang-mai-3n4d-course", "bali-ubud-seminyak-3n4d-course", "danang-hoian-3n5d",
                    "entry-immigration-guide", "vietnam-esim", "thailand-souvenir-list"],
        "ctaTitle": "푸꾸옥 3박4일, 내 날짜로 총액 계산",
        "ctaText": "인원과 여행 날짜를 넣으면 숙소·항공·액티비티를 같은 기준으로 계산합니다.",
        "fxNote": "100동 5.21원 · 2026-11-25 고시 기준",
        "read": 13,
        "faq": [
            ["푸꾸옥 3박4일은 남부와 북부 중 어디에 하루를 쓰나요?",
             "첫 여행이면 남부 혼똠 케이블카를 권합니다. 왕복 850,000동 표에 혼똠섬 입장과 아쿠아토피아 워터파크가 포함돼 하루가 그대로 채워집니다. 아이와 함께라면 북부 사파리(950,000동)·빈원더스(1,050,000동)가 낫고, 이때는 그랜드월드 쪽 숙소를 잡으면 공항에서 무료 빈버스로 이동합니다."],
            ["케이블카는 몇 시에 타야 하나요?",
             "2026년 1월 1일부터 운행이 09:30~11:30, 13:30~14:00, 15:30~17:30 네 구간입니다. 오전 첫 구간을 타면 오후 내내 워터파크를 쓸 수 있고, 마지막 구간은 노을과 겹칩니다. 연말·설 연휴에는 09:30 구간이 먼저 마감되니 날짜 지정권으로 미리 잡으세요."],
            ["사파리와 빈원더스를 하루에 다 볼 수 있나요?",
             "가능하지만 콤보가 필요합니다. 사파리는 09시 개장, 15시 이후 입장 마감이라 오전에 사파리를 돌고 오후에 빈원더스를 쓰는 순서가 맞습니다. 사파리 단독(950,000동)과 빈원더스 단독(1,050,000동)을 따로 사면 200만동인데, 1일 콤보는 1,500,000동으로 50만동(2만 6,050원) 쌉니다."],
            ["푸꾸옥 입국에 비자가 필요한가요?",
             "필요 없습니다. 한국 여권은 45일 무비자이고, 입국일 기준 여권 6개월 이상과 귀국·다음 목적지 항공권이 조건입니다. 푸꾸옥(PQC)은 2026년 6월 1일부터 PAI 시범 운영 공항이라, 도착 72시간 전에 prearrival.immigration.gov.vn에서 무료로 내고 QR을 저장해 두면 안전합니다."],
            ["3박4일 2인 경비는 얼마인가요?",
             "항공을 제외하면 42만 6,854원~116만 2,251원입니다. 숙소 3박이 15만 5,934원(Palm Haven)이냐 83만 4,021원(라하나)이냐가 가장 크게 갈리고, 여기에 케이블카 2인 8만 8,570원과 액티비티 9만 8,990~15만 6,300원, 식비 8만 3,360원(1끼 1인 10만동 가정)이 붙습니다."],
        ],
    },
    {
        "slug": "cebu-3n4d-course",
        "category": "일정·경비",
        "navTitle": "세부 3박4일 — 막탄·세부시티·오슬롭 1,000페소",
        "h1": "세부 3박4일, <em>막탄 2박 + 시티 1박</em>이 기본입니다",
        "seoTitle": "세부 3박4일 코스·경비 — 오슬롭 1,000페소·MyBus 50페소 | 트립픽",
        "dek": ("세부는 공항이 있는 막탄, 옛 시가지 세부시티, 남쪽 모알보알이 서로 멉니다. 3박4일은 막탄 2박+시티 1박이 "
                "이동을 덜 쓰고, 오슬롭 고래상어는 외국인 1,000페소·오전 6~10시입니다. 숙소는 1박 3만 6,684원부터 32만 3,657원."),
        "desc": ("세부 3박4일 코스. 오슬롭 고래상어 외국인 1,000페소(보트·가이드 포함, 6~10시), 공항 MyBus 50페소·택시 기본 65/115페소, "
                 "숙소 1박 3만 6,684~32만 3,657원(2인), 무비자 30일·eTravel 무료, 2인 경비 23만~109만 원(항공 제외). 2026-11 확인."),
        "keywords": ("세부 3박4일, 세부 여행 경비, 오슬롭 고래상어 요금, 세부 막탄 숙소, 세부시티 호텔, 막탄공항 MyBus, "
                     "필리핀 무비자 30일, eTravel, 세부 모알보알"),
        "published": "2026-11-26",
        "updated": "2026-11-26",
        "image": "images/v59/cebu-3n4d-course.jpg",
        "ogImage": "images/og/v59-cebu-og.jpg",
        "imageAlt": "세부 모알보알 바다를 헤엄치는 다이버",
        "imageCredit": "사진: Pexels (Elaine Bernadine Castro)",
        "tours": [],
        "essentials": ["cp-waterproof-sinji", "cp-powerbank-spidy", "cp-neckpillow-rango"],
        "related": ["guam-4n5d-course", "singapore-3n4d-course-budget", "taipei-3n4d-course-budget",
                    "entry-immigration-guide", "travel-insurance-guide", "currency-payment-fees"],
        "ctaTitle": "세부 3박4일, 숙소·항공 한 번에",
        "ctaText": "출발일과 인원을 넣으면 막탄·시티 호텔과 항공을 같은 기준으로 비교합니다.",
        "fxNote": "1페소 21.05원 · 2026-11-25 고시 기준",
        "read": 13,
        "faq": [
            ["세부 3박4일은 막탄과 세부시티 중 어디에 묵나요?",
             "첫 세부면 막탄 2박 + 세부시티 1박이 무난합니다. 도착일 밤늦게 막탄에서 자고, 둘째 날 오슬롭이나 호핑에 하루를 쓰고, 셋째 날 시티로 옮겨 성당·쇼핑·야시장을 봅니다. 리조트 휴양이 목적이면 막탄 3박에 시티 반나절을 더하는 쪽이 편합니다."],
            ["오슬롭 고래상어 요금은 얼마인가요?",
             "외국인 1,000페소(2만 1,054원)이고 보트·가이드가 포함됩니다. 필리핀 여권자는 500페소입니다. 2025년 3월 21일 시행된 오슬로브 시 조례 요금이고, 2026년 5월 현지 보도로 같은 금액이 확인됐습니다. 스쿠버는 시 요금 1,500페소에 장비·업체 요금이 따로 붙습니다."],
            ["오슬롭은 몇 시에 가야 하나요?",
             "오전 6시에 시작해 10시에 끝납니다. 고래상어가 나타나지 않으면 그보다 일찍 닫기도 합니다(2026년 5월에는 나흘 연속 출현이 없어 조기 종료). 세부시티에서 차로 3시간 안팎이라 새벽 4~5시에 출발해야 6시 세션을 맞출 수 있습니다."],
            ["공항에서 시내까지 가장 싼 방법은?",
             "MyBus가 50페소(1,053원)로 가장 쌉니다. 다만 운행이 07:00~22:00이라, 밤 10시 이후에 내리는 한국 직항편으로는 사실상 못 탑니다. 그때는 흰 일반택시(기본 65페소)나 그랩(시티까지 300~500페소, 2026-09 인상 전 안내값)을 쓰세요."],
            ["필리핀 입국에 무엇이 필요한가요?",
             "무비자 30일이라 비자는 필요 없고, ① 귀국 또는 다음 목적지 항공권 ② 체류 종료일부터 6개월 이상 남은 여권 ③ eTravel(etravel.gov.ph, 무료) QR 세 가지입니다. 관광객은 필리핀 여행세를 내지 않습니다(체류 1년 미만 비이민 외국인 면제)."],
        ],
    },
    {
        "slug": "hanoi-halong-3n4d-course",
        "category": "일정·경비",
        "navTitle": "하노이·하롱베이 3박4일 — 86번 버스 50,000동",
        "h1": "하노이·하롱베이 3박4일, <em>1박 크루즈</em>를 넣으면 하노이가 하루 반",
        "seoTitle": "하노이·하롱베이 3박4일 — 86번 버스 50,000동·관람료 25만동 | 트립픽",
        "dek": ("하노이에서 하롱까지 170~180km·2~2.5시간. 당일치기는 왕복 5시간을 차에서 보내고, 1박 크루즈는 하노이 실관광이 "
                "하루 반으로 줄지만 새벽·석양과 루온 동굴 카약을 봅니다. 공항버스 86번 50,000동, 관람료 250,000동, 숙소 1박 1만 6,328원부터."),
        "desc": ("하노이·하롱베이 3박4일 코스. 노이바이 86번 버스 50,000동(06:40~22:15), 하롱베이 관람료 1·2코스 250,000동·1박 550,000동·2박 750,000동, "
                 "루온 대나무배 50,000동, 숙소 1박 1만 6,328~10만 9,350원(2인), 무비자 45일·PAI, 2인 경비 18만~37만 원. 2026-11 확인."),
        "keywords": ("하노이 3박4일, 하롱베이 1박 크루즈, 하롱베이 관람료, 하노이 공항버스 86번, 노이바이 50,000동, "
                     "하노이 구시가지 숙소, 하롱베이 당일치기, 베트남 무비자 45일"),
        "published": "2026-11-26",
        "updated": "2026-11-26",
        "image": "images/v59/hanoi-halong-3n4d-course.jpg",
        "ogImage": "images/og/v59-hanoi-og.jpg",
        "imageAlt": "하노이 호안끼엠 호수와 응옥썬 사당",
        "imageCredit": "사진: Pexels (Valeria Drozdova)",
        "tours": [],
        "essentials": ["vn-esim-lingsim-1d", "cp-neckpillow-rango", "cp-adapter-nemotab"],
        "related": ["danang-hoian-3n5d", "chiang-mai-3n4d-course", "travel-card-fees-comparison",
                    "entry-immigration-guide", "flight-cheap-booking-baggage", "currency-payment-fees"],
        "ctaTitle": "하노이·하롱베이 3박4일 총액 계산",
        "ctaText": "인원과 날짜를 넣으면 하노이 숙소·항공·크루즈를 같은 기준으로 계산합니다.",
        "fxNote": "100동 5.21원 · 2026-11-25 고시 기준",
        "read": 12,
        "faq": [
            ["하롱베이는 당일치기와 1박 중 어느 쪽이 낫나요?",
             "첫 하노이면 1박을 권합니다. 하노이에서 하롱까지 170~180km·2~2.5시간이라 당일치기는 왕복 5시간 이상을 차에서 보냅니다. 1박 크루즈면 하노이 실관광이 하루 반으로 줄지만 새벽·석양과 루온 동굴 카약을 다 볼 수 있습니다."],
            ["하롱베이 관람료는 얼마인가요?",
             "코스 단위로 냅니다. 관리위원회 요금표 기준 1·2번 코스(당일) 250,000동, 2번 코스 + 1박 550,000동, 2박 750,000동이고, 1~4번 코스를 도는 탐험 크루즈는 600,000동입니다. 이 금액은 베이 관람료이고 크루즈·식사는 별도입니다."],
            ["공항에서 시내까지 얼마인가요?",
             "86번 공항버스가 50,000동(2,605원)이고 06:40~22:15에 30분 간격으로 다닙니다. 하노이 기차역까지 약 50~70분입니다. 07번은 15,000동, 17번 19,000동, 68번 55,000동이고, 막차 이후에는 그랩·택시를 써야 합니다."],
            ["하노이 12월 날씨는 어떤가요?",
             "아침저녁으로 쌀쌀해 얇은 패딩이 필요하고, 하롱베이 쪽은 안개가 잦아 당일 크루즈가 단축·취소되는 날이 있습니다. 크루즈를 예약할 때는 안개로 운항이 바뀔 때의 환불 규정을 확인하세요."],
            ["2인 경비는 얼마나 드나요?",
             "항공과 크루즈 요금을 빼면 18만 3,746원~36만 9,790원입니다. 하노이 숙소 2박(3만 2,656~21만 8,700원), 하롱베이 관람료 2인 5만 7,310원, 86번 버스 왕복 2인 1만 420원, 식비 8끼 8만 3,360원(1끼 1인 10만동 가정)입니다."],
        ],
    },
]

EXTRA = {
    "phu-quoc-3n4d-4n5d-course": {
        "hub": None,
        "regions": ["vn"],
        "tags": ["숙소", "가성비", "eSIM"],
        "takeaway": "3박4일은 남부 케이블카(850,000동, 아쿠아토피아 포함)나 북부 사파리·빈원더스 중 하나만, 4박5일은 양쪽을 도는 구성이 이동을 덜 씁니다. 공항↔그랜드월드는 무료 빈버스라 북부 숙소면 교통비가 0원입니다.",
        "facts": [["혼똠 케이블카 왕복", "850,000동"], ["사파리+빈원더스 1일 콤보", "1,500,000동"]],
    },
    "cebu-3n4d-course": {
        "hub": None,
        "regions": ["ph", "etc"],
        "tags": ["숙소", "가성비"],
        "takeaway": "3박4일은 막탄 2박+시티 1박이 이동을 덜 씁니다. 오슬롭 고래상어는 외국인 1,000페소·오전 6~10시이고, 공항 MyBus는 50페소지만 막차가 22시라 한국 직항 도착편으로는 탑승이 어렵습니다.",
        "facts": [["오슬롭 외국인", "1,000페소"], ["공항 MyBus", "50페소"]],
    },
    "hanoi-halong-3n4d-course": {
        "hub": None,
        "regions": ["vn"],
        "tags": ["숙소", "가성비", "교통패스"],
        "takeaway": "하롱베이 1박을 넣으면 하노이가 하루 반이 됩니다. 86번 공항버스 50,000동, 하롱베이 관람료는 1·2번 코스 250,000동·1박 550,000동이고 크루즈 요금은 별도입니다.",
        "facts": [["86번 공항버스", "50,000동"], ["하롱베이 2번 코스", "250,000동"]],
    },
}

REVERSE = {
    "chiang-mai-3n4d-course": "phu-quoc-3n4d-4n5d-course",
    "bali-ubud-seminyak-3n4d-course": "phu-quoc-3n4d-4n5d-course",
    "danang-hoian-3n5d": "phu-quoc-3n4d-4n5d-course",
    "vietnam-esim": "phu-quoc-3n4d-4n5d-course",
    "entry-immigration-guide": "phu-quoc-3n4d-4n5d-course",
    "guam-4n5d-course": "cebu-3n4d-course",
    "singapore-3n4d-course-budget": "cebu-3n4d-course",
    "taipei-3n4d-course-budget": "cebu-3n4d-course",
    "travel-insurance-guide": "cebu-3n4d-course",
    "currency-payment-fees": "cebu-3n4d-course",
    "flight-cheap-booking-baggage": "hanoi-halong-3n4d-course",
    "travel-card-fees-comparison": "hanoi-halong-3n4d-course",
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
        print(f"  · {item['slug']} seoTitle {len(item['seoTitle'])}자")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
