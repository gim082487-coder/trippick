#!/usr/bin/env python3
"""v56: 상품 데이터(tripcom·essentials·stays)와 오키나와 허브를 넣는다.

    python3 tools/apply_v56_data.py

숫자는 전부 2026-11-26 조회분이다.
- 트립닷컴 eSIM 목록: kr.trip.com/things-to-do/experiences/{hongkong,macau,chiangmai,bali,okinawa}-simcard/ 의 JSON-LD(ItemList.numberOfItems·Offer.price·reviewCount)
- 상품 상세: kr.trip.com/things-to-do/detail/{id}/ HTTP 200 + 한국어 title
- 공항픽업: kr.trip.com/airport-transfers/airport-{oka,hkg,cnx}/ 차종별 표시가
- 호텔: kr.trip.com/hotels/list (2026-12-10~11 · 온나 12-11~12 · 성인 2명 · KRW)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
AID = "Allianceid=11407530&SID=336341874"
SUB3 = "trip_sub3=D21303312"


def load(name):
    return json.loads((D / name).read_text(encoding="utf-8"))


def save(name, obj):
    (D / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# ────────────────────────────── tripcom.json ──────────────────────────────
ESIMS = [
    {
        "id": "esim_hongkong", "city": "홍콩", "cityId": "hongkong", "country": "홍콩", "flag": "hk",
        "category": "esim", "label": "eSIM·유심", "title": "홍콩 유심·eSIM",
        "highlight": "홍콩 eSIM 26개 상품 · 1일 112원부터",
        "summary": "홍콩 도착 전에 설치하는 5G eSIM·유심 26개 상품. 1일 요금제가 112원(4.7점·리뷰 3,498건, 듀얼 네트워크)부터이고, 1~30일 요금제가 대부분입니다. 마카오·중국 대륙을 함께 쓰는 5개 통신사 상품(1일 109원·리뷰 24,874건)과 6개 통신사·1~365일 상품(1일 106원)도 같은 목록에 있습니다. 홍콩 현지 유심은 실명등록이 필요하지만, QR로 설치하는 로밍 eSIM은 그 절차가 없습니다.",
        "products": 26, "fromPrice": 112,
        "url": f"https://kr.trip.com/things-to-do/experiences/hongkong-simcard/?{AID}&trip_sub1=esim_hongkong&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "esim_macau", "city": "마카오", "cityId": "macau", "country": "마카오", "flag": "mo",
        "category": "esim", "label": "eSIM·유심", "title": "마카오 유심·eSIM",
        "highlight": "마카오 eSIM 27개 상품 · 1일 106원부터",
        "summary": "마카오 도착 전에 설치하는 eSIM·유심 27개 상품. 중국 대륙·홍콩·마카오를 함께 쓰는 5개 통신사 상품이 1일 109원(4.6점·리뷰 24,874건), 6개 통신사·1~365일 상품이 1일 106원(4.5점·리뷰 8,345건)입니다. 마카오 전용 상품은 1일 241원(4.6점·리뷰 238건)부터이고, 홍콩을 같이 도는 일정이면 공용 상품 한 장이 계산이 쉽습니다.",
        "products": 27, "fromPrice": 106,
        "url": f"https://kr.trip.com/things-to-do/experiences/macau-simcard/?{AID}&trip_sub1=esim_macau&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "esim_chiangmai", "city": "치앙마이", "cityId": "chiangmai", "country": "태국", "flag": "th",
        "category": "esim", "label": "eSIM·유심", "title": "치앙마이 유심·eSIM",
        "highlight": "태국 eSIM 37개 상품 · 1일 110원부터",
        "summary": "치앙마이 도착 전에 설치하는 태국 eSIM·유심 37개 상품. 태국 5G eSIM이 1일 110원(4.6점·리뷰 16,554건)부터이고, 방콕·푸켓과 같은 상품을 씁니다. 현지 번호가 필요한 사람은 AIS(리뷰 4,729건)나 Dtac(리뷰 6,277건) 실명인증형이 1일 5,730원입니다.",
        "products": 37, "fromPrice": 110,
        "url": f"https://kr.trip.com/things-to-do/experiences/chiangmai-simcard/?{AID}&trip_sub1=esim_chiangmai&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "esim_bali", "city": "발리", "cityId": "bali", "country": "인도네시아", "flag": "id",
        "category": "esim", "label": "eSIM·유심", "title": "발리 유심·eSIM",
        "highlight": "인도네시아 eSIM 24개 상품 · 1일 101원부터",
        "summary": "발리 도착 전에 설치하는 인도네시아 eSIM·유심 24개 상품. 인도네시아 5G eSIM이 1일 101원(4.6점·리뷰 6,471건)부터이고 4대 통신사 지원 상품이 103원, 동남아 여러 나라 공용 상품이 110원입니다. 우붓·스미냑 모두 시내 데이터 속도는 비슷하고, 길리섬·누사페니다 쪽은 해상 구간에서 끊길 수 있습니다.",
        "products": 24, "fromPrice": 101,
        "url": f"https://kr.trip.com/things-to-do/experiences/bali-simcard/?{AID}&trip_sub1=esim_bali&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "esim_okinawa", "city": "오키나와", "cityId": "okinawa", "country": "일본", "flag": "jp",
        "category": "esim", "label": "eSIM·유심", "title": "오키나와 유심·eSIM",
        "highlight": "오키나와 eSIM 32개 상품 · 1일 101원부터",
        "summary": "오키나와 도착 전에 설치하는 일본 eSIM·유심 32개 상품. 일본 전역 5G 상품이 1일 110원(4.6점·리뷰 13,938건)부터이고, SoftBank 회선 5G가 1일 388원(4.7점·리뷰 13,841건), DOCOMO 회선이 1일 150원(4.4점·리뷰 919건)입니다. 렌터카로 북부까지 내려가면 도코모·소프트뱅크 커버리지 차이가 나므로 회선을 확인하세요.",
        "products": 32, "fromPrice": 101,
        "url": f"https://kr.trip.com/things-to-do/experiences/okinawa-simcard/?{AID}&trip_sub1=esim_okinawa&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
]

TRANSFERS = [
    {
        "id": "transfer_oka", "city": "오키나와", "cityId": "okinawa", "country": "일본", "flag": "jp",
        "category": "transfer", "label": "공항픽업", "title": "나하공항(OKA) 공항픽업",
        "highlight": "스탠다드 100,764원~ · 미니 73,768원~",
        "summary": "나하공항에서 나하 시내·온나·차탄까지 차종별 예약. 미니 차량 73,768원, 스탠다드 100,764원, 택시 114,028원, 비즈니스 6인승 120,917원, 미니버스 9인승 141,069원(2026-11-26 표시가). 짐이 많거나 밤 도착이면 모노레일(290엔·13분)과 비교해 인원수로 나눠 보세요.",
        "url": f"https://kr.trip.com/airport-transfers/airport-oka/?{AID}&trip_sub1=transfer_oka&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "transfer_hkg", "city": "홍콩", "cityId": "hongkong", "country": "홍콩", "flag": "hk",
        "category": "transfer", "label": "공항픽업", "title": "홍콩공항(HKG) 공항픽업",
        "highlight": "스탠다드 51,893원~ · 6인승 70,057원",
        "summary": "홍콩국제공항에서 침사추이·코즈웨이베이·센트럴까지 단독 차량. 스탠다드 51,893원, 중형 53,159원, 프리미엄 64,348원, 컴포트 플러스 65,906원, 비즈니스 6인승 70,057원(2026-11-26 표시가). 에어포트익스프레스 옥토퍼스 120홍콩달러와 인원수로 비교하면 2인은 공항철도, 4인은 차량이 낮아집니다.",
        "url": f"https://kr.trip.com/airport-transfers/airport-hkg/?{AID}&trip_sub1=transfer_hkg&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "transfer_cnx", "city": "치앙마이", "cityId": "chiangmai", "country": "태국", "flag": "th",
        "category": "transfer", "label": "공항픽업", "title": "치앙마이공항(CNX) 공항픽업",
        "highlight": "스탠다드 10,530원~ · 9인승 30,250원",
        "summary": "치앙마이국제공항에서 올드시티·님만해민까지 단독 차량. 스탠다드 10,530원, 컴포트 플러스 23,781원, 중형 24,184원, 미니버스 9인승 30,250원, 11인승 38,291원(2026-11-26 표시가). 공항 정액택시 150밧(약 5,940원)보다 비싸지만, 심야 도착이나 4인 이상이면 문 앞까지 가는 값으로 낫습니다.",
        "url": f"https://kr.trip.com/airport-transfers/airport-cnx/?{AID}&trip_sub1=transfer_cnx&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
]

TICKETS = [
    {
        "id": "ticket_okinawa", "city": "오키나와", "cityId": "okinawa", "country": "일본", "flag": "jp",
        "category": "ticket", "label": "입장권·액티비티", "title": "오키나와 입장권·액티비티",
        "highlight": "츄라우미 FunPASS·오키나와 월드·네오파크·정글리아",
        "summary": "오키나와 본섬 입장권·액티비티 4,819개 상품. 츄라우미 수족관 입장권과 어트랙션·교통 할인을 묶은 FunPASS가 41,048원(리뷰 307건), 오키나와 월드 15,800원(4.6점·리뷰 570건), 네오파크 오키나와 9,173원(4.4점·188건), 정글리아 오키나와 72,700원(3.4점·875건), 어린이나라 6,900원(4.6점·429건)입니다. 모노레일 1일 승차권과 쇼핑 할인권 묶음도 7,054원에 있습니다.",
        "url": f"https://kr.trip.com/things-to-do/experiences/okinawa/?{AID}&trip_sub1=ticket_okinawa&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "ticket_hongkong", "city": "홍콩", "cityId": "hongkong", "country": "홍콩", "flag": "hk",
        "category": "ticket", "label": "입장권·액티비티", "title": "홍콩 투어·액티비티",
        "highlight": "피크 트램 야경투어·란타우 360·빅토리아 하버",
        "summary": "홍콩 투어·액티비티 37개 상품. 피크 트램 익스프레스+센트럴 산책+빅토리아 하버 야경투어가 103,217원(4.7점·리뷰 32건), 란타우섬 360 케이블카+빅부다+타이오 투어 147,945원(4.7점·10건), 중환 타이퀸+야경+대관람차 코스 100,607원입니다. 공항철도·피크트램 같은 교통 패스형 상품은 별도 목록에 있습니다.",
        "url": f"https://kr.trip.com/things-to-do/experiences/hongkong/?{AID}&trip_sub1=ticket_hongkong&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "ticket_macau", "city": "마카오", "cityId": "macau", "country": "마카오", "flag": "mo",
        "category": "ticket", "label": "입장권·액티비티", "title": "마카오 투어·액티비티",
        "highlight": "야간 리조트투어·세계문화유산 시티투어·오픈탑 버스",
        "summary": "마카오 투어·액티비티 36개 상품. 윈 팰리스+그랜드 리스보아 야간투어가 42,649원(5.0점·1건), 세계문화유산 시티투어 44,894원, 야경 오픈탑 버스 투어 25,521원(4.7점·리뷰 72건), 7인승 전세차량 하루 20,203원(4.9점·30건)부터입니다. 반도와 코타이를 하루에 묶는 상품이 대부분입니다.",
        "url": f"https://kr.trip.com/things-to-do/experiences/macau/?{AID}&trip_sub1=ticket_macau&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "ticket_saipan", "city": "사이판", "cityId": "saipan", "country": "북마리아나 제도", "flag": "gu",
        "category": "ticket", "label": "입장권·액티비티", "title": "사이판 투어·액티비티",
        "highlight": "마나가하·그로토·버드섬 · 현지 액티비티 143개",
        "summary": "사이판 액티비티 143개 상품. 그로토(4.5점·리뷰 723건)와 버드섬(4.5점·525건)은 무료 입장으로 목록에 있고, 사이판·괌 공용 eSIM이 1,052원부터 섞여 있습니다. 마나가하섬·북부 렌터카 투어처럼 현지에서 붙이는 상품이 많아, 항공·숙소만 잡고 액티비티를 따로 예약하는 방식이 됩니다.",
        "url": f"https://kr.trip.com/things-to-do/experiences/saipan/?{AID}&trip_sub1=ticket_saipan&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "ticket_chiangmai", "city": "치앙마이", "cityId": "chiangmai", "country": "태국", "flag": "th",
        "category": "ticket", "label": "입장권·액티비티", "title": "치앙마이 투어·액티비티",
        "highlight": "도이인타논·스티키 폭포·치앙라이 일일투어",
        "summary": "치앙마이 투어 29개 상품. 도이인타논 국립공원 하이라이트+트레킹이 50,490원(4.7점·15건), 도이수텝·왓우몽 야간투어 21,384원(4.8점·35건), 스티키 폭포 반나절 18,384원(4.8점·26건), 치앙라이 3색 사원+롱넥 빌리지 59,270원(4.7점·43건)입니다. 올드시티 숙소에서 픽업하는 상품이 대부분입니다.",
        "url": f"https://kr.trip.com/things-to-do/experiences/chiangmai/?{AID}&trip_sub1=ticket_chiangmai&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
    {
        "id": "ticket_bali", "city": "발리", "cityId": "bali", "country": "인도네시아", "flag": "id",
        "category": "ticket", "label": "입장권·액티비티", "title": "발리 투어·액티비티",
        "highlight": "우붓 원숭이숲·누사페니다 스노클링·전용차량",
        "summary": "발리 투어 30개 상품. 프라이빗 차량 12시간 대절 52,526원(4.7점·213건), 우붓 원숭이숲·계단식 논·폭포 올인클루시브 42,546원(4.9점·749건), 누사페니다 3~4개 스팟 스노클링 16,162원(4.6점·49건), 한국어 운전기사 남부 데이투어 52,364원입니다. 우붓·스미냑 숙소 픽업이 기본입니다.",
        "url": f"https://kr.trip.com/things-to-do/experiences/bali/?{AID}&trip_sub1=ticket_bali&{SUB3}",
        "status": "verified_200_ko", "checked": "2026-11-26",
    },
]

FLIGHTS = [
    {"route": "서울 → 괌", "sub": "안토니오 B. 원팻(GUM) · 직항",
     "url": f"https://kr.trip.com/flights/Seoul-to-Guam/tickets-SEL-GUM?flighttype=S&dcity=SEL&acity=GUM&{AID}&trip_sub1=flight_sel_gum&trip_sub3=D21275837",
     "tags": ["flight"]},
    {"route": "서울 → 사이판", "sub": "프란시스코 C. 아다(SPN) · 직항",
     "url": f"https://kr.trip.com/flights/Seoul-to-Saipan/tickets-SEL-SPN?flighttype=S&dcity=SEL&acity=SPN&{AID}&trip_sub1=flight_sel_spn&trip_sub3=D21275837",
     "tags": ["flight"]},
]

HOTEL_CITIES = [
    {"city": "오키나와", "flag": "jp", "sub": "나하·온나 · 오키나와 3박4일", "note": "유이레일 공항역에서 13분",
     "url": f"https://kr.trip.com/hotels/list?city=92573&display=%EC%98%A4%ED%82%A4%EB%82%98%EC%99%80&optionId=92573&optionType=City&optionName=%EC%98%A4%ED%82%A4%EB%82%98%EC%99%80&{AID}&trip_sub1=hotel_okinawa&trip_sub3=D21372570",
     "cityId": "okinawa", "tags": ["value", "airport"]},
]


def patch_tripcom() -> None:
    t = load("tripcom.json")

    def add(key, rows):
        have = {r.get("id") for r in t[key] if "id" in r}
        have_routes = {r.get("route") for r in t[key]}
        added = 0
        for r in rows:
            if r.get("route"):
                if r["route"] in have_routes:
                    continue
            elif r["id"] in have:
                continue
            t[key].append(r)
            added += 1
        print(f"  tripcom.{key}: +{added}")

    add("esims", ESIMS)
    add("transfers", TRANSFERS)
    add("tickets", TICKETS)
    add("flights", FLIGHTS)
    have_city = {h.get("cityId") for h in t["hotels"]}
    for h in HOTEL_CITIES:
        if h["cityId"] not in have_city:
            t["hotels"].append(h)
            print("  tripcom.hotels: +1", h["city"])
    t["source"]["v56"] = (
        "2026-11-26: 홍콩·마카오·치앙마이·발리·오키나와 eSIM 목록 5건, 공항픽업 3건(나하·홍콩·치앙마이), "
        "투어·입장권 6건(오키나와·홍콩·마카오·사이판·치앙마이·발리), 항공권 2건(괌·사이판), 오키나와 호텔 목록 1건을 추가했습니다. "
        "모두 기존 검증 패턴(Allianceid 11407530/SID 336341874, trip_sub3 D21303312·D21275837·D21372570)이고, "
        "curl(iPhone UA) HTTP 200 + 한국어 title, 상품 수·최저가는 JSON-LD(ItemList.numberOfItems·Offer.price), "
        "공항픽업 차종별 요금은 페이지 표시가, 항공권 2건은 관리 브라우저에서 HTTP 200 + '서울 출발 괌/사이판 도착 저렴한 항공권' 제목으로 확인했습니다."
    )
    save("tripcom.json", t)


# ────────────────────────────── essentials.json ──────────────────────────────
ESS = [
    {
        "id": "hk-esim-trip-93409303", "partner": "trip.com", "category": "eSIM",
        "categoryLabel": "홍콩 eSIM(1일부터)", "store": "트립닷컴",
        "name": "홍콩 5G eSIM | 듀얼 네트워크 · All AI & TikTok | 1~30일 | QR코드",
        "price": 112, "listPrice": 112, "discountRate": 0, "rating": 4.7,
        "url": f"https://kr.trip.com/things-to-do/detail/93409303/?{AID}&trip_sub1=ess_hk_esim&{SUB3}",
        "productId": "93409303", "cities": ["홍콩", "마카오"], "courses": ["hongkong"],
        "reviews": 3498,
        "pitch": "홍콩 eSIM 목록 1위. 1일 112원부터, 4.7점·리뷰 3,498건·듀얼 네트워크.",
        "usage": "3박4일이면 4일 총량형이나 1일 2GB형을 고르고, 출국 전 QR로 설치합니다. 홍콩·마카오를 같이 돌면 마카오에서도 그대로 터집니다.",
        "caution": "표시가는 1일 최저가입니다. 총량형·무제한형은 값이 다르고, 기기 eSIM 지원 여부를 먼저 확인하세요.",
        "checkedAt": "2026-11-26",
    },
    {
        "id": "mo-esim-trip-100451304", "partner": "trip.com", "category": "eSIM",
        "categoryLabel": "마카오 eSIM(1일부터)", "store": "트립닷컴",
        "name": "마카오 5G eSIM | ChatGPT | 1~30일 | QR코드",
        "price": 241, "listPrice": 241, "discountRate": 0, "rating": 4.6,
        "url": f"https://kr.trip.com/things-to-do/detail/100451304/?{AID}&trip_sub1=ess_mo_esim&{SUB3}",
        "productId": "100451304", "cities": ["마카오"], "courses": ["macau"],
        "reviews": 238,
        "pitch": "마카오 전용 5G eSIM 1일 241원부터. 4.6점·리뷰 238건.",
        "usage": "마카오만 1~2일 도는 일정이면 이 상품, 홍콩을 같이 돌면 홍콩·마카오 공용 상품이 계산이 쉽습니다.",
        "caution": "표시가는 1일 최저가입니다. 마카오·홍콩 공용 상품(1일 106~109원)보다 단가가 높으니 일정에 맞춰 고르세요.",
        "checkedAt": "2026-11-26",
    },
    {
        "id": "th-esim-trip-46275998", "partner": "trip.com", "category": "eSIM",
        "categoryLabel": "태국 eSIM(1일부터)", "store": "트립닷컴",
        "name": "태국 5G eSIM | Google 지도 / ChatGPT 지원 | 일일·총 데이터 | 1~30일 | QR코드",
        "price": 110, "listPrice": 110, "discountRate": 0, "rating": 4.6,
        "url": f"https://kr.trip.com/things-to-do/detail/46275998/?{AID}&trip_sub1=ess_th_esim&{SUB3}",
        "productId": "46275998", "cities": ["방콕", "치앙마이"], "courses": ["bangkok", "chiangmai"],
        "reviews": 16554,
        "pitch": "태국 eSIM 1일 110원부터. 4.6점·리뷰 16,554건으로 태국 eSIM 중 후기가 가장 많습니다.",
        "usage": "방콕·치앙마이 모두 같은 상품입니다. 3박4일이면 4일 총량형 한 장, 영상통화가 많으면 1일 2GB형을 섞으세요.",
        "caution": "표시가는 1일 최저가입니다. 현지 번호·통화가 필요하면 AIS 실명인증형(1일 5,730원)을 따로 보세요.",
        "checkedAt": "2026-11-26",
    },
    {
        "id": "id-esim-trip-46278708", "partner": "trip.com", "category": "eSIM",
        "categoryLabel": "인도네시아(발리) eSIM(1일부터)", "store": "트립닷컴",
        "name": "인도네시아 5G eSIM | Google 지도 / ChatGPT 지원 | 일일·총 데이터 | 1~30일 | QR코드",
        "price": 101, "listPrice": 101, "discountRate": 0, "rating": 4.6,
        "url": f"https://kr.trip.com/things-to-do/detail/46278708/?{AID}&trip_sub1=ess_id_esim&{SUB3}",
        "productId": "46278708", "cities": ["발리"], "courses": ["bali"],
        "reviews": 6471,
        "pitch": "발리·인도네시아 eSIM 1일 101원부터. 4.6점·리뷰 6,471건.",
        "usage": "우붓·스미냑 3박4일이면 4일 총량형 한 장. 길리섬·누사페니다로 넘어가는 날은 해상 구간에서 끊길 수 있습니다.",
        "caution": "표시가는 1일 최저가입니다. 4대 통신사 지원 상품(1일 103원)이 커버리지가 넓습니다.",
        "checkedAt": "2026-11-26",
    },
    {
        "id": "jp-esim-trip-37658069", "partner": "trip.com", "category": "eSIM",
        "categoryLabel": "오키나와·일본 eSIM(SoftBank)", "store": "트립닷컴",
        "name": "일본 SoftBank 5G eSIM | 일본 IP · All AI & TikTok | 일일·총 데이터 | 1~30일",
        "price": 388, "listPrice": 388, "discountRate": 0, "rating": 4.7,
        "url": f"https://kr.trip.com/things-to-do/detail/37658069/?{AID}&trip_sub1=ess_jp_esim&{SUB3}",
        "productId": "37658069", "cities": ["오키나와"], "courses": ["okinawa"],
        "reviews": 13841,
        "pitch": "SoftBank 회선 5G eSIM 1일 388원부터. 4.7점·리뷰 13,841건.",
        "usage": "오키나와는 나하·온나 모두 SoftBank 커버리지가 좋습니다. 3박4일이면 4일 총량형 한 장으로 끝납니다.",
        "caution": "표시가는 1일 최저가입니다. 더 싼 일본 전역 상품(1일 110원)은 회선이 달라, 북부 산간에서 속도 차이가 날 수 있습니다.",
        "checkedAt": "2026-11-26",
    },
]


def patch_essentials() -> None:
    e = load("essentials.json")
    have = {p["id"] for p in e["products"]}
    n = 0
    for p in ESS:
        if p["id"] in have:
            continue
        e["products"].append(p)
        n += 1
    print(f"  essentials: +{n} (총 {len(e['products'])})")
    save("essentials.json", e)


# ────────────────────────────── stays.json ──────────────────────────────
OKI_BASIS = "2026-12-10~11 · 1박 · 성인 2명 · 세금·봉사료 포함 최저가"
ONNA_BASIS = "2026-12-11~12 · 1박 · 성인 2명 · 세금·봉사료 포함 최저가"
HK_BASIS = "2026-12-10~11 · 1박 · 성인 2명 · 세금·봉사료 포함 최저가"


def stay(region, city_id, hid, name, star, score, reviews, zone, access, reason, price, basis, themes, tags):
    return {
        "region": region, "id": hid, "name": name, "star": star, "type": "hotel", "typeLabel": "호텔",
        "score": score, "reviews": reviews, "zone": zone, "access": access, "reason": reason,
        "price": price, "priceBasis": basis,
        "img": f"images/stays/{region}-{hid}.jpg",
        "url": (f"https://kr.trip.com/hotels/detail/?cityId={city_id}&hotelId={hid}&curr=KRW"
                f"&Allianceid=11407530&SID=336341874&trip_sub1=stays_{region}_{hid}&trip_sub3=D21372570"),
        "themes": themes, "pointTags": tags,
    }


STAYS = [
    stay("okinawa", "92573", "2612287", "하얏트 리젠시 나하 오키나와", 5, 9.3, 1295,
         "나하(오모로마치)", "유이레일 오모로마치역 도보권 · 공항 20분",
         "리뷰 1,295개·9.3 — 나하 시내에서 국제거리와 오모로마치 사이에 있어 공항에서 모노레일로 20분 안팎입니다. "
         "수영장과 조식 평가가 좋아 3박4일 첫 숙소로 무난하고, 1박 22만 원대는 나하 5성 중 중간값입니다.",
         222461, OKI_BASIS, ["pool", "station"], ["오모로마치", "공항 20분"]),
    stay("okinawa", "92573", "7420938", "JR 규슈 호텔 블라섬 나하", 4, 9.3, 2002,
         "나하(마키시)", "유이레일 마키시역 도보 5분 · 국제거리 동쪽 끝",
         "리뷰 2,002개·9.3 — 국제거리 동쪽 끝 마키시역 도보 5분이라 저녁 식사와 쇼핑이 짧습니다. "
         "조식과 청결 평가가 높고, 하얏트보다 1박 1만 5천 원가량 낮습니다.",
         207924, OKI_BASIS, ["station", "value"], ["국제거리", "조식"]),
    stay("okinawa", "92573", "3916196", "알몬트 호텔 나하 겐초마에", 3, 9.2, 634,
         "나하(겐초마에)", "유이레일 겐초마에역 도보 2분",
         "리뷰 634개·9.2 — 겐초마에역에서 2분이라 공항 290엔·13분 동선이 그대로 이어집니다. "
         "1박 9만 5천 원대로 나하 시내 3성 중 평점이 높은 축이고, 방은 좁은 편입니다.",
         95239, OKI_BASIS, ["station", "value"], ["겐초마에", "가성비"]),
    stay("okinawa", "92573", "48522063", "호텔 칵테일 스테이 나하", 3, 9.0, 679,
         "나하(미에바시)", "유이레일 미에바시역 도보권 · 국제거리 가운데",
         "리뷰 679개·9.0 — 1박 6만 6,400원으로 나하 시내에서 가장 낮은 축입니다. "
         "국제거리 가운데 미에바시 쪽이라 식당·편의점이 도보권이고, 객실 크기를 감수하면 3박 예산을 20만 원 넘게 줄입니다.",
         66400, OKI_BASIS, ["value"], ["최저가", "국제거리"]),
    stay("okinawa", "35725", "1005498", "호텔 몬토레 오키나와 스파＆리조트", 4, 9.3, 1279,
         "온나손(기노자)", "만좌모·푸른동굴 차로 15분 · 해변 리조트",
         "리뷰 1,279개·9.3 — 온나손 해안 리조트로 수영장·스파와 오션뷰 객실이 있고, 만좌모·푸른동굴·츄라우미 쪽 동선에 가깝습니다. "
         "12월 11~12일 1박 20만 6,340원으로 나하 5성과 같은 값대라, 3박 중 하루를 리조트로 바꾸는 선택지가 됩니다.",
         206340, ONNA_BASIS, ["pool", "ocean", "villa"], ["리조트", "온나"]),
    stay("okinawa", "35725", "1182095", "베스트 웨스턴 오키나와 온나 비치", 3, 8.7, 141,
         "온나손(온나 선셋 비치)", "해변 바로 앞 · 만좌모 차로 20분",
         "리뷰 141개·8.7 — 온나 해변 바로 앞인데 1박 13만 2,221원으로 온나 리조트 중 가장 낮습니다. "
         "리뷰 수가 적은 대신 위치 값이 확실하고, 렌터카 없이 가면 이동이 불편합니다.",
         132221, ONNA_BASIS, ["ocean", "value"], ["비치프론트", "가성비"]),
    stay("hongkong", "58", "469825", "MK 스테이(이전 명칭: 호텔 MK)", 3, 8.0, 1819,
         "몽콕", "MTR 몽콕역 도보권 · 레이디스 마켓 인접",
         "리뷰 1,819개·8.0 — 몽콕 MTR 도보권에 1박 8만 4,386원으로 홍콩 6곳 중 가장 낮습니다. "
         "객실이 좁고 평점은 8.0이라, 잠만 자고 시내를 도는 3박4일에서 값을 아끼는 쪽입니다.",
         84386, HK_BASIS, ["value"], ["몽콕", "가성비"]),
    stay("hongkong", "58", "24403644", "엠파이어 프레스티지 침사추이", 5, 9.3, 7810,
         "침사추이", "침사추이 MTR·하버시티 도보권",
         "리뷰 7,810개·9.3 — 침사추이 5성 중 평점이 높고 하버시티·빅토리아 하버가 도보권입니다. "
         "1박 22만 7,449원으로 엠파이어 침사추이(18만 원대)보다 4만 원가량 비싸지만 조식과 객실 크기가 다릅니다.",
         227449, HK_BASIS, ["station"], ["침사추이", "5성"]),
    stay("macau", "59", "344977", "베네시안 마카오", 5, 9.5, 20160,
         "코타이", "코타이 스트립 중심 · 쇼핑몰·공연 건물 내",
         "리뷰 20,160개·9.5 — 코타이 5성 중 리뷰가 가장 많은 축입니다. "
         "1박 29만 5,590원으로 파리지앵(27만 원대)보다 2만 원가량 높고, 쇼핑몰·곤돌라·공연이 건물 안에 있습니다.",
         295590, HK_BASIS, ["pool", "villa"], ["코타이", "5성"]),
    stay("macau", "59", "531723", "골든 크라운 차이나 호텔", 3, 8.5, 4280,
         "마카오 반도(북쪽)", "세나도 광장 도보 20분 · 국경 검문소 인접",
         "리뷰 4,280개·8.5 — 1박 7만 9,551원으로 마카오 6곳 중 최저입니다. "
         "세나도 광장까지 걸어 20분 안팎이고, 홍콩에서 대교 셔틀로 들어와 하루 묵는 일정에 맞습니다.",
         79551, HK_BASIS, ["value"], ["반도", "가성비"]),
]


def patch_stays() -> None:
    s = load("stays.json")
    have = {h["id"] for h in s["hotels"]}
    n = 0
    for h in STAYS:
        if h["id"] not in have:
            s["hotels"].append(h)
            n += 1
    print(f"  stays.hotels: +{n}")
    regions = {r["id"]: r for r in s["regions"]}
    if "okinawa" not in regions:
        s["regions"].append({
            "id": "okinawa", "name": "오키나와", "country": "일본",
            "note": "나하는 유이레일 한 줄로 공항·국제거리·슈리성이 이어지고, 온나·차탄은 렌터카로 40~60분 걸립니다. 3박4일이면 나하 2박+온나 1박, 시내만 보면 나하 3박이 이동이 짧습니다.",
            "count": 0, "top": "", "listUrl":
            (f"https://kr.trip.com/hotels/list?city=92573&display=%EC%98%A4%ED%82%A4%EB%82%98%EC%99%80&optionId=92573"
             f"&optionType=City&optionName=%EC%98%A4%ED%82%A4%EB%82%98%EC%99%80&{AID}&trip_sub1=hotel_okinawa&trip_sub3=D21372570"),
            "cityId": "92573", "scope": "intl", "hub": None,
            "guides": [{"slug": "okinawa-3n4d-course", "label": "오키나와 3박4일"}],
        })
        regions = {r["id"]: r for r in s["regions"]}
    for rid in ("okinawa", "hongkong", "macau"):
        rows = [h for h in s["hotels"] if h["region"] == rid]
        regions[rid]["count"] = len(rows)
        regions[rid]["top"] = max(rows, key=lambda h: h["score"])["name"]
    s["source"]["v56"] = (
        "2026-11-26: 오키나와 지역(나하 4·온나 2 = 6곳)을 새로 넣고, 홍콩에 MK 스테이·엠파이어 프레스티지 침사추이, "
        "마카오에 베네시안 마카오·골든 크라운 차이나를 추가했습니다. 가격은 트립닷컴 숙소 목록에서 2026-12-10~11"
        "(온나 12-11~12) 성인 2명·세금 포함 최저가로 조회한 값이고, 카드마다 기준일을 적었습니다."
    )
    save("stays.json", s)


# ────────────────────────────── city_hubs.json ──────────────────────────────
OKINAWA_HUB = {
    "slug": "okinawa", "name": "오키나와", "nav": "오키나와",
    "cityIds": ["okinawa"], "country": "jp", "flag": "jp", "kicker": "OKINAWA",
    "seoTitle": "오키나와 여행 숙소·렌터카·츄라우미·3박4일 총정리 (2026년 11월) | 트립픽",
    "metaDesc": "오키나와 숙소 6곳 1박 6만 6,400원~22만 2,461원(2인), 츄라우미 2,180엔, 유이레일 공항→국제거리 290엔·13분, eSIM 1일 101원부터.",
    "keywords": "오키나와 여행, 오키나와 3박4일, 나하 숙소, 온나 리조트, 츄라우미 수족관, 오키나와 렌터카, 유이레일, 오키나와 eSIM",
    "h1": "오키나와 여행, <em>숙소·렌터카·츄라우미</em>를 한 페이지에",
    "intro": (
        "오키나와는 나하 시내와 온나·차탄 리조트 지역이 차로 40~60분 떨어져 있어, 3박을 어디에 나눌지가 하루 동선을 정합니다. "
        "숙소는 1박·2인 기준 호텔 칵테일 스테이 나하 6만 6,400원, 알몬트 겐초마에 9만 5,239원, JR 규슈 블라섬 나하 20만 7,924원, "
        "하얏트 리젠시 나하 22만 2,461원, 온나 리조트는 베스트 웨스턴 온나 비치 13만 2,221원·몬토레 오키나와 20만 6,340원입니다. "
        "공항에서 국제거리까지 유이레일 290엔·13분이고, 츄라우미 수족관은 성인 2,180엔, 렌터카는 컴팩트 24시간 6,600엔부터입니다."
    ),
    "giftFallback": "오키나와 선물·기념품 가격표는 매장별 확인이 끝나면 다음 업데이트에 넣습니다. 그전까지는 출발 전에 사 두면 현지에서 번거로운 준비물만 모았습니다.",
    "foodFallback": "오키나와 맛집은 영업 여부와 메뉴판 가격을 확인한 뒤 싣습니다. 그전까지 식비와 하루 동선은 아래 3박4일 코스 가이드에 숫자로 계산해 두었습니다.",
    "hotels": ["okinawa"],
    "image": "images/v56/okinawa.jpg",
    "imageAlt": "오키나와 바다와 해안 도로",
    "imageCredit": "사진: Pexels",
    "ogImage": "images/og/v56-okinawa-og.jpg",
    "stayCards": True,
    "tips": [
        {"k": "공항 → 국제거리", "v": "유이레일 290엔·13분. 첫차 6:00·막차 23:30, 1일권 1,000엔"},
        {"k": "숙소 1박(2인)", "v": "칵테일 스테이 6만 6,400원 · JR 블라섬 20만 7,924원 · 몬토레 온나 20만 6,340원"},
        {"k": "츄라우미 수족관", "v": "성인 2,180엔(고등학생 1,440·초중학생 710). 8:30 개장, 재입장 가능"},
        {"k": "렌터카", "v": "컴팩트 24시간 6,600~8,910엔 · 나하~허도 ETC 35.5% 할인(2027-03-31까지)"},
    ],
    "guides": [
        "okinawa-3n4d-course", "japan-rental-car-etc-guide", "japan-esim",
        "airport-arrival-city-transfer-guide", "overseas-roaming-esim-install-troubleshooting",
        "travel-card-fees-comparison", "travel-insurance-guide", "hotel-booking-timing-refund-tips",
    ],
    "updated": "2026-11-26",
}


def patch_hubs() -> None:
    c = load("city_hubs.json")
    slugs = {h["slug"] for h in c["cities"]}
    if "okinawa" not in slugs:
        # 도쿄 다음(일본 도시끼리 붙게) 넣는다
        idx = next((i for i, h in enumerate(c["cities"]) if h["slug"] == "fukuoka"), len(c["cities"]))
        c["cities"].insert(idx + 1, OKINAWA_HUB)
        print("  city_hubs: +okinawa")
    save("city_hubs.json", c)


if __name__ == "__main__":
    print("v56 데이터 반영")
    patch_tripcom()
    patch_essentials()
    patch_stays()
    patch_hubs()
    print("완료")
