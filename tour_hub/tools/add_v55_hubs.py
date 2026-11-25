#!/usr/bin/env python3
"""v55: 미개설 9개 도시 허브(괌·사이판·싱가포르·홍콩·마카오·파리·런던·로마·바르셀로나)를 city_hubs.json 에 넣는다.

    python3 tools/add_v55_hubs.py

숫자는 모두 저장소 데이터에서 확인한 값이다.
- 숙소 1박·2인·세금 포함 최저가: data/stays.json (2026-11 트립닷컴 조회)
- 투어·패키지: data/tours.json 표시가(1인)
- 교통·패스: data/passes.json (싱가포르 SimplyGo·Tourist Pass, 홍콩 MTR 공항철도)
- 입국서류·수수료: data/checklist.json (ESTA 40.62달러, 영국 ETA £20)
- 시즌: data/season.json, 환율: data/fx.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "city_hubs.json"

GENERIC = [
    "overseas-roaming-esim-install-troubleshooting",
    "airport-arrival-city-transfer-guide",
    "travel-card-fees-comparison",
]

HUBS = [
    {
        "slug": "guam",
        "name": "괌",
        "nav": "괌",
        "cityIds": ["guam"],
        "country": "us",
        "flag": "gu",
        "kicker": "GUAM",
        "seoTitle": "괌 여행 숙소·에어텔·eSIM·4박5일 코스 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "괌 숙소 3곳 1박 12만 5,474원~47만 5,553원(2인), 4박5일 에어텔 58만 1,030원부터. 투몬·공항 10~15분, eSIM 1일 1,050원부터.",
        "keywords": "괌 여행, 괌 숙소, 괌 리조트, 괌 4박5일, 괌 에어텔, 투몬 베이, 괌 eSIM, 괌 렌터카, 괌 vs 사이판",
        "h1": "괌 여행, <em>숙소·에어텔·eSIM</em>을 한 페이지에",
        "intro": "괌은 투몬 베이 한 축에 리조트·쇼핑·식당이 몰려 있어 공항에서 차로 10~15분이면 숙소에 닿습니다. 4박5일 에어텔은 리가로얄 오션뷰 58만 1,030원(인천 출발), PIC 골드패스 79만 2,490원(부산 출발), 두짓타니 오션프론트 94만 9,630원이고, 숙소만 잡으면 1박·2인 기준 12만 5,474원(괌 플라자)부터 47만 5,553원(더 츠바키 타워)까지입니다. 남부 드라이브는 렌터카가 있어야 하고, eSIM은 1일 1,050원부터라 5일이면 5,250원입니다. 아래에서 숙소 가격, 4박5일 동선, 괌·사이판 비교 순서로 확인하세요.",
        "giftFallback": "괌의 선물·기념품은 매장별 가격 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 미리 사 두면 현지에서 사기 번거로운 준비물만 모았습니다.",
        "foodFallback": "괌 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 하루 동선은 아래 4박5일 코스 가이드에 숫자로 계산해 두었습니다.",
        "hotels": ["guam"],
        "image": "images/v55/guam.jpg",
        "imageAlt": "괌 투몬 만의 리조트와 바다",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-guam-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "공항 → 투몬", "v": "차로 10~15분. 도착일 이동이 짧아 첫날 오후 일정을 살릴 수 있습니다."},
            {"k": "숙소 1박(2인)", "v": "괌 플라자 12만 5,474원 · 두짓타니 31만 4,743원 · 더 츠바키 타워 47만 5,553원"},
            {"k": "입국 서류", "v": "ESTA 40.62달러(54,230원). 출발 72시간 전까지 신청, 승인 후 2년 유효"},
            {"k": "eSIM", "v": "괌·사이판 공용 1일 1,050원부터. 4박5일이면 5일권 한 장"},
        ],
        "guides": ["guam-4n5d-course", "guam-resorts", "guam-vs-saipan-comparison",
                   "overseas-roaming-esim-install-troubleshooting", "airport-arrival-city-transfer-guide",
                   "travel-card-fees-comparison", "travel-insurance-guide", "incheon-airport-smartpass-lounge"],
    },
    {
        "slug": "saipan",
        "name": "사이판",
        "nav": "사이판",
        "cityIds": ["saipan"],
        "country": "us",
        "flag": "gu",
        "kicker": "SAIPAN",
        "seoTitle": "사이판 여행 숙소·리조트·eSIM·렌터카 준비 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "사이판 숙소 3곳 1박 14만 1,439원~24만 293원(2인). 가라판·북부 차로 20~40분, 단독 투어 없음, eSIM 1일 1,050원부터.",
        "keywords": "사이판 여행, 사이판 숙소, 사이판 리조트, 코럴 오션 리조트, PIC 사이판, 가라판, 마나가하, 그로토, 사이판 eSIM",
        "h1": "사이판 여행, <em>숙소·렌터카·액티비티</em>를 한 페이지에",
        "intro": "사이판은 가라판 중심과 마나가하·그로토 쪽 북부가 차로 20~40분 떨어져 있어, 어디에 묵느냐가 하루 동선을 정합니다. 숙소는 1박·2인 기준 코럴 오션 리조트 14만 1,439원, 퍼시픽 아일랜드 클럽 16만 1,369원, 크라운 플라자 24만 293원이고, 지금은 단독 투어·패키지 상품이 없어 항공·숙소를 따로 잡고 렌터카와 현지 액티비티로 채우는 여행입니다. eSIM은 괌과 같은 상품으로 1일 1,050원부터이고 4박5일이면 5,250원입니다. 괌과의 2인 경비·비행시간 차이는 비교 가이드에 숫자로 정리했습니다.",
        "giftFallback": "사이판의 선물·기념품은 매장별 가격 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 미리 사 두면 현지에서 사기 번거로운 준비물만 모았습니다.",
        "foodFallback": "사이판 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 괌·사이판 비교 가이드에서 볼 수 있습니다.",
        "tourNote": "사이판은 지금 판매 중인 단독 투어·패키지 상품이 없습니다. 항공·숙소를 따로 잡고 마나가하·그로토·만세비치 쪽 액티비티를 현지에서 붙이는 방식이 기본이고, 렌터카가 있으면 북부 동선이 하루로 줄어듭니다.",
        "hotels": [],
        "image": "images/v55/saipan.jpg",
        "imageAlt": "사이판 산호초에서 만난 바다거북과 다이버",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-saipan-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "가라판 ↔ 북부", "v": "차로 20~40분. 리조트에서 쉬는 여행이면 가라판, 섬과 자연이 목적이면 북부 동선을 먼저 보세요."},
            {"k": "숙소 1박(2인)", "v": "코럴 오션 14만 1,439원 · PIC 16만 1,369원 · 크라운 플라자 24만 293원"},
            {"k": "입국 서류", "v": "ESTA 40.62달러(54,230원). 출발 72시간 전까지 신청"},
            {"k": "eSIM", "v": "괌·사이판 공용 1일 1,050원부터. 4박5일이면 5일권 한 장"},
        ],
        "guides": ["guam-vs-saipan-comparison", "guam-4n5d-course",
                   "overseas-roaming-esim-install-troubleshooting", "airport-arrival-city-transfer-guide",
                   "travel-card-fees-comparison", "travel-insurance-guide", "hotel-booking-timing-refund-tips"],
    },
    {
        "slug": "singapore",
        "name": "싱가포르",
        "nav": "싱가포르",
        "cityIds": ["singapore"],
        "country": "sg",
        "flag": "sg",
        "kicker": "SINGAPORE",
        "seoTitle": "싱가포르 여행 투어·입장권·숙소·교통패스 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "싱가포르 투어·입장권 5개 3만 5,815원부터, 숙소 4곳 1박 12만 8,557원~38만 6,190원(2인), MRT 1.28~2.57싱가포르달러.",
        "keywords": "싱가포르 여행, 싱가포르 3박4일, 마리나 베이, 가든스 바이 더 베이, 유니버설 스튜디오 싱가포르, 싱가포르 숙소, 싱가포르 교통카드, 투어리스트 패스, 싱가포르 eSIM",
        "h1": "싱가포르 여행, <em>투어·입장권·숙소·교통</em>을 한 페이지에",
        "intro": "싱가포르는 마리나 베이·시청이 관광 동선, 벤쿨렌·부기스가 가성비, 센토사가 유니버설과 비치 축이라 3박이면 두 지역을 나눠 잡아야 이동이 짧습니다. 숙소는 1박·2인 기준 호텔 미 로처 12만 8,557원, 칼튼 24만 4,375원, 센토사 빌리지 25만 5,040원, 스위소텔 더 스탬퍼드 38만 6,190원이고, 투어·입장권은 가든스 바이 더 베이 3만 5,815원부터 유니버설 스튜디오 7만 552원까지 5개입니다. 교통은 해외 카드 컨택트리스에 하루 0.60싱가포르달러 수수료가 붙고 MRT·버스가 1.28~2.57싱가포르달러, 관광객용 투어리스트 패스는 1일 17·2일 24·3일 29싱가포르달러입니다. 3박4일 2인 실경비는 아래 가이드에 계산해 두었습니다.",
        "giftFallback": "싱가포르 선물·기념품 가격표는 공식 판매처 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 사 두면 좋은 준비물만 모았습니다.",
        "foodFallback": "싱가포르 맛집은 호커센터 점포별 영업 여부를 확인한 뒤 싣습니다. 그전까지 식비와 하루 동선은 아래 3박4일 가이드에 숫자로 계산해 두었습니다.",
        "hotels": ["singapore"],
        "image": "images/v55/singapore.jpg",
        "imageAlt": "마리나 베이 샌즈와 싱가포르 스카이라인",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-singapore-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "창이 → 시청", "v": "MRT 약 18km 2.20싱가포르달러. 컨택트리스 카드는 쓰는 날마다 0.60싱가포르달러 수수료"},
            {"k": "관광객 패스", "v": "Singapore Tourist Pass 1일 17 · 2일 24 · 3일 29싱가포르달러(MRT·버스 무제한)"},
            {"k": "숙소 1박(2인)", "v": "호텔 미 로처 12만 8,557원 · 칼튼 24만 4,375원 · 스위소텔 스탬퍼드 38만 6,190원"},
            {"k": "eSIM", "v": "1일 500MB 109원부터 · 리뷰 5,512개·4.6점"},
        ],
        "guides": ["singapore-3n4d-course-budget", "southeast-asia-gift-list", "sea-grab-taxi-scam-guide",
                   "airport-arrival-city-transfer-guide", "overseas-roaming-esim-install-troubleshooting",
                   "travel-card-fees-comparison", "travel-insurance-guide", "hotel-booking-timing-refund-tips"],
    },
    {
        "slug": "hongkong",
        "name": "홍콩",
        "nav": "홍콩",
        "cityIds": ["hongkong"],
        "country": "hk",
        "flag": "hk",
        "kicker": "HONG KONG",
        "seoTitle": "홍콩 여행 숙소·공항철도·야경투어·3박4일 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "홍콩 숙소 4곳 1박 8만 2,636원~21만 8,841원(2인), 공항철도 24분·옥토퍼스 120홍콩달러, 피크 야경투어 10만 2,596원.",
        "keywords": "홍콩 여행, 홍콩 3박4일, 침사추이 숙소, 코즈웨이베이, 빅토리아 피크, 홍콩 공항철도, 옥토퍼스, 홍콩 마카오, 홍콩 야경",
        "h1": "홍콩 여행, <em>숙소·공항철도·야경</em>을 한 페이지에",
        "intro": "홍콩은 침사추이(구룡)와 코즈웨이베이(홍콩섬) 두 축으로 갈립니다. 야경·쇼핑은 침사추이, 식당·카페는 코즈웨이베이·센트럴이 편하고, 공항에서는 에어포트익스프레스로 홍콩역까지 24분·옥토퍼스 120홍콩달러입니다. 숙소는 1박·2인 기준 로그 인 8만 2,636원, 엠파이어 코즈웨이 베이 16만 412원, 엠파이어 침사추이 18만 2,285원, 더 카오룽 21만 8,841원이고, 빅토리아 피크 야경투어는 1인 10만 2,596원입니다. 11월은 22.2도·비 5.7일로 12개월 중 쾌적도가 가장 높은 달(94점)이라 지금이 걷기 좋습니다.",
        "giftFallback": "홍콩 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 사 두면 좋은 준비물만 모았습니다.",
        "foodFallback": "홍콩 맛집은 점포별 영업 여부와 차지(茶餐廳) 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 3박4일 가이드에 있습니다.",
        "hotels": [],
        "image": "images/v55/hongkong.jpg",
        "imageAlt": "빅토리아 하버에서 본 홍콩 스카이라인",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-hongkong-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "공항 → 홍콩역", "v": "에어포트익스프레스 24분 · 옥토퍼스 120홍콩달러(스마트 티켓 130 · 왕복 215)"},
            {"k": "공항 버스", "v": "A21 34.6 · A11 41.9홍콩달러. 택시는 침사추이 290·센트럴 375홍콩달러 어림값"},
            {"k": "숙소 1박(2인)", "v": "로그 인 8만 2,636원 · 엠파이어 침사추이 18만 2,285원 · 더 카오룽 21만 8,841원"},
            {"k": "11월 날씨", "v": "22.2도 · 비 5.7일 · 쾌적도 94점(연중 최고). 12월 중순부터 숙소가 크게 오릅니다"},
        ],
        "guides": ["hongkong-macau-3n4d-course", "taiwan-hongkong-gift-list",
                   "airport-arrival-city-transfer-guide", "currency-payment-fees",
                   "travel-card-fees-comparison", "hotel-booking-timing-refund-tips"],
    },
    {
        "slug": "macau",
        "name": "마카오",
        "nav": "마카오",
        "cityIds": ["macau"],
        "country": "mo",
        "flag": "cn",
        "kicker": "MACAU",
        "seoTitle": "마카오 여행 숙소·코타이 리조트·홍콩 당일치기 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "마카오 숙소 4곳 1박 11만 4,522원~27만 214원(2인). 코타이 야경과 반도 먹거리, 시내버스 6파타카(약 1,050원)·홍콩 페리 194홍콩달러.",
        "keywords": "마카오 여행, 마카오 숙소, 코타이, 파리지앵 마카오, 세나도 광장, 마카오 홍콩, 마카오 버스, 마카오 당일치기",
        "h1": "마카오 여행, <em>숙소·코타이·홍콩 동선</em>을 한 페이지에",
        "intro": "마카오는 코타이(베네시안·파리지앵)와 마카오 반도(세나도 광장·성바울)가 성격이 다릅니다. 1박이면 야경을 볼 코타이, 걷고 먹을 반도 쪽으로 갈리고, 홍콩에서 페리 194홍콩달러나 대교 셔틀 65홍콩달러로 건너와 하루를 쓰는 일정이 가장 흔합니다. 숙소는 1박·2인 기준 소피텔 앳 폰테 16 11만 4,522원, 호텔 센트럴 14만 3,892원, 스튜디오 시티 21만 9,213원, 파리지앵 마카오 27만 214원입니다. 시내버스는 거리와 상관없이 현금 6파타카(약 1,050원)·마카오패스 3파타카이고, 공항철도와 대교 셔틀까지 묶은 3박4일 동선은 아래 가이드에 있습니다.",
        "giftFallback": "마카오 선물·기념품(아몬드 쿠키 등) 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 사 두면 좋은 준비물만 모았습니다.",
        "foodFallback": "마카오 맛집은 포장이사(葡撻)·차지 가격을 매장별로 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 홍콩·마카오 3박4일 가이드에 있습니다.",
        "tourNote": "마카오는 단독 투어·패키지 상품이 없습니다. 홍콩에서 페리(194홍콩달러)나 대교 셔틀(65홍콩달러)로 건너와 하루를 쓰거나, 코타이 리조트에 1박을 붙이는 방식이 기본입니다.",
        "hotels": [],
        "image": "images/v55/macau.jpg",
        "imageAlt": "마카오 세나도 광장의 물결 무늬 보도",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-macau-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "홍콩 → 마카오", "v": "페리 194홍콩달러 · 대교 셔틀 65홍콩달러. 입국심사 포함 2시간 30분을 잡으세요"},
            {"k": "시내버스", "v": "거리와 상관없이 현금 6파타카(약 1,050원) · 마카오패스 3파타카"},
            {"k": "숙소 1박(2인)", "v": "소피텔 폰테 16 11만 4,522원 · 호텔 센트럴 14만 3,892원 · 파리지앵 27만 214원"},
            {"k": "경전철", "v": "LRT 6·8·10·12파타카(역 수 기준), 카드 결제는 절반"},
        ],
        "guides": ["hongkong-macau-3n4d-course", "taiwan-hongkong-gift-list",
                   "currency-payment-fees", "travel-card-fees-comparison",
                   "airport-arrival-city-transfer-guide", "hotel-booking-timing-refund-tips"],
    },
    {
        "slug": "paris",
        "name": "파리",
        "nav": "파리",
        "cityIds": ["paris", "eu_west"],
        "country": "fr",
        "flag": "fr",
        "kicker": "PARIS",
        "seoTitle": "파리 여행 투어·숙소·택스리펀·런던 연결 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "파리 숙소 3곳 1박 19만 7,653원~33만 2,946원(2인), 루브르 9만 4,019원·센강 유람선 1만 6,429원. 직항 14시간 30분, 택스리펀 100유로부터.",
        "keywords": "파리 여행, 파리 숙소, 루브르 박물관, 센강 유람선, 몽생미셸 투어, 파리 택스리펀, 파리 런던 유로스타, 파리 3박",
        "h1": "파리 여행, <em>투어·숙소·택스리펀</em>을 한 페이지에",
        "intro": "파리는 에펠탑·몽파르나스와 샹젤리제·에투알 두 축으로 숙소를 잡고 루브르·마레는 지하철로 오갑니다. 인천에서 샤를드골까지 직항 14시간 30분이라 첫날은 이동으로 끝나므로 3박 이상이 기본입니다. 숙소는 1박·2인 기준 에펠 빌라 가리발디 19만 7,653원, 퍼스트 호텔 파리 투어 에펠 22만 5,239원, 오텔 레장스 에투알 33만 2,946원이고, 루브르 가이드투어 9만 4,019원·센강 유람선 1만 6,429원·몽생미셸 당일치기 20만 9,237원입니다. 택스리펀은 프랑스 100유로부터이고, 유로스타로 런던까지 2시간 16분이면 붙일 수 있습니다.",
        "hotels": ["paris"],
        "flight": "파리",
        "image": "images/v55/paris.jpg",
        "imageAlt": "에펠탑과 파리 시내가 보이는 드론 항공샷",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-paris-og.jpg",
        "stayCards": True,
        "giftCountry": "eu",
        "foodFallback": "파리 맛집은 브라스리 영업 여부와 메뉴 가격을 확인한 뒤 싣습니다. 그전까지 식비와 하루 동선은 아래 5박7일 가이드에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "항공", "v": "인천 → 샤를드골(CDG) 직항 14시간 30분"},
            {"k": "숙소 1박(2인)", "v": "에펠 빌라 19만 7,653원 · 퍼스트 호텔 에펠 22만 5,239원 · 레장스 에투알 33만 2,946원"},
            {"k": "택스리펀", "v": "프랑스 100유로부터. 실환급률은 수수료를 빼고 10~15%"},
            {"k": "런던 연결", "v": "유로스타 2시간 16분(£39~). 5박7일 두 도시 일정은 아래 가이드"},
        ],
        "guides": ["paris-london-5n7d", "europe-shopping-tax-refund", "europe-pickpocket-tax-refund-guide",
                   "europe-ees-etias-guide", "europe-train-eurail-vs-point", "solo-vs-couple-travel-budget",
                   "travel-card-fees-comparison", "overseas-roaming-esim-install-troubleshooting"],
    },
    {
        "slug": "london",
        "name": "런던",
        "nav": "런던",
        "cityIds": ["london"],
        "country": "gb",
        "flag": "gb",
        "kicker": "LONDON",
        "seoTitle": "런던 여행 숙소·히드로 공항·당일투어·영국 ETA 총정리 (2026년 11월)",
        "metaDesc": "런던 숙소 3곳 1박 37만 1,537원~47만 9,398원(2인), 히드로 직항 14시간 40분, 코츠월즈 당일투어 13만 8,704원, 영국 ETA £20.",
        "keywords": "런던 여행, 런던 숙소, 패딩턴 호텔, 히드로 익스프레스, 코츠월즈 투어, 영국 ETA, 런던 파리, 런던 3박",
        "h1": "런던 여행, <em>숙소·공항 이동·당일투어</em>를 한 페이지에",
        "intro": "런던은 블룸즈버리(대영박물관)·켄싱턴·패딩턴 세 구역으로 숙소가 갈리고, 패딩턴은 히드로 익스프레스 종점이라 귀국일이 편합니다. 인천에서 히드로까지 직항 14시간 40분이고, 숙소는 1박·2인 기준 힐튼 런던 켄싱턴 37만 1,537원, 힐튼 런던 메트로폴 47만 3,249원, 로열 내셔널 47만 9,398원입니다. 투어는 런던 출발 코츠월즈·옥스퍼드 당일투어 13만 8,704원 한 건이라 나머지 일정은 박물관·공원·마켓 쪽으로 직접 짜게 됩니다. 영국은 유럽연합이 아니라 입국과 환급 규정이 따로이니, ETA £20(약 35,000원)은 출발 2주 전에 준비하세요.",
        "hotels": ["london"],
        "flight": "런던",
        "image": "images/v55/london.jpg",
        "imageAlt": "템스강 위 런던 타워 브리지",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-london-og.jpg",
        "stayCards": True,
        "giftFallback": "런던은 유럽연합 밖이라 EU 공통 택스리펀·면세 기준을 그대로 쓸 수 없습니다. 영국 환급 기준을 확인해 다음 업데이트에 싣고, 그전까지는 출발 전 준비물만 모았습니다.",
        "foodFallback": "런던 맛집은 펍·마켓 점포별 영업 여부와 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 5박7일 가이드에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "항공", "v": "인천 → 히드로(LHR) 직항 14시간 40분"},
            {"k": "공항 → 패딩턴", "v": "히드로 익스프레스 종점. 패딩턴에 잡으면 귀국일이 편합니다"},
            {"k": "숙소 1박(2인)", "v": "힐튼 켄싱턴 37만 1,537원 · 힐튼 메트로폴 47만 3,249원 · 로열 내셔널 47만 9,398원"},
            {"k": "입국 서류", "v": "영국 ETA £20(약 35,000원) · 출발 2주 전 · 2년 유효. 환승이라도 영국 입국심사를 거치면 필요"},
        ],
        "guides": ["paris-london-5n7d", "europe-pickpocket-tax-refund-guide", "entry-immigration-guide",
                   "travel-card-fees-comparison", "currency-payment-fees", "solo-vs-couple-travel-budget",
                   "airport-arrival-city-transfer-guide"],
    },
    {
        "slug": "rome",
        "name": "로마",
        "nav": "로마",
        "cityIds": ["rome", "italy"],
        "country": "it",
        "flag": "it",
        "kicker": "ROME",
        "seoTitle": "로마 여행 투어·숙소·이탈리아 9일 패키지 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "로마 투어 3개 6만 9,154원부터, 숙소 2곳 1박 21만 2,872원~36만 2,252원(2인), 이탈리아 9일 패키지 270만 8,240원부터.",
        "keywords": "로마 여행, 로마 숙소, 테르미니 호텔, 콜로세움 투어, 바티칸 미술관, 이탈리아 9일, 피렌체 열차, 로마 택스리펀",
        "h1": "로마 여행, <em>투어·숙소·이탈리아 일주</em>를 한 페이지에",
        "intro": "로마는 테르미니 역 반경 500m에 4성이 몰려 있고, 피렌체·베네치아로 넘어가는 열차가 모두 테르미니에서 출발합니다. 인천에서 피우미치노까지 직항 13시간 30분이고, 숙소는 1박·2인 기준 UNA 호텔 데코 로마 21만 2,872원, iQ 호텔 로마 36만 2,252원입니다. 당일 투어는 콜로세움·포로 로마노·팔라티노 가이드 6만 9,154원, 바티칸 미술관 가이드 10만 1,523원, 소규모 바티칸 18만 9,804원이고, 이탈리아 일주는 9일 패키지가 270만 8,240원부터입니다. 피렌체는 97분, 베네치아는 134분이라 로마를 거점으로 6박8일을 짜는 조합이 가장 많습니다.",
        "hotels": ["rome"],
        "flight": "로마",
        "image": "images/v55/rome.jpg",
        "imageAlt": "로마 콜로세움",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-rome-og.jpg",
        "stayCards": True,
        "giftCountry": "eu",
        "foodFallback": "로마 맛집은 트라토리아 영업 여부와 코페르토(자릿세) 조건을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 이탈리아 6박8일 가이드에 있습니다.",
        "tips": [
            {"k": "항공", "v": "인천 → 피우미치노(FCO) 직항 13시간 30분"},
            {"k": "열차", "v": "테르미니 출발 — 피렌체 97분 · 베네치아 134분"},
            {"k": "숙소 1박(2인)", "v": "UNA 호텔 데코 21만 2,872원 · iQ 호텔 로마 36만 2,252원(테르미니 반경 500m)"},
            {"k": "택스리펀", "v": "이탈리아 70유로부터 · 실환급률 10~15%(수수료 차감 후)"},
        ],
        "guides": ["italy-rome-florence-venice", "italy-9d-packages", "europe-shopping-tax-refund",
                   "europe-pickpocket-tax-refund-guide", "europe-ees-etias-guide", "europe-train-eurail-vs-point",
                   "travel-insurance-guide", "solo-vs-couple-travel-budget"],
    },
    {
        "slug": "barcelona",
        "name": "바르셀로나",
        "nav": "바르셀로나",
        "cityIds": ["barcelona", "eu_iberia"],
        "country": "es",
        "flag": "es",
        "kicker": "BARCELONA",
        "seoTitle": "바르셀로나 여행 사그라다 파밀리아·숙소·스페인 일주 총정리 (2026년 11월)",
        "metaDesc": "바르셀로나 숙소 2곳 1박 18만 4,212원~21만 3,603원(2인), 사그라다 파밀리아 7만 9,453원, 스페인·포르투갈 9일 280만 5,240원부터.",
        "keywords": "바르셀로나 여행, 사그라다 파밀리아, 가우디, 바르셀로나 숙소, 산츠역, 스페인 9일, 마드리드 열차, 스페인 택스리펀",
        "h1": "바르셀로나 여행, <em>가우디·숙소·스페인 일주</em>를 한 페이지에",
        "intro": "바르셀로나는 산츠 역(마드리드행 출발)과 그라시아 거리(가우디 3곳) 중 어디에 묵느냐로 동선이 갈립니다. 엘프라트 공항버스는 카탈루냐 광장에 내리고, 인천에서는 직항이 없어 경유 16시간부터입니다. 숙소는 1박·2인 기준 바르셀로 산츠 18만 4,212원, 베스트 웨스턴 프리미어 단테 21만 3,603원이고, 사그라다 파밀리아 빠른 입장 가이드투어가 7만 9,453원, 스페인·포르투갈 9일 패키지가 280만 5,240원부터입니다. 마드리드는 3시간 28분이고, 스페인 택스리펀은 최소 금액이 0원이라 소액 구매도 환급 대상입니다.",
        "hotels": ["barcelona"],
        "flight": "바르셀로나",
        "image": "images/v55/barcelona.jpg",
        "imageAlt": "바르셀로나 사그라다 파밀리아 성당",
        "imageCredit": "사진: Pexels",
        "ogImage": "images/og/v55-barcelona-og.jpg",
        "stayCards": True,
        "giftCountry": "eu",
        "foodFallback": "바르셀로나 맛집은 타파스 바 영업 여부와 메뉴 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 스페인 5박7일 가이드에 있습니다.",
        "tips": [
            {"k": "항공", "v": "인천 → 엘프라트(BCN) 직항 없음 · 경유 16시간부터"},
            {"k": "공항버스", "v": "엘프라트 → 카탈루냐 광장. 시내 숙소를 광장 축에 잡으면 이동이 짧습니다"},
            {"k": "숙소 1박(2인)", "v": "바르셀로 산츠 18만 4,212원 · 단테 21만 3,603원"},
            {"k": "택스리펀", "v": "스페인 최소 금액 0원 — 소액 구매도 환급 대상"},
        ],
        "guides": ["spain-barcelona-madrid", "spain-portugal-9-vs-11", "europe-shopping-tax-refund",
                   "europe-pickpocket-tax-refund-guide", "europe-ees-etias-guide", "solo-vs-couple-travel-budget",
                   "currency-payment-fees", "travel-insurance-guide"],
    },
]


def main() -> None:
    spec = json.loads(PATH.read_text(encoding="utf-8"))
    have = {c["slug"] for c in spec["cities"]}
    guides = {g["slug"] for g in json.loads((ROOT / "data" / "guides.json").read_text(encoding="utf-8"))["guides"]}
    added = 0
    for hub in HUBS:
        t, d = hub["seoTitle"], hub["metaDesc"]
        assert len(t) <= 60, (hub["slug"], "title", len(t), t)
        assert len(d) <= 155, (hub["slug"], "desc", len(d), d)
        for g in hub["guides"]:
            assert g in guides, (hub["slug"], "missing guide", g)
        assert (ROOT / hub["image"]).exists(), hub["image"]
        assert (ROOT / hub["ogImage"]).exists(), hub["ogImage"]
        if hub["slug"] in have:
            spec["cities"] = [hub if c["slug"] == hub["slug"] else c for c in spec["cities"]]
            continue
        spec["cities"].append(hub)
        added += 1
    PATH.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"hubs added {added} / total {len(spec['cities'])}")


if __name__ == "__main__":
    main()
