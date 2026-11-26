#!/usr/bin/env python3
"""v59: 도시 허브 3곳(치앙마이·발리·상하이) + 찐숙소 15곳.

    python3 tools/add_v59_hubs.py

숙소 값은 2026-11-26 트립닷컴 숙소 목록(2026-12-10~11 · 성인 2명 · 세금 포함 최저가)에서,
성급·존·공항/역 거리는 같은 호텔 상세 페이지에서 확인한 값이다. 이미지는 상세 페이지 대표 이미지.
도시 기본정보(공항 요금·입장료)는 data/guides.json·tripcom.json·checklist.json 의 2026-11 확인값.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"

STAY_BASIS = "2026-12-10~11 · 1박 · 성인 2명 · 세금·봉사료 포함 최저가"

HOTELS = {
    "chiangmai": {
        "cityId": "623",
        "name": "치앙마이",
        "note": "올드시티(성벽 안)와 님만해민·후웨이 깨우, 야시장(창 클란) 세 축입니다. 사원·도보 관광은 올드시티, 카페·쇼핑은 님만해민이 편하고, 공항에서는 차로 13분 안팎입니다.",
        "top": "스테이 위드 님만 치앙마이",
        "listUrl": "https://kr.trip.com/hotels/list?city=623&display=%EC%B9%98%EC%95%99%EB%A7%88%EC%9D%B4&optionId=623&optionType=City&optionName=%EC%B9%98%EC%95%99%EB%A7%88%EC%9D%B4&Allianceid=11407530&SID=336341874&trip_sub1=hotel_chiangmai&trip_sub3=D21372570",
        "guides": [{"slug": "chiang-mai-3n4d-course", "label": "치앙마이 3박4일"},
                   {"slug": "thailand-souvenir-list", "label": "태국 선물 목록"},
                   {"slug": "sea-grab-taxi-scam-guide", "label": "동남아 그랩·택시"}],
        "hotels": [
            {"id": "661433", "name": "파타라 플레이스", "star": 3, "score": 9.0, "reviews": 321, "price": 23620,
             "zone": "창 푸악", "access": "치앙마이 기차역 5km · 차로 15분",
             "reason": "리뷰 321개·9.0 — 1박 2만 3,620원으로 치앙마이 5곳 중 가장 낮습니다. 올드시티 북쪽 창 푸악에 있어 도보 관광보다는 썽태우·그랩 이동 기준으로 잡을 때 맞습니다.",
             "themes": ["value"], "pointTags": ["창 푸악", "가성비"]},
            {"id": "1547475", "name": "홀리데이 가든 호텔 & 리조트 치앙 마이", "star": 3, "score": 8.6, "reviews": 1629, "price": 44392,
             "zone": "후웨이 깨우", "access": "치앙마이 국제공항 5.1km · 차로 13분",
             "reason": "리뷰 1,629개·8.6 — 공항에서 차로 13분, 야외 수영장과 정원이 있는 리조트형입니다. 님만해민 카페 거리까지 도보 15분 거리라 아침·저녁 동선이 짧습니다.",
             "themes": ["pool"], "pointTags": ["후웨이 깨우", "수영장"]},
            {"id": "25926084", "name": "아이콘 파크 호텔 치앙마이", "star": 4, "score": 8.9, "reviews": 1055, "price": 58461,
             "zone": "창 푸악", "access": "치앙마이 기차역 4.6km · 차로 14분",
             "reason": "리뷰 1,055개·8.9 — 4성급 중 가격이 낮은 쪽입니다. 성벽 북쪽 창 푸악이라 올드시티 사원까지 차로 5~10분, 야시장은 10분 안팎입니다.",
             "themes": [], "pointTags": ["창 푸악"]},
            {"id": "997792", "name": "두앙따완 호텔 치앙마이", "star": 4, "score": 8.2, "reviews": 1225, "price": 70859,
             "zone": "야시장", "access": "치앙마이 기차역 3.2km · 차로 10분",
             "reason": "리뷰 1,225개·8.2 — 야시장(나이트 바자) 바로 옆이라 저녁 식사·쇼핑이 도보권입니다. 고층 객실 전망이 좋다는 평이 많고, 공항까지 차로 15분 안팎입니다.",
             "themes": ["station"], "pointTags": ["야시장", "도보 관광"]},
            {"id": "12591320", "name": "스테이 위드 님만 치앙마이", "star": 4, "score": 9.1, "reviews": 1834, "price": 97722,
             "zone": "님만해민", "access": "치앙마이 국제공항 4km · 차로 11분",
             "reason": "리뷰 1,834개·9.1 — 님만해민 한가운데라 카페·마야몰·원님만이 도보권입니다. 공항 11분, 5곳 중 평점이 가장 높습니다.",
             "themes": ["pool"], "pointTags": ["님만해민", "쇼핑"]},
        ],
    },
    "bali": {
        "cityId": "723",
        "name": "발리",
        "note": "쿠타·스미냑(해변·비치클럽), 우붓(논·사원·요가), 공항 인접 쿠타 투반이 서로 차로 30분~1시간 40분 떨어집니다. 3박이면 우붓 2박+스미냑 1박, 공항 도착일 밤이 늦으면 공항 근처 1박이 안전합니다.",
        "top": "케란 리조트 우붓",
        "listUrl": "https://kr.trip.com/hotels/list?city=723&display=%EB%B0%9C%EB%A6%AC&optionId=723&optionType=City&optionName=%EB%B0%9C%EB%A6%AC&Allianceid=11407530&SID=336341874&trip_sub1=hotel_bali&trip_sub3=D21372570",
        "guides": [{"slug": "bali-ubud-seminyak-3n4d-course", "label": "발리 3박4일"},
                   {"slug": "entry-immigration-guide", "label": "입국서류 총정리"},
                   {"slug": "sea-grab-taxi-scam-guide", "label": "그랩·택시 요금"}],
        "hotels": [
            {"id": "685020", "name": "호텔 테라스 앳 쿠타", "star": 3, "score": 8.9, "reviews": 328, "price": 27289,
             "zone": "쿠타", "access": "응우라라이 국제공항 5.7km · 차로 19분",
             "reason": "리뷰 328개·8.9 — 1박 2만 7,289원으로 발리 5곳 중 최저입니다. 쿠타 해변까지 걸어갈 수 있고 공항에서 19분이라, 늦은 도착 첫날 밤에 맞습니다.",
             "themes": ["value"], "pointTags": ["쿠타", "가성비"]},
            {"id": "2625052", "name": "디프리마 호텔 페티텡게트 세미냑", "star": 4, "score": 8.9, "reviews": 489, "price": 30440,
             "zone": "스미냑", "access": "응우라라이 국제공항 13.4km · 차로 32분",
             "reason": "리뷰 489개·8.9 — 스미냑 페티텡게트 거리 안쪽이라 비치클럽·식당이 도보권인데 1박 3만 440원입니다. 수영장이 있는 4성급 중 가장 낮은 값입니다.",
             "themes": ["value", "pool"], "pointTags": ["스미냑", "가성비"]},
            {"id": "1837738", "name": "힐튼 가든 인 발리 응우라 라이 에어포트", "star": 4, "score": 8.3, "reviews": 1927, "price": 79525,
             "zone": "쿠타(공항)", "access": "응우라라이 국제공항 730m · 도보 10분",
             "reason": "리뷰 1,927개·8.3 — 공항에서 도보 10분(730m)이라 새벽 출발·심야 도착에 가장 안전합니다. 브랜드 호텔이라 조식과 체크인 절차가 안정적입니다.",
             "themes": ["station"], "pointTags": ["공항 도보", "심야 도착"]},
            {"id": "54563964", "name": "케란 리조트 우붓", "star": 5, "score": 8.7, "reviews": 419, "price": 128523,
             "zone": "우붓", "access": "응우라라이 국제공항 44.3km · 차로 1시간 25분",
             "reason": "리뷰 419개·8.7 — 우붓 북쪽 켄데란의 5성 리조트로 1박 12만 8,523원입니다. 우붓 중심까지 차로 15분 안팎이고, 논·계곡 전망 객실이 중심입니다.",
             "themes": ["pool", "villa"], "pointTags": ["우붓", "리조트"]},
            {"id": "23591673", "name": "더 카욘 정글 리조트", "star": 5, "score": 9.6, "reviews": 139, "price": 310550,
             "zone": "우붓(파양안)", "access": "응우라라이 국제공항 52km · 차로 1시간 41분",
             "reason": "리뷰 139개·9.6 — 발리 5곳 중 평점이 가장 높은 정글 리조트입니다. 공항에서 1시간 41분이라 3박 중 1~2박을 통째로 리조트에서 쓰는 일정에 맞습니다.",
             "themes": ["pool", "villa"], "pointTags": ["우붓", "정글뷰"]},
        ],
    },
    "shanghai": {
        "cityId": "2",
        "name": "상하이",
        "note": "인민광장·난징동루(관광·쇼핑), 푸둥 루자쭈이(전망·비즈니스), 푸동공항·디즈니 쪽이 서로 멉니다. 2박3일이면 인민광장·난징동루에 몰고, 푸동공항 도착이 밤이면 공항 근처 1박이 이동을 줄입니다.",
        "top": "호텔 샬레 상하이",
        "listUrl": "https://kr.trip.com/hotels/list?city=2&display=%EC%83%81%ED%95%98%EC%9D%B4&optionId=2&optionType=City&optionName=%EC%83%81%ED%95%98%EC%9D%B4&Allianceid=11407530&SID=336341874&trip_sub1=hotel_shanghai&trip_sub3=D21372570",
        "guides": [{"slug": "shanghai-2n3d-3n4d-course", "label": "상하이 2박3일·3박4일"},
                   {"slug": "entry-immigration-guide", "label": "무비자·입국서류"},
                   {"slug": "currency-payment-fees", "label": "환전·결제 수수료"}],
        "hotels": [
            {"id": "1073814", "name": "비엔나 호텔 푸동 에어포트", "star": 4, "score": 9.5, "reviews": 18514, "price": 55837,
             "zone": "푸둥·공항지구", "access": "지하철 링콩루 4.3km · 차로 11분",
             "reason": "리뷰 18,514개·9.5 — 푸동공항 권역에서 평점이 높고 1박 5만 5,837원입니다. 시내 관광보다 환승·새벽 출발에 맞고, 인민광장까지는 지하철로 40분 안팎 걸립니다.",
             "themes": ["value"], "pointTags": ["푸동공항", "환승"]},
            {"id": "98063418", "name": "JI 호텔 상하이 둥징루 스테이션", "star": 3, "score": 9.5, "reviews": 1239, "price": 75402,
             "zone": "푸둥와이가오차오", "access": "지하철 둥징루 역 도보권",
             "reason": "리뷰 1,239개·9.5 — 둥징루 역 도보권이라 2호선으로 인민광장·푸둥을 바로 오갑니다. 1박 7만 5,402원으로 시내 4성급보다 40% 이상 낮습니다.",
             "themes": ["station"], "pointTags": ["둥징루", "지하철"]},
            {"id": "133202575", "name": "상하이 SK 루소 호텔", "star": 4, "score": 9.3, "reviews": 2611, "price": 120181,
             "zone": "인민광장지구", "access": "지하철 난징동루 790m · 도보 13분",
             "reason": "리뷰 2,611개·9.3 — 인민광장 권역에서 1박 12만 181원으로 가격과 위치의 균형이 좋습니다. 난징동루 보행거리까지 도보 13분, 와이탄은 20분 안팎입니다.",
             "themes": ["station"], "pointTags": ["인민광장", "난징동루"]},
            {"id": "387239", "name": "센트럴 호텔 상하이", "star": 4, "score": 9.0, "reviews": 1831, "price": 142930,
             "zone": "인민광장지구", "access": "지하철 난징동루 320m · 도보 6분",
             "reason": "리뷰 1,831개·9.0 — 난징동루 역에서 도보 6분이라 짐을 끌고 와도 부담이 없습니다. 와이탄·인민광장·예원이 모두 도보·지하철 한 정거장권입니다.",
             "themes": ["station"], "pointTags": ["난징동루", "도보 관광"]},
            {"id": "72926277", "name": "호텔 샬레 상하이", "star": 4, "score": 9.5, "reviews": 15622, "price": 149017,
             "zone": "인민광장지구", "access": "지하철 인민광장 390m · 도보 6분",
             "reason": "리뷰 15,622개·9.5 — 상하이 5곳 중 리뷰가 가장 많고 평점도 최상위입니다. 인민광장 역 도보 6분이라 1·2·8호선을 모두 쓸 수 있습니다.",
             "themes": ["station"], "pointTags": ["인민광장", "리뷰 다수"]},
        ],
    },
}

HUBS = [
    {
        "slug": "chiangmai", "name": "치앙마이", "nav": "치앙마이", "country": "th", "flag": "th", "kicker": "CHIANG MAI",
        "seoTitle": "치앙마이 여행 숙소·3박4일·썽태우 요금 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "치앙마이 숙소 5곳 1박 2만 3,620원~9만 7,722원(2인). 공항 정액택시 150밧·썽태우 30밧, 도이수텝 30밧, eSIM 1일 110원부터.",
        "keywords": "치앙마이 여행, 치앙마이 숙소, 치앙마이 3박4일, 치앙마이 공항 택시 150밧, 썽태우 30밧, 도이수텝, 님만해민, 치앙마이 eSIM",
        "h1": "치앙마이 여행, <em>숙소·썽태우·3박4일</em>을 한 페이지에",
        "intro": ("치앙마이는 올드시티(성벽 안)와 님만해민·후웨이 깨우, 야시장이 차로 10~15분씩 떨어져 있어 어디에 묵느냐가 하루 동선을 정합니다. "
                  "숙소는 1박·2인 기준 파타라 플레이스 2만 3,620원, 홀리데이 가든 4만 4,392원, 스테이 위드 님만 9만 7,722원이고, "
                  "공항에서는 정액택시 150밧(약 5,940원)으로 15분, 시내 이동은 빨간 썽태우 1인 30밧이면 대부분 해결됩니다. "
                  "도이수텝 입장료는 30밧, 코끼리 보호구역 반나절은 2,500밧입니다."),
        "giftFallback": "치앙마이 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 태국 선물 목록 가이드에서 출발 전에 사 두면 좋은 것만 모았습니다.",
        "foodFallback": "치앙마이 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 하루 동선은 아래 3박4일 코스 가이드에 숫자로 계산해 두었습니다.",
        "hotels": ["chiangmai"],
        "image": "images/v59/chiangmai.jpg",
        "imageAlt": "치앙마이 도이수텝 사원의 금탑과 등불",
        "imageCredit": "사진: Pexels (Vishal Chokkala)",
        "ogImage": "images/og/v59-chiangmai-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "공항 → 시내", "v": "정액택시 150밧(약 5,940원)·15분, SUV 250밧. 그랩 80~200밧, 시내버스 30밧"},
            {"k": "숙소 1박(2인)", "v": "파타라 2만 3,620원 · 홀리데이 가든 4만 4,392원 · 스테이 위드 님만 9만 7,722원"},
            {"k": "시내 이동", "v": "빨간 썽태우 1인 30밧(님만해민 40~60밧). 목적지 보여주고 '1인 30밧'을 먼저 말하기"},
            {"k": "도이수텝", "v": "입장 30밧(현금) + 푸니쿨라 편도 20~50밧. 창푸악 게이트 합승 썽태우 1인 40~50밧"},
        ],
        "guides": ["chiang-mai-3n4d-course", "thailand-souvenir-list", "sea-grab-taxi-scam-guide",
                   "entry-immigration-guide", "travel-card-fees-comparison", "travel-insurance-guide",
                   "hotel-booking-timing-refund-tips", "overseas-roaming-esim-install-troubleshooting"],
    },
    {
        "slug": "bali", "name": "발리", "nav": "발리", "country": "id", "flag": "id", "kicker": "BALI",
        "seoTitle": "발리 여행 숙소·비자·관광세·3박4일 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "발리 숙소 5곳 1박 2만 7,289원~31만 550원(2인). 도착비자 500,000·관광세 150,000루피아, 공항→우붓 그랩 340,000루피아, eSIM 1일 101원.",
        "keywords": "발리 여행, 발리 숙소, 발리 3박4일, 발리 비자 e-VOA 500000, 발리 관광세 150000, 우붓 리조트, 스미냑 호텔, 발리 eSIM",
        "h1": "발리 여행, <em>숙소·비자·관광세</em>를 한 페이지에",
        "intro": ("발리는 쿠타·스미냑과 우붓이 차로 1시간 안팎 떨어져 있어, 3박을 어디에 나눌지가 하루 동선을 정합니다. "
                  "숙소는 1박·2인 기준 호텔 테라스 앳 쿠타 2만 7,289원, 디프리마 세미냑 3만 440원, 공항 도보권 힐튼 가든 인 7만 9,525원, "
                  "우붓 케란 리조트 12만 8,523원, 더 카욘 정글 리조트 31만 550원입니다. "
                  "한국 여권은 무비자가 아니라 도착비자(e-VOA) 500,000루피아가 필요하고, 관광세 150,000루피아가 따로 붙습니다."),
        "giftFallback": "발리 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 사 두면 현지에서 번거로운 준비물만 모았습니다.",
        "foodFallback": "발리 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 3박4일 코스 가이드에 숫자로 계산해 두었습니다.",
        "hotels": ["bali"],
        "image": "images/v59/bali.jpg",
        "imageAlt": "발리 우붓 논과 전통 가옥의 초록 풍경",
        "imageCredit": "사진: Pexels (Evelin Magnus)",
        "ogImage": "images/og/v59-bali-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "입국 비자", "v": "e-VOA 500,000루피아(1인). 30일 체류·1회 연장 가능, 여권 6개월 이상"},
            {"k": "관광세", "v": "150,000루피아 1회. lovebali.baliprov.go.id 또는 러브발리 앱에서 카드 결제"},
            {"k": "숙소 1박(2인)", "v": "테라스 앳 쿠타 2만 7,289원 · 힐튼 가든 인(공항 도보) 7만 9,525원 · 케란 리조트 우붓 12만 8,523원"},
            {"k": "공항 → 우붓", "v": "그랩 340,000~380,000루피아·60~120분. 오전 7시 30분 이전 출발이 병목을 피함"},
        ],
        "guides": ["bali-ubud-seminyak-3n4d-course", "entry-immigration-guide", "sea-grab-taxi-scam-guide",
                   "currency-payment-fees", "travel-insurance-guide", "travel-card-fees-comparison",
                   "hotel-booking-timing-refund-tips", "overseas-roaming-esim-install-troubleshooting"],
    },
    {
        "slug": "shanghai", "name": "상하이", "nav": "상하이", "country": "cn", "flag": "cn", "kicker": "SHANGHAI",
        "seoTitle": "상하이 여행 숙소·무비자 30일·2박3일 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "상하이 숙소 5곳 1박 5만 5,837원~14만 9,017원(2인). 무비자 30일(2026-12-31까지), 푸둥공항→인민광장 지하철 7위안, 예원 40위안.",
        "keywords": "상하이 여행, 상하이 숙소, 상하이 2박3일, 상하이 무비자 30일, 푸둥공항 지하철 7위안, 난징동루 호텔, 예원 입장료, 상하이 eSIM",
        "h1": "상하이 여행, <em>숙소·무비자·공항 이동</em>을 한 페이지에",
        "intro": ("상하이는 인민광장·난징동루와 푸둥 루자쭈이, 푸동공항 권역이 서로 멀어 숙소 위치가 이동 시간을 정합니다. "
                  "숙소는 1박·2인 기준 비엔나 호텔 푸동 에어포트 5만 5,837원, JI 호텔 둥징루 7만 5,402원, SK 루소 12만 181원, "
                  "센트럴 호텔 14만 2,930원, 호텔 샬레 14만 9,017원입니다. "
                  "한국 여권은 2026년 12월 31일까지 30일 무비자이고, 푸둥공항에서 인민광장까지 지하철 7위안·자기부상 50위안입니다."),
        "giftFallback": "상하이 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 사 두면 현지에서 번거로운 준비물만 모았습니다.",
        "foodFallback": "상하이 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 2박3일·3박4일 가이드에 숫자로 계산해 두었습니다.",
        "hotels": ["shanghai"],
        "image": "images/v59/shanghai.jpg",
        "imageAlt": "와이탄에서 바라본 상하이 푸둥의 야경",
        "imageCredit": "사진: Pexels (YFS Visuals)",
        "ogImage": "images/og/v59-shanghai-og.jpg",
        "stayCards": True,
        "tips": [
            {"k": "무비자", "v": "한국 일반여권 30일 무비자(2026-12-31까지). 여권 유효기간 6개월 이상 권장"},
            {"k": "공항 → 인민광장", "v": "지하철 7위안, 자기부상 50위안(용양로 환승). 푸동공항에서 시내까지 50~70분"},
            {"k": "숙소 1박(2인)", "v": "비엔나(푸동공항) 5만 5,837원 · JI 호텔(둥징루) 7만 5,402원 · 호텔 샬레(인민광장) 14만 9,017원"},
            {"k": "입장료", "v": "예원 40위안 · 상하이타워 180위안 · 황푸강 크루즈 120~150위안 · 디즈니 475~799위안"},
        ],
        "guides": ["shanghai-2n3d-3n4d-course", "entry-immigration-guide", "currency-payment-fees",
                   "hongkong-macau-3n4d-course", "flight-cheap-booking-baggage", "travel-card-fees-comparison",
                   "travel-insurance-guide", "overseas-roaming-esim-install-troubleshooting"],
    },
]


def load(n):
    return json.loads((D / n).read_text(encoding="utf-8"))


def save(n, o):
    (D / n).write_text(json.dumps(o, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main() -> int:
    stays = load("stays.json")
    regions = {r["id"] for r in stays["regions"]}
    existing = {(h["region"], h["id"]) for h in stays["hotels"]}
    added_h = 0
    for rid, cfg in HOTELS.items():
        if rid not in regions:
            stays["regions"].append({
                "id": rid, "name": cfg["name"], "country": {"chiangmai": "태국", "bali": "인도네시아", "shanghai": "중국"}[rid],
                "note": cfg["note"], "count": len(cfg["hotels"]), "top": cfg["top"], "listUrl": cfg["listUrl"],
                "cityId": cfg["cityId"], "scope": "intl", "hub": rid, "guides": cfg["guides"],
            })
        for h in cfg["hotels"]:
            if (rid, h["id"]) in existing:
                continue
            stays["hotels"].append({
                "region": rid, "id": h["id"], "name": h["name"], "star": h["star"], "type": "hotel", "typeLabel": "호텔",
                "score": h["score"], "reviews": h["reviews"], "zone": h["zone"], "access": h["access"],
                "reason": h["reason"], "price": h["price"], "priceBasis": STAY_BASIS,
                "img": f"images/stays/{rid}-{h['id']}.jpg",
                "url": (f"https://kr.trip.com/hotels/detail/?cityId={cfg['cityId']}&hotelId={h['id']}&curr=KRW"
                        f"&Allianceid=11407530&SID=336341874&trip_sub1=stays_{rid}_{h['id']}&trip_sub3=D21372570"),
                "themes": h["themes"], "pointTags": h["pointTags"],
            })
            added_h += 1
    stays["source"]["v59"] = ("2026-11-26: 치앙마이(5)·발리(5)·상하이(5) 숙소 15곳을 새로 넣었습니다. 가격은 트립닷컴 숙소 목록에서 "
                              "2026-12-10~11 성인 2명·세금 포함 1박 최저가로 조회한 값이고, 성급·존·공항/역 거리는 같은 호텔 상세 페이지에서 확인했습니다.")
    save("stays.json", stays)
    print(f"stays +{added_h} → {len(stays['hotels'])}곳 · 지역 {len(stays['regions'])}곳")

    ch = load("city_hubs.json")
    slugs = {c["slug"] for c in ch["cities"]}
    added_c = 0
    for hub in HUBS:
        if hub["slug"] in slugs:
            continue
        row = dict(hub)
        row["cityIds"] = [hub["slug"]]
        row["updated"] = "2026-11-26"
        ch["cities"].append(row)
        added_c += 1
    save("city_hubs.json", ch)
    print(f"city_hubs +{added_c} → {len(ch['cities'])}곳")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
