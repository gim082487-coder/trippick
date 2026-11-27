#!/usr/bin/env python3
"""v65: 찐숙소 30곳 + 신규 도시 허브 6곳(city_hubs.json·stays.json).

    python3 tools/apply_v65_data.py

숙소 값은 2026-11-27 트립닷컴 목록(2027-01-15~16 · 성인 2명 · KRW)과
각 호텔 상세 페이지(HTTP 200)에서 받은 성급·세부 점수·주소다.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
SCRAPED = json.loads(Path("/workspace/v65_stays_scraped.json").read_text(encoding="utf-8"))
BASIS = "2027-01-15~16 · 1박 · 2인 · 세금·봉사료 포함 최저가"

# region, id, name, en, star, typeLabel, score, reviews, zone, access, reason, price, themes, pointTags
HOTELS = [
    ("newyork", "2092657", "하이 뉴욕 시티 - 호스텔", "HI New York City Hostel", 2, "호스텔", 8.9, 421,
     "어퍼 웨스트 사이드", "센트럴 파크 인근 · 891 Amsterdam Ave",
     "리뷰 421개·8.9 — 어퍼 웨스트 사이드에서 센트럴 파크가 가깝고, 2인 1박 11만 8,148원으로 이 도시 조회분 5곳 중 가장 낮습니다. 도미토리(침대 2개) 기준입니다.",
     118148, ["value"], ["호스텔", "센트럴파크"]),
    ("newyork", "2192841", "더블트리 바이 힐튼 뉴욕 다운타운", "DoubleTree by Hilton New York Downtown", 4, "호텔", 8.3, 2001,
     "파이낸셜 디스트릭트", "월스트리트 인근 · 8 Stone St",
     "리뷰 2,001개·8.3 — 월스트리트 도보권이고 위치 8.8입니다. 리뷰 수가 가장 많아 시설 편차를 가늠하기 좋고 1박 18만 6,919원입니다.",
     186919, ["station"], ["월스트리트", "리뷰 최다"]),
    ("newyork", "105237897", "모토 바이 힐튼 뉴욕 시티 타임스 스퀘어", "Motto by Hilton New York City Times Square", 4, "호텔", 8.6, 733,
     "타임스 스퀘어", "센트럴 파크 인근 · 150 A W 48th St",
     "리뷰 733개·8.6 — 타임스 스퀘어 권역에서 위치 9.1입니다. 벽장형 침대의 컴팩트 룸이지만 1박 20만 8,093원으로 미드타운 4성급 중 낮은 편입니다.",
     208093, ["station"], ["타임스스퀘어", "위치 최고"]),
    ("newyork", "1565906", "하얏트 리젠시 타임스 스퀘어", "Hyatt Regency Times Square", 4, "호텔", 8.7, 153,
     "타임스 스퀘어", "센트럴 파크 인근 · 1605 Broadway",
     "2025년 문을 연 호텔로 리뷰 153개·8.7, 위치 9.1입니다. 브로드웨이 1605번지라 극장가와 센트럴 파크가 도보권이고 1박 30만 3,888원입니다.",
     303888, ["station"], ["신축", "브로드웨이"]),
    ("newyork", "2193990", "브라이언트 파크 호텔", "Bryant Park Hotel", 4, "호텔", 9.3, 102,
     "브라이언트 파크", "브라이언트 공원 인근 · 40 W 40th St",
     "리뷰 102개·9.3 — 청결·시설·위치·서비스가 모두 9.3으로 이 도시 조회분 중 평점이 가장 높습니다. 브라이언트 공원 바로 앞, 1박 53만 4,667원입니다.",
     534667, ["station"], ["평점 최고", "브라이언트파크"]),
    ("nagoya", "8344318", "나고야 JR 게이트 타워 호텔", "Nagoya JR Gate Tower Hotel", 4, "호텔", 9.4, 3321,
     "나고야역", "메이테쓰나고야 인근 · 나카무라구 1-1-3",
     "리뷰 3,321개·9.4 — 위치 9.6으로 나고야역·메이테쓰나고야와 바로 연결됩니다. 1박 21만 7,056원.",
     217056, ["station"], ["역 직결", "위치 최고"]),
    ("nagoya", "5086203", "미쓰이 가든 호텔 나고야 프리미어", "Mitsui Garden Hotel Nagoya Premier", 5, "호텔", 9.3, 2314,
     "메이에키", "메이테쓰나고야·나고야 지하철역 인근",
     "리뷰 2,314개·9.3 — 고층 야경과 일출 전망 평가가 높고 위치 9.5입니다. 1박 14만 8,773원.",
     148773, ["station", "value"], ["고층 야경", "조식"]),
    ("nagoya", "703777", "나고야 도큐 호텔", "Nagoya Tokyu Hotel", 5, "호텔", 9.2, 1580,
     "사카에", "사카에 4-6-8",
     "리뷰 1,580개·9.2 — 사카에 중심의 5성급으로 서비스 9.3, 일식당·가이세키 평가가 높습니다. 1박 13만 7,967원.",
     137967, ["value"], ["가이세키", "사카에"]),
    ("nagoya", "72147574", "액세스 바이 르와지르 호텔 나고야", "Access by Loisir Hotel Nagoya", 3, "호텔", 9.2, 476,
     "사카에마치", "사카에마치·히가시사쿠라 1-9-22",
     "리뷰 476개·9.2 — 서비스 9.5로 이 도시 조회분 중 가장 높고, 1박 6만 6,144원으로 최저가입니다.",
     66144, ["value", "station"], ["가성비", "서비스 최고"]),
    ("nagoya", "93970929", "코코 호텔 나고야 사카에", "Koko Hotel Nagoya Sakae", 4, "호텔", 8.9, 1429,
     "사카에", "사카에 지하철역 인근 · 니시키 3-15-21",
     "리뷰 1,429개·8.9 — 사카에 지하철역 도보권으로 위치 9.4, 일본식 조식 평가가 좋습니다. 1박 7만 4,163원.",
     74163, ["station", "value"], ["일본식 조식", "지하철"]),
    ("phuquoc", "10200862", "씨셸스 푸꾸옥 호텔 & 스파", "Seashells Phu Quoc Hotel & Spa", 5, "호텔", 9.0, 2185,
     "즈엉동", "푸꾸옥 야시장 인근 · 01 Võ Thị Sáu",
     "리뷰 2,185개·9.0 — 야시장 인근 위치 9.4, 오션뷰와 비치풀 평가가 높습니다. 조식 포함 1박 30만 9,983원.",
     309983, ["pool", "ocean"], ["야시장", "오션뷰"]),
    ("phuquoc", "31583072", "베스트 웨스턴 프리미어 소나씨 푸꾸옥", "Best Western Premier Sonasea Phu Quoc", 5, "호텔", 8.8, 1377,
     "롱비치(바이쯔엉)", "Sonasea 공용해변 인근 · Đường Bào",
     "리뷰 1,377개·8.8 — 롱비치 해변 구간의 5성 리조트로 위치 9.2. 조식 포함 1박 27만 750원입니다.",
     270750, ["pool", "ocean", "villa"], ["비치 리조트", "조식 포함"]),
    ("phuquoc", "9585235", "라하나 리조트 푸꾸옥 & 스파", "Lahana Resort Phu Quoc & Spa", 4, "호텔", 9.3, 688,
     "즈엉동", "푸꾸옥 야시장·공항 인근 · 91/3 Tran Hung Dao",
     "리뷰 688개·9.3 — 청결 9.4·서비스 9.5로 이 도시 조회분 중 평점이 가장 높습니다. 일몰 뷰와 풀사이드 레스토랑, 조식 포함 1박 29만 2,007원.",
     292007, ["pool", "value"], ["평점 최고", "일몰 뷰"]),
    ("phuquoc", "91307436", "세일링 클럽 시그니처 리조트 푸꾸옥", "Sailing Club Signature Resort Phu Quoc", 5, "호텔", 9.2, 528,
     "즈엉바오", "Regent Club 인근 · Group 6, Đường Bào",
     "리뷰 528개·9.2 — 침실 2개·개인 수영장 빌라로 4인까지 묵습니다. 불꽃놀이 전망 평가가 높고 조식 포함 1박 59만 2,363원입니다.",
     592363, ["villa", "pool"], ["개인 풀", "빌라"]),
    ("phuquoc", "2562937", "시 스타 리조트", "Sea Star Resort", 3, "호텔", 8.9, 305,
     "롱비치", "즈엉동 인근 · 98/2 Trần Hưng Đạo",
     "리뷰 305개·8.9 — 위치 9.5로 해변·시내 접근이 좋고, 1박 7만 983원으로 이 도시 조회분 최저가입니다.",
     70983, ["value", "ocean"], ["가성비", "오션뷰"]),
    ("cebu", "102030816", "머큐어 막탄 세부", "Mercure Mactan Cebu", 4, "호텔", 8.9, 1885,
     "막탄 뉴타운", "막탄섬 · Newtown Blvd",
     "리뷰 1,885개·8.9 — 공항과 가까운 막탄 뉴타운, 풀·비치·바 평가가 좋습니다. 1박 7만 6,553원.",
     76553, ["pool", "ocean", "station"], ["공항 인접", "비치 클럽"]),
    ("cebu", "759892", "블루워터 마리바고 비치 리조트", "Bluewater Maribago Beach Resort", 4, "호텔", 9.0, 799,
     "막탄 마리바고", "마리바고 해변 · Buyong",
     "리뷰 799개·9.0 — 세부 업스케일 호텔 1위, 청결 9.2·서비스 9.2입니다. 라군 수영장과 전용 해변, 1박 13만 8,006원.",
     138006, ["ocean", "pool", "villa"], ["전용 해변", "리조트"]),
    ("cebu", "5902851", "솔레아 막탄 리조트 앤 워터파크", "Solea Mactan Resort and Waterpark", 4, "호텔", 8.4, 801,
     "막탄 코도바", "막탄섬 · Victor Wahing Street",
     "리뷰 801개·8.4 — 2026년 리모델링한 워터파크 리조트로 아이 동반에 맞습니다. 1박 10만 541원.",
     100541, ["pool", "villa"], ["워터파크", "가족"]),
    ("cebu", "10549822", "도요코 인 세부", "Toyoko Inn Cebu", 3, "호텔", 8.8, 1132,
     "세부시티 만다웨", "SM J Mall 인근 · 165 A. S. Fortuna St",
     "리뷰 1,132개·8.8 — 무료 공항 셔틀과 일본식 조식 평가가 높습니다. 시티 쇼핑·야시장 동선에 맞고 1박 5만 6,110원입니다.",
     56110, ["value", "station"], ["공항 셔틀", "일본식 조식"]),
    ("cebu", "99386475", "쎄프리 프레미어 잉 막탄 공항 호텔", "Sempre Premier Inn - Mactan Airport Hotel", 3, "호텔", 8.8, 274,
     "막탄 공항", "막탄섬 · ML Quezon National Hwy",
     "리뷰 274개·8.8 — 공항 셔틀(06:00~01:00)이 있어 새벽 도착·출발에 맞습니다. 옥상 레스토랑, 1박 4만 3,415원으로 최저가.",
     43415, ["value", "station"], ["공항 셔틀", "새벽 출발"]),
    ("sydney", "9341526", "더 캡슐 호텔", "The Capsule Hotel", 3, "호텔", 8.4, 398,
     "CBD(조지스트리트)", "달링 하버 인근 · 640 George St",
     "리뷰 398개·8.4 — 조지스트리트 위치 9.4, 여성전용 캡슐(침대 2개) 1박 8만 9,632원으로 최저가입니다.",
     89632, ["value", "station"], ["캡슐", "위치 최고"]),
    ("sydney", "29958862", "베리우 그린 스퀘어", "Veriu Green Square", 4, "호텔", 9.1, 415,
     "그린 스퀘어", "공항 인근 · 18 O'Riordan St",
     "리뷰 415개·9.1 — 공항과 시내 사이 그린 스퀘어, 위치 9.3입니다. 1박 13만 2,442원.",
     132442, ["value", "station"], ["공항 인근", "평점"]),
    ("sydney", "736187", "더 풀러턴 호텔 시드니", "The Fullerton Hotel Sydney", 5, "호텔", 9.2, 887,
     "CBD 마틴 플레이스", "오페라하우스 인근 · 1 Martin Pl",
     "리뷰 887개·9.2 — 마틴 플레이스의 역사적 건물을 리노베이션, 위치 9.6입니다. 조식 포함 1박 27만 7,164원.",
     277164, ["station"], ["위치 최고", "조식 포함"]),
    ("sydney", "734373", "메리턴 스위트 켄트 스트리트, 시드니", "Meriton Suites Kent Street", 5, "호텔", 8.7, 364,
     "달링 하버", "달링 하버·전시장 인근 · 528 Kent St",
     "리뷰 364개·8.7 — 달링 하버 도보권 위치 9.4, 스튜디오 스위트에 실내 온수풀이 있습니다. 1박 32만 5,388원.",
     325388, ["pool", "station"], ["스위트", "달링하버"]),
    ("sydney", "714671", "샹그릴라 시드니", "Shangri-La Sydney", 5, "호텔", 8.9, 1182,
     "록스", "오페라하우스·달링 하버 인근 · 176 Cumberland St",
     "리뷰 1,182개·8.9 — 록스의 하버뷰 호텔로 고층 레스토랑·수영장 평가가 높습니다. 1박 40만 2,192원.",
     402192, ["pool", "ocean"], ["하버뷰", "고층 레스토랑"]),
    ("sapporo", "705841", "삿포로 뷰 호텔 오도리 파크", "Sapporo View Hotel Odori Park", 5, "호텔", 9.0, 954,
     "오도리", "오도리 공원·삿포로역 인근 · Odori Nishi 8",
     "리뷰 954개·9.0 — 오도리 공원 앞, 일본식 조식과 정원 뷰 평가가 높습니다. 1박 8만 7,205원으로 이 도시 조회분 최저가.",
     87205, ["value", "station"], ["오도리 공원", "일본식 조식"]),
    ("sapporo", "62987948", "솔라리아 니시테츠 호텔 삿포로", "Solaria Nishitetsu Hotel Sapporo", 4, "호텔", 9.3, 1073,
     "삿포로역·다마코지", "삿포로역·다마코지 상점가 인근 · Kita 4 Nishi 5",
     "리뷰 1,073개·9.3 — 청결 9.4·위치 9.4, 야외 온천과 다양한 조식이 강점입니다. 1박 24만 9,868원.",
     249868, ["onsen", "station"], ["야외 온천", "조식"]),
    ("sapporo", "31315741", "베셀 호텔 캄파나 스스키노", "Vessel Hotel Campana Susukino", 4, "호텔", 9.3, 2332,
     "스스키노", "스스키노·삿포로역 인근 · Minami 5 Nishi 6",
     "리뷰 2,332개·9.3 — 청결 9.5·서비스 9.4, 대욕장과 조식 평가가 높습니다. 1박 19만 9,942원.",
     199942, ["onsen", "value"], ["대욕장", "조식"]),
    ("sapporo", "52762809", "호텔 포르자 삿포로 스테이션", "Hotel Forza Sapporo Station", 4, "호텔", 9.2, 2226,
     "삿포로역", "삿포로역·오도리 공원 인근 · Kita 3 Nishi 2",
     "리뷰 2,226개·9.2 — 삿포로역 도보권 위치 9.5, 조식과 전망 평가가 좋습니다. 1박 17만 9,208원.",
     179208, ["station", "value"], ["삿포로역", "조식"]),
    ("sapporo", "44402748", "더 비 삿포로", "the b sapporo", 3, "호텔", 9.2, 1527,
     "오도리", "오도리 공원·삿포로역 인근 · Minami 3 Nishi 2",
     "리뷰 1,527개·9.2 — 청결 9.4·위치 9.5로 가성비가 좋습니다. 1박 10만 973원.",
     100973, ["value", "station"], ["가성비", "청결"]),
]

REGIONS = [
    {"id": "newyork", "name": "뉴욕", "country": "미국",
     "note": "맨해튼은 미드타운·다운타운·어퍼 웨스트로 숙소값이 갈립니다. 미드타운은 극장가·센트럴 파크, 다운타운은 월스트리트·브루클린 브리지, 어퍼 웨스트는 공원과 박물관 쪽입니다.",
     "count": 5, "top": "브라이언트 파크 호텔",
     "listUrl": "https://kr.trip.com/hotels/list?city=633&display=%EB%89%B4%EC%9A%95&optionId=633&optionType=City&optionName=%EB%89%B4%EC%9A%95&Allianceid=11407530&SID=336341874&trip_sub1=hotel_newyork&trip_sub3=D21372570",
     "cityId": "633", "scope": "intl", "hub": "newyork",
     "guides": [{"slug": "new-york-4n5d-course-budget", "label": "뉴욕 4박5일"},
                {"slug": "us-esta-application-guide", "label": "미국 ESTA"}]},
    {"id": "nagoya", "name": "나고야", "country": "일본",
     "note": "나고야역·메이에키는 신칸센과 공항 접근이 좋고, 사카에·니시키는 쇼핑·야식이 중심입니다. 지브리파크와 시라카와고는 시내에서 따로 반나절을 잡아야 합니다.",
     "count": 5, "top": "나고야 JR 게이트 타워 호텔",
     "listUrl": "https://kr.trip.com/hotels/list?city=360&display=%EB%82%98%EA%B3%A0%EC%95%BC&optionId=360&optionType=City&optionName=%EB%82%98%EA%B3%A0%EC%95%BC&Allianceid=11407530&SID=336341874&trip_sub1=hotel_nagoya&trip_sub3=D21372570",
     "cityId": "360", "scope": "intl", "hub": "nagoya",
     "guides": [{"slug": "nagoya-3n4d-course-budget", "label": "나고야 3박4일"},
                {"slug": "japan-ic-card", "label": "일본 IC카드"}]},
    {"id": "phuquoc", "name": "푸꾸옥", "country": "베트남",
     "note": "즈엉동은 야시장·시내, 롱비치(바이쯔엉)는 리조트 해변, 즈엉바오는 선셋타운·케이블카 쪽입니다. 11~4월이 건기이고 6~9월은 비가 많습니다.",
     "count": 5, "top": "라하나 리조트 푸꾸옥 & 스파",
     "listUrl": "https://kr.trip.com/hotels/list?city=5649&display=%ED%91%B8%EA%BE%B8%EC%98%A5+%EC%84%AC&optionId=5649&optionType=City&optionName=%ED%91%B8%EA%BE%B8%EC%98%A5+%EC%84%AC&Allianceid=11407530&SID=336341874&trip_sub1=hotel_phuquoc&trip_sub3=D21372570",
     "cityId": "5649", "scope": "intl", "hub": "phuquoc",
     "guides": [{"slug": "phu-quoc-3n4d-4n5d-course", "label": "푸꾸옥 3박4일"},
                {"slug": "vietnam-4cities-comparison-guide", "label": "베트남 4도시 비교"}]},
    {"id": "cebu", "name": "세부", "country": "필리핀",
     "note": "막탄은 공항과 리조트, 세부시티는 성당·쇼핑·야시장, 모알보알은 남쪽 3시간 거리 다이빙 마을입니다. 보홀로 넘어가려면 피어1에서 오션젯을 탑니다.",
     "count": 5, "top": "블루워터 마리바고 비치 리조트",
     "listUrl": "https://kr.trip.com/hotels/list?city=1239&display=%EC%84%B8%EB%B6%80&optionId=1239&optionType=City&optionName=%EC%84%B8%EB%B6%80&Allianceid=11407530&SID=336341874&trip_sub1=hotel_cebu&trip_sub3=D21372570",
     "cityId": "1239", "scope": "intl", "hub": "cebu",
     "guides": [{"slug": "cebu-3n4d-course", "label": "세부 3박4일"},
                {"slug": "cebu-bohol-ferry-transfer-guide", "label": "세부·보홀 이동"}]},
    {"id": "sydney", "name": "시드니", "country": "호주",
     "note": "서큘러키는 오페라하우스·페리 선착장, 센트럴은 기차·경전철, 달링하버는 전시장·가족 숙소가 모입니다. 공항은 T8 기차로 센트럴까지 13~15분입니다.",
     "count": 5, "top": "더 풀러턴 호텔 시드니",
     "listUrl": "https://kr.trip.com/hotels/list?city=501&display=%EC%8B%9C%EB%93%9C%EB%8B%88&optionId=501&optionType=City&optionName=%EC%8B%9C%EB%93%9C%EB%8B%88&Allianceid=11407530&SID=336341874&trip_sub1=hotel_sydney&trip_sub3=D21372570",
     "cityId": "501", "scope": "intl", "hub": "sydney",
     "guides": [{"slug": "sydney-4n5d-course", "label": "시드니 4박5일"},
                {"slug": "oceania-eta-nzeta", "label": "호주 ETA"}]},
]

HUBS = [
    {
        "slug": "sapporo", "name": "삿포로", "nav": "삿포로", "cityIds": ["sapporo"],
        "country": "jp", "flag": "jp", "kicker": "SAPPORO",
        "seoTitle": "삿포로 여행 숙소·신치토세공항·눈축제 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "삿포로 찐숙소 9곳 1박 8만 7,205원~24만 9,868원(2인), 신치토세공항 JR 1,230엔·33~37분, 눈축제 2월 4~11일, 겨울 복장과 3박4일 경비.",
        "keywords": "삿포로 여행, 삿포로 숙소, 삿포로 눈축제, 신치토세공항 JR, 삿포로 겨울, 스스키노 호텔, 오도리 공원, 삿포로 3박4일, 홋카이도 여행, 비에이 투어",
        "h1": "삿포로 여행, <em>숙소·공항 이동·눈축제</em>를 한 페이지에",
        "intro": "삿포로는 삿포로역·오도리·스스키노 세 구역이 지하철 두 정거장 안에 모여 있고, 신치토세공항에서는 JR 쾌속 에어포트 1,230엔으로 33~37분이면 들어옵니다. 숙소는 1박·2인 기준 오도리 파크 앞 8만 7,205원부터 스스키노 대욕장 19만 9,942원, 역 도보권 17만 9,208원까지입니다. 2월 눈축제는 2월 4~11일이고, 비에이·후라노 눈 투어는 2인 15만 원 안팎을 잡아야 합니다. 겨울 기온이 영하로 내려가니 복장과 미끄럼 방지부터 확인하세요.",
        "hotels": ["sapporo"], "flight": "삿포로",
        "image": "images/v39/sapporo-winter.jpg", "imageAlt": "눈 내린 삿포로 오도리 공원",
        "imageCredit": "사진: Pexels", "ogImage": "images/og/v39-sapporo-winter-og.jpg",
        "stayCards": True,
        "giftFallback": "삿포로 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 일본 선물 리스트에서 홋카이도 품목을 확인하세요.",
        "foodFallback": "삿포로 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 3박4일 겨울 코스에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "공항 → 삿포로", "v": "JR 쾌속 에어포트 1,230엔 · 33~37분. 공항버스 1,500엔은 68~74분"},
            {"k": "숙소 1박(2인)", "v": "오도리 파크 8만 7,205원 · 스스키노 19만 9,942원 · 삿포로역 17만 9,208원"},
            {"k": "눈축제", "v": "2월 4~11일 · 오도리 공원·스스키노"},
            {"k": "겨울 준비", "v": "2월 영하권 · 미끄럼 방지 신발·핫팩·방한 장갑"},
        ],
        "guides": ["sapporo-hokkaido-3n4d-winter", "sapporo-biei-winter", "sapporo-winter", "japan-winter-clothing",
                   "japan-ic-card", "japan-esim", "japan-rental-car-etc-guide"],
        "updated": "2026-11-27",
    },
    {
        "slug": "nagoya", "name": "나고야", "nav": "나고야", "cityIds": ["nagoya"],
        "country": "jp", "flag": "jp", "kicker": "NAGOYA",
        "seoTitle": "나고야 여행 숙소·지브리파크·시라카와고 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "나고야 찐숙소 5곳 1박 6만 6,144원~21만 7,056원(2인). 뮤스카이 1,430엔·28~34분, 지브리파크 3,300엔, 시라카와고 3,600~4,700엔.",
        "keywords": "나고야 여행, 나고야 숙소, 지브리파크 예약, 시라카와고 투어, 뮤스카이 요금, 나고야 3박4일, 나고야성, 사카에 호텔, 나고야역 호텔, 나고야 공항",
        "h1": "나고야 여행, <em>숙소·지브리파크·공항 이동</em>을 한 페이지에",
        "intro": "나고야는 나고야역·메이에키와 사카에 두 축으로 나뉘고, 중부국제공항에서는 명철 뮤스카이 1,430엔으로 28~34분이면 들어옵니다. 숙소는 1박·2인 기준 사카에 6만 6,144원부터 나고야역 직결 21만 7,056원까지입니다. 지브리파크는 스탠더드 3,300엔에 2개월 전 10일 예약이 필요하고, 시라카와고 당일버스는 왕복 3,600~4,700엔입니다. 3박4일이면 시내 이틀에 지브리파크 하루, 여유가 있으면 시라카와고를 넣습니다.",
        "hotels": [], "flight": "",
        "image": "images/v64/nagoya-3n4d-course-budget.jpg", "imageAlt": "푸른 하늘 아래 나고야성",
        "imageCredit": "사진: Pexels (Alen Joe Chacko)", "ogImage": "images/og/v64-nagoya-og.jpg",
        "stayCards": True,
        "giftFallback": "나고야 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 일본 선물 리스트를 참고하세요.",
        "foodFallback": "나고야 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 3박4일 코스에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "공항 → 나고야역", "v": "뮤스카이 1,430엔(980+450) · 28~34분"},
            {"k": "숙소 1박(2인)", "v": "사카에 6만 6,144원 · 메이에키 14만 8,773원 · 나고야역 직결 21만 7,056원"},
            {"k": "지브리파크", "v": "스탠더드 3,300엔(평일) · 2개월 전 10일 예약"},
            {"k": "시라카와고", "v": "당일버스 왕복 3,600~4,700엔 · 다카야마 3,600엔"},
        ],
        "guides": ["nagoya-3n4d-course-budget", "japan-ic-card", "japan-restaurant-reservation-guide",
                   "japan-esim", "japan-souvenir-list", "japan-winter-clothing"],
        "updated": "2026-11-27",
    },
    {
        "slug": "phuquoc", "name": "푸꾸옥", "nav": "푸꾸옥", "cityIds": ["phuquoc"],
        "country": "vn", "flag": "vn", "kicker": "PHU QUOC",
        "seoTitle": "푸꾸옥 여행 숙소·케이블카·사파리 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "푸꾸옥 찐숙소 5곳 1박 7만 983원~59만 2,363원(2인). 공항→즈엉동 10~15분, 혼똠 케이블카 850,000동, 빈원더스 사파리 950,000동, 12월 강수 60mm.",
        "keywords": "푸꾸옥 여행, 푸꾸옥 숙소, 푸꾸옥 케이블카, 혼똠섬, 빈원더스 사파리, 푸꾸옥 3박4일, 푸꾸옥 리조트, 푸꾸옥 날씨, 푸꾸옥 공항, 그랜드월드",
        "h1": "푸꾸옥 여행, <em>숙소·케이블카·사파리</em>를 한 페이지에",
        "intro": "푸꾸옥은 즈엉동 시내와 롱비치 리조트, 남쪽 즈엉바오(선셋타운) 세 구역으로 나뉩니다. 공항에서 즈엉동까지 차로 10~15분이고, 그랜드월드 단지 숙소면 공항↔단지 무료 빈버스가 있습니다. 숙소는 1박·2인 기준 시 스타 리조트 7만 983원부터 세일링클럽 2베드룸 빌라 59만 2,363원까지입니다. 혼똠 케이블카 850,000동, 빈원더스 사파리 950,000동이라 3박4일에는 하나만 고르는 편이 낫습니다. 12월 강수량이 60mm로 연중 가장 건조합니다.",
        "hotels": [], "flight": "", "tripcomCity": "phu_quoc",
        "image": "images/v59/phu-quoc-3n4d-4n5d-course.jpg", "imageAlt": "푸꾸옥 해변과 리조트",
        "imageCredit": "사진: Pexels (Quang Nguyen Vinh)", "ogImage": "images/og/v59-phu-quoc-og.jpg",
        "stayCards": True,
        "giftFallback": "푸꾸옥 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 베트남 선물 리스트를 참고하세요.",
        "foodFallback": "푸꾸옥 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 3박4일 코스에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "공항 → 즈엉동", "v": "차로 10~15분 · 그랜드월드 숙소는 빈버스 무료"},
            {"k": "숙소 1박(2인)", "v": "시 스타 7만 983원 · 씨셸스 30만 9,983원 · 세일링클럽 59만 2,363원"},
            {"k": "케이블카·사파리", "v": "혼똠 케이블카 850,000동 · 빈원더스 사파리 950,000동"},
            {"k": "12월 날씨", "v": "평균 강수 60mm · 건기(11~4월)"},
        ],
        "guides": ["phu-quoc-3n4d-4n5d-course", "vietnam-4cities-comparison-guide", "vietnam-souvenir-list",
                   "visa-free-stay-duration-guide", "vietnam-esim", "sea-grab-taxi-scam-guide"],
        "updated": "2026-11-27",
    },
    {
        "slug": "cebu", "name": "세부", "nav": "세부", "cityIds": ["cebu"],
        "country": "ph", "flag": "ph", "kicker": "CEBU",
        "seoTitle": "세부 여행 숙소·막탄공항·오션젯 보홀 이동 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "세부 찐숙소 5곳 1박 4만 3,415원~13만 8,006원(2인). 막탄공항 MyBus 50페소, 오션젯 보홀 960페소·2시간, 오슬롭 1,000페소, 보홀까지 문에서 문 4시간.",
        "keywords": "세부 여행, 세부 숙소, 막탄 호텔, 세부 보홀 페리, 오션젯, 오슬롭 고래상어, 세부 3박4일, 막탄공항, 세부 리조트, 세부 시티",
        "h1": "세부 여행, <em>숙소·공항 이동·보홀 페리</em>를 한 페이지에",
        "intro": "세부는 공항이 있는 막탄섬과 세부시티, 남쪽 모알보알 세 권역으로 갈립니다. 막탄 리조트는 공항에서 10~20분, 세부시티는 15km·35~50분이고, 공항버스 MyBus는 50페소지만 22시 막차라 한국 직항 도착편으로는 타기 어렵습니다. 숙소는 1박·2인 기준 공항 호텔 4만 3,415원부터 마리바고 비치 리조트 13만 8,006원까지입니다. 보홀로 넘어가려면 피어1에서 오션젯 960페소·2시간을 타고, 타그빌라란에서 알로나까지 30~40분이 더 걸립니다.",
        "hotels": [], "flight": "",
        "image": "images/v59/cebu-3n4d-course.jpg", "imageAlt": "세부 막탄 해변과 리조트",
        "imageCredit": "사진: Pexels (Elaine Bernadine Castro)", "ogImage": "images/og/v59-cebu-og.jpg",
        "stayCards": True,
        "giftFallback": "세부 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 동남아 선물 리스트를 참고하세요.",
        "foodFallback": "세부 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 3박4일 코스에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "공항 → 시티", "v": "MyBus 50페소·07:00~22:00 · 세부시티 35~50분"},
            {"k": "숙소 1박(2인)", "v": "쎄프리 4만 3,415원 · 머큐어 7만 6,553원 · 마리바고 13만 8,006원"},
            {"k": "보홀 페리", "v": "오션젯 960페소·2시간·하루 10편 · 터미널료 25페소"},
            {"k": "오슬롭", "v": "고래상어 입장 1,000페소 · 새벽 출발 권장"},
        ],
        "guides": ["cebu-3n4d-course", "cebu-bohol-ferry-transfer-guide", "bohol-3n4d-course",
                   "visa-free-stay-duration-guide", "southeast-asia-injection-guide", "sea-grab-taxi-scam-guide"],
        "updated": "2026-11-27",
    },
    {
        "slug": "newyork", "name": "뉴욕", "nav": "뉴욕", "cityIds": ["newyork"],
        "country": "us", "flag": "us", "kicker": "NEW YORK",
        "seoTitle": "뉴욕 여행 숙소·JFK 공항 이동·전망대 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "뉴욕 찐숙소 5곳 1박 11만 8,148원~53만 4,667원(2인). JFK AirTrain $8.75+지하철 $3.00, 택시 $70, ESTA $40.62, 4박5일 현지 경비.",
        "keywords": "뉴욕 여행, 뉴욕 숙소, 맨해튼 호텔, JFK 공항 이동, AirTrain 요금, 뉴욕 4박5일, 자유의 여신상, 엠파이어스테이트 전망대, 미국 ESTA, 뉴욕 지하철",
        "h1": "뉴욕 여행, <em>숙소·공항 이동·전망대</em>를 한 페이지에",
        "intro": "뉴욕은 미드타운·다운타운·어퍼 웨스트로 숙소값이 갈립니다. JFK에서는 AirTrain $8.75에 지하철 $3.00을 더해 맨해튼까지 $11.75·60~75분이고, 택시는 맨해튼까지 $70 정액에 부대비용·팁이 붙습니다. 숙소는 1박·2인 기준 어퍼 웨스트 호스텔 11만 8,148원부터 브라이언트 파크 53만 4,667원까지입니다. 유료 전망대는 한 곳만 고르고, 자유의 여신상 $26과 메트 $30을 예산에 넣으세요. ESTA는 $40.62, 출발 72시간 전 신청입니다.",
        "hotels": [], "flight": "",
        "image": "images/v64/new-york-4n5d-course-budget.jpg", "imageAlt": "맨해튼 스카이라인과 엠파이어스테이트빌딩",
        "imageCredit": "사진: Pexels (Craig Adderley)", "ogImage": "images/og/v64-nyc-og.jpg",
        "stayCards": True,
        "giftFallback": "뉴욕 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전 준비물만 모았습니다.",
        "foodFallback": "뉴욕 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 4박5일 코스에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "JFK → 맨해튼", "v": "AirTrain $8.75 + 지하철 $3.00 = $11.75 · 60~75분"},
            {"k": "택시(JFK)", "v": "맨해튼 $70 정액 + 부대비용·팁 · 45~70분"},
            {"k": "숙소 1박(2인)", "v": "어퍼 웨스트 11만 8,148원 · 타임스스퀘어 20만 8,093원 · 브라이언트 53만 4,667원"},
            {"k": "입국", "v": "ESTA $40.62 · 2년 유효 · 출발 72시간 전 신청"},
        ],
        "guides": ["new-york-4n5d-course-budget", "us-esta-application-guide", "entry-immigration-guide",
                   "flight-cheap-booking-baggage", "travel-card-fees-comparison", "travel-insurance-guide"],
        "updated": "2026-11-27",
    },
    {
        "slug": "sydney", "name": "시드니", "nav": "시드니", "cityIds": ["sydney"],
        "country": "au", "flag": "au", "kicker": "SYDNEY",
        "seoTitle": "시드니 여행 숙소·공항 T8·오팔 카드 총정리 (2026년 11월) | 트립픽",
        "metaDesc": "시드니 찐숙소 5곳 1박 8만 9,632원~40만 2,192원(2인). 공항 T8 13~15분·역 이용료 18호주달러대, 오팔 주간 상한 50호주달러, 호주 ETA 20호주달러.",
        "keywords": "시드니 여행, 시드니 숙소, 시드니 공항 기차, 오팔 카드, 시드니 4박5일, 오페라하우스, 달링하버 호텔, 블루마운틴, 호주 ETA, 시드니 교통",
        "h1": "시드니 여행, <em>숙소·공항 기차·오팔 카드</em>를 한 페이지에",
        "intro": "시드니는 서큘러키·센트럴·달링하버 세 축으로 숙소가 나뉩니다. 공항에서는 T8 기차로 센트럴까지 13~15분이고, 공항역 이용료가 별도로 붙습니다. 오팔(또는 컨택리스 카드) 주간 상한은 50호주달러이고, 공항역은 이 상한과 따로 계산되는 주간 한도가 있습니다. 숙소는 1박·2인 기준 캡슐 8만 9,632원부터 샹그릴라 하버뷰 40만 2,192원까지입니다. 호주 ETA는 앱 수수료 20호주달러로 출발 전에 받습니다.",
        "hotels": [], "flight": "",
        "image": "images/v60/sydney-4n5d-course.jpg", "imageAlt": "시드니 오페라하우스와 하버브리지",
        "imageCredit": "사진: Pexels", "ogImage": "images/og/v60-sydney-og.jpg",
        "stayCards": True,
        "giftFallback": "시드니 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전 준비물만 모았습니다.",
        "foodFallback": "시드니 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 동선은 아래 4박5일 코스에 숫자로 계산해 두었습니다.",
        "tips": [
            {"k": "공항 → 센트럴", "v": "T8 기차 13~15분 · 공항역 이용료 별도"},
            {"k": "오팔 카드", "v": "주간 상한 50호주달러 · 공항역은 별도 한도"},
            {"k": "숙소 1박(2인)", "v": "캡슐 8만 9,632원 · 풀러턴 27만 7,164원 · 샹그릴라 40만 2,192원"},
            {"k": "입국", "v": "호주 ETA 앱 수수료 20호주달러 · 여권과 같은 이름"},
        ],
        "guides": ["sydney-4n5d-course", "oceania-eta-nzeta", "currency-payment-fees",
                   "travel-card-fees-comparison", "travel-insurance-guide", "flight-cheap-booking-baggage"],
        "updated": "2026-11-27",
    },
]


def main() -> int:
    # stays.json — 호텔·지역
    st = json.loads((D / "stays.json").read_text(encoding="utf-8"))
    have = {(h["region"], h["id"]) for h in st["hotels"]}
    for (region, hid, name, en, star, label, score, reviews, zone, access, reason, price, themes, tags) in HOTELS:
        if (region, hid) in have:
            continue
        sub = SCRAPED[region][[x["id"] for x in SCRAPED[region]].index(hid)]["sub"]
        cid = {"sapporo": "641"}.get(region) or next(r["cityId"] for r in REGIONS if r["id"] == region)
        st["hotels"].append({
            "region": region, "id": hid, "name": name, "en": en, "star": star,
            "type": "hotel", "typeLabel": label, "score": score, "reviews": reviews,
            "sub": {k: sub.get(k, "") for k in ("청결도", "시설", "위치", "서비스")},
            "zone": zone, "access": access, "reason": reason, "price": price,
            "priceBasis": BASIS, "img": f"images/stays/{region}-{hid}.jpg",
            "url": (f"https://kr.trip.com/hotels/detail/?cityId={cid}"
                    f"&hotelId={hid}&curr=KRW&Allianceid=11407530&SID=336341874"
                    f"&trip_sub1=stays_{region}_{hid}&trip_sub3=D21372570"),
            "themes": themes, "pointTags": tags,
        })
    regions = {r["id"]: r for r in st["regions"]}
    for r in REGIONS:
        if r["id"] in regions:
            regions[r["id"]].update(r)
        else:
            st["regions"].append(r)
    # sapporo 지역을 새 허브와 연결(기존 4곳 + 신규 5곳 = 9곳)
    sp = regions["sapporo"]
    sp["count"] = len([h for h in st["hotels"] if h["region"] == "sapporo"])
    sp["hub"] = "sapporo"
    sp["top"] = "삿포로 그랜드 호텔"
    (D / "stays.json").write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # city_hubs.json
    ch = json.loads((D / "city_hubs.json").read_text(encoding="utf-8"))
    slugs = {c["slug"] for c in ch["cities"]}
    for hub in HUBS:
        if hub["slug"] in slugs:
            continue
        ch["cities"].append(hub)
    ch["updated"] = "2026-11-27"
    (D / "city_hubs.json").write_text(json.dumps(ch, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"[v65] stays {len(st['hotels'])}곳 · regions {len(st['regions'])} · cities {len(ch['cities'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
