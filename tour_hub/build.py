#!/usr/bin/env python3
"""
트립픽(tour_hub) 정적 페이지 생성기 v4
------------------------------------
template.html 의 마커 자리에 data/*.json 내용을 그려 index.html 을 만듭니다.

    python3 build.py               # index.html 다시 생성
    python3 build.py --check       # 생성 결과가 현재 파일과 같은지 확인
    python3 build.py --out X.html  # 다른 경로로 미리보기 빌드(index.html 유지)

상품은 data/tours.json, 추천 코스는 data/courses.json,
여행 필수품은 data/essentials.json, 현장 추가금 추정과 계산기 설정은 data/planner.json,
검색용 FAQ는 data/faq.json 이 원본입니다.
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "template.html"
INDEX = ROOT / "index.html"

COUNTRIES = [
    ("kr", "국내 (제주·부산·강원)", "f-kr"),
    ("jp", "일본", "f-jp"),
    ("vn", "베트남", "f-vn"),
    ("th", "태국", "f-th"),
    ("tw", "대만", "f-tw"),
    ("eu", "유럽", "f-eu"),
    ("us", "미주·하와이", "f-us"),
    ("oc", "대양주", "f-oc"),
    ("cn", "중국", "f-cn"),
    ("gu", "괌·사이판", "f-gu"),
]
COUNTRY_NAME = {c: n for c, n, _ in COUNTRIES}
FLAG_SYMBOL = {c: f for c, _, f in COUNTRIES}
TYPE_ORDER = ["가이드투어", "풀패키지", "세미패키지", "에어텔", "골프패키지", "국내패키지", "레저·액티비티"]
PREMIUM_FLOOR = 3_000_000

ESS_GROUPS = [
    ("여행용품", "🧳 여행 준비물 · 쿠팡", "출발 3일 전에 주문하면 배송일 안에 도착"),
    ("eSIM", "📶 eSIM · 데이터", "도착 전에 설치하고 내리면 바로 켭니다"),
    ("교통패스", "🎫 교통 패스", "공항에서 시내까지, 하루 종일 타는 패스"),
    ("교통", "🚄 공항철도 · 셔틀", "예약 없이 타는 열차·버스"),
    ("공항픽업", "🚗 공항 픽업", "새벽 도착도 추가금 없는 단독차량"),
    ("입장권", "🎟️ 입장권", "현장 줄 서지 않고 바로 입장"),
]


PLANNER = json.loads((DATA / "planner.json").read_text(encoding="utf-8"))
FAQ = json.loads((DATA / "faq.json").read_text(encoding="utf-8"))
EXTRAS = PLANNER["extras"]
ESS_BY_ID = {e["id"]: e for e in json.loads((DATA / "essentials.json").read_text(encoding="utf-8"))["products"]}

DEPART_RE = re.compile(r"(인천|부산|대구|청주|김포|묵호)\s*출발")
KR_DEPART = {
    "jeju": "전국 출발(항공)",
    "ulleung": "묵호항 출발",
    "busan": "광안리·해운대 현장",
    "gangwon": "현지(비발디·강릉)",
}

def flag_svg(country: str, w: int = 18, h: int = 12.6) -> str:
    sym = FLAG_SYMBOL.get(country)
    if not sym:
        return ""
    return f'<svg class="flag-ic" style="width:{w}px;height:{h}px" aria-hidden="true"><use href="#{sym}"/></svg>'


def won(n: int) -> str:
    return f"{n:,}"


def esc(s) -> str:
    return escape(str(s), quote=True)


def duration_text(d: str) -> str:
    try:
        h, m = d.split(":")
        h, m = int(h), int(m)
    except ValueError:
        return d
    return f"{h}시간" + (f" {m}분" if m else "")


def pct_off(t: dict) -> int:
    if t["price"] <= t["sale"]:
        return 0
    return round((t["price"] - t["sale"]) / t["price"] * 100)


def is_noshop(t: dict) -> bool:
    return "노쇼핑" in (t.get("tags") or [])


def is_team_item(t: dict) -> bool:
    """팀·척·차량 단위로 파는 상품인가 (인원수 곱셈 제외 대상).

    priceUnit="team" 인 상품만 해당한다. 예) 부산 라나요트 단독대여 249,000원은
    1팀(1척) 단가이므로 2명이어도 2배가 되지 않는다.
    """
    return t.get("priceUnit") == "team"


def is_premium(t: dict) -> bool:
    return t["sale"] >= PREMIUM_FLOOR


# ---------------------------------------------------------------- 현장 추가금·출발지
def extra_rec(t: dict) -> dict:
    return EXTRAS.get(t["id"], {"krw": 0, "basis": "", "aside": "", "partial": False})


def real_price(t: dict) -> int:
    return t["sale"] + extra_rec(t)["krw"]


def depart_of(t: dict) -> str:
    m = DEPART_RE.search(t["title"])
    if m:
        return f"{m.group(1)} 출발"
    if t["country"] == "kr":
        return KR_DEPART.get(t["city"], "현지")
    return "현지 집결"


def flights_of(t: dict) -> bool:
    return "항공" in (t.get("includes") or "")


def trip_days(t: dict) -> int:
    for src in (t.get("duration") or "", t.get("title") or ""):
        m = re.search(r"(\d+)박\s*(\d+)일", src)
        if m:
            return int(m.group(2))
    return 1


def shopping_count(t: dict):
    """태그에 적힌 쇼핑 횟수. 노쇼핑은 0, 표기가 없으면 None."""
    if is_noshop(t):
        return 0
    for tag in t.get("tags") or []:
        m = re.search(r"쇼핑\s*(\d)\s*회", tag)
        if m:
            return int(m.group(1))
    return None


# ---------------------------------------------------------------- 상품 카드
def tag_html(t: dict) -> str:
    """카드 위 배지는 최대 2개 — 대표 라벨 + (노쇼핑 또는 출발확정)만."""
    hot = t["label"] in ("인기 1위", "베스트", "최저가", "베스트셀러")
    cls = "tag hot" if hot else "tag"
    out = f'<span class="{cls}">{esc(t["label"])}</span>'
    if is_noshop(t) and "노쇼핑" not in t["label"]:
        out += '<span class="tag noshop">노쇼핑</span>'
    elif t.get("booked") in ("출발확정", "실시간 확정") and t["booked"] not in t["label"]:
        out += f'<span class="tag confirm">{esc(t["booked"])}</span>'
    return out


def rating_html(t: dict) -> str:
    star = ('<svg class="star" viewBox="0 0 24 24" aria-hidden="true">'
            '<path d="m12 3.6 2.6 5.4 5.9.8-4.3 4.1 1 5.9-5.2-2.9-5.2 2.9 1-5.9L3.5 9.8l5.9-.8L12 3.6Z"/></svg>')
    if t.get("rating") in (None, "", "—"):
        if t.get("country") == "kr":
            return f'<p class="rate">{star}정상가 그대로 비교 <span>· 할인 표기 없음</span></p>'
        booked = t.get("booked") or "가격·조건 한눈에 비교"
        return f'<p class="rate">{star}{esc(booked)} <span>· 네이버 여행 기준</span></p>'
    rv = t["reviews"] or 0
    rv_txt = f'{rv/10000:.1f}만' if rv >= 10000 else (f'{rv:,}' if rv else "")
    tail = f' <span>· 리뷰 {rv_txt} · 네이버 쇼핑 기준</span>' if rv else ' <span>· 네이버 쇼핑 기준</span>'
    return f'<p class="rate">{star}{esc(t["rating"])}{tail}</p>'


def price_html(t: dict) -> str:
    pct = pct_off(t)
    badge = f'<span class="pct">{pct}%</span>' if pct else '<span class="pct flat">정가</span>'
    was = f'<s>{won(t["price"])}원</s>' if pct else ''
    # 팀·척 단위 상품은 "1인"이 아니라 "1팀" 기준임을 카드에 밝힌다.
    unit = "/ 1팀(1척)" if is_team_item(t) else "/ 1인"
    return f'<div class="priceline">{badge}<b>{won(t["sale"])}원</b>{was}<span class="unit">{unit}</span></div>'


def real_line(t: dict) -> str:
    ex = extra_rec(t)
    if not ex["krw"]:
        return ""
    tip = f'현장 추가금 근거: {ex["basis"]}'
    return (f'<p class="real" title="{esc(tip)}">현장 추가금 포함 실질 '
            f'<b>{won(real_price(t))}원</b></p>')


def card_html(t: dict, order: int, extra_cls: str = "") -> str:
    search_key = " ".join([
        t["title"], t["seller"], t.get("theme", ""), t.get("label", ""),
        t.get("type", ""), COUNTRY_NAME.get(t["country"], ""), t["city_label"],
        " ".join(t.get("tags", [])),
    ]).lower()

    specs = [
        f'<li><svg class="ic" aria-hidden="true"><use href="#i-clock"/></svg><span>{esc(duration_text(t["duration"]))}</span></li>',
        f'<li><svg class="ic" aria-hidden="true"><use href="#i-pin"/></svg><span>{esc(t["meetShort"])}</span></li>',
        f'<li class="{"alert" if "별도" in t["ticket"] else ""}"><svg class="ic" aria-hidden="true"><use href="#i-ticket"/></svg><span>{esc(t["ticket"])}</span></li>',
    ]
    ex = extra_rec(t)
    if t["extraFees"]:
        label = f'현장 +{won(ex["krw"])}원' if ex["krw"] else "현장 추가금"
        specs.append('<li class="alert" title="' + esc(ex["basis"]) + '">'
                     '<svg class="ic" aria-hidden="true"><use href="#i-info"/></svg>'
                     f'<span>{esc(label)}</span></li>')

    caution = (f'<p class="caution"><svg class="ic" aria-hidden="true"><use href="#i-info"/></svg>'
               f'<span>{esc(t["caution"])}</span></p>') if t.get("caution") else ""

    return f"""<article class="pcard{(' ' + extra_cls) if extra_cls else ''}" data-id="{t['id']}" data-city="{t['city']}" data-country="{t['country']}"
        data-type="{esc(t.get('type',''))}" data-fee="{t.get('fee', 3)}"
        data-extra="{1 if t['extraFees'] else 0}" data-korean="{1 if '한국어' in t['guide'] else 0}"
        data-notip="{1 if '노팁' in t.get('tags', []) else 0}" data-noshop="{1 if is_noshop(t) else 0}"
        data-premium="{1 if is_premium(t) else 0}" data-private="{1 if t.get('private') else 0}"
        data-price="{t['sale']}" data-cancel="{t['cancelDays']}" data-order="{order}" data-search="{esc(search_key)}">
        <div class="thumb">
          <img src="{esc(t['img'])}" srcset="{esc(t['img'])} 660w, {esc(t['imgLg'])} 1200w"
               sizes="(max-width:620px) 92vw, (max-width:1000px) 46vw, 380px"
               width="1200" height="800" alt="{esc(t['theme'])} — {esc(t['title'])}" loading="lazy" />
          {tag_html(t)}
        </div>
        <div class="body">
          <p class="loc">{flag_svg(t['country'], 15, 10.5)}<span>{esc(t['city_label'])} · {esc(t['seller'])}</span></p>
          <h3>{esc(t['title'])}</h3>
          {rating_html(t)}
          <ul class="specs">{''.join(specs)}</ul>
          <p class="cancels"><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>{esc(t['cancelShort'])}</p>
          {caution}
          {price_html(t)}
          {real_line(t)}
          <div class="card-actions">
            <a class="book" href="{esc(t['url'])}" target="_blank" rel="noopener sponsored">{(lambda u: "네이버에서 구매" if "shopping-connect" == t.get("affiliate") else "네이버 여행에서 예약")(t["url"])} <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>
            <button class="cmp-btn" type="button" data-cmp-add="{t['id']}" aria-pressed="false" title="이 상품을 비교 바구니에 담기">비교</button>
          </div>
        </div>
      </article>"""


def table_row(t: dict) -> str:
    if t["extraFees"]:
        more = f' 외 {len(t["extraFees"]) - 1}건' if len(t["extraFees"]) > 1 else ""
        extra = f'<span class="extra">⚠ {esc(t["extraFees"][0])}{more}</span>'
    else:
        extra = '<span class="none">없음</span>'
    minpax = (
        '<span class="na">상세페이지 확인 필요</span>'
        if "확인" in t["minPax"]
        else f'{esc(t["minPax"])} / {esc(t["maxPax"])}'
    )
    pct = pct_off(t)
    price_cell = (f'<span class="was">{won(t["price"])}원</span>{won(t["sale"])}원 <em>{pct}% 할인가</em>'
                  if pct else f'{won(t["sale"])}원 <em>정가 판매</em>')
    return f"""<tr data-id="{t['id']}">
              <td class="pname"><a href="{esc(t['url'])}" target="_blank" rel="noopener sponsored">{esc(t['title'])}</a><span>{esc(t['seller'])} · {esc(t['type'])}</span></td>
              <td class="price">{price_cell}</td>
              <td class="cell">{esc(t['duration'])}<br /><span class="na">{esc(t['guide'])}</span></td>
              <td class="cell">{esc(t['meeting'])}<br /><span class="na">{esc(t['meetingTime'])}</span></td>
              <td class="cell">{esc(t['includes'])}</td>
              <td class="cell">{extra}</td>
              <td class="cell">{minpax}</td>
              <td class="cell">{esc(t['cancel'])}</td>
            </tr>"""


def promo_tile(city: dict, count: int, wide: bool = False) -> str:
    if count == 1:
        title = f"{esc(city['title'])} 상품<br />가격·조건 상세표"
        sub = "미팅 장소·포함 내역·취소 규정을 한 줄로 정리했어요"
        kicker = "DETAIL"
    else:
        title = f"{esc(city['title'])} {count}개 상품<br />가격·조건 비교표"
        sub = "입장료·현장 추가금·취소 규정을 한 줄로 정리했어요"
        kicker = "COMPARE"
    cls = "promo promo--wide" if wide else "promo"
    return f"""<button class="{cls}" type="button" data-open-cmp="{city['id']}">
        <span class="promo-ic"><svg class="ic" aria-hidden="true"><use href="#i-ticket"/></svg></span>
        <span class="promo-kicker">{kicker}</span>
        <b>{title}</b>
        <span class="promo-sub">{sub}</span>
        <span class="promo-go">표 펼쳐보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span>
      </button>"""


def city_section(city: dict, items: list, tours: list) -> str:
    lowest = min(t["sale"] for t in items)
    korean_n = sum(1 for t in items if "한국어" in t["guide"])
    free_n = sum(1 for t in items if "자유" in t["guide"])
    extra_count = sum(1 for t in items if t["extraFees"])
    types = []
    for t in items:
        if t["type"] not in types:
            types.append(t["type"])
    cards = "\n        ".join(
        card_html(t, tours.index(t), "pcard--wide" if len(items) == 1 else "") for t in items
    )
    grid_cls = "pgrid"
    strip = ""
    if len(items) == 1:
        grid_cls += " pgrid--single"
        cards += "\n        " + promo_tile(city, len(items))
    elif len(items) % 3 == 1:
        grid_cls += " pgrid--two"
    elif len(items) % 3 == 2:
        cards += "\n        " + promo_tile(city, len(items))
    rows = "\n            ".join(table_row(t) for t in items)

    if korean_n == len(items):
        guide_stat = "전 상품 한국어 가이드"
    elif korean_n and free_n:
        guide_stat = f"한국어 가이드 {korean_n}개 · 자유일정 {free_n}개"
    elif free_n == len(items):
        guide_stat = "전 상품 자유일정(가이드 없음)"
    else:
        guide_stat = "가이드 언어 확인"

    stats = [
        f'<span class="stat low">최저 {won(lowest)}원</span>',
        f'<span class="stat">상품 {len(items)}개 · {"·".join(types)}</span>',
        f'<span class="stat{" warn" if extra_count else ""}">현장 추가금 {extra_count}개 상품</span>',
        f'<span class="stat">{guide_stat}</span>',
    ]
    tc_city = TC_CITY.get(city["id"])
    if tc_city:
        stats.append(
            f'<a class="stat stat-link" href="#tripcom" data-tc-city="{esc(tc_city[0])}">'
            f'🏨 {esc(tc_city[1])} 숙소·항공 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
        )

    return f"""<section class="city" id="{city['id']}" data-country="{city['country']}">
      <div class="city-head">
        <div class="city-title">
          <span class="flag" aria-hidden="true">{flag_svg(city['country'], 25, 17.5)}</span>
          <h2>{esc(city['title'])}</h2>
          <span class="cnt">{len(items)}개 상품</span>
        </div>
        <p class="sub">{esc(city['tagline'])}</p>
        <div class="city-stats">
          {''.join(stats)}
        </div>
      </div>

      <div class="{grid_cls}">
        {cards}
      </div>{strip}

      <details class="cmp">
        <summary>
          <span class="lhs"><svg class="ic" aria-hidden="true"><use href="#i-ticket"/></svg><span>{esc(city['title'])} {len(items)}개 상품, 가격·조건 한눈에 비교표</span></span>
          <span class="hint">표 펼치기</span>
        </summary>
        <div class="table-wrap">
          <table class="compare">
            <caption class="sr-only">{esc(city['title'])} 네이버 여행 상품 {len(items)}개 비교표</caption>
            <thead>
              <tr>
                <th scope="col">상품</th>
                <th scope="col">가격(1인)</th>
                <th scope="col">소요·가이드</th>
                <th scope="col">미팅·시각</th>
                <th scope="col">포함 사항</th>
                <th scope="col">현장 추가금</th>
                <th scope="col">최소/최대 인원</th>
                <th scope="col">취소 규정</th>
              </tr>
            </thead>
            <tbody>
            {rows}
            </tbody>
          </table>
        </div>
        <p class="scroll-hint">표는 좌우로 넘겨서 볼 수 있습니다. 취소선은 할인 전 판매가이고, ‘상세페이지 확인 필요’는 판매 페이지에 값이 표기되지 않은 항목입니다.</p>
      </details>
    </section>"""


# ---------------------------------------------------------------- 탭/필터/검색
def country_counts(tours: list) -> dict:
    counts = {c: 0 for c, _, _ in COUNTRIES}
    for t in tours:
        if t["country"] in counts:
            counts[t["country"]] += 1
    return counts


def render_quickstrip(data: dict, courses: dict, essentials: dict, tripcom: dict) -> str:
    tc_flights = tripcom["flights"]
    tc_hotels = tripcom["hotels"]
    tours = data["tours"]
    counts = country_counts(tours)
    kr_n = counts.get("kr", 0)
    sea_n = counts.get("vn", 0) + counts.get("th", 0)
    west_n = counts.get("eu", 0) + counts.get("us", 0) + counts.get("oc", 0)

    items = [
        f'<a class="qn accent" href="#regions"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-search"/></svg></span><b>투어 찾기</b><i>{len(tours)}개</i></a>',
        f'<a class="qn" href="#tripcom"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-plane"/></svg></span><b>숙소·항공</b><i>{len(tc_flights) + len(tc_hotels)}개</i></a>',
        f'<a class="qn" href="#planner"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-won"/></svg></span><b>예산 계산기</b><i>1분</i></a>',
        '<a class="qn" href="#checklist"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-check"/></svg></span><b>출국 준비</b><i>입국서류</i></a>',
        f'<a class="qn" href="#essentials"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-signal"/></svg></span><b>필수품</b><i>{len(essentials["products"])}개</i></a>',
        '<a class="qn" href="guides/"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-compass"/></svg></span><b>여행 가이드</b><i>36편</i></a>',
        '<a class="qn" href="#alert"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-bell"/></svg></span><b>특가 알림</b><i>무료</i></a>',
        f'<a class="qn" href="#courses"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-image"/></svg></span><b>여행 코스</b><i>{len(courses["courses"])}개</i></a>',
        f'<button class="qn" type="button" data-quick-scope="kr"><span class="qn-ic"><svg class="flag-ic" aria-hidden="true"><use href="#f-kr"/></svg></span><b>국내</b><i>{kr_n}개</i></button>',
        f'<button class="qn" type="button" data-quick-scope="jp"><span class="qn-ic"><svg class="flag-ic" aria-hidden="true"><use href="#f-jp"/></svg></span><b>일본</b><i>{counts.get("jp", 0)}개</i></button>',
        f'<button class="qn" type="button" data-quick-scope="sea"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-sun"/></svg></span><b>동남아</b><i>{sea_n}개</i></button>',
        f'<button class="qn" type="button" data-quick-scope="eu_us"><span class="qn-ic"><svg aria-hidden="true"><use href="#i-globe"/></svg></span><b>유럽·미주</b><i>{west_n}개</i></button>',
    ]
    return "\n    ".join(items)


def render_hot_strip(data: dict, courses: dict, essentials: dict, tripcom: dict) -> str:
    """모바일 첫 화면용 '최저가 바로가기' 6장 (v10).

    도시별 최저가 상품 4개 + 트립닷컴 숙소 1개 + eSIM 1개를 실제 제휴 링크로 바로 건다.
    데스크톱에서는 CSS 로 숨기고, 모바일(<=768px)에서만 보인다.
    """
    tours = data["tours"]
    cards = []
    for city in ("osaka", "tokyo", "danang", "jeju"):
        items = [t for t in tours if t["city"] == city]
        if not items:
            continue
        t = min(items, key=lambda x: x["sale"])
        short = re.split(r"\s*[(（]", t["title"])[0].strip()
        cards.append(
            f'<a class="hot-c" href="{esc(t["url"])}" target="_blank" rel="noopener sponsored">'
            f'<span class="hot-th"><img src="{esc(t["img"])}" alt="" width="320" height="180" loading="lazy" /></span>'
            f'<span class="hot-k">{flag_svg(t["country"], 13, 9.1)} {esc(t["city_label"])}</span>'
            f'<b>{esc(short)}</b>'
            f'<span class="hot-p">{won(t["sale"])}원~ <em>1인</em></span></a>'
        )

    hotel = next((h for h in tripcom["hotels"] if h.get("cityId") == "osaka"), tripcom["hotels"][0])
    cards.append(
        f'<a class="hot-c" href="{esc(hotel["url"])}" target="_blank" rel="noopener sponsored">'
        f'<span class="hot-th hot-th--ic"><svg aria-hidden="true"><use href="#i-pin"/></svg></span>'
        f'<span class="hot-k">트립닷컴 · 숙소</span>'
        f'<b>{esc(hotel["city"])} 숙소 최저가 검색</b>'
        f'<span class="hot-p">가격비교 <em>무료취소</em></span></a>'
    )

    esim = next((e for e in essentials["products"] if e["id"] == "jp-esim-usimsa-3d"), None)
    if esim:
        cards.append(
            f'<a class="hot-c" href="{esc(ess_url(esim))}" target="_blank" rel="noopener sponsored">'
            f'<span class="hot-th hot-th--ic"><svg aria-hidden="true"><use href="#i-signal"/></svg></span>'
            f'<span class="hot-k">일본 · eSIM</span>'
            f'<b>일본 eSIM 3일 무제한</b>'
            f'<span class="hot-p">{won(esim["price"])}원~ <em>도착 즉시</em></span></a>'
        )

    head = ('<div class="hot-head"><b>지금 눈에 띄는 최저가</b><span>1인 기준</span>'
            f'<a href="#regions">투어 {len(tours)}개 전체 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a></div>')
    return head + '<div class="hot-row">' + "".join(cards) + "</div>"


def render_city_select(data: dict) -> str:
    tours = data["tours"]
    counts = country_counts(tours)
    per_city = {}
    for t in tours:
        per_city[t["city"]] = per_city.get(t["city"], 0) + 1
    out = ['<option value="all">전체 여행지</option>']
    for code, name, _ in COUNTRIES:
        if not counts[code]:
            continue
        out.append(f'<option value="{code}">{esc(name)} 전체</option>')
        for c in data["cities"]:
            if c["country"] == code and per_city.get(c["id"]):
                out.append(f'<option value="{c["id"]}">{esc(name)} · {esc(c["name"])}</option>')
    return ("\n            ").join(out)


def render_country_tabs(data: dict) -> str:
    tours = data["tours"]
    counts = country_counts(tours)
    out = [f'<button type="button" role="tab" class="ctab" data-scope="all" aria-selected="true">전체 <b class="n">{len(tours)}</b></button>']
    for code, name, sym in COUNTRIES:
        if counts[code]:
            out.append(
                f'<button type="button" role="tab" class="ctab" data-scope="{code}" aria-selected="false">'
                f'<svg class="flag-ic"><use href="#{sym}"/></svg> {esc(name)} <b class="n">{counts[code]}</b></button>'
            )
    return ("\n      ").join(out)


def render_city_chips(data: dict) -> str:
    per_city = {}
    for t in data["tours"]:
        per_city[t["city"]] = per_city.get(t["city"], 0) + 1
    out = []
    for c in data["cities"]:
        n = per_city.get(c["id"])
        if not n:
            continue
        out.append(
            f'<button type="button" class="cchip" data-city="{c["id"]}" data-country="{c["country"]}">'
            f'{flag_svg(c["country"], 14, 9.8)} {esc(c["name"])} <span class="n">{n}</span></button>'
        )
    return ("\n        ").join(out)


def render_typebar(data: dict) -> str:
    tours = data["tours"]
    type_counts = {}
    for t in tours:
        type_counts[t["type"]] = type_counts.get(t["type"], 0) + 1
    types = ['<button class="chip type-chip" type="button" data-type="all" aria-pressed="true">전체 유형</button>']
    for typ in TYPE_ORDER:
        if type_counts.get(typ):
            types.append(f'<button class="chip type-chip" type="button" data-type="{esc(typ)}" aria-pressed="false">{esc(typ)} <b>{type_counts[typ]}</b></button>')
    notip = sum(1 for t in tours if "노팁" in (t.get("tags") or []))
    noshop = sum(1 for t in tours if is_noshop(t))
    premium = sum(1 for t in tours if is_premium(t))
    filters = [
        f'<button class="chip" type="button" data-filter="notip" aria-pressed="false">노팁 <b>{notip}</b></button>',
        f'<button class="chip" type="button" data-filter="noshop" aria-pressed="false">노쇼핑 <b>{noshop}</b></button>',
        '<button class="chip" type="button" data-filter="korean" aria-pressed="false">한국어 가이드</button>',
        f'<button class="chip" type="button" data-filter="premium" aria-pressed="false">300만원+ <b>{premium}</b></button>',
    ]
    return ('<div class="tgroup">' + "".join(types) + '</div>'
            '<div class="tgroup tgroup--filters">' + "".join(filters) + '</div>')


# ---------------------------------------------------------------- 추천 코스
PRICE_TEXT = {
    "danang-bana-hills": "4,890원~",
    "tokyo-skyliner": "12,200원~",
    "tokyo-metro-pass": "5,600원~",
}


def course_item_html(item: dict, tours_by_id: dict, ess_by_id: dict) -> str:
    if item["kind"] == "tour":
        t = tours_by_id[item["ref"]]
        kind = t["type"]
        name = t["title"]
        price = f'{won(t["sale"])}원'
        url = t["url"]
    else:
        e = ess_by_id[item["ref"]]
        kind = e.get("categoryLabel") or e["category"]
        name = e["name"]
        price = PRICE_TEXT.get(e["id"]) or f'{won(e["price"])}원'
        url = ess_url(e)
    note = f'<span class="tdl-why">{esc(item["note"])}</span>' if item.get("note") else ""
    warn = (f'<p class="tdl-note"><svg class="ic" aria-hidden="true"><use href="#i-info"/></svg>{esc(item["warn"])}</p>'
            if item.get("warn") else "")
    return f"""<a class="tdl" href="{esc(url)}" target="_blank" rel="noopener sponsored">
                  <span class="tdl-kind">{esc(kind)}</span>
                  <span class="tdl-txt"><b>{esc(name)}</b>{note}</span>
                  <span class="tdl-price">{esc(price)}</span>
                  <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg>
                </a>{warn}"""


def course_pick(course: dict, idx: int, link_count: int) -> str:
    sel = "true" if idx == 0 else "false"
    nights = ""
    m = re.search(r"(\d박\s*\d일)", course["title"])
    if m:
        nights = m.group(1)
    return f"""<button type="button" class="pick" role="tab" data-course="{course['id']}" aria-selected="{sel}"
        aria-controls="course-{course['id']}" id="cpick-{course['id']}">
        <img src="{esc(course['img'])}" alt="{esc(course['title'])} 대표 사진" width="1600" height="1000" loading="lazy" />
        <span class="pk-tag">{esc(course.get('tag', nights))}</span>
        <span class="pk-b"><b>{esc(course['title'])}</b><span class="pk-d">{len(course['days'])}일 일정 · 예약 링크 {link_count}곳</span></span>
      </button>"""


def course_panel(course: dict, idx: int, tours_by_id: dict, ess_by_id: dict) -> str:
    days = []
    link_count = 0
    for d in course["days"]:
        items = "\n              ".join(course_item_html(i, tours_by_id, ess_by_id) for i in d["items"])
        link_count += len(d["items"])
        if d.get("img"):
            photo = (f'<div class="day-photo"><img src="{esc(d["img"])}" alt="{esc(d["title"])}" '
                     f'width="900" height="600" loading="lazy" /></div>')
        else:
            photo = '<div class="day-photo empty"><svg aria-hidden="true"><use href="#i-image"/></svg></div>'
        links = (f'<div class="day-links">\n              {items}\n              </div>'
                 if d["items"] else
                 '<p class="day-free"><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>자유일정 · 예약할 것이 없습니다</p>')
        days.append(f"""<li class="day">
            <div class="day-no"><span>DAY</span><b>{d['no']}</b></div>
            {photo}
            <div class="day-main">
              <h4>{esc(d['title'])}</h4>
              <p class="day-memo">{esc(d['memo'])}</p>
              {links}
            </div>
          </li>""")

    pkg = course["package"]
    p = tours_by_id[pkg["ref"]]
    more_n = len(course["days"]) - 2
    days_more = ("" if more_n < 1 else
                 f'<button class="days-more" type="button" data-days-more aria-expanded="false" '
                 f'data-more-label="남은 {more_n}일 일정 더 보기">남은 {more_n}일 일정 더 보기 '
                 '<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></button>')
    active = " active" if idx == 0 else ""
    hidden = "" if idx == 0 else " hidden"
    why = "".join(f"<li>{esc(w)}</li>" for w in course.get("why", []))
    prices = [tours_by_id[i["ref"]]["sale"] for d in course["days"] for i in d["items"] if i["kind"] == "tour"]
    lowest = min(prices) if prices else p["sale"]

    return f"""<div class="panel{active}" id="course-{course['id']}" role="tabpanel" aria-labelledby="cpick-{course['id']}"{hidden}>
      <div class="panel-hero">
        <img src="{esc(course['img'])}" alt="{esc(course['title'])} 분위기 사진" width="1600" height="1000" loading="lazy" />
        <div class="ph-t">
          <div class="left">
            <span class="ph-k">COURSE {idx + 1:02d} · {esc(COUNTRY_NAME.get(course['country'], ''))} · {esc(course.get('tag', ''))}</span>
            <h3>{esc(course['title'])}</h3>
            <p class="ph-hook">{esc(course.get('hook', ''))}</p>
          </div>
          <div class="ph-facts">
            <span><b>{len(course['days'])}일</b> 일정</span>
            <span>예약 링크 <b>{link_count}곳</b></span>
            <span>최저 <b>{won(lowest)}원</b>~</span>
          </div>
        </div>
      </div>

      <div class="panel-body">
        <div class="p-main">
          <p class="p-lead">{esc(course['lead'])}</p>
          <ol class="timeline">
            {''.join(days)}
          </ol>
          {days_more}
        </div>

        <aside class="side">
          <div class="side-card why-card">
            <span class="side-k"><svg aria-hidden="true"><use href="#i-compass"/></svg>왜 이 코스인가</span>
            <ul class="why-list">{why}</ul>
          </div>
          <div class="side-card lodge">
            <span class="side-k"><svg aria-hidden="true"><use href="#i-pin"/></svg>숙소 추천 지역</span>
            <b>{esc(course['lodge']['area'])}</b>
            <p>{esc(course['lodge']['note'])}</p>
            <a class="lodge-link" href="#alert">특가 뜨면 알림 신청 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>
          </div>
          <a class="side-card pkg" href="{esc(p['url'])}" target="_blank" rel="noopener sponsored">
            <span class="pkg-k">항공+숙소까지 한 번에</span>
            <b>{esc(p['title'])}</b>
            <span class="pkg-p">{won(p['sale'])}원~ · {esc(p['seller'])}</span>
            <span class="pkg-n">{esc(pkg['note'])}</span>
            <span class="pkg-go">패키지 보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span>
          </a>
        </aside>
      </div>
    </div>"""


def render_course_picker(courses: dict, tours_by_id: dict, ess_by_id: dict) -> str:
    out = []
    for idx, c in enumerate(courses["courses"]):
        n = sum(len(d["items"]) for d in c["days"])
        out.append(course_pick(c, idx, n))
    return ("\n      ").join(out)


def render_course_panels(courses: dict, tours_by_id: dict, ess_by_id: dict) -> str:
    return ("\n\n    ").join(
        course_panel(c, i, tours_by_id, ess_by_id) for i, c in enumerate(courses["courses"])
    )


# ---------------------------------------------------------------- 여행 필수품
def ess_url(e: dict) -> str:
    """제휴 링크: 쿠팡 파트너스는 url, 네이버 커넥트는 naverMe."""
    return e.get("url") or e["naverMe"]


def ess_cta(e: dict) -> str:
    return "쿠팡에서 구매" if e.get("partner") == "coupang" else "네이버에서 구매"


def render_essentials(essentials: dict) -> str:
    groups = {}
    for e in essentials["products"]:
        groups.setdefault(e["category"], []).append(e)

    blocks = []
    for key, label, note in ESS_GROUPS:
        items = groups.get(key, [])
        if not items:
            continue
        cards = []
        for e in items:
            city = e.get("cities", ["공통"])[0]
            flag = ""
            for code, cname, _ in COUNTRIES:
                if city in ("오사카", "도쿄", "후쿠오카", "삿포로") and code == "jp":
                    flag = flag_svg("jp", 13, 9.1)
                elif city in ("다낭", "나트랑", "푸꾸옥", "호이안") and code == "vn":
                    flag = flag_svg("vn", 13, 9.1)
            city_txt = "모든 여행지" if city == "공통" else city
            thumb = ""
            if e.get("image"):
                thumb = (f'<span class="ess-thumb"><img src="{esc(e["image"])}" alt="{esc(e["name"])}"'
                         f' width="400" height="400" loading="lazy" /></span>')
            if e.get("listPrice") and e["listPrice"] > e["price"]:
                price_html = f'{won(e["price"])}원<small class="sl">{won(e["listPrice"])}원</small>'
            else:
                price_html = f'{won(e["price"])}원<small>~</small>'
            cards.append(f"""<a class="ess" href="{esc(ess_url(e))}" target="_blank" rel="noopener sponsored">
              {thumb}
              <span class="ess-k">{flag}{esc(city_txt)} · {esc(e.get('categoryLabel') or e['category'])}</span>
              <b>{esc(e['name'])}</b>
              <span class="ess-store">{esc(e['store'])}</span>
              <span class="ess-foot"><span class="ess-price">{price_html}</span>
                <span class="ess-go">{ess_cta(e)} <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span></span>
            </a>""")
        cp_note = (""
                   if key != "여행용품" else
                   '<p class="ess-cp-note">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다. '
                   '가격·재고는 2026년 11월 17일 확인 기준이며 판매자가 수시로 바꿀 수 있습니다.</p>')
        grid_cls = "ess-grid ess-grid-4" if key == "여행용품" else "ess-grid"
        blocks.append(f"""<div class="ess-group">
      <div class="ess-ghead"><h3>{label}</h3><span class="n">{len(items)}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">{esc(note)}</span></div>
      <div class="{grid_cls}">
        {''.join(cards)}
      </div>
      {cp_note}
    </div>""")
    return "\n    ".join(blocks)


# ---------------------------------------------------------------- 출국 준비 체크리스트
def render_checklist(check: dict, ess_by_id: dict, tripcom: dict) -> str:
    """나라를 고르면 입국서류·기내반입·준비물 체크가 바뀌는 인터랙티브 섹션.

    체크 상태는 브라우저 localStorage 에 저장하고, 서버는 나라별 패널을 모두 그려 둔 뒤
    JS 가 보이는 패널만 바꾼다. 스크립트가 꺼져 있어도 첫 나라 내용은 읽을 수 있다.
    """
    tc_by_city = {h.get("cityId"): h for h in tripcom["hotels"] if h.get("cityId")}
    pb = check["powerbank"]
    liquid = check["liquid"]
    tabs, panels = [], []
    for i, c in enumerate(check["countries"]):
        on = i == 0
        tabs.append(
            f'<button class="cl-tab{" on" if on else ""}" type="button" role="tab" id="cltab-{c["id"]}"'
            f' aria-controls="clpanel-{c["id"]}" aria-selected="{"true" if on else "false"}" data-cl-tab="{c["id"]}">'
            f'{flag_svg(c["flag"], 16, 11.2)}<b>{esc(c["name"])}</b><span>{esc(c["badge"])}</span></button>'
        )

        docs = []
        for d in c["docs"]:
            must = '<em class="cl-must">필수</em>' if d.get("must") else '<em class="cl-opt">선택</em>'
            fee = ""
            if d.get("fee") and d["fee"] not in ("—", "-", ""):
                fee = f'<span class="cl-doc-fee">{esc(d["fee"])}</span>'
            link = (f'<a class="cl-doc-go" href="{esc(d["url"])}" target="_blank" rel="noopener">공식 사이트</a>'
                    if d.get("url") else "")
            docs.append(
                f'<li><div class="cl-doc-h"><b>{esc(d["name"])}</b>{must}{fee}</div>'
                f'<p>{esc(d["note"])}</p>'
                f'<div class="cl-doc-m"><span>{esc(d["when"])}</span>{link}</div></li>'
            )

        items = []
        for it in c["checklist"]:
            hint = f'<i>{esc(it["hint"])}</i>' if it.get("hint") else ""
            items.append(
                f'<li><label class="cl-item"><input type="checkbox" data-cl-id="{c["id"]}:{esc(it["id"])}" />'
                f'<span class="cl-box" aria-hidden="true"></span>'
                f'<span class="cl-txt"><b>{esc(it["label"])}</b>{hint}</span></label></li>'
            )

        links = []
        for eid in c.get("links", []):
            e = ess_by_id.get(eid)
            if not e:
                continue
            links.append(
                f'<a class="cl-link" href="{esc(ess_url(e))}" target="_blank" rel="noopener sponsored">'
                f'<span class="cl-link-k">{esc(e.get("categoryLabel") or e["category"])}</span>'
                f'<b>{esc(e["name"])}</b><span class="cl-link-p">{won(e["price"])}원</span></a>'
            )
        tc_city = c.get("tcCity") or ""
        if tc_city and tc_city in tc_by_city:
            h = tc_by_city[tc_city]
            links.append(
                f'<a class="cl-link cl-link--tc" href="#tripcom" data-tc-city="{esc(tc_city)}">'
                f'<span class="cl-link-k">숙소·항공</span><b>{esc(h["city"])} 숙소 최저가(트립닷컴)</b>'
                f'<span class="cl-link-p">{esc(h["sub"])}</span></a>'
            )

        notes = "".join(f"<li>{esc(n)}</li>" for n in c.get("notes", []))
        panels.append(f"""<div class="cl-panel" id="clpanel-{c['id']}" role="tabpanel" aria-labelledby="cltab-{c['id']}" data-cl-panel="{c['id']}"{' hidden' if not on else ''}>
      <div class="cl-grid">
        <div class="cl-col">
          <div class="cl-block">
            <div class="cl-h"><h3>입국서류·수수료</h3><span class="cl-fee">{esc(c['feeTotal'])}</span></div>
            <p class="cl-sum">{esc(c['summary'])}</p>
            <ul class="cl-docs">{''.join(docs)}</ul>
          </div>
        </div>
        <div class="cl-col">
          <div class="cl-block">
            <div class="cl-h"><h3>출발 전 체크</h3><span class="cl-prog"><b data-cl-count>0</b>/{len(c['checklist'])}</span></div>
            <div class="cl-bar" aria-hidden="true"><i data-cl-bar></i></div>
            <ul class="cl-items">{''.join(items)}</ul>
            <button class="cl-reset" type="button" data-cl-reset="{c['id']}">이 나라 체크 초기화</button>
          </div>
        </div>
      </div>
      <div class="cl-grid cl-grid--2">
        <details class="cl-block cl-fold" data-mfold open>
          <summary class="cl-h"><h3>기내반입 규정</h3><span class="cl-tag">2026.4.20 기준</span></summary>
          <dl class="cl-facts">
            <div><dt>보조배터리</dt><dd>{esc(pb['rule'])}</dd></div>
            <div><dt>액체류</dt><dd>{esc(liquid['rule'])}</dd></div>
            <div><dt>전원·플러그</dt><dd>{esc(c['plug'])}</dd></div>
            <div><dt>현금</dt><dd>{esc(c['cash'])}</dd></div>
          </dl>
          <ul class="cl-notes">{notes}</ul>
        </details>
        <div class="cl-block">
          <div class="cl-h"><h3>이 나라 준비물 바로 사기</h3><span class="cl-tag">제휴</span></div>
          <div class="cl-links">{''.join(links)}</div>
        </div>
      </div>
    </div>""")

    examples = "".join(
        f'<tr><td>{ex["mah"]:,}mAh</td><td class="num">{ex["wh"]}</td><td>{"기내 2개까지" if ex["mah"] <= 27000 else "항공사 승인"}</td></tr>'
        for ex in pb["examples"]
    )
    src = " · ".join(pb["sources"][:3])
    return f"""<div class="cl-tabs" role="tablist" aria-label="나라 선택">{''.join(tabs)}</div>
    {''.join(panels)}
    <details class="cl-calc-box" data-mfold open>
    <summary class="cl-calc-sum">보조배터리 mAh → Wh 계산기 <span>기내 반입 기준</span></summary>
    <div class="cl-calc">
      <div class="cl-calc-in">
        <h3>보조배터리 mAh → Wh 계산기</h3>
        <p>항공사가 보는 기준은 mAh가 아니라 Wh(와트시)입니다. 보조배터리 셀 전압 3.7V로 환산합니다.</p>
        <label class="cl-input"><span>표시 용량(mAh)</span>
          <input id="clMah" type="number" inputmode="numeric" min="0" step="1000" placeholder="20000" aria-label="보조배터리 용량 mAh" />
        </label>
        <div class="cl-verdict" id="clVerdict" aria-live="polite">용량을 넣으면 기내 반입 가능 여부가 바로 나옵니다.</div>
        <p class="cl-calc-note">충전·사용은 기내에서 금지이고, 위탁 수하물에는 어떤 용량도 넣을 수 없습니다. 단자 테이프·개별 지퍼백으로 단락을 막으세요.</p>
      </div>
      <div class="cl-calc-out">
        <h4>용량별 기준</h4>
        <table class="cl-table"><thead><tr><th scope="col">표시 용량</th><th scope="col" class="num">환산</th><th scope="col">기내 반입</th></tr></thead>
        <tbody>{examples}</tbody></table>
        <p class="cl-src">기준: {esc(src)}. 160Wh 초과는 반입 불가입니다.</p>
      </div>
    </div>
    </details>
    <p class="cl-note">수수료·규정은 {esc(check['updated'])} 확인 기준입니다. 정부 요금은 예고 없이 바뀌므로 결제·출국 직전에 각 공식 사이트에서 다시 확인하세요. 체크 상태는 이 브라우저에만 저장되며 서버로 보내지 않습니다.</p>"""


# ---------------------------------------------------------------- 트립닷컴 제휴
def render_tripcom(tc: dict) -> str:
    """트립닷컴 파트너스 전용 숙소·항공 큐레이션.

    네이버·쿠팡 링크와 섞지 않고 이 섹션 안에서만 노출한다.
    숙소 카드는 data-tags·data-city 를 달아 필터 탭과 지역 섹션의 딥링크가 같은 카드를 가리키게 한다.
    """
    flights = "".join(
        f'<a class="tc-flight" href="{esc(f["url"])}" target="_blank" rel="noopener sponsored">'
        f'<span class="tc-fr">{esc(f["route"])}</span>'
        f'<span class="tc-fs">{esc(f["sub"])}</span>'
        f'<span class="tc-go">항공권 검색 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span>'
        f'</a>'
        for f in tc["flights"]
    )
    hotels = "".join(
        f'<a class="tc-card" href="{esc(h["url"])}" target="_blank" rel="noopener sponsored"'
        f' data-city="{esc(h.get("cityId", ""))}" data-tags="{esc(" ".join(h.get("tags", [])))}">'
        f'<span class="tc-city">{esc(h["city"])}{flag_svg(h["flag"], 14, 9.8)}</span>'
        f'<span class="tc-sub">{esc(h["sub"])}</span>'
        f'<span class="tc-note">{esc(h["note"])}</span>'
        f'<span class="tc-go">숙소 최저가 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span>'
        f'</a>'
        for h in tc["hotels"]
    )
    filters = tc.get("filters") or [
        ("all", "전체"),
        ("value", "가성비 숙소"),
        ("family", "가족·리조트"),
        ("airport", "공항 이동 편한 곳"),
        ("flight", "항공권"),
    ]
    tabs = "".join(
        f'<button class="tc-tab{" on" if i == 0 else ""}" type="button" data-tc-filter="{esc(f["id"] if isinstance(f, dict) else f[0])}"'
        f' aria-pressed="{"true" if i == 0 else "false"}">'
        f'{esc(f["label"] if isinstance(f, dict) else f[1])}</button>'
        for i, f in enumerate(filters)
    )
    src = tc["source"]
    return f"""<div class="tc-filter">
      <div class="tc-tabs" role="group" aria-label="트립닷컴 숙소·항공 필터">{tabs}</div>
      <p class="tc-filter-note" id="tcFilterNote">숙소 {len(tc["hotels"])}곳·항공 {len(tc["flights"])}개 노선을 용도별로 추렸습니다. 지역 섹션의 ‘이 도시 숙소’ 버튼을 누르면 그 도시 카드로 바로 내려갑니다.</p>
    </div>
    <div class="tc-group" data-tc-group="flight">
      <div class="ess-ghead"><h3>✈️ 항공권 검색</h3><span class="n">{len(tc["flights"])}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">편도 기준 · 실시간 최저가</span></div>
      <div class="tc-flights">{flights}</div>
    </div>
    <div class="tc-group" data-tc-group="hotel">
      <div class="ess-ghead"><h3>🏨 도시별 숙소</h3><span class="n">{len(tc["hotels"])}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">체크인 날짜를 넣으면 그날 최저가로 열립니다</span></div>
      <div class="tc-grid">{hotels}</div>
      <p class="tc-empty" id="tcEmpty" hidden>이 분류에 해당하는 숙소가 아직 없습니다. ‘전체’로 돌아가면 도시 15곳을 모두 볼 수 있습니다.</p>
      <p class="ess-cp-note">{esc(tc["disclosure"])} 링크는 {esc(src["checked"])} 트립닷컴 파트너스에서 발급했고, 요율은 호텔 5~7%·국제선 항공 0.5~0.8%(예약 건수에 따라)입니다.</p>
    </div>"""


# ---------------------------------------------------------------- 예산 계산기
def style_score(t: dict, style: str) -> float:
    tags = t.get("tags") or []
    tagset = " ".join(tags)
    price = t["sale"]
    typ = t["type"]
    s = 0.0
    if style == "value":
        if typ == "에어텔":
            s += 34
        if "자유일정" in tagset:
            s += 16
        if "최저가" in tagset:
            s += 15
        if typ == "세미패키지":
            s += 8
        if typ == "국내패키지":
            s += 8
        if typ == "레저·액티비티":
            s -= 6
        if typ == "가이드투어":
            s -= 10
        if "골프" in tagset:
            s -= 18
        s -= price / 150_000
    elif style == "nosh":
        if is_noshop(t):
            s += 45
        if "노팁" in tags:
            s += 14
        if "노옵션" in tags:
            s += 10
        if "인솔자동행" in tags:
            s += 9
        if typ == "풀패키지":
            s += 10
        if typ in ("세미패키지", "에어텔"):
            s += 4
        if typ == "레저·액티비티":
            s -= 45
        if typ == "가이드투어":
            s -= 22
        if "골프" in tagset:
            s -= 20
        s += min(price / 300_000, 10)
        sh = shopping_count(t)
        if sh:
            s -= 25 * sh
    elif style == "family":
        if "효도" in tags:
            s += 40
        if "가족" in tags:
            s += 34
        if "온천" in tags:
            s += 12
        if "5성호텔" in tagset or "5성리조트" in tagset:
            s += 10
        if "조식포함" in tags:
            s += 8
        if "인솔자동행" in tags:
            s += 8
        if t["ticket"].startswith("입장료 포함"):
            s += 8
        if typ == "풀패키지":
            s += 12
        if typ == "세미패키지":
            s += 10
        if typ == "국내패키지":
            s += 8
        if typ in ("레저·액티비티", "가이드투어"):
            s -= 35
        if "골프" in tagset:
            s -= 25
        sh = shopping_count(t)
        if sh:
            s -= 6 * sh
    elif style == "active":
        if typ == "레저·액티비티":
            s += 50
        for k, w in (("요트", 10), ("스키", 10), ("스노우래프팅", 14), ("호핑투어", 10), ("골프", 8),
                     ("바나힐", 8), ("트래킹", 12), ("크루즈", 6), ("단독대여", 8), ("리프트", 10),
                     ("골드패스", 12), ("워터파크", 10), ("온천", 4), ("체험", 4)):
            if k in tagset or k in t["title"]:
                s += w
        if typ == "풀패키지":
            s += 4
        if "자유일정" in tags:
            s -= 8
    return s


ACTIVITY_KW = ("요트", "스키", "스노우래프팅", "호핑투어", "골프", "바나힐", "트래킹", "크루즈",
                "단독대여", "리프트", "골드패스", "워터파크")


def activity_key(t: dict) -> str:
    hay = " ".join(t.get("tags") or []) + " " + t["title"]
    for k in ACTIVITY_KW:
        if k in hay:
            return k
    return ""


def combo_note(pool: list, style: str) -> str:
    """지역에 그 스타일의 전용 상품이 아예 없을 때만 한 줄로 알린다."""
    if style == "nosh" and not any(is_noshop(t) for t in pool):
        return "이 지역엔 쇼핑 0회 상품이 없어, 쇼핑 횟수가 적고 가격대가 높은 상품 위주로 골랐습니다."
    if style == "family" and not any(("효도" in (t.get("tags") or []) or "가족" in (t.get("tags") or [])) for t in pool):
        return "가족·효도 전용 상품이 없어 5성 호텔·온천·조식 포함 상품 위주로 골랐습니다."
    if style == "active" and not any(t["type"] == "레저·액티비티" for t in pool):
        return "전용 액티비티 상품이 없어 트래킹·워터파크·온천처럼 몸을 쓰는 일정으로 골랐습니다."
    if style == "value" and not any(t["type"] == "에어텔" for t in pool):
        return "자유여행(에어텔) 상품이 없는 지역이라 가장 저렴한 패키지로 골랐습니다."
    return ""


TRANSIT = {"osaka": "osaka-nankai-rapit", "tokyo": "tokyo-skyliner"}
CITY_PASS = {"osaka": "osaka-amazing-pass", "tokyo": "tokyo-metro-pass"}
CITY_PICKUP = {"danang": "danang-airport-pickup"}
CITY_TICKET = {"danang": "danang-bana-hills"}
ESS_KIND = {"eSIM": "eSIM", "교통패스": "패스", "교통": "교통", "공항픽업": "픽업", "입장권": "입장권"}


def ess_kind(e: dict) -> str:
    return ESS_KIND.get(e["category"], e.get("categoryLabel") or e["category"])


def ess_ids_for(t: dict) -> list:
    out = []
    days = trip_days(t)
    if t["country"] == "jp":
        out.append("jp-esim-usimsa-3d" if days >= 3 else "jp-esim-usimsa-1d")
    elif t["country"] == "vn":
        out.append("vn-esim-usimsa-3d" if days >= 3 else "vn-esim-usimsa-1d")
    city = t["city"]
    inc = t.get("includes") or ""
    if days >= 2 and city in TRANSIT and "항공" in inc:
        out.append(TRANSIT[city])
    if city in CITY_PASS and days >= 2:
        out.append(CITY_PASS[city])
    if city in CITY_PICKUP and "픽업" not in inc and "전용차량" not in inc:
        out.append(CITY_PICKUP[city])
    if city in CITY_TICKET and "바나힐" not in (t["title"] + inc):
        out.append(CITY_TICKET[city])
    return out[:3]


def build_plans(data: dict):
    plans, notes = {}, {}
    for region in PLANNER["regions"]:
        pool = [t for t in data["tours"] if t["country"] in region["countries"]]
        for style in PLANNER["styles"]:
            ordered = sorted(pool, key=lambda t: (-style_score(t, style["id"]), t["sale"]))
            chosen = []
            used_kw = set()
            # 1차: 같은 도시·같은 유형(액티비티는 같은 활동 키워드)은 한 번만
            for t in ordered:
                if t["type"] != "레저·액티비티" and any(
                        t["city"] == c["city"] and t["type"] == c["type"] for c in chosen):
                    continue
                kw = activity_key(t)
                if style["id"] == "active" and kw and kw in used_kw:
                    continue
                chosen.append(t)
                if kw:
                    used_kw.add(kw)
                if len(chosen) == 3:
                    break
            # 2차: 후보가 3개가 안 되면 조건을 풀어 빈자리를 채운다
            if len(chosen) < 3:
                for t in ordered:
                    if t in chosen:
                        continue
                    chosen.append(t)
                    if len(chosen) == 3:
                        break
            key = f"{region['id']}|{style['id']}"
            plans[key] = [{"t": t["id"], "e": ess_ids_for(t)} for t in chosen]
            notes[key] = combo_note(pool, style["id"])
    return plans, notes


def plan_lines(plan: dict, pax: int, tours_by_id: dict, ess_by_id: dict) -> list:
    t = tours_by_id[plan["t"]]
    ex = extra_rec(t)
    short = re.split(r"\s*\(", t["title"])[0]
    # 팀·척 단위로 파는 상품(요트 단독대여 등)은 인원수를 곱하지 않는다.
    per_team = is_team_item(t)
    team_label = t.get("priceUnitLabel") or "1팀 기준"
    lines = [{
        "k": "상품", "n": short, "u": t["url"], "unit": t["sale"],
        "qty": 1 if per_team else pax,
        "sub": f'{t["seller"]} · {t["type"]}' + (f' · {team_label}' if per_team else ""),
    }]
    if ex["krw"]:
        lines.append({"k": "현장", "n": "현장 필수 추가금", "u": None,
                      "unit": ex["krw"], "qty": pax, "sub": ex["basis"]})
    for eid in plan["e"]:
        e = ess_by_id[eid]
        per_vehicle = e["category"] == "공항픽업"
        lines.append({
            "k": ess_kind(e), "n": e["name"], "u": ess_url(e),
            "unit": e["price"], "qty": 1 if per_vehicle else pax,
            "sub": "1대 기준(차량)" if per_vehicle else "",
        })
    return lines


def plan_card_html(plan: dict, idx: int, pax: int, tours_by_id: dict, ess_by_id: dict,
                   courses_by_city: dict, active: bool = True) -> str:
    t = tours_by_id[plan["t"]]
    lines = plan_lines(plan, pax, tours_by_id, ess_by_id)
    total = sum(l["unit"] * l["qty"] for l in lines)
    badge = "ABC"[idx] if idx < 3 else str(idx + 1)

    rows = []
    for l in lines:
        name = esc(l["n"])
        if l["u"]:
            name = f'<a href="{esc(l["u"])}" target="_blank" rel="noopener sponsored">{name}</a>'
        qty = f'{won(l["unit"])}' + (f' × {l["qty"]}' if l["qty"] > 1 else "")
        rows.append(
            f'<li><span class="pl-k">{esc(l["k"])}</span>'
            f'<span class="pl-n"><span class="pl-t">{name}</span><em>{esc(l["sub"])}</em></span>'
            f'<span class="pl-q">{qty}</span><b>{won(l["unit"] * l["qty"])}원</b></li>'
        )

    ex = extra_rec(t)
    note_parts = []
    if ex["krw"]:
        note_parts.append(f'현장 추가금 근거: {ex["basis"]}')
    if ex["aside"]:
        note_parts.append(f'별도: {ex["aside"]}')
    if not plan["e"]:
        if t["country"] == "kr":
            note_parts.append("국내 상품은 eSIM·교통패스가 필요 없어 상품가만 계산했습니다")
        else:
            note_parts.append("이 지역은 eSIM·패스 링크가 없어 상품가만 계산했습니다")
    note = " · ".join(note_parts)

    fl = '항공·숙소 포함' if flights_of(t) else '항공·숙소 별도'
    fl_cls = "on" if flights_of(t) else "off"
    course = courses_by_city.get(t["city"])
    course_link = (f'<a class="plan-course" href="#course-{course["id"]}">{esc(course["title"])} 코스 일정 보기 →</a>'
                   if course else "")
    cls = "plan on" if active else "plan"
    return f"""<div class="{cls}" data-plan="{idx}"{'' if active else ' hidden'}>
            <div class="plan-head">
              <span class="plan-badge">{badge}안</span>
              <h4><a href="{esc(t['url'])}" target="_blank" rel="noopener sponsored">{esc(t['title'])}</a></h4>
              <p class="plan-meta"><span class="flag-chip {fl_cls}">{fl}</span>{esc(t['seller'])} · {esc(t['type'])} · {esc(t['duration'])}</p>
              {course_link}
            </div>
            <ul class="plan-lines">{''.join(rows)}</ul>
            <div class="plan-total">
              <div><span>{pax}인 총액</span><b>{won(total)}원</b></div>
              <div><span>1인 환산</span><b>{won(round(total / pax))}원</b></div>
            </div>
            <p class="plan-note">{esc(note)}</p>
          </div>"""


def render_region_chips() -> str:
    out = []
    for i, r in enumerate(PLANNER["regions"]):
        sel = "true" if i == 1 else "false"
        out.append(f'<button type="button" class="pc-chip" data-region="{r["id"]}" aria-pressed="{sel}">'
                   f'{esc(r["label"])}<em>{esc(r["sub"])}</em></button>')
    return "\n            ".join(out)


def render_style_chips() -> str:
    out = []
    for i, st in enumerate(PLANNER["styles"]):
        sel = "true" if i == 0 else "false"
        out.append(f'<button type="button" class="pc-chip" data-style="{st["id"]}" aria-pressed="{sel}">'
                   f'{esc(st["label"])}<em>{esc(st["sub"])}</em></button>')
    return "\n            ".join(out)


def render_plan_tabs(region: str, style: str, pax: int, plans: dict, tours_by_id: dict, courses_by_city: dict) -> str:
    out = []
    for i, plan in enumerate(plans[f"{region}|{style}"]):
        t = tours_by_id[plan["t"]]
        lines = plan_lines(plan, pax, tours_by_id, ESS_BY_ID)
        total = sum(l["unit"] * l["qty"] for l in lines)
        sel = "true" if i == 0 else "false"
        out.append(f'<button type="button" class="pl-tab" data-plan-tab="{i}" aria-selected="{sel}">'
                   f'<span class="pt-b">{"ABC"[i]}안</span>'
                   f'<span class="pt-n">{esc(t["city_label"])} · {esc(t["type"])}</span>'
                   f'<b>{won(total)}원</b></button>')
    return "\n          ".join(out)


def render_planner_default(plans: dict, tours_by_id: dict, ess_by_id: dict, courses_by_city: dict,
                           region: str = "jp", style: str = "value", pax: int = 2) -> str:
    return "\n          ".join(
        plan_card_html(plan, i, pax, tours_by_id, ess_by_id, courses_by_city, active=(i == 0))
        for i, plan in enumerate(plans[f"{region}|{style}"])
    )


def render_tp_data(data: dict, essentials: dict, courses: dict) -> str:
    tours = {}
    for t in data["tours"]:
        ex = extra_rec(t)
        tours[t["id"]] = {
            "ti": t["title"], "se": t["seller"], "sa": t["sale"], "ex": ex["krw"],
            "ba": ex["basis"], "as": ex["aside"], "pt": 1 if ex["partial"] else 0,
            "de": depart_of(t), "fl": 1 if flights_of(t) else 0, "inc": t["includes"],
            "ca": t["cancelShort"], "ns": 1 if is_noshop(t) else 0,
            "sh": shopping_count(t), "u": t["url"], "ty": t["type"], "du": t["duration"],
            "ci": t["city_label"], "cid": t["city"], "co": t["country"], "im": t["img"], "id": t["id"],
            "ptm": 1 if is_team_item(t) else 0, "ptl": t.get("priceUnitLabel") or "1팀 기준",
        }
    ess = {}
    for e in essentials["products"]:
        ess[e["id"]] = {
            "n": e["name"], "p": e["price"], "c": ess_kind(e),
            "u": ess_url(e), "v": 1 if e["category"] == "공항픽업" else 0,
        }
    course = {c["city"]: {"id": c["id"], "title": c["title"]} for c in courses["courses"] if c.get("city")}
    payload = {"tours": tours, "ess": ess, "fx": PLANNER["fx"], "course": course}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="tpData">{raw}</script>'


def render_plans_json(plans: dict, notes: dict) -> str:
    raw = json.dumps({"plans": plans, "notes": notes}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="plansData">{raw}</script>'


# ---------------------------------------------------------------- FAQ
def faq_text(s: str, tokens: dict) -> str:
    for k, v in tokens.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def render_faq(items: list, tokens: dict) -> str:
    blocks = []
    for i, it in enumerate(items):
        q = faq_text(it["q"], tokens)
        a = faq_text(it["a"], tokens)
        points = "".join(f"<li>{esc(faq_text(p, tokens))}</li>" for p in it.get("points") or [])
        open_attr = " open" if i == 0 else ""
        pts = f'<ul>{points}</ul>' if points else ""
        blocks.append(f"""<details class="fq"{open_attr}>
        <summary><span class="fq-q"><b>Q.</b> {esc(q)}</span><span class="fq-ic" aria-hidden="true"></span></summary>
        <div class="fq-a"><p>{esc(a)}</p>{pts}</div>
      </details>""")
    return "\n      ".join(blocks)


# ---------------------------------------------------------------- 렌더
def render_sections(data: dict) -> str:
    tours = data["tours"]
    city_label = {c["id"]: c["name"] for c in data["cities"]}
    for t in tours:
        t["city_label"] = city_label.get(t["city"], "")

    blocks = []
    for city in data["cities"]:
        items = [t for t in tours if t["city"] == city["id"]]
        if items:
            blocks.append(city_section(city, items, tours))
    return "\n\n".join(blocks)


DEFAULT_REGION, DEFAULT_STYLE, DEFAULT_PAX = "jp", "value", 2
SITE = "https://trippick.pages.dev"
SITE_NAME = "트립픽"
# main() 에서 채운다: 도시 id → (트립닷컴 cityId, 도시명). 지역 섹션에서 숙소 섹션으로 딥링크할 때 쓴다.
TC_CITY: dict[str, tuple[str, str]] = {}


def abs_url(path: str) -> str:
    if path.startswith("http"):
        return path
    return SITE + "/" + path.lstrip("/")


def clean_site_urls(text: str, site: str = SITE) -> str:
    """Cloudflare Pages 는 `*.html` 주소를 확장자 없는 주소로 308 리다이렉트한다.

    정본(canonical)·og:url·JSON-LD·내부 링크·사이트맵을 실제로 200 이 오는
    확장자 없는 주소로 맞춘다. 폴더의 index.html 은 폴더 주소(`/guides/`)로 바꾼다.
    """

    def _abs(m: "re.Match") -> str:
        path = m.group(1)
        if path.endswith("index.html"):
            path = path[: -len("index.html")]
        else:
            path = path[:-len(".html")]
        return site + "/" + path

    text = re.sub(re.escape(site) + r"/([A-Za-z0-9_\-./]*\.html)", _abs, text)

    def _rel(m: "re.Match") -> str:
        path = m.group(2)
        if path.endswith("index.html"):
            path = path[: -len("index.html")] or "./"
        else:
            path = path[: -len(".html")]
        return m.group(1) + path + m.group(3) + m.group(4)

    return re.sub(
        r'(href=")(?!https?:|mailto:|tel:|data:|javascript:|#)([^"#?]*?\.html)([^"]*)(")',
        _rel,
        text,
    )


def faq_tokens(data: dict, courses: dict, essentials: dict) -> dict:
    tours = data["tours"]
    return {
        "TOTAL": len(tours),
        "ESS_COUNT": len(essentials["products"]),
        "COURSE_COUNT": len(courses["courses"]),
        "NOSHOP": sum(1 for t in tours if is_noshop(t)),
        "MINPAX_KNOWN": sum(1 for t in tours if "확인" not in t["minPax"]),
        "MINPAX_UNKNOWN": sum(1 for t in tours if "확인" in t["minPax"]),
    }


def render_jsonld(data: dict, courses: dict, essentials: dict) -> str:
    tours = data["tours"]
    FAQ_TOKENS = faq_tokens(data, courses, essentials)
    city_name = {c["id"]: c["name"] for c in data["cities"]}

    course_items = []
    for i, c in enumerate(courses["courses"], start=1):
        course_items.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "TouristTrip",
                "name": c["title"],
                "description": f'{c.get("hook", "")} {c["lead"]}'.strip(),
                "url": SITE + "/#course-" + c["id"],
                "image": abs_url(c["img"]),
                "touristType": c.get("tag", ""),
                "itinerary": {
                    "@type": "ItemList",
                    "numberOfItems": len(c["days"]),
                    "itemListElement": [
                        {"@type": "ListItem", "position": d["no"],
                         "item": {"@type": "TouristAttraction", "name": d["title"], "description": d["memo"]}}
                        for d in c["days"]
                    ],
                },
            },
        })

    tour_items = []
    for i, t in enumerate(tours, start=1):
        # 주의: 트립픽은 판매 당사자가 아니라 제휴 링크를 모아 비교하는 사이트다.
        # Product/Offer 로 두면 구글 '제품 스니펫'·'판매자 목록'이 평점·리뷰·
        # 반품정책·배송정보를 요구하고, 없는 값을 지어내야 한다. 그래서 실제 성격인
        # TouristTrip(여행 상품)으로 표기하고, 판매·가격·재고는 주장하지 않는다.
        # 가격은 페이지 본문에만 크게 표시하고 구조화 데이터에는 넣지 않는다.
        item = {
            "@type": "TouristTrip",
            "name": t["title"],
            "description": f'{t["theme"]} · {t["type"]} · {t["duration"]} · {t["includes"]}',
            "image": abs_url(t["imgLg"]),
            "url": t["url"],
            "touristType": t["type"],
            "provider": {"@type": "Organization", "name": t["seller"]},
            "areaServed": {"@type": "Place", "name": city_name.get(t["city"], t["city"])},
        }
        tour_items.append({"@type": "ListItem", "position": i, "item": item})

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": SITE + "/#website",
                "url": SITE + "/",
                "name": "트립픽",
                "alternateName": "TripPick",
                "description": "네이버 여행 실제 판매 상품을 가격·미팅·입장료·현장 추가금·취소 규정까지 같은 기준으로 비교하는 여행 코스·투어 사이트",
                "inLanguage": "ko-KR",
                "publisher": {"@type": "Organization", "name": "트립픽", "url": SITE + "/"},
            },
            {
                "@type": "ItemList",
                "@id": SITE + "/#courses",
                "name": "추천 여행 코스",
                "description": "오사카·교토, 도쿄·후지, 다낭·호이안, 삿포로·홋카이도, 제주 2박3일 일차별 동선",
                "numberOfItems": len(course_items),
                "itemListElement": course_items,
            },
            {
                "@type": "FAQPage",
                "@id": SITE + "/#faq",
                "name": "여행 예약 전 자주 묻는 질문",
                "inLanguage": "ko-KR",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq_text(it["q"], FAQ_TOKENS),
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": " ".join([faq_text(it["a"], FAQ_TOKENS)] + [faq_text(x, FAQ_TOKENS) for x in it.get("points") or []]),
                        },
                    }
                    for it in FAQ["items"]
                ],
            },
            {
                "@type": "ItemList",
                "@id": SITE + "/#tours",
                "name": "지역별 가이드투어·패키지",
                "description": f"{len(tours)}개 여행 상품 — 지역·가격·취소 규정 비교",
                "numberOfItems": len(tour_items),
                "itemListElement": tour_items,
            },
        ],
    }
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return '<script type="application/ld+json">' + payload + "</script>"


def render_sitemap(data: dict, courses: dict) -> str:
    lastmod = "2026-11-17"
    # 단일 페이지 사이트: #fragment 는 검색엔진이 별도 URL로 색인하지 않으므로
    # 사이트맵에는 정규 URL만 넣는다(중복·무효 URL 경고 방지).
    # 가이드·필수 페이지(data/guides.json)가 있으면 그 URL도 함께 넣는다.
    urls = [(SITE + "/", "1.0", "weekly")]
    gpath = DATA / "guides.json"
    if gpath.exists():
        gspec = json.loads(gpath.read_text(encoding="utf-8"))
        urls.append((SITE + "/guides/", "0.9", "weekly"))
        urls += [(f"{SITE}/guides/{g['slug']}.html", "0.8", "monthly") for g in gspec.get("guides", [])]
        urls += [(f"{SITE}/{p['slug']}.html", "0.6" if p["slug"] in ("about", "contact") else "0.4",
                  "monthly" if p["slug"] in ("about", "contact") else "yearly") for p in gspec.get("pages", [])]
    body = "".join(
        f'  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod>'
        f'<changefreq>{cf}</changefreq><priority>{pr}</priority></url>\n'
        for u, pr, cf in urls
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '</urlset>\n')


def replace_block(html: str, marker: str, body: str) -> str:
    if marker not in html:
        raise SystemExit(f"template.html 에 {marker} 마커가 없습니다.")
    return html.replace(marker, body, 1)


# ----------------------------------------------------------------------
# 애드센스 슬롯 (승인 전에는 빈 박스 없이 내부 추천 배너로 대체)
# ----------------------------------------------------------------------
ADSENSE_CLIENT = "ca-pub-0000000000000000"


def ad_slot(slot: str, title: str, text: str, href: str, cta: str, kicker: str = "트립픽 추천") -> str:
    """승인 전: 내부 추천 배너만 보입니다(빈 <ins> 없음 → 레이아웃 깨짐 없음).
    승인 후: 주석을 풀고 ca-pub-… / data-ad-slot 두 값만 복사하면 바로 켜집니다."""
    return f'''<aside class="adslot" data-ad-slot="{slot}" aria-label="광고·추천 영역">
  <!-- 애드센스 승인 후 사용법
       ① <head> 에 로더 스크립트를 한 번 넣기:
          <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
       ② 아래 주석을 풀고 {ADSENSE_CLIENT} 와 data-ad-slot 값만 발급받은 값으로 바꾸기.
       승인 전에는 <ins> 가 없으므로 빈 박스가 생기지 않고, 내부 추천 배너가 대신 보입니다. -->
  <!--
  <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="0000000000" data-ad-format="auto" data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  -->
  <a class="adslot-in" href="{href}">
    <span class="adslot-tag">{kicker}</span>
    <span class="adslot-copy"><b>{title}</b><span>{text}</span></span>
    <span class="adslot-go">{cta} →</span>
  </a>
</aside>'''


def render_ad_slots() -> dict:
    return {
        "<!-- @AD_SLOT_1 -->": ad_slot(
            "home-after-courses",
            "내 날짜·인원으로 항공+숙소+투어 총액 계산",
            "출발일과 인원을 넣으면 A/B/C 세 가지 예산안으로 한 번에 보여줍니다.",
            "#planner",
            "계산기 열기",
        ),
        "<!-- @AD_SLOT_2 -->": ad_slot(
            "home-after-regions",
            "숙소는 도시별 최저가로 비교해 보세요",
            "트립닷컴 파트너스 링크로 도시 15곳 숙소와 항공 6개 노선을 모았습니다.",
            "#tripcom",
            "숙소·항공 보기",
        ),
        "<!-- @AD_SLOT_3 -->": ad_slot(
            "home-after-tripcom",
            "특가가 뜨면 가장 먼저 알려드릴게요",
            "원하는 여행지와 예산만 남기면 특가·땡처리 소식을 메일로 보내드립니다.",
            "#alert",
            "알림 신청",
        ),
    }


def main() -> int:
    check = "--check" in sys.argv
    data = json.loads((DATA / "tours.json").read_text(encoding="utf-8"))
    courses = json.loads((DATA / "courses.json").read_text(encoding="utf-8"))
    essentials = json.loads((DATA / "essentials.json").read_text(encoding="utf-8"))
    tripcom = json.loads((DATA / "tripcom.json").read_text(encoding="utf-8"))
    checklist = json.loads((DATA / "checklist.json").read_text(encoding="utf-8"))

    TC_CITY.clear()
    for h in tripcom["hotels"]:
        if h.get("cityId"):
            TC_CITY[h["cityId"]] = (h["cityId"], h["city"])
    for alias, target in {"vietnam_golf": "danang", "hawaii": "honolulu", "gangwon": "pyeongchang"}.items():
        if target in TC_CITY:
            TC_CITY[alias] = TC_CITY[target]

    tours_by_id = {t["id"]: t for t in data["tours"]}
    ess_by_id = {e["id"]: e for e in essentials["products"]}
    city_label = {c["id"]: c["name"] for c in data["cities"]}
    for t in data["tours"]:
        t["city_label"] = city_label.get(t["city"], "")
    courses_by_city = {c["city"]: c for c in courses["courses"] if c.get("city")}
    plans, plan_notes = build_plans(data)

    html = TEMPLATE.read_text(encoding="utf-8")

    tokens = {
        "TOTAL": str(len(data["tours"])),
        "CITY_COUNT": str(len(data["cities"])),
        "COUNTRY_COUNT": str(len([c for c in COUNTRIES if any(t["country"] == c[0] for t in data["tours"])])),
        "COURSE_COUNT": str(len(courses["courses"])),
        "ESS_COUNT": str(len(essentials["products"])),
    }
    for k, v in tokens.items():
        html = html.replace("{{" + k + "}}", v)

    html = replace_block(html, "<!-- @CITYSELECT -->", render_city_select(data))
    html = replace_block(html, "<!-- @COURSE_PICKER -->", render_course_picker(courses, tours_by_id, ess_by_id))
    html = replace_block(html, "<!-- @COURSE_PANELS -->", render_course_panels(courses, tours_by_id, ess_by_id))
    html = replace_block(html, "<!-- @COUNTRY_TABS -->", render_country_tabs(data))
    html = replace_block(html, "<!-- @CITY_CHIPS -->", render_city_chips(data))
    html = replace_block(html, "<!-- @TYPEBAR -->", render_typebar(data))
    html = replace_block(html, "<!-- @CITIES -->", render_sections(data))
    html = replace_block(html, "<!-- @ESSENTIALS -->", render_essentials(essentials))
    html = replace_block(html, "<!-- @CHECKLIST -->", render_checklist(checklist, ess_by_id, tripcom))
    html = replace_block(html, "<!-- @TRIPCOM -->", render_tripcom(tripcom))
    html = replace_block(html, "<!-- @QUICKSTRIP -->", render_quickstrip(data, courses, essentials, tripcom))
    html = replace_block(html, "<!-- @HOTSTRIP -->", render_hot_strip(data, courses, essentials, tripcom))
    html = replace_block(html, "<!-- @REGION_CHIPS -->", render_region_chips())
    html = replace_block(html, "<!-- @STYLE_CHIPS -->", render_style_chips())
    html = replace_block(html, "<!-- @PLAN_NOTE -->", plan_notes.get(f"{DEFAULT_REGION}|{DEFAULT_STYLE}", ""))
    html = replace_block(html, "<!-- @PLAN_TABS -->", render_plan_tabs(DEFAULT_REGION, DEFAULT_STYLE, DEFAULT_PAX, plans, tours_by_id, courses_by_city))
    html = replace_block(html, "<!-- @PLAN_BODY -->", render_planner_default(plans, tours_by_id, ess_by_id, courses_by_city))
    html = replace_block(html, "<!-- @FAQ -->", render_faq(FAQ["items"], faq_tokens(data, courses, essentials)))
    html = replace_block(html, "<!-- @TP_DATA -->", render_tp_data(data, essentials, courses) + "\n" + render_plans_json(plans, plan_notes))
    html = replace_block(html, "<!-- @JSONLD -->", render_jsonld(data, courses, essentials))
    for marker, slot_html in render_ad_slots().items():
        html = replace_block(html, marker, slot_html)

    if "{{" in html:
        raise SystemExit("치환되지 않은 토큰이 있습니다: " + str(re.findall(r"\{\{\w+\}\}", html)))

    # Cloudflare Pages 가 200 으로 서빙하는 확장자 없는 주소로 정본·내부 링크를 맞춘다
    html = clean_site_urls(html)

    out_path = INDEX
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out_path = ROOT / sys.argv[i + 1]

    if check:
        current = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        same = current == html
        print("변경 없음" if same else "변경 있음 (build.py 실행 필요)")
        return 0 if same else 2

    out_path.write_text(html, encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(clean_site_urls(render_sitemap(data, courses)), encoding="utf-8")
    print(f"index.html 생성 완료 — 상품 {len(data['tours'])}개, 도시 {len(data['cities'])}곳, "
          f"코스 {len(courses['courses'])}개, 필수품 {len(essentials['products'])}개, {len(html) // 1024}KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
