#!/usr/bin/env python3
"""v64: 신규 가이드 8편 메타데이터(guides.json·guide_extra.json)·상호 링크.

    python3 tools/apply_v64_guides.py

값은 2026-11-27 확인분이다.
- ESTA: 공식 사이트 수수료 $40.62(처리 $10.62+승인 $30), 2년/여권만료, 90일, 72시간 전 신청, 최대 72시간 처리
- 영국 ETA: £20, 2년, 1회 6개월, 1일~3영업일, 한국은 2025-01-08부터, landside 환승 필요
- 간사이공항: 난카이 공항급행 970엔(43~45분)·라피트 1,670엔(디지털 1,410엔)·리무진 1,400/1,800/2,800엔·
  JR 간쿠쾌속 1,210엔·하루카 할인권 1,600/1,900/2,700엔(2026-11-01 개정)·USJ 1,210엔
- 뉴욕: AirTrain $8.75·지하철 $3.00·OMNY 7일 상한 $35·LIRR CityTicket $5.25/7.25·
  자유의 여신상 $26·ESB $46~·톱오브더록 $42~·SUMMIT $44+$3·메트 $30·택시 JFK-맨해튼 $70 정액
- 나고야: 뮤스카이 1,430엔(980+450)·지하철 24시간 760엔·도니치에코 620엔·나고야성 1,000엔(2026-10-01)·
  지브리파크 스탠더드 3,300/3,800엔·프리미엄 7,300/7,800엔·시스템 110엔·2개월 전 10일 14시·
  시라카와고 3,600~4,700엔·다카야마 3,600엔(웹 3,300엔)
- 일본 식당: 타베로그 다국어 1인 440엔(환불 없음)·OMAKASE 1좌석 390엔·TableCheck 카드·당일/노쇼 100%
- 마카오: 터보젯 194/212/242HK$·코타이 192/209/242HK$·금바 65/70HK$·버스 MOP6·LRT 6~12MOP
- 파리: 2026-01-01 요금 — 1회 €2.55·버스 €2.05·공항 €14·주르 €12.30·세멘 €32.40·비지트 30.60/45.40/63.80/78.00·
  나비고 이지 €2·데쿠베르트 €5
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
        "slug": "us-esta-application-guide",
        "category": "준비물·경비",
        "navTitle": "미국 ESTA 신청 — $40.62·2년·72시간",
        "h1": "미국 ESTA, <em>수수료 $40.62</em>와 <em>72시간</em>만 알면 끝",
        "seoTitle": "미국 ESTA 신청 방법·수수료 $40.62·유효기간 2년·처리 72시간 (2026) | 트립픽",
        "dek": ("한국 여권으로 미국 90일 이하 관광·상용이면 ESTA입니다. 공식 수수료 $40.62, 유효 2년, "
                "출발 72시간 전 신청, 승인은 수 분~최대 72시간. 여권 교체 시 재신청 조건과 대행 사이트 구별법까지 정리했습니다."),
        "desc": ("미국 ESTA 신청(2026-11). 공식 수수료 $40.62(처리 $10.62+승인 $30), 유효 2년 또는 여권 만료, "
                 "1회 90일, 출발 72시간 전 신청, 처리 수 분~72시간. 셀피 사진·전자여권 요건, 재신청 5가지, "
                 "거절 시 비자 전환까지."),
        "keywords": ("미국 ESTA, ESTA 신청, ESTA 수수료, 미국 전자여행허가, ESTA 40달러, ESTA 유효기간, "
                     "ESTA 72시간, ESTA 거절, ESTA 재신청, 미국 무비자 90일, ESTA 대행 사이트, 미국 입국 서류"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/us-esta-application-guide.jpg",
        "ogImage": "images/og/v64-esta-og.jpg",
        "imageAlt": "여권 스탬프가 찍힌 여권 면을 손에 든 모습",
        "imageCredit": "사진: Ekaterina Belinskaya / Pexels",
        "tours": [],
        "essentials": ["cp-passport-reindeer", "cp-powerbank-spidy"],
        "related": ["entry-immigration-guide", "passport-application-guide", "uk-eta-application-guide",
                    "airport-checkin-customs-guide", "flight-cheap-booking-baggage", "europe-ees-etias-guide"],
        "ctaTitle": "미국 항공·숙소 비교",
        "ctaText": "ESTA 승인 뒤 날짜를 정하고, 항공과 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "1달러 1,344.09원 · 2026-11-27 고시 기준",
        "read": 11,
        "faq": [
            ["ESTA 수수료는 얼마인가요?",
             "공식 사이트(esta.cbp.dhs.gov) 결제 화면 기준 $40.62입니다. 처리 수수료 $10.62와 승인 수수료 $30으로 나뉘고, 2025년 9월 30일부터 기존 $21에서 인상됐습니다. 카드 해외결제 수수료가 별도로 붙을 수 있으며, 거절돼도 환불되지 않습니다."],
            ["ESTA는 언제 신청해야 하나요?",
             "출발 최소 72시간 전에 신청하라고 CBP가 안내합니다. 승인은 대개 몇 분 안에 나지만 추가 심사에 걸리면 최대 72시간 걸리고, 승인 전에는 탑승이 거절됩니다. 항공권을 예약하는 날 함께 신청하는 편이 안전합니다."],
            ["여권을 새로 발급받으면 ESTA도 다시 받아야 하나요?",
             "네. ESTA는 여권에 전자적으로 연결되므로 새 여권으로 바꾸면 기존 승인은 효력이 없습니다. 2년 유효기간이 남아 있어도 새 여권번호로 다시 신청해야 합니다. 이름·국적이 바뀌거나 적격성 답변이 달라져도 재신청 대상입니다."],
            ["아이도 ESTA를 받아야 하나요?",
             "네. 좌석을 쓰지 않는 유아를 포함해 1인당 각각 ESTA가 필요합니다. 4인 가족이면 4건을 신청하고 $162.48을 결제합니다. 부모가 대신 신청할 수 있지만 신청서는 사람마다 따로 작성합니다."],
            ["ESTA가 거절되면 미국에 못 가나요?",
             "ESTA로는 갈 수 없지만 영구 입국 금지는 아닙니다. 미국 비자(관광 B1/B2 등)를 정식으로 신청해야 하고, 거절 사유는 공개되지 않습니다. 비자 신청은 대사관 인터뷰와 별도 수수료가 필요합니다."],
        ],
    },
    {
        "slug": "uk-eta-application-guide",
        "category": "준비물·경비",
        "navTitle": "영국 ETA 신청 — £20·2년·6개월",
        "h1": "영국 ETA, <em>£20</em>과 <em>6개월</em>만 확인하면 됩니다",
        "seoTitle": "영국 ETA 신청 방법·수수료 £20·유효기간 2년·환승 기준 (2026) | 트립픽",
        "dek": ("한국 여권으로 영국 6개월 이하 방문이면 ETA가 필요합니다. 수수료 £20, 유효 2년, 1회 6개월, "
                "승인 1일~3영업일. 한국은 2025년 1월 8일부터 대상이고, 공항 환승은 landside만 해당합니다."),
        "desc": ("영국 ETA 신청(2026-11). GOV.UK 기준 £20, 유효 2년 또는 여권 만료, 1회 6개월, 처리 1일~3영업일. "
                 "한국 2025-01-08부터 대상, landside 환승 필요·airside 불필요, ETA로 불가한 활동과 거절 시 비자 전환."),
        "keywords": ("영국 ETA, 영국 전자여행허가, UK ETA 신청, 영국 ETA 수수료, 영국 ETA 20파운드, "
                     "영국 무비자 6개월, 영국 환승 ETA, 히스로 환승, 영국 입국 서류, UK ETA 앱, 영국 여행 준비"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/uk-eta-application-guide.jpg",
        "ogImage": "images/og/v64-eta-og.jpg",
        "imageAlt": "템스강 위 런던 타워 브리지",
        "imageCredit": "사진: David Pickup / Pexels",
        "tours": [],
        "essentials": ["cp-adapter-nemotab", "cp-passport-reindeer"],
        "related": ["europe-ees-etias-guide", "paris-london-5n7d", "us-esta-application-guide",
                    "europe-pickpocket-tax-refund-guide", "entry-immigration-guide", "europe-shopping-tax-refund"],
        "ctaTitle": "런던 항공·숙소 비교",
        "ctaText": "ETA 승인 뒤 날짜를 정하고, 히스로·개트윅 도착 항공과 숙소를 같은 기준으로 봅니다.",
        "fxNote": "1파운드 1,760.56원 · 2026-11-27 고시 기준",
        "read": 10,
        "faq": [
            ["영국 ETA 수수료는 얼마인가요?",
             "GOV.UK 기준 £20입니다(2026-11-27 확인). 신청 후에는 환불되지 않고, 거절되거나 내용을 고쳐 다시 내도 새로 결제해야 합니다. 2025년 4월 £16, 그 이전 £10이던 시절 안내가 아직 많으니 결제 화면 금액을 확인하세요."],
            ["한국인은 언제부터 ETA가 필요했나요?",
             "2025년 1월 8일 이후 영국에 도착하는 여행부터입니다. 한국은 영국 내무부 ETA 대상국 명단에 2025-01-08 여행분부터 들어가 있습니다. 유효한 영국 비자나 거주·취업·유학 허가가 있으면 ETA가 필요 없습니다."],
            ["영국에서 환승만 하는데 ETA가 필요한가요?",
             "입국 심사를 통과해 공항 밖으로 나가는 landside 환승이면 필요합니다. 반대로 환승 구역을 벗어나지 않는 airside 환승은 필요 없습니다. 히스로와 개트윅처럼 공항을 옮기는 경우에는 ETA가 필요합니다."],
            ["ETA는 얼마나 걸리나요?",
             "보통 1일 이내에 결정되고, 최대 3영업일이 걸릴 수 있습니다. 승인 메일에는 16자리 참조번호가 오고, 승인 전에는 탑승할 수 없습니다. 출발 3영업일 전에는 신청하고, 주말·공휴일이 끼면 더 여유를 두세요."],
            ["ETA로 일할 수 있나요?",
             "영국 회사에 고용되거나 자영업으로 일할 수 없습니다. 관광·친지 방문·단기 비즈니스·단기 연수·최대 6개월 체류만 가능합니다. 결혼·동반자 등록, 공적 부조 수령, 6개월 초과 체류도 안 됩니다."],
        ],
    },
    {
        "slug": "kansai-airport-osaka-kyoto-transfer",
        "category": "일본",
        "navTitle": "간사이공항→난바·우메다·교토·USJ 이동 비교",
        "h1": "간사이공항에서 <em>난바 970엔</em>, <em>교토 2,700엔</em>",
        "seoTitle": "간사이공항(KIX) → 난바·우메다·교토·USJ 이동 비교 — 요금·시간·막차 (2026) | 트립픽",
        "dek": ("난바는 난카이 공항급행 970엔·43분, 라피트는 디지털 티켓 1,410엔·34분. 우메다는 JR 1,210엔, "
                "교토는 하루카 할인권 2,700엔·80분, 리무진버스 2,800엔. USJ 1,210엔과 23:55 막차까지 비교했습니다."),
        "desc": ("간사이공항 이동(2026-11). 난바 공항급행 970엔·라피트 1,410엔(디지털), 우메다 간쿠쾌속 1,210엔, "
                 "교토 하루카 2,700엔·버스 2,800엔, USJ 1,210엔, 리무진 1,400/1,800엔. 막차 23:55·2터미널 셔틀까지."),
        "keywords": ("간사이공항 난바, 간사이공항 교토, 간사이공항 우메다, 라피트 요금, 하루카 할인권, "
                     "난카이 공항급행 970엔, 간사이공항 리무진버스, 간사이공항 막차, 간사이공항 USJ, "
                     "KIX 교통, 간사이공항 2터미널"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/kansai-airport-osaka-kyoto-transfer.jpg",
        "ogImage": "images/og/v64-kix-og.jpg",
        "imageAlt": "간사이국제공항 철도역 승강장",
        "imageCredit": "사진: Wikimedia Commons (CC0)",
        "tours": [],
        "essentials": ["osaka-nankai-rapit", "jp-esim-lingsim-1d"],
        "related": ["osaka-usj-transfer", "osaka-kyoto-3n4d", "osaka-amazing-pass",
                    "airport-arrival-city-transfer-guide", "narita-haneda-transfer", "japan-ic-card"],
        "ctaTitle": "간사이공항 픽업·라피트 예약",
        "ctaText": "도착 시간과 숙소를 넣으면 공항철도·픽업·숙소를 같은 기준으로 비교합니다.",
        "fxNote": "100엔 844.26원 · 2026-11-25 고시 기준",
        "read": 12,
        "faq": [
            ["난바까지 가장 싼 방법은 무엇인가요?",
             "난카이 공항급행 970엔(약 43~45분)입니다. 특급요금이 없고 15분 간격으로 다닙니다. 34분 만에 가려면 라피트를 타는데, 창구 1,670엔보다 스마트폰 디지털 티켓 1,410엔이 쌉니다."],
            ["교토까지 하루카와 버스 중 어느 쪽이 좋나요?",
             "가격은 하루카 할인권 2,700엔, 리무진버스 2,800엔으로 거의 같습니다. 하루카는 약 80분·30분 간격이고, 버스는 85~90분·교토행 전 좌석 예약제입니다. 짐이 많고 호텔이 교토역 남쪽이면 버스, 시간을 아끼려면 하루카입니다."],
            ["하루카 할인권은 어디서 사나요?",
             "JR-WEST 온라인 예약 또는 해외 여행사에서 미리 사야 합니다. 일본 국내에서는 살 수 없습니다. 2026년 11월 1일 구매분부터 오사카·신오사카 1,900엔, 덴노지 1,600엔, 교토 2,700엔입니다."],
            ["밤늦게 도착하면 어떻게 가나요?",
             "난바행 마지막은 공항급행 23:55이고, 라피트는 23:00에 끊깁니다. 그 뒤에는 택시(난바까지 약 2만 엔)뿐입니다. 교토는 하루카 막차가 22:16이라, 그 이후 도착이면 오사카에서 1박하는 편이 낫습니다."],
            ["제2터미널에 도착하면 어떻게 하나요?",
             "무료 셔틀버스로 제1터미널까지 5~10분 이동한 뒤 철도·리무진버스를 타야 합니다. 피치항공 등 LCC가 제2터미널을 쓰므로, 탑승 수속 때 터미널을 확인하고 셔틀 시간 10분을 더 잡으세요."],
        ],
    },
    {
        "slug": "new-york-4n5d-course-budget",
        "category": "유럽·장거리",
        "navTitle": "뉴욕 4박5일 — AirTrain $11.75·전망대 하나",
        "h1": "뉴욕 4박5일, <em>전망대 하나</em>와 <em>동네 두 곳</em>이면 됩니다",
        "seoTitle": "뉴욕 자유여행 4박5일 — JFK 에어트레인·OMNY 상한·전망대 (2026) | 트립픽",
        "dek": ("JFK에서 AirTrain+지하철 $11.75, 지하철 1회 $3.00에 7일 상한 $35. 자유의 여신상 $26, "
                "엠파이어스테이트 $46~, 메트 $30. 4박5일 동선과 2인 현지 경비 173만 원을 계산했습니다."),
        "desc": ("뉴욕 4박5일(2026-11). JFK AirTrain $8.75+지하철 $3.00, LIRR $5.25/7.25, OMNY 7일 상한 $35, "
                 "자유의 여신상 $26·ESB $46~·톱오브더록 $42~·메트 $30, JFK 택시 $70 정액, 2인 173만 원."),
        "keywords": ("뉴욕 4박5일, 뉴욕 여행 경비, 뉴욕 지하철 요금, OMNY 7일 상한, JFK 에어트레인, "
                     "뉴욕 전망대 비교, 자유의 여신상 페리 26달러, 메트로폴리탄 미술관 입장료, "
                     "뉴욕 숙소 추천, 뉴욕 4박5일 코스, 뉴욕 택시 70달러"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/new-york-4n5d-course-budget.jpg",
        "ogImage": "images/og/v64-nyc-og.jpg",
        "imageAlt": "맨해튼 스카이라인과 엠파이어스테이트빌딩",
        "imageCredit": "사진: Craig Adderley / Pexels",
        "tours": [],
        "essentials": ["cp-passport-reindeer", "cp-powerbank-spidy"],
        "related": ["us-esta-application-guide", "us-east-canada-10d", "travel-card-fees-comparison",
                    "hotel-booking-timing-refund-tips", "solo-vs-couple-travel-budget", "flight-delay-card-lost-emergency"],
        "ctaTitle": "뉴욕 항공·숙소 비교",
        "ctaText": "날짜와 인원을 넣으면 JFK·EWR 항공과 맨해튼 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "1달러 1,344.09원 · 2026-11-27 고시 기준",
        "read": 13,
        "faq": [
            ["JFK에서 맨해튼까지 가장 싼 방법은 무엇인가요?",
             "AirTrain $8.75와 지하철 $3.00을 합쳐 $11.75입니다. 재메이카역에서 지하철로 갈아타며 60~75분 걸립니다. 2인 왕복이면 $47입니다. LIRR를 쓰면 $5.25(비첨두)를 더 내고 45분대로 줄일 수 있습니다."],
            ["뉴욕 지하철 7일권이 있나요?",
             "2026년 1월부터 7일 무제한 메트로카드는 판매가 끝났고, OMNY 7일 상한 $35가 그 역할을 합니다. 같은 카드·휴대폰으로 7일 안에 $35를 채우면 그 뒤는 무료입니다. $3 × 12회 = $36이므로 12번째 탑승부터 이득입니다."],
            ["전망대는 어디가 좋나요?",
             "처음이면 엠파이어스테이트빌딩 86층($46~)이 무난하고, 엠파이어스테이트가 보이는 사진을 원하면 톱오브더록($42~)입니다. SUMMIT는 $44+$3 수수료로 유리·거울 전시가 강점입니다. 4박5일이면 유료 한 곳과 무료 전망 포인트 한 곳이면 충분합니다."],
            ["자유의 여신상은 예약해야 하나요?",
             "페리는 Statue City Cruises만 공식이고 성인 $26입니다. 크라운은 몇 달 전에 마감되고, 페데스탈은 +$0.30에 별도 예약이 필요합니다. 배터리파크 주변에서 표를 파는 사람은 공식 판매원이 아니므로 무시하세요."],
            ["뉴욕 4박5일 2인 경비는 얼마인가요?",
             "항공·식비를 빼고 숙소 4박 132만 144원, AirTrain 왕복 4만 7,043원, 지하철 상한 9만 4,086원, 자유의 여신상·ESB·메트 2인 27만 4,195원으로합계 173만 5,468원입니다. 택시로 바꾸면 18만 원 이상 더 듭니다."],
        ],
    },
    {
        "slug": "nagoya-3n4d-course-budget",
        "category": "일본",
        "navTitle": "나고야 3박4일 — 지브리파크 3,300엔·센트레아 1,430엔",
        "h1": "나고야 3박4일, <em>지브리파크</em>와 <em>시라카와고</em>를 한 번에",
        "seoTitle": "나고야 3박4일 코스·경비 — 지브리파크 3,300엔·시라카와고 버스 (2026) | 트립픽",
        "dek": ("센트레아→나고야 뮤스카이 1,430엔·28분, 지브리파크 스탠더드 3,300엔(2개월 전 10일 예약), "
                "시라카와고 버스 3,600~4,700엔. 3박4일 동선과 2인 현지 경비 58만 원을 계산했습니다."),
        "desc": ("나고야 3박4일(2026-11). 뮤스카이 1,430엔·28~34분, 지하철 24시간 760엔, "
                 "지브리파크 스탠더드 3,300/3,800엔, 나고야성 1,000엔, 시라카와고 3,600~4,700엔, "
                 "다카야마 3,600엔, 2인 58만 원."),
        "keywords": ("나고야 3박4일, 나고야 여행 경비, 지브리파크 예약, 지브리파크 티켓 3300엔, "
                     "지브리파크 가는 법, 시라카와고 버스, 다카야마 고속버스, 센트레아 뮤스카이, "
                     "나고야성 입장료, 나고야 여행 코스, 나고야메시"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/nagoya-3n4d-course-budget.jpg",
        "ogImage": "images/og/v64-nagoya-og.jpg",
        "imageAlt": "푸른 하늘 아래 나고야성",
        "imageCredit": "사진: Alen Joe Chacko / Pexels",
        "tours": [],
        "essentials": ["jp-esim-usimsa-1d", "cp-adapter-nemotab"],
        "related": ["tokyo-3n4d-course-budget", "osaka-kyoto-3n4d", "japan-restaurant-reservation-guide",
                    "japan-shinkansen-jr-pass-guide", "japan-ic-card", "japan-souvenir-list"],
        "ctaTitle": "나고야 항공·숙소 비교",
        "ctaText": "날짜와 인원을 넣으면 센트레아 항공과 사카에 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "100엔 844.26원 · 2026-11-25 고시 기준",
        "read": 12,
        "faq": [
            ["지브리파크 티켓은 얼마인가요?",
             "대산책권 스탠더드는 평일 3,300엔, 주말·공휴일 3,800엔입니다. 대창고·모노노케노사토·마녀의 골짜기에 들어갈 수 있고, 대창고만 2,000엔, 전 구역+모든 건물 내부 프리미엄은 7,300/7,800엔입니다. 티켓 1장당 시스템 이용료 110엔이 붙습니다."],
            ["지브리파크 예약은 언제 해야 하나요?",
             "입장 2개월 전 10일 14시에 판매가 열립니다. 12월 입장분은 10월 10일 14시, 2월 입장분은 12월 10일 14시입니다. 전 좌석 예약제이고 현장에서 일반 입장권을 팔지 않으므로, 날짜를 먼저 정하고 오픈 시간에 맞춰 예약하세요."],
            ["센트레아에서 나고야역까지 얼마인가요?",
             "뮤스카이 1,430엔(승차권 980엔+특별차량권 450엔)으로 28~34분입니다. 일반차 특급은 980엔·약 38분이고, 리무진버스는 사카에까지 2,000엔·약 55분입니다. 뮤스카이는 차내 구매 시 50엔이 더 붙습니다."],
            ["시라카와고는 당일치기로 가능한가요?",
             "가능합니다. 명철버스센터 7:50발 버스로 10:32 도착하면 2시간 30분 정도 머물 수 있습니다. 요금은 출발일 캘린더에 따라 왕복 3,600~4,700엔이고, 다카야마까지 이어 가려면 농히버스 2,800엔·50분을 더하면 됩니다."],
            ["나고야 시내 교통패스는 무엇이 유리한가요?",
             "하루에 지하철을 3번 이상 타면 지하철 24시간권 760엔이 이득입니다. 토·일·공휴일·매월 8일에는 버스·지하철 하루권 도니치에코쿠 620엔이 더 쌉니다. 명철·JR·아오나미선·리니모는 포함되지 않습니다."],
        ],
    },
    {
        "slug": "japan-restaurant-reservation-guide",
        "category": "맛집·미식",
        "navTitle": "일본 식당 예약·웨이팅 — 수수료 390~440엔·노쇼 100%",
        "h1": "일본 식당 예약, <em>수수료 390~440엔</em>과 <em>노쇼 100%</em>를 먼저 보세요",
        "seoTitle": "일본 식당 예약 방법 — 타베로그 440엔·OMAKASE 390엔·노쇼 취소료 (2026) | 트립픽",
        "dek": ("타베로그 다국어 예약은 1인 440엔, OMAKASE는 1좌석 390엔, TableCheck는 카드 등록이 기본입니다. "
                "당일·노쇼는 코스 값 100%가 흔합니다. 취소 규정, 전화 문장 6개, 예약 없이 먹는 법까지 정리했습니다."),
        "desc": ("일본 식당 예약(2026-11). 타베로그 1인 440엔(환불 없음), OMAKASE 1좌석 390엔, TableCheck 카드·선결제, "
                 "2일 전 30%·전날 50%·당일 100%, 오토오시 300~800엔, 전화 예약 일본어 문장, 발권기·기장표."),
        "keywords": ("일본 식당 예약, 타베로그 예약 수수료, OMAKASE 예약, TableCheck 예약, 일본 오마카세 예약, "
                     "일본 식당 노쇼, 일본 예약 취소료, 일본 전화 예약 일본어, 스시 예약, 일본 웨이팅, 오토오시"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/japan-restaurant-reservation-guide.jpg",
        "ogImage": "images/og/v64-restaurant-og.jpg",
        "imageAlt": "도쿄 스시집에서 초밥을 만드는 셰프",
        "imageCredit": "사진: Lawrence Lam / Pexels",
        "tours": [],
        "essentials": ["jp-esim-usimsa-kddi-1d", "cp-powerbank-spidy"],
        "related": ["tokyo-food-route", "osaka-food-route", "japan-convenience-store-must-buy",
                    "japan-ryokan-onsen-etiquette-budget", "nagoya-3n4d-course-budget", "tokyo-3n4d-course-budget"],
        "ctaTitle": "일본 미식 투어 비교",
        "ctaText": "예약이 어려운 집 대신 가이드 동반 미식 투어를 같은 기준으로 비교합니다.",
        "fxNote": "100엔 844.26원 · 2026-11-25 고시 기준",
        "read": 12,
        "faq": [
            ["타베로그 예약 수수료는 얼마인가요?",
             "다국어(한국어·영어) 예약은 확정과 동시에 1인 440엔이 결제되고, 취소해도 환불되지 않습니다. 4인이면 1,760엔입니다. 일본어 사이트 예약은 수수료가 없지만 일본어 화면과 일본 연락처가 필요합니다."],
            ["OMAKASE 예약은 어떻게 결제되나요?",
             "예약 시 1좌석 390엔의 예약 수수료가 붙고, 매장에 따라 코스 대금 전액을 미리 결제합니다. 선결제 금액은 원칙적으로 환불되지 않습니다. 예약 화면에서 '수수료만'인지 '코스 선결제 포함'인지 확인하세요."],
            ["노쇼하면 얼마가 청구되나요?",
             "매장 정책에 따르지만 코스 요리는 당일·노쇼 100%, 전날 50%, 2일 전 30%가 흔합니다. 좌석만 예약한 경우에도 당일 4,000엔, 전날 2,000엔 같은 정액 취소료를 받는 곳이 있습니다. 2인이면 두 배입니다."],
            ["일본어를 못 하는데 전화 예약할 수 있나요?",
             "준비된 문장 여섯 개면 됩니다. '予約をお願いしたいのですが(예약하고 싶습니다)', 날짜·시간·인원, 코스 유무, 알레르기, 이름과 +82 연락처, 취소 마감 확인 순서로 말하면 통합니다. 영업 전 오전이나 오후 2~5시가 연결이 잘 됩니다."],
            ["예약 없이 인기 식당에 갈 수 있나요?",
             "라멘·우동·돈카쓰는 대부분 예약을 받지 않고 발권기로 줄을 섭니다. 스시·야키토리는 문 앞 기장표에 이름을 적고 시간을 받는 방식이 많습니다. 저녁보다 점심이 대기 짧고 값도 30~50% 쌉니다."],
        ],
    },
    {
        "slug": "macau-1n2d-ferry-bus-guide",
        "category": "중국",
        "navTitle": "마카오 1박2일 — 페리 HK$194 vs 금바 HK$65",
        "h1": "마카오 1박2일, <em>페리 HK$194</em>와 <em>금바 HK$65</em> 사이",
        "seoTitle": "마카오 1박2일 코스·경비 — 홍콩 페리·금바 버스·무료 셔틀 (2026) | 트립픽",
        "dek": ("홍콩에서 마카오까지 터보젯 HK$194(60~70분), 금바 HK$65(35~40분). 마카오 버스 MOP6, LRT 6~12 MOP, "
                "호텔 무료 셔틀. 1박2일 코스와 2인 경비 15만~24만 원을 계산했습니다."),
        "desc": ("마카오 1박2일(2026-11). 터보젯 194/212/242HK$, 코타이워터젯 192/209/242HK$, 금바 65/70HK$ 24시간, "
                 "버스 MOP6·LRT 6~12MOP, 세나도·성바울·콜로안 코스, 에그타르트 MOP11~13, 2인 15만~24만 원."),
        "keywords": ("마카오 1박2일, 홍콩 마카오 페리, 터보젯 요금, 코타이워터젯, 금바 버스,강주아오 대교 셔틀, "
                     "마카오 버스 요금, 마카오 LRT, 마카오 무료 셔틀, 마카오 코스, 마카오 에그타르트, 세나도 광장"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/macau-1n2d-ferry-bus-guide.jpg",
        "ogImage": "images/og/v64-macau-og.jpg",
        "imageAlt": "마카오 세나도 광장의 물결 무늬 보도",
        "imageCredit": "사진: Guillaume Kremer / Pexels",
        "tours": [],
        "essentials": ["cp-passport-reindeer", "cp-powerbank-spidy"],
        "related": ["hongkong-macau-3n4d-course", "taiwan-hongkong-gift-list", "esim-roaming-insurance-guide",
                    "airport-arrival-city-transfer-guide", "travel-card-fees-comparison", "hotel-booking-timing-refund-tips"],
        "ctaTitle": "마카오 숙소·투어 비교",
        "ctaText": "날짜와 인원을 넣으면 타이파·코타이 숙소와 야경투어를 같은 기준으로 비교합니다.",
        "fxNote": "1홍콩달러 171.53원 · 2026-11-25 고시 기준(파타카 1:1)",
        "read": 11,
        "faq": [
            ["홍콩에서 마카오까지 얼마나 걸리나요?",
             "페리는 60~70분, 금바(대교 셔틀)는 35~40분입니다. 여기에 출입국 심사 20~30분이 각각 붙습니다. 금바는 홍콩 시내에서 홍콩항까지 가는 시간(30~60분)이 따로 필요합니다."],
            ["페리와 금바 중 무엇이 싼가요?",
             "금바가 HK$65로 페리 HK$194의 3분의 1입니다. 2인 왕복이면 페리 13만 3,105원, 금바 4만 4,597원으로 8만 8천 원 차이입니다. 다만 금바는 홍콩 시내→홍콩항 이동과 마카오 시내버스 환승이 붙습니다."],
            ["마카오 시내버스는 얼마인가요?",
             "현금 MOP6입니다. 잔돈을 주지 않으므로 동전을 준비하세요. 마카오패스를 사면 MOP3으로 절반이 되고 45분 내 환승이 무료·차액만 내면 됩니다. LRT는 역 수에 따라 MOP6·8·10·12입니다."],
            ["마카오 호텔 무료 셔틀은 어떻게 타나요?",
             "타이파 페리터미널·공항·국경 검문소에서 베네시안·파리지앵·갤럭시 등 리조트 셔틀이 무료로 다닙니다. 탑승 전에 호텔 이름과 노선을 확인하고, 코타이 리조트끼리는 걸어서 이동할 수 있습니다."],
            ["1박2일이면 어디를 봐야 하나요?",
             "첫날은 세나도 광장·성바울 성당·몬테 요새·아마 사원을 도는 반도 코스, 저녁에 코타이 야경을 봅니다. 둘째 날은 콜로안 빌리지에서 로드스토우 에그타르트를 먹고 타이파 빌리지를 거쳐 페리로 돌아오는 동선이 좋습니다."],
        ],
    },
    {
        "slug": "paris-metro-navigo-guide",
        "category": "유럽·장거리",
        "navTitle": "파리 교통권 2026 — 1회 €2.55·공항 €14·주간 €32.40",
        "h1": "파리 교통, <em>2026년엔 1회 €2.55</em> 하나만 기억하세요",
        "seoTitle": "파리 교통권 총정리 — 나비고 이지·주간권·공항 RER B·2026 요금 (2026) | 트립픽",
        "dek": ("2026년 1월부터 종이 티켓이 사라지고 지하철·RER 1회 €2.55, 공항 €14, 주간권 €32.40이 됐습니다. "
                "나비고 이지 €2, 일일권 €12.30, 파리 비지트 비교와 3박4일 2인 교통비 17만 6천 원을 정리했습니다."),
        "desc": ("파리 교통권(2026-11). 메트로 1회 €2.55·버스 €2.05·공항 €14·주르 €12.30·세멘 €32.40·비지트 30.60/63.80/78, "
                 "나비고 이지 €2, CDG RER B·오를리 14호선, 3박4일 최적 조합 €57.70, 2인 17만 6천 원."),
        "keywords": ("파리 교통권, 파리 지하철 요금, 나비고 이지, 나비고 주간권, 파리 비지트, "
                     "파리 공항 티켓 14유로, CDG RER B, 오를리 14호선, 파리 메트로 2.55유로, "
                     "파리 여행 교통, 파리 3박4일 경비"),
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "image": "images/v64/paris-metro-navigo-guide.jpg",
        "ogImage": "images/og/v64-paris-og.jpg",
        "imageAlt": "에펠탑과 파리 시내가 보이는 드론 항공샷",
        "imageCredit": "사진: Mo Eid / Pexels",
        "tours": [],
        "essentials": ["cp-adapter-nemotab", "cp-passport-reindeer"],
        "related": ["paris-london-5n7d", "europe-train-eurail-vs-point", "europe-pickpocket-tax-refund-guide",
                    "europe-shopping-tax-refund", "europe-ees-etias-guide", "hotel-booking-timing-refund-tips"],
        "ctaTitle": "파리 항공·숙소 비교",
        "ctaText": "날짜와 인원을 넣으면 CDG·오를리 항공과 파리 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "1유로 1,474.93원 · 2026-11-27 고시 기준",
        "read": 12,
        "faq": [
            ["파리 지하철 1회 요금은 얼마인가요?",
             "2026년 1월부터 거리와 상관없이 €2.55입니다. 공항만 빼고 일드프랑스 전역에 쓸 수 있고, 2시간 안에 지하철·RER·트레인 환승이 됩니다. 버스·트램은 €2.05로 별도입니다."],
            ["파리 공항에서 시내까지 얼마인가요?",
             "CDG는 RER B, 오를리는 14호선으로 공항 티켓 €14 하나면 됩니다. 일일권·주간권에는 공항이 포함되지 않으므로, 도착일과 출발일에는 공항 티켓을 따로 사야 합니다."],
            ["나비고 이지와 주간권 중 무엇이 좋나요?",
             "3박4일이면 나비고 이지(€2)에 일일권·1회권을 충전하는 쪽이 쌉니다. 주간권 €32.40은 월~일 고정이라 수요일에 도착하면 손해이고, 나비고 이지에는 주간권을 담을 수 없습니다. 주간권은 나비고 데쿠베르트(€5)나 스마트폰이 필요합니다."],
            ["파리 비지트는 사는 게 좋나요?",
             "3박4일 기준 파리 비지트 3일 €63.80은 공항 티켓 2장+일일권 2장+1회권 2장(€57.70)보다 6유로 이상 비쌉니다. 공항 포함·박물관 할인 같은 혜택이 필요할 때만 고르고, 보통은 일일권 조합이 낫습니다."],
            ["종이 티켓을 아직 쓸 수 있나요?",
             "2026년부터 종이 t+ 티켓과 10장 묶음은 판매하지 않습니다. 남은 종이 티켓은 2027년 1월 14일까지 나비고 이지로 교환할 수 있습니다(1일 5장 한도). 새로 사는 경우에는 나비고 이지나 스마트폰 앱을 쓰세요."],
        ],
    },
]

EXTRA = {
    "us-esta-application-guide": {
        "hub": None,
        "regions": ["long"],
        "tags": ["시즌·서류", "가성비"],
        "takeaway": "미국 ESTA는 공식 사이트에서 $40.62를 내고 2년 유효로 받습니다. 출발 72시간 전에 신청하고, 여권을 바꾸면 다시 받아야 합니다. 승인 전에는 탑승이 거절됩니다.",
        "facts": [["ESTA 수수료", "$40.62 · 2년 유효"], ["신청 시점", "출발 72시간 전 · 처리 최대 72시간"]],
    },
    "uk-eta-application-guide": {
        "hub": None,
        "regions": ["long"],
        "tags": ["시즌·서류", "가성비"],
        "takeaway": "영국 ETA는 £20으로 2년 유효, 1회 6개월 체류입니다. 한국은 2025년 1월 8일부터 대상이고, 공항에서 입국 심사를 통과하는 landside 환승이면 ETA가 필요합니다.",
        "facts": [["영국 ETA", "£20 · 2년 · 1회 6개월"], ["처리", "1일 이내 · 최대 3영업일"]],
    },
    "kansai-airport-osaka-kyoto-transfer": {
        "hub": "osaka",
        "regions": ["jp"],
        "tags": ["교통패스", "가성비"],
        "stayRegions": ["osaka"],
        "takeaway": "간사이공항에서 난바는 공항급행 970엔, 우메다는 JR 1,210엔, 교토는 하루카 할인권 2,700엔이 기준입니다. 23시 이후 도착이면 공항급행 막차 23:55 아니면 택시뿐입니다.",
        "facts": [["난바 공항급행", "970엔 · 43~45분 · 막차 23:55"], ["교토 하루카", "2,700엔 · 약 80분"]],
    },
    "new-york-4n5d-course-budget": {
        "hub": None,
        "regions": ["long"],
        "tags": ["숙소", "가성비"],
        "takeaway": "뉴욕 4박5일은 JFK AirTrain+지하철 $11.75, 지하철 7일 상한 $35, 유료 전망대 한 곳이면 2인 현지 경비 173만 원입니다. 숙소를 다운타운에 잡으면 미드타운보다 400만 원 가까이 줄어듭니다.",
        "facts": [["JFK→맨해튼", "$11.75 · 60~75분"], ["지하철 7일 상한", "$35 · 12회부터 무료"]],
    },
    "nagoya-3n4d-course-budget": {
        "hub": None,
        "regions": ["jp"],
        "tags": ["숙소", "가성비"],
        "takeaway": "나고야 3박4일은 지브리파크(스탠더드 3,300엔)와 시라카와고 당일치기(왕복 3,600~4,700엔)를 넣고, 센트레아는 뮤스카이 1,430엔으로 들어오면 2인 현지 경비 58만 원입니다.",
        "facts": [["지브리파크", "3,300엔(평일) · 2개월 전 예약"], ["센트레아→나고야", "뮤스카이 1,430엔 · 28분"]],
    },
    "japan-restaurant-reservation-guide": {
        "hub": None,
        "regions": ["jp"],
        "tags": ["맛집", "시즌·서류"],
        "takeaway": "일본 온라인 예약은 타베로그 1인 440엔, OMAKASE 1좌석 390엔이 붙고 환불되지 않습니다. 당일·노쇼는 코스 값 100%가 흔하니, 취소 정책을 스크린샷으로 남기고 일정이 확정된 뒤 예약하세요.",
        "facts": [["타베로그 수수료", "1인 440엔 · 환불 없음"], ["당일·노쇼", "코스 값 100%"]],
    },
    "macau-1n2d-ferry-bus-guide": {
        "hub": "macau",
        "regions": ["cn"],
        "tags": ["교통패스", "가성비"],
        "stayRegions": ["macau"],
        "takeaway": "홍콩→마카오는 페리 HK$194(60~70분)와 금바 HK$65(35~40분)로 갈립니다. 2인 왕복 차이가 8만 8천 원이라, 홍콩섬 출발이면 페리, 공항·란타우 출발이면 금바가 맞습니다.",
        "facts": [["터보젯", "HK$194 · 60~70분"], ["금바", "HK$65 · 35~40분"]],
    },
    "paris-metro-navigo-guide": {
        "hub": "paris",
        "regions": ["long"],
        "tags": ["교통패스", "가성비"],
        "stayRegions": ["paris"],
        "takeaway": "2026년 파리는 지하철 1회 €2.55, 공항 €14, 일일권 €12.30입니다. 3박4일이면 공항 2장+일일권 2장+1회권 2장(€57.70)이 파리 비지트 3일(€63.80)보다 쌉니다.",
        "facts": [["메트로 1회", "€2.55 · 공항 제외 전 지역"], ["공항 티켓", "€14 · CDG RER B·오를리 14호선"]],
    },
}


HUB_ADD = {
    "osaka": ["kansai-airport-osaka-kyoto-transfer"],
    "macau": ["macau-1n2d-ferry-bus-guide"],
    "paris": ["paris-metro-navigo-guide"],
}

REVERSE = {
    "entry-immigration-guide": ["us-esta-application-guide", "uk-eta-application-guide"],
    "passport-application-guide": ["us-esta-application-guide", "uk-eta-application-guide"],
    "us-east-canada-10d": ["new-york-4n5d-course-budget"],
    "osaka-usj-transfer": ["kansai-airport-osaka-kyoto-transfer"],
    "airport-arrival-city-transfer-guide": ["kansai-airport-osaka-kyoto-transfer", "macau-1n2d-ferry-bus-guide"],
    "hongkong-macau-3n4d-course": ["macau-1n2d-ferry-bus-guide"],
    "paris-london-5n7d": ["paris-metro-navigo-guide", "uk-eta-application-guide"],
    "europe-ees-etias-guide": ["uk-eta-application-guide"],
    "tokyo-food-route": ["japan-restaurant-reservation-guide"],
    "osaka-food-route": ["japan-restaurant-reservation-guide"],
    "tokyo-3n4d-course-budget": ["nagoya-3n4d-course-budget", "japan-restaurant-reservation-guide"],
    "osaka-kyoto-3n4d": ["kansai-airport-osaka-kyoto-transfer", "nagoya-3n4d-course-budget"],
    "japan-ic-card": ["kansai-airport-osaka-kyoto-transfer", "paris-metro-navigo-guide"],
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

    for src, dsts in REVERSE.items():
        row = next((x for x in g["guides"] if x["slug"] == src), None)
        if not row:
            print("  ! 없는 가이드", src)
            continue
        rel = row.setdefault("related", [])
        for dst in dsts:
            if dst not in rel:
                rel.append(dst)
    save("guides.json", g)

    hubs = load("city_hubs.json")
    HUB_DROP = {"osaka": ["japan-souvenir-list"]}
    for city in hubs["cities"]:
        for slug in HUB_DROP.get(city["slug"], []):
            if slug in city.get("guides", []):
                city["guides"].remove(slug)
        for slug in HUB_ADD.get(city["slug"], []):
            gl = city.setdefault("guides", [])
            if slug not in gl:
                gl.insert(0, slug)
    save("city_hubs.json", hubs)
    print(f"city_hubs +{sum(len(v) for v in HUB_ADD.values())} 연결")

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
