#!/usr/bin/env python3
"""
트립픽 가이드·필수 페이지 생성기
================================================
index.html(build.py) 은 그대로 두고, 같은 디자인 토큰을 쓰는
서브 페이지를 만듭니다.

    python3 build_pages.py                 # tour_hub/ 안에 생성
    python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev
    python3 build_pages.py --check-links   # 생성 후 내부 링크 전수 검사

원본
----
- template.html   : <style> 블록과 SVG 스프라이트를 그대로 가져와 assets/site.css 로 저장
- content/pages.css: 페이지 전용 추가 CSS(site.css 뒤에 붙임)
- data/guides.json: 가이드 메타데이터
- content/guides/*.html : 가이드 본문(HTML 조각)
- content/pages/*.html  : 소개·약관·개인정보·문의 본문(HTML 조각)
- data/tours.json, data/essentials.json : 사이드의 실제 판매 상품 카드

생성물
------
about.html privacy.html terms.html contact.html
guides/index.html guides/<slug>.html ...
assets/site.css  sitemap.xml
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import build as B  # 상품 카드·비교표·추가금 계산을 홈과 똑같이 쓰기 위해

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "template.html"
DATA = ROOT / "data"
CONTENT = ROOT / "content"
GUIDES = CONTENT / "guides"
PAGES = CONTENT / "pages"

SITE_NAME = "트립픽"
SITE_TAGLINE = "여행 코스 · 가이드투어 비교"
CONTACT_MAIL = "gim082487@gmail.com"
FORMSPREE = "https://formspree.io/f/xwlolrod"
TODAY = datetime.now(ZoneInfo("Asia/Seoul")).date()   # v47: 하드코딩 제거 — 실행 시점 KST 날짜(사이트맵 lastmod·최종 검증일)
CSS_V = "49"   # assets/site.css 캐시 버전 — CSS·디자인을 바꿀 때 함께 올린다 (v47: 폰트 대체 메트릭·D-Day 필)
JS_V = "26"    # assets/trip-save.js (v25 이어보기·공유) 캐시 버전
JS_V35 = "36"  # assets/tp-v35.js (제휴 클릭 추적 tp_clicks_v1 · 묶음 CTA) 캐시 버전
JS_V43 = "5"   # assets/tp-v43.js (통합 퀵서치 · 파인더 · 찜 견적서 · 내 여행 D-Day · ★ 참고 글 저장) 캐시 버전
JS_V44 = "2"   # assets/tp-v44.js (/sos 국가 전환 · 현지어 큰 글씨 카드 · v45 ?country= 프리셋) 캐시 버전


def ga4_head() -> str:
    """GA4 로더 — data/analytics.json 의 ga4.measurementId 한 곳만 채우면 전 페이지에 붙는다.

    비어 있으면(기본값) 아무 스크립트도 넣지 않는다. 홈은 build.py 가 같은 파일을 읽어
    template.html 의 <!-- @GA4 --> 자리에 같은 문자열을 넣으므로, 두 빌드가 같은 설정을 쓴다.
    """
    try:
        cfg = json.loads((DATA / "analytics.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    mid = str((cfg.get("ga4") or {}).get("measurementId") or "").strip()
    if not re.fullmatch(r"G-[A-Z0-9]{6,}", mid):
        return ""
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={mid}"></script>\n'
            "<script>window.dataLayer=window.dataLayer||[];"
            "function gtag(){dataLayer.push(arguments);}"
            f"gtag('js',new Date());gtag('config','{mid}',{{anonymize_ip:true}});</script>")

# index.html 에 실제로 있는 앵커만 쓴다(build.py --check-links 로 검증)
# v18: 메뉴 9개 + '도구' 드롭다운 1개. 1280px에서 한 줄에 들어오도록 계산기·표 페이지는 드롭다운으로 묶는다.
NAV = [
    ("index.html#courses", "추천 코스", "courses"),
    ("index.html#planner", "예산 계산기", "planner"),
    ("checklist.html", "여행 준비", "checklist"),
    ("index.html#regions", "지역·투어", "regions"),
    ("cities/index.html", "도시별", "cities"),
    ("stays.html", "찐숙소", "stays"),
    ("guides/index.html", "여행 가이드", "guides"),
    ("index.html#foods", "맛집", "foods"),
    ("index.html#essentials", "여행 필수품", "essentials"),
    ("index.html#alert", "특가 알림", "alert"),
    ("coupons.html", "할인쿠폰", "coupons"),
]

# 드롭다운에 들어가는 계산기·표 페이지 (v18에 /passes · /calendar 추가)
TOOLS = [
    ("sos.html", "여행 중 위기상황 SOS", "sos", "10개국 경찰·구급·대사관"),
    ("exchange.html", "환율·일본 면세 계산기", "exchange", "12개 통화 · 면세 환급"),
    ("baggage.html", "항공사 수하물 규정", "baggage", "기내·위탁·배터리"),
    ("passes.html", "교통패스 본전 계산기", "passes", "오사카·도쿄·방콕·타이베이·싱가포르·홍콩"),
    ("calendar.html", "월별 시즌 캘린더", "calendar", "19개 도시 12개월"),
]
TOOL_KEYS = {k for _, _, k, _ in TOOLS}

# 1080px 이하에서 숨길 보조 메뉴(핵심 메뉴와 드롭다운만 남긴다)
HIDE_SM = {"checklist", "foods", "alert"}
STAYS: dict = {}   # data/stays.json — v21 /stays
GLOBAL_CSS = ""    # v50: assets/site.css 내용(빌드 시 채움) — 특정 페이지는 HTML 안에 인라인한다
SEASON_IDS: set = set()   # data/season.json 도시 — 허브의 시즌 캘린더 탭 앵커 판단
KLOOK: dict = {}   # data/klook.json (main 에서 채운다)
PACKAGES: dict = {}  # data/packages.json — v20 고단가 패키지

# 도시 허브 → /passes 탭 (없는 도시는 전체 페이지로)
HUB_PASS_TOOL = {
    "osaka": ("passes.html#osaka", "오사카 주유패스, 사면 남는가", "시설 체크로 본전 계산"),
    "tokyo": ("passes.html#tokyo", "도쿄 지하철 패스·나리타 비교", "24·48·72시간 본전"),
    "bangkok": ("passes.html#bangkok", "방콕 BTS 1일권 본전", "150밧 vs 개별권"),
    "taipei": ("passes.html#taipei", "타이베이 펑패스 vs 이지카드", "1·2·3·5일 비교"),
    "fukuoka": ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이·싱가포르"),
    "danang": ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이·싱가포르"),
    "jeju": ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이·싱가포르"),
}

# 도시 허브·가이드 → 도구 페이지 원클릭 프리셋 (v45)
#   /exchange?cur=JPY · /passes?city=tokyo · /sos?country=JP  — 도착하면 그 도시·국가가 이미 선택된 상태
CUR_OF_COUNTRY = {"jp": "JPY", "vn": "VND", "th": "THB", "tw": "TWD",
                  "us": "USD", "sg": "SGD", "hk": "HKD", "fr": "EUR", "it": "EUR", "es": "EUR", "gb": "GBP"}
SOS_OF_COUNTRY = {"jp": "JP", "vn": "VN", "th": "TH", "tw": "TW", "kr": "KR",
                 "sg": "SG", "fr": "FR", "it": "IT", "es": "ES", "gb": "GB"}
CUR_UNIT = {"JPY": (100, "엔"), "VND": (100, "동"), "THB": (1, "밧"), "TWD": (1, "대만달러"),
            "USD": (1, "달러"), "EUR": (1, "유로"), "GBP": (1, "파운드")}
_FX_PER_UNIT: dict = {}


def fx_basis(code: str) -> str:
    """fx.json staticBasis.perUnit 에서 ‘100엔 = 838원’ 같은 표기를 만든다(환율이 바뀌면 따라온다)."""
    global _FX_PER_UNIT
    if not _FX_PER_UNIT:
        _FX_PER_UNIT = load_json("fx.json")["staticBasis"]["perUnit"]
    raw = str(_FX_PER_UNIT.get(code) or "")
    if not raw:
        return ""
    try:
        val = float(raw.split()[0])
    except ValueError:
        return raw
    unit, name = CUR_UNIT.get(code, (1, code))
    total = val * unit
    # v51: 도구 바 한 줄에는 본문·고시 문구와 같은 원 단위로 반올림해 보여 준다(838.34원 → 838원).
    text = f"{round(total):,}"
    return f"{unit}{name} = {text}원"


def tool_links(hub_slug: str, country: str, up: str = "") -> dict:
    """허브 slug·국가 코드 → 도구 3종 주소(프리셋 파라미터 포함)."""
    cur = CUR_OF_COUNTRY.get(country)
    # HTML 속성에 들어가므로 & 는 &amp; 로 쓴다
    exchange = (f"{up}exchange.html?cur={cur}&amp;city={hub_slug}" if cur else f"{up}exchange.html")
    pass_city = hub_slug if hub_slug in ("osaka", "tokyo", "bangkok", "taipei", "singapore", "hongkong") else ""
    passes = f"{up}passes.html?city={pass_city}" if pass_city else f"{up}passes.html"
    # v55: 긴급번호 자료가 있는 나라만 국가를 미리 고른다(없는 나라는 KR로 잘못 열리지 않게 기본 페이지)
    sos = f"{up}sos.html?country={SOS_OF_COUNTRY[country]}" if country in SOS_OF_COUNTRY else f"{up}sos.html"
    return {"exchange": exchange, "passes": passes, "sos": sos, "cur": cur or ""}


VERIFY_META = """<meta name="google-site-verification" content="LcZmYDzmsn2pIDvvwDXtLezOnQi8dEOjQ67-xBWdfCw" />
<meta name="google-site-verification" content="Y3lrh6zGKCcwxVcFKL8ujJ1QK1Xi4HjHaL2KhZLku78" />
<meta name="naver-site-verification" content="de9b4241355a3ab6e83e5c102d1f6f1e6f244302" />
<meta name="naver-site-verification" content="ab10e600052c8a46301698e6f7c1dd39c3c2aa95" />
<meta name="naver-site-verification" content="ed075b14e9af849ab81ed9569f8e97f418a88c83" />"""

# v17.2 애드센스 사이트 연결 — 모든 서브페이지 head 에 들어가는 메타태그·광고 스크립트(빌드에서 자동 삽입)
ADSENSE = (
    '<meta name="google-adsense-account" content="ca-pub-9563082990728787" />\n'
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9563082990728787" crossorigin="anonymous"></script>'
)

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='9' fill='%231b5cf0'/%3E"
    "%3Cpath d='M9 17.5 23 12.8l-3.2 6.4-4.6.7-2 2.6-.7-3.2-3.5-1.8Z' fill='%23fff'/%3E%3C/svg%3E"
)


# ----------------------------------------------------------------------
# 공통 조각
# ----------------------------------------------------------------------
def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


# v49: 같은 이미지의 WebP 변형(tools/v49_img_variants.py)이 있으면 <picture> 로 감싸
#       모바일이 480·720px 변형을 받게 한다. 변형이 없으면 기존 <img> 그대로.
def pic_sources(img: str, pref: str, sizes: str) -> str:
    p = ROOT / img
    if not p.exists() or p.suffix.lower() not in (".jpg", ".jpeg"):
        return ""
    folder = img.rsplit("/", 1)[0] + "/" if "/" in img else ""
    parts = [f"{pref}{folder}{p.stem}-{w}.webp {w}w"
             for w in (480, 720, 960, 1440) if p.with_name(f"{p.stem}-{w}.webp").exists()]
    if not parts:
        return ""
    return f'<source type="image/webp" srcset="{esc(", ".join(parts))}" sizes="{sizes}" />'


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def template_parts():
    """template.html 에서 <style> 내용과 SVG 스프라이트를 그대로 추출."""
    tpl = read(TEMPLATE)
    m = re.search(r"<style>(.*?)</style>", tpl, re.S)
    if not m:
        raise SystemExit("template.html 에서 <style> 블록을 찾지 못했습니다.")
    style = m.group(1).strip()
    s = re.search(r'(<svg width="0" height="0".*?</svg>)', tpl, re.S)
    if not s:
        raise SystemExit("template.html 에서 SVG 스프라이트를 찾지 못했습니다.")
    return style, s.group(1).strip()


def header_html(up: str, active: str = "") -> str:
    links = []
    for href, label, key in NAV:
        on = " on" if key == active else ""
        sm = " data-hide-sm" if key in HIDE_SM else ""
        links.append(f'      <a href="{up}{href}"{sm}{f" class=\"on\"" if on else ""}>{label}</a>')
    tool_items = []
    for href, label, key, sub in TOOLS:
        on = " on" if key == active else ""
        tool_items.append(
            f'        <a href="{up}{href}"{f" class=\"on\"" if on else ""}><b>{label}</b><span>{sub}</span></a>'
        )
    drop_on = " on" if active in TOOL_KEYS else ""
    links.append(
        '      <details class="nav-drop" id="navTools">\n'
        f'        <summary class="nav-drop-sum{drop_on}"><span>도구</span></summary>\n'
        '        <div class="nav-drop-menu">\n'
        + "\n".join(tool_items)
        + "\n        </div>\n      </details>"
    )
    nav = "\n".join(links)
    return f"""<a class="pg-skip" href="#main">본문 바로가기</a>
<header class="site-head" id="siteHead">
  <div class="wrap">
    <a class="logo" href="{up}index.html">
      <span class="mark" aria-hidden="true"><svg><use href="#i-plane"/></svg></span>
      <span><span class="lt">트립픽</span><small class="ls">{SITE_TAGLINE}</small></span>
    </a>
    <nav class="nav" aria-label="주요 메뉴">
{nav}
    </nav>
    <div class="head-right">
      <button class="hd-ico" type="button" data-qs-open aria-label="통합 검색" title="통합 검색 (Ctrl/⌘ K)">
        <svg aria-hidden="true"><use href="#i-search"/></svg><kbd>⌘K</kbd>
      </button>
      <button class="hd-ico" type="button" data-wl-open aria-label="찜한 항목" title="찜한 항목">
        <svg aria-hidden="true"><use href="#i-heart"/></svg><span class="hd-n" data-wl-count hidden>0</span>
      </button>
      <a class="hd-sos" href="{up}sos.html" aria-label="여행 중 위기상황 SOS — 10개국 긴급번호"><svg aria-hidden="true"><use href="#i-shield"/></svg><span>SOS</span></a>
      <a class="btn" href="{up}index.html#regions">투어 {TOTAL}개 찾기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </div>
  </div>
</header>"""


def footer_html(up: str) -> str:
    return f"""<footer>
  <div class="wrap">
    <div class="top">
      <div class="flogo">
        <span class="mark" aria-hidden="true"><svg><use href="#i-plane"/></svg></span>
        <span>트립픽</span>
      </div>
      <div class="flinks">
        <div class="fl-col">
          <span class="fl-group">여행</span>
          <a href="{up}index.html#courses">추천 코스</a>
          <a href="{up}index.html#regions">지역·투어</a>
          <a href="{up}index.html#essentials">여행 필수품</a>
          <a href="{up}index.html#gifts">선물·기념품</a>
          <a href="{up}index.html#planner">예산 계산기</a>
          <a href="{up}checklist.html">여행 준비 D-Day</a>
          <a href="{up}exchange.html">환율·일본 면세 계산기</a>
          <a href="{up}baggage.html">항공사 수하물 규정</a>
          <a href="{up}passes.html">교통패스 본전 계산기</a>
          <a href="{up}calendar.html">월별 시즌·최저가 캘린더</a>
          <a href="{up}sos.html">여행 중 위기상황 SOS</a>
          <a href="{up}cities/index.html">도시별 여행 페이지</a>
          <a href="{up}stays.html">찐숙소 — 국내·해외 {len(STAYS.get("hotels", [])) or 30}곳</a>
          <a href="{up}guides/index.html">여행 가이드</a>
          <a href="{up}index.html#alert">특가 알림</a>
          <a href="{up}coupons.html">여행 할인코드·쿠폰</a>
        </div>
        <div class="fl-col">
          <span class="fl-group">사이트 안내</span>
          <a href="{up}about.html">서비스 소개</a>
          <a href="{up}contact.html">문의</a>
          <a href="{up}privacy.html">개인정보처리방침</a>
          <a href="{up}terms.html">이용약관</a>
        </div>
        <div class="fl-col">
          <span class="fl-group">지역·도움말</span>
          <a href="{up}index.html#jeju">제주·울릉</a>
          <a href="{up}index.html#busan">부산 요트</a>
          <a href="{up}index.html#gangwon">강원 스키</a>
          <a href="{up}index.html#faq">자주 묻는 질문</a>
          <a href="{up}index.html#howto">예약 전 체크</a>
        </div>
        <div class="fl-col fl-col--pick">
          <span class="fl-group">추천 사이트</span>
          <a class="fl-ext" href="https://jinyou1129-bit.github.io/star-fit-pick/" target="_blank" rel="noopener">
            <b>스타핏픽 ↗</b>
            <span>공항패션·예능 착장 좌표</span>
          </a>
        </div>
      </div>
    </div>

    <div class="disclose">
      <b>제휴 및 대가성 고지</b> — 본 사이트는 <b>네이버 여행 커넥트</b>·<b>네이버 쇼핑 커넥트</b>·<b>쿠팡 파트너스</b>·<b>트립닷컴 파트너스</b>에 참여하고 있습니다.
      상품의 <b>[네이버 여행에서 예약]</b> 링크로 예약이 이루어지면 판매자로부터 가이드투어 결제 금액의 5%, 패키지 3%를,
      추천 코스의 교통·입장권·eSIM, 부산·강원 레저 상품 같은 <b>쇼핑 커넥트 링크</b>로 구매가 이루어지면 상품별로 정해진 수수료를 지급받을 수 있습니다.
      여행 준비물의 <b>쿠팡 링크</b>로 구매가 이루어지면 쿠팡 파트너스를 통해 상품별 수수료를 지급받습니다. (이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.)
      맨 아래 <b>트립닷컴 숙소·항공권</b> 링크로 예약이 이루어지면 트립닷컴 파트너스를 통해 호텔 5~7%·국제선 항공 0.5~0.8%의 수수료를 지급받습니다. (이 포스팅은 트립닷컴 파트너스 활동의 일환으로, 예약 시 일정액의 수수료를 제공받습니다.)
      이 수수료는 <b>구매자가 지불하는 가격에 영향을 주지 않으며</b>, 순위와 편집 내용에도 영향을 주지 않습니다.
    </div>

    <div class="legal">
      <p>· 본 사이트는 여행 상품의 <strong>판매 당사자가 아닙니다</strong>. 상품의 판매·계약·환불 등에 대한 권리와 의무는 각 판매자(여행사·판매처)에게 있으며, 가격·포함 사항·취소 규정은 <strong>예약 전 반드시 상세페이지에서 최종 확인</strong>하세요.</p>
      <p>· 표시 가격은 각 판매 페이지 기준 최저가이며 날짜·좌석·환율에 따라 달라질 수 있습니다. 자세한 기준은 <a href="{up}about.html">서비스 소개</a>와 <a href="{up}terms.html">이용약관</a>에 있습니다.</p>
      <p>· 개인정보 수집·이용(특가 알림, 문의)에 대한 내용은 <a href="{up}privacy.html">개인정보처리방침</a>에서 확인할 수 있습니다. 문의: <strong>{CONTACT_MAIL}</strong></p>
    </div>
    <p class="copyline"><span>© 2026 트립픽 · 여행 코스 &amp; 가이드투어 비교</span><span>사진: Pexels · 상품 이미지: 각 판매처</span></p>
  </div>
</footer>
<script>
(function(){{
  var h=document.getElementById('siteHead');
  if(!h) return;
  var on=function(){{ h.classList.toggle('stuck', window.scrollY>8); }};
  on(); window.addEventListener('scroll', on, {{passive:true}});
  var nd=document.getElementById('navTools');
  if(nd){{
    document.addEventListener('click', function(e){{ if(nd.open && !nd.contains(e.target)) nd.open=false; }});
    Array.prototype.forEach.call(nd.querySelectorAll('a'), function(a){{ a.addEventListener('click', function(){{ nd.open=false; }}); }});
    document.addEventListener('keydown', function(e){{ if(e.key==='Escape') nd.open=false; }});
  }}
}})();
</script>"""


def share_row(kind: str = "page", title: str = "", text: str = "", url: str = "", extra: str = "") -> str:
    """v25 외부 공유 — 링크 복사 + 모바일 navigator.share.

    url·title 을 비우면 스크립트가 canonical·og:title 을 그대로 쓴다(빌드 시점에
    확정되지 않는 값(퀴즈 결과 등)은 JS 가 data-share-url 을 덮어쓴다).
    """
    attrs = ['class="share-row"', "data-share"]
    if url:
        attrs.append(f'data-share-url="{esc(url)}"')
    if title:
        attrs.append(f'data-share-title="{esc(title)}"')
    if text:
        attrs.append(f'data-share-text="{esc(text)}"')
    label = {
        "result": "이 결과 공유하기",
        "stays": "숙소 목록 공유하기",
        "guide": "이 가이드 공유하기",
        "hub": "이 도시 페이지 공유하기",
    }.get(kind, "이 페이지 공유하기")
    return f"""<div {' '.join(attrs)}>
  <span class="share-k"><svg aria-hidden="true"><use href="#i-globe"/></svg>{label}</span>
  <button type="button" class="share-btn share-btn--main" data-share-act="native">
    <svg aria-hidden="true"><use href="#i-arrow"/></svg>카톡·인스타·스레드로 보내기</button>
  <button type="button" class="share-btn" data-share-act="copy">
    <svg aria-hidden="true"><use href="#i-check"/></svg>링크 복사</button>
  {extra}
  <span class="share-note">복사하면 ‘복사됨 ✓’ 이 뜨고, 카톡·문자·메모 어디든 붙여넣으면 미리보기가 나옵니다.</span>
</div>"""


def cont_bar(kind: str, title: str, url: str, img: str = "") -> str:
    """v25 이어보기 — 이 페이지를 최근 본 목록에 기록할 때 쓰는 빈 상자.

    페이지 안 흐름에 놓이는 일반 블록이라(v22 비교바처럼 fixed 가 아님) 모바일
    하단 바와 겹치지 않는다. 내용은 assets/trip-save.js 가 localStorage 로 채운다.
    """
    return (
        f'<div class="cont-bar" id="contBar" hidden data-tp-kind="{esc(kind)}" '
        f'data-tp-title="{esc(title)}" data-tp-url="{esc(url)}" data-tp-img="{esc(_site_path(img))}"></div>'
    )


def _site_path(src: str) -> str:
    """이어보기·공유 카드에 쓰는 이미지 경로를 사이트 루트 기준(/images/…)으로 맞춘다.

    페이지 깊이가 달라도(허브는 /, 가이드는 /guides/) 같은 이미지가 열리도록 한다.
    """
    if not src:
        return ""
    if src.startswith(("http://", "https://", "/", "data:")):
        return src
    return "/" + src


def clean_site_urls(text: str, site: str) -> str:
    """Cloudflare Pages 는 `*.html` 주소를 확장자 없는 주소로 308 리다이렉트한다.

    정본(canonical)·og:url·JSON-LD·내부 링크·사이트맵을 실제로 200 이 오는
    확장자 없는 주소로 맞춘다. 폴더의 index.html 은 폴더 주소(`/guides/`)로 바꾼다.
    """
    site = site.rstrip("/")

    def _abs(m: "re.Match") -> str:
        path = m.group(1)
        if path.endswith("index.html"):
            path = path[: -len("index.html")]
        else:
            path = path[: -len(".html")]
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


def bundles_payload() -> str:
    """v34 — data/bundles.json(도시별 제휴 묶음)을 페이지에 심을 JSON 문자열로."""
    path = DATA / "bundles.json"
    if not path.exists():
        return "{}"
    return path.read_text(encoding="utf-8").replace("</", "<\\/")


def page(
    out_root: Path,
    rel_path: str,
    *,
    title: str,
    desc: str,
    body: str,
    base: str,
    active: str = "",
    og_type: str = "website",
    jsonld: str = "",
    keywords: str = "",
    extra_head: str = "",
    og_image: str = "",
    og_image_alt: str = "",
    og_image_size: tuple[int, int] | None = None,
    scripts: str = "",
    inline_css: bool = False,
) -> Path:
    up = "../" * rel_path.count("/")
    canonical = f"{base.rstrip('/')}/{rel_path}"
    if rel_path.endswith("index.html"):
        canonical = f"{base.rstrip('/')}/{rel_path[: -len('index.html')]}"
    share_img = og_image or (base.rstrip('/') + '/images/courses/hero_kyoto_street.jpg')
    if og_image and not og_image_size:
        # v36: og:image 를 직접 넘긴 페이지(가이드·도시 허브)가 og:image:width/height 를 빠짐없이 갖도록
        # 실제 이미지 파일에서 픽셀 크기를 읽는다(없으면 기존처럼 생략).
        try:
            from urllib.parse import unquote as _unq, urlparse as _urlparse
            from PIL import Image as _PILImage
            _fp = ROOT / _unq(_urlparse(og_image).path).lstrip('/')
            if _fp.is_file():
                with _PILImage.open(_fp) as _im:
                    og_image_size = (_im.width, _im.height)
        except Exception:
            pass
    img_w, img_h = og_image_size or ((2000, 1125) if not og_image else (0, 0))
    size_meta = (
        f'\n<meta property="og:image:width" content="{img_w}" />'
        f'\n<meta property="og:image:height" content="{img_h}" />'
        if img_w and img_h else ""
    )
    head = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}" />
{f'<meta name="keywords" content="{esc(keywords)}" />' if keywords else ''}
<meta name="robots" content="index, follow, max-image-preview:large" />
<meta name="googlebot" content="index, follow" />
{VERIFY_META}
{ADSENSE}
<meta name="author" content="{SITE_NAME}" />
<link rel="canonical" href="{canonical}" />
<meta name="theme-color" content="#F4F6F8" />
<meta property="og:type" content="{og_type}" />
<meta property="og:site_name" content="{SITE_NAME}" />
<meta property="og:locale" content="ko_KR" />
<meta property="og:url" content="{canonical}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="{share_img}" />{size_meta}
<meta property="og:image:alt" content="{esc(og_image_alt or title)}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@trippick.travel" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<meta name="twitter:image" content="{share_img}" />
<meta name="twitter:image:alt" content="{esc(og_image_alt or title)}" />
<link rel="preload" as="font" type="font/woff2" href="{up}assets/fonts/PretendardVariable.subset.91.woff2" crossorigin />
<link rel="preload" as="font" type="font/woff2" href="{up}assets/fonts/PretendardVariable.subset.86.woff2" crossorigin />
<link rel="preload" as="font" type="font/woff2" href="{up}assets/fonts/PretendardVariable.subset.90.woff2" crossorigin />
<link rel="stylesheet" href="{up}assets/site.css?v={CSS_V}" />
<link rel="stylesheet" href="{up}assets/fonts/pretendard.css" />
<link rel="icon" href="{FAVICON}" />
{ga4_head()}
{jsonld}
{extra_head}
</head>
<body>
{SPRITE}
{header_html(up, active)}
<main class="pg-main" id="main">
{body}
</main>
{footer_html(up)}
<script src="{up}assets/trip-save.js?v={JS_V}" defer></script>
{f'<script type="application/json" id="tpBundles">{bundles_payload()}</script>' if "data-tp-bundle" in body else ''}
<script src="{up}assets/tp-v35.js?v={JS_V35}" defer></script>
<script src="{up}assets/tp-v43.js?v={JS_V43}" defer></script>
{f'<script src="{up}assets/tp-v44.js?v={JS_V44}" defer></script>' if 'id="sosPanels"' in body else ''}
{scripts}
</body>
</html>
"""
    target = out_root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if inline_css:
        # v50: /stays 처럼 유입이 많은 페이지는 CSS 를 HTML 안에 넣어 왕복(RTT) 한 번을 줄인다
        link = f'<link rel="stylesheet" href="{up}assets/site.css?v={CSS_V}" />'
        if link in head and GLOBAL_CSS:
            head = head.replace(link, "<style>\n" + GLOBAL_CSS + "\n</style>", 1)
    # v49: 지연 로드 이미지는 디코딩을 메인 스레드에서 떼어낸다(INP·렌더 부담 감소)
    html_out = re.sub(r'<img\b(?![^>]*\bdecoding=)', '<img decoding="async"', clean_site_urls(head, base))
    target.write_text(html_out, encoding="utf-8")
    return target


# ----------------------------------------------------------------------
# v48 — 구조화 데이터 공통 노드(Organization·WebSite·BreadcrumbList)
#   구글은 Article·도구 페이지의 publisher/logo 와 사이트 단위 Organization 을
#   같은 @id 로 묶을 때 브랜드 엔티티를 안정적으로 인식합니다.
#   로고는 images/logo-512.png(빌드가 deploy_site 로 복사합니다).
# ----------------------------------------------------------------------
ORG_LOGO_PATH = "/images/logo-512.png"
ORG_DESC = "여행 상품·숙소·환전·수하물·공항 이동을 같은 기준으로 비교하는 여행 준비 사이트"


def org_ld(base: str) -> dict:
    b = base.rstrip("/")
    return {
        "@type": "Organization",
        "@id": b + "/#organization",
        "name": SITE_NAME,
        "url": b + "/",
        "logo": {"@type": "ImageObject", "url": b + ORG_LOGO_PATH, "width": 512, "height": 512},
        "description": ORG_DESC,
    }


def website_ld(base: str) -> dict:
    b = base.rstrip("/")
    return {
        "@type": "WebSite",
        "@id": b + "/#website",
        "url": b + "/",
        "name": SITE_NAME,
        "inLanguage": "ko-KR",
        "publisher": {"@id": b + "/#organization"},
    }


def breadcrumb_ld(base: str, items: list) -> dict:
    """items = [(이름, 경로 or None), …] — 마지막 항목은 현재 페이지라 item 을 비웁니다."""
    b = base.rstrip("/")
    els = []
    for i, (name, path) in enumerate(items, 1):
        node = {"@type": "ListItem", "position": i, "name": name}
        if path:
            node["item"] = b + "/" + path.lstrip("/")
        els.append(node)
    return {"@type": "BreadcrumbList", "itemListElement": els}


def graph_ld(*nodes) -> str:
    body = {"@context": "https://schema.org", "@graph": [n for n in nodes if n]}
    raw = json.dumps(body, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{raw}</script>'


# ----------------------------------------------------------------------
# 상품 카드 (data/*.json 의 실제 판매 상품)
# ----------------------------------------------------------------------
def won(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def product_cards(guide: dict) -> str:
    rows = []
    tours = {t["id"]: t for t in TOURS}
    ess = {e["id"]: e for e in ESSENTIALS}

    for pid in guide.get("tours", [])[:3]:
        t = tours.get(pid)
        if not t:
            continue
        rows.append(
            f"""      <a class="side-prod" href="{t['url']}" target="_blank" rel="noopener sponsored">
        <span class="sp-top"><span class="sp-n">{esc(t['type'])}</span><span class="sp-m">{esc(t['duration'] if t.get('duration') else '')}</span></span>
        <span class="sp-t">{esc(t['title'])}</span>
        <span class="sp-m"><span>{esc(t['seller'])}</span><span><b>{won(t['sale'])}원</b>~</span><span>제휴</span></span>
      </a>"""
        )
    for pid in guide.get("essentials", [])[:2]:
        e = ess.get(pid)
        if not e:
            continue
        rows.append(
            f"""      <a class="side-prod" href="{e.get('url') or e['naverMe']}" target="_blank" rel="noopener sponsored">
        <span class="sp-top"><span class="sp-n">{esc(e['categoryLabel'])}</span></span>
        <span class="sp-t">{esc(e['name'])}</span>
        <span class="sp-m"><span>{esc(e['store'])}</span><span><b>{won(e['price'])}원</b></span><span>제휴</span></span>
      </a>"""
        )
    if not rows:
        return ""
    return f"""    <div class="side-card">
      <h3>이 글에 나온 상품 <em>제휴</em></h3>
{chr(10).join(rows)}
      <p class="side-note">가격은 2026-11-20 확인 기준 최저가입니다. 예약·구매 시점에 상세페이지에서 최종 확인하세요.</p>
    </div>"""


def related_guides(guide: dict) -> str:
    items = []
    by_slug = {g["slug"]: g for g in GUIDES_LIST}
    for slug in guide.get("related", [])[:5]:
        g = by_slug.get(slug)
        if not g:
            continue
        items.append(
            f'        <li><a href="{g["slug"]}.html">{esc(g["navTitle"])}<span>{esc(g["category"])} · {g["read"]}분</span></a></li>'
        )
    if not items:
        return ""
    return f"""    <div class="side-card">
      <h3>함께 읽으면 좋은 글</h3>
      <ul class="side-list">
{chr(10).join(items)}
      </ul>
    </div>"""


def cta_band(up: str, title: str, text: str) -> str:
    return f"""<div class="pg-cta">
  <div><b>{title}</b><p>{text}</p></div>
  <div class="btns">
    <a href="{up}index.html#planner">예산 계산기</a>
    <a class="line" href="{up}index.html#alert">특가 알림 받기</a>
  </div>
</div>"""


ADSENSE_CLIENT = "ca-pub-9563082990728787"


def ad_slot(slot: str, title: str, text: str, href: str, cta: str, kicker: str = "트립픽 추천") -> str:
    """가이드·목록 페이지용 광고 슬롯.
    승인 전에는 내부 추천 배너만 보이고(빈 <ins> 없음) 레이아웃이 깨지지 않습니다.
    승인 후에는 주석을 풀고 {client}·data-ad-slot 두 값만 바꾸면 바로 켜집니다."""
    return f'''<aside class="adslot adslot--flat" data-ad-slot="{slot}" aria-label="광고·추천 영역">
  <!-- v22 광고 슬롯 — 승인 전이라 주석 상태입니다. 로더 스크립트는 <head> 에 이미 있고,
       아래 주석을 풀고 data-ad-slot="0000000000" 만 애드센스 광고 단위 ID로 바꾸면 표시됩니다.
  <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="0000000000" data-ad-format="auto" data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  -->
  <a class="adslot-in" href="{href}">
    <span class="adslot-tag">{kicker}</span>
    <span class="adslot-copy"><b>{title}</b><span>{text}</span></span>
    <span class="adslot-go">{cta} →</span>
  </a>
</aside>'''


def inject_mid_ad(body_html: str, slot_html: str) -> str:
    """본문 세 번째 <h2> 앞에 광고 슬롯 삽입(글 중간). h2가 모자라면 본문 끝에 붙입니다."""
    parts = re.split(r"(?=<h2\b)", body_html)
    if len(parts) >= 4:
        return "".join(parts[:3]) + slot_html + "\n\n" + "".join(parts[3:])
    return body_html + "\n\n" + slot_html


def side_common(up: str) -> str:
    return f"""    <div class="side-card side-common">
      <h3>바로가기</h3>
      <p>도시별 페이지에서 투어·맛집·선물·숙소를 한 번에 볼 수 있습니다.</p>
      <a class="go" href="{up}cities/index.html">도시별 여행 페이지 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <p>코스·상품·필수품을 한 화면에서 같은 기준으로 비교합니다.</p>
      <a class="go" href="{up}index.html#planner">내 예산으로 총액 계산 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#essentials">여행 필수품 보기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#gifts">나라별 선물·기념품 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}checklist.html">여행 준비 D-Day 순서 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}exchange.html">환율·일본 면세 계산기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}baggage.html">항공사별 수하물 규정 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#tripcom">도시별 숙소·항공권 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#regions">지역별 투어 보기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}guides/index.html">가이드 전체 보기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </div>"""


# ----------------------------------------------------------------------
# v15: 가이드 요약 박스 · 도시 연결 블록 · 가이드 검색 메타
# ----------------------------------------------------------------------
def guide_extra(slug: str) -> dict:
    return (EXTRA.get("guides") or {}).get(slug) or {}


def hub_by_slug(slug):
    if not slug:
        return None
    return next((h for h in hub_list() if h["slug"] == slug), None)


def guide_summary(g: dict) -> str:
    """본문 맨 위 요약 박스 — 결론 한 줄 + 확인한 값 2개 + 최종 검증일."""
    ex = guide_extra(g["slug"])
    take = ex.get("takeaway")
    if not take:
        return ""
    facts = "".join(
        f'<li><span>{esc(k)}</span><b>{esc(v)}</b></li>' for k, v in (ex.get("facts") or [])[:2]
    )
    hub = hub_by_slug(ex.get("hub"))
    hub_link = ""
    if hub:
        hub_link = (
            f'<a class="g-sum-hub" href="../{hub["slug"]}.html">'
            f'<span>{esc(hub["name"])} 페이지</span>'
            f'<b>투어·맛집·선물·숙소를 한 화면에</b>'
            f'<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
        )
    fact_list = f'<ul class="g-sum-facts">{facts}</ul>' if facts else ""
    return f"""<div class="g-sum">
  <div class="g-sum-top"><b>3줄 요약</b><span class="g-sum-date">최종 검증일 {g['updated'].replace('-', '.')} · {esc(g.get('fxNote') or '가격 확인 2026.11')}</span></div>
  <p class="g-sum-lead">{esc(take)}</p>
  {fact_list}
  {hub_link}
</div>"""


# 가이드 → 도시 허브 하단에 붙일 실제 판매 링크(tripcom id · essentials id)
HUB_NEXT = {
    "osaka": {"trip": ["ticket_osaka", "rail_osaka", "transfer_kix", "esim_osaka"], "ess": []},
    "tokyo": {"trip": ["rail_skyliner", "ticket_tokyo", "esim_tokyo"], "ess": ["tokyo-metro-pass"]},
    "fukuoka": {"trip": ["ticket_fukuoka", "transfer_fuk"], "ess": ["jp-esim-usimsa-3d"]},
    "danang": {"trip": ["ticket_danang", "transfer_dad", "esim_danang"], "ess": ["danang-bana-hills"]},
    "bangkok": {"trip": ["ticket_bangkok", "transfer_bkk", "esim_bangkok"], "ess": []},
    "taipei": {"trip": ["ticket_taipei", "transfer_tpe", "esim_taipei"], "ess": []},
    "jeju": {"trip": ["ticket_jeju", "transfer_cju", "car_jeju"], "ess": []},
}


def tripcom_items() -> dict:
    out = {}
    for key in ("tickets", "transfers", "cars", "esims", "rails"):
        for it in TRIPCOM.get(key) or []:
            out[it["id"]] = it
    return out


def guide_next(g: dict) -> str:
    """가이드 하단 — 해당 도시 허브 + 실수익 상품 3 + 같은 도시 가이드 3."""
    ex = guide_extra(g["slug"])
    hub = hub_by_slug(ex.get("hub"))
    tc = tripcom_items()
    ess = {e["id"]: e for e in ESSENTIALS}

    prods = []
    if hub:
        conf = HUB_NEXT.get(hub["slug"], {"trip": [], "ess": []})
        for pid in conf["trip"]:
            it = tc.get(pid)
            if not it:
                continue
            prods.append(
                f'<a class="gnext-p" href="{esc(it["url"])}" target="_blank" rel="noopener sponsored">'
                f'<span class="gnext-k">{esc(it["label"])}</span>'
                f'<b>{esc(it["title"])}</b>'
                f'<span class="gnext-m">{esc(it.get("highlight") or "")}</span>'
                f'<span class="gnext-go">예약 페이지 →</span></a>'
            )
            if len(prods) == 3:
                break
        if len(prods) < 3:
            for eid in conf["ess"]:
                e = ess.get(eid)
                if not e:
                    continue
                prods.append(
                    f'<a class="gnext-p" href="{esc(e.get("url") or e["naverMe"])}" target="_blank" rel="noopener sponsored">'
                    f'<span class="gnext-k">{esc(e["categoryLabel"])}</span>'
                    f'<b>{esc(e["name"])}</b>'
                    f'<span class="gnext-m">{esc(e["store"])} · {won(e["price"])}원</span>'
                    f'<span class="gnext-go">구매 페이지 →</span></a>'
                )
                if len(prods) == 3:
                    break
    grid = "".join(prods)
    grid_html = f'<div class="gnext-grid">{grid}</div>' if grid else ""

    # 같은 도시(없으면 같은 지역) 가이드 3편
    region_codes = set(ex.get("regions") or [])
    pool = []
    for other in GUIDES_LIST:
        if other["slug"] == g["slug"]:
            continue
        oex = guide_extra(other["slug"])
        if hub and oex.get("hub") == hub["slug"]:
            pool.append(other)
        elif not hub and region_codes & set(oex.get("regions") or []):
            pool.append(other)
    # 관련 글에 적힌 순서를 먼저
    related = [s for s in (g.get("related") or [])]
    pool.sort(key=lambda x: (related.index(x["slug"]) if x["slug"] in related else 99, x["read"]))
    picks = pool[:3]
    glinks = "".join(
        f'<a href="{p["slug"]}.html"><span>{esc(p["category"])}</span>{esc(p["navTitle"])}<i>{p["read"]}분</i></a>'
        for p in picks
    )
    gtitle = f"{esc(hub['name'])} 가이드 더 보기" if hub else "같은 지역 가이드 더 보기"
    head_link = (
        f'<a href="../{hub["slug"]}.html">{esc(hub["name"])} 도시 페이지 전체 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
        if hub
        else '<a href="../cities/index.html">도시별 페이지 7곳 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
    )
    sub = (
        f'<span>{esc(hub["name"])} · 제휴 링크는 실제 예약·구매 페이지로 연결됩니다</span>'
        if hub
        else '<span>이 지역 글은 도시 허브로 이어지지 않아, 같은 지역 가이드와 필수품으로 연결했습니다</span>'
    )
    return f"""<section class="gnext" aria-label="이 여행에서 바로 쓰는 것">
  <div class="gnext-head"><div><b>이 여행에서 바로 쓰는 것</b>{sub}</div>{head_link}</div>
{grid_html}
  <div class="gnext-g"><b>{gtitle}</b>{glinks}</div>
</section>"""


def guide_actions(g: dict) -> str:
    """v28 가이드 하단 — 숙소·준비·다음 글로 이어지는 3장 카드(모든 가이드 공통).
    지역을 알 수 없으면 테마 숙소로, 도시 허브가 없으면 같은 지역 가이드로 잇는다."""
    ex = guide_extra(g["slug"])
    regions = {r["id"]: r for r in STAYS.get("regions", [])}
    hotels = STAYS.get("hotels", [])

    def n_of(rid):
        return sum(1 for h in hotels if h["region"] == rid)

    targets = [rid for rid in (ex.get("stayRegions") or []) if rid in regions and n_of(rid)]
    if not targets:
        for key, rid in STAYS_GUIDE_REGION:
            if key in g["slug"] and rid in regions and n_of(rid):
                targets = [rid]
                break

    if targets:
        rid = max(targets, key=n_of)
        r = regions[rid]
        if len(targets) > 1:
            total_n = sum(n_of(x) for x in targets)
            label = "·".join(regions[x]["name"] for x in targets)
            stay = (
                f'<a class="gact" href="../stays.html#{rid}">'
                f'<span class="gact-k">숙소 · 바로 확인</span>'
                f'<b>{esc(label)} 숙소 {total_n}곳</b>'
                f'<span class="gact-m">평점·리뷰·1박 최저가를 한 표에서 비교</span>'
                f'<span class="gact-go">숙소 표 보기 →</span></a>'
            )
        else:
            stay = (
                f'<a class="gact" href="../stays.html#{rid}">'
                f'<span class="gact-k">숙소 · 바로 확인</span>'
                f'<b>{esc(r["name"])} 숙소 {n_of(rid)}곳</b>'
                f'<span class="gact-m">평점·리뷰·1박 최저가를 한 표에서 비교</span>'
                f'<span class="gact-go">숙소 표 보기 →</span></a>'
            )
    else:
        theme = next((t for k, t in STAYS_GUIDE_THEME.items() if k in g["slug"]), "ocean")
        tname = _stay_theme_name().get(theme, "오션뷰")
        cnt = sum(1 for h in hotels if theme in (h.get("themes") or []))
        stay = (
            f'<a class="gact" href="../stays.html?theme={theme}">'
            f'<span class="gact-k">숙소 · 바로 확인</span>'
            f'<b>{esc(tname)} 숙소 {cnt}곳</b>'
            f'<span class="gact-m">국내·해외 숙소를 같은 테마로 비교</span>'
            f'<span class="gact-go">숙소 표 보기 →</span></a>'
        )

    prep = (
        '<a class="gact" href="../checklist.html">'
        '<span class="gact-k">준비 · 다음 단계</span>'
        '<b>여행 준비 D-Day 타임라인</b>'
        '<span class="gact-m">D-30 숙소·항공 → D-14 투어 → D-3 짐 → D-0 체크인</span>'
        '<span class="gact-go">체크리스트 열기 →</span></a>'
    )

    hub = hub_by_slug(ex.get("hub"))
    if hub:
        third = (
            f'<a class="gact" href="../{hub["slug"]}.html">'
            f'<span class="gact-k">도시 · 한 화면에</span>'
            f'<b>{esc(hub["name"])} 도시 페이지</b>'
            f'<span class="gact-m">투어·맛집·선물·숙소를 한 화면에서</span>'
            f'<span class="gact-go">도시 페이지 열기 →</span></a>'
        )
    else:
        by_slug = {x["slug"]: x for x in GUIDES_LIST}
        pick = next((by_slug[s] for s in (g.get("related") or []) if s in by_slug and s != g["slug"]), None)
        if not pick:
            pool = [x for x in GUIDES_LIST if x["slug"] != g["slug"] and x["category"] == g["category"]]
            pick = pool[0] if pool else None
        if pick:
            third = (
                f'<a class="gact" href="{pick["slug"]}.html">'
                f'<span class="gact-k">다음 추천 글</span>'
                f'<b>{esc(pick["navTitle"])}</b>'
                f'<span class="gact-m">{esc(pick["category"])} · 읽는 시간 {pick["read"]}분</span>'
                f'<span class="gact-go">이어서 읽기 →</span></a>'
            )
        else:
            third = (
                '<a class="gact" href="index.html">'
                '<span class="gact-k">다음 추천 글</span><b>가이드 전체 보기</b>'
                f'<span class="gact-m">국내·해외 {len(GUIDES_LIST)}편을 지역·주제로 찾기</span>'
                '<span class="gact-go">가이드 목록 →</span></a>'
            )

    return f"""<section class="gacts" aria-label="다음 단계로 바로 확인">
  <div class="gacts-h"><b>다음 단계 · 바로 확인</b><span>이 글에서 계산한 일정에 그대로 쓰는 3가지</span></div>
  <div class="gacts-grid">{stay}{prep}{third}</div>
</section>"""


def guide_search_blob(g: dict) -> str:
    ex = guide_extra(g["slug"])
    parts = [
        g["navTitle"],
        strip_tags(g["h1"]),
        g.get("dek", ""),
        g.get("keywords", ""),
        g["category"],
        " ".join(ex.get("tags") or []),
        " ".join(ex.get("regions") or []),
        ex.get("takeaway") or "",
    ]
    for k, v in ex.get("facts") or []:
        parts += [k, v]
    return re.sub(r"\s+", " ", " ".join(parts)).strip().lower()


def guide_filter_script() -> str:
    """가이드 인덱스 실시간 검색·필터 (서버 없이 카드 data 속성만 사용)."""
    return """<script>
(function () {
  var bar = document.querySelector('.gfind');
  if (!bar) return;
  var q = document.getElementById('gq');
  var clearBtn = document.getElementById('gqClear');
  var countEl = document.getElementById('gcount');
  var emptyEl = document.getElementById('gempty');
  var resetBtn = document.getElementById('greset');
  var cards = [].slice.call(document.querySelectorAll('.gcard'));
  var secs = [].slice.call(document.querySelectorAll('.gi-sec'));
  var st = { q: '', region: 'all', tag: 'all' };

  function norm(s) { return (s || '').toLowerCase().replace(/\\s+/g, ' ').trim(); }

  function apply() {
    var tokens = norm(st.q).split(' ').filter(Boolean);
    var n = 0;
    cards.forEach(function (c) {
      var hay = c.getAttribute('data-q') || '';
      var okQ = tokens.every(function (t) { return hay.indexOf(t) > -1; });
      var okR = st.region === 'all' || (' ' + (c.getAttribute('data-region') || '') + ' ').indexOf(' ' + st.region + ' ') > -1;
      var okT = st.tag === 'all' || (' ' + (c.getAttribute('data-tags') || '') + ' ').indexOf(' ' + st.tag + ' ') > -1;
      var on = okQ && okR && okT;
      c.hidden = !on;
      if (on) n++;
    });
    secs.forEach(function (s) {
      var any = [].slice.call(s.querySelectorAll('.gcard')).some(function (c) { return !c.hidden; });
      s.hidden = !any;
    });
    if (countEl) countEl.textContent = n;
    if (emptyEl) emptyEl.hidden = n > 0;
    if (clearBtn) clearBtn.hidden = !st.q;
  }

  function syncUrl() {
    if (!window.history || !history.replaceState) return;
    var p = [];
    if (st.q) p.push('q=' + encodeURIComponent(st.q));
    if (st.region !== 'all') p.push('region=' + st.region);
    if (st.tag !== 'all') p.push('tag=' + encodeURIComponent(st.tag));
    history.replaceState(null, '', location.pathname + (p.length ? '?' + p.join('&') : '') + location.hash);
  }

  function setRegion(v) {
    st.region = v;
    bar.querySelectorAll('.gf-chip[data-region]').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-region') === v);
      b.setAttribute('aria-pressed', String(b.getAttribute('data-region') === v));
    });
  }
  function setTag(v) {
    st.tag = v;
    bar.querySelectorAll('.gf-chip[data-tag]').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-tag') === v);
      b.setAttribute('aria-pressed', String(b.getAttribute('data-tag') === v));
    });
  }

  bar.addEventListener('click', function (e) {
    var chip = e.target.closest('.gf-chip');
    if (!chip) return;
    if (chip.hasAttribute('data-region')) setRegion(chip.getAttribute('data-region'));
    if (chip.hasAttribute('data-tag')) setTag(chip.getAttribute('data-tag'));
    apply(); syncUrl();
  });

  if (q) {
    q.addEventListener('input', function () { st.q = q.value; apply(); syncUrl(); });
    q.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { q.value = ''; st.q = ''; apply(); syncUrl(); }
    });
  }
  if (clearBtn) clearBtn.addEventListener('click', function () { q.value = ''; st.q = ''; q.focus(); apply(); syncUrl(); });
  if (resetBtn) resetBtn.addEventListener('click', function () {
    q.value = ''; st.q = ''; setRegion('all'); setTag('all'); apply(); syncUrl();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); }
  });

  var params = new URLSearchParams(location.search);
  if (params.get('q')) { st.q = params.get('q'); q.value = st.q; }
  if (params.get('region')) setRegion(params.get('region'));
  if (params.get('tag')) setTag(params.get('tag'));
  apply();
})();
</script>"""


# ----------------------------------------------------------------------
# 가이드 목차 바로가기 + 읽기 시간 (v38)
# ----------------------------------------------------------------------
def _toc_label(inner: str) -> str:
    """h2 안의 태그를 걷어내고 칩에 넣을 짧은 제목으로 다듬는다."""
    t = html.unescape(re.sub(r"<[^>]+>", "", inner))
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 28:
        for sep in (" — ", " – ", " · ", "·", ",", "("):
            if sep in t:
                cut = t.split(sep)[0].strip()
                if len(cut) >= 6:
                    t = cut
                    break
    if len(t) > 30:
        t = t[:29].rstrip() + "…"
    return t


def auto_toc(body_html: str) -> tuple[str, str, int, int]:
    """본문 h2 에서 목차·읽기 시간을 자동 생성한다.

    손으로 쓴 <nav class="toc"> 는 같은 목차가 두 번 나오지 않도록 걷어내고,
    h2 에 id 가 없으면 secN 을 붙여 앵커를 만든다.
    반환: (정리된 본문, 목차 HTML, 공백 제외 글자수, 예상 읽기 분)
    """
    body_html = re.sub(r'<nav class="toc".*?</nav>\s*', "", body_html, count=1, flags=re.S)
    heads: list[tuple[str, str]] = []

    def _h2(m: "re.Match") -> str:
        attrs, inner = m.group(1), m.group(2)
        mid = re.search(r'id="([^"]+)"', attrs)
        if mid:
            hid = mid.group(1)
        else:
            hid = f"sec{len(heads) + 1}"
            attrs = f'{attrs} id="{hid}"'
        heads.append((hid, _toc_label(inner)))
        return f"<h2{attrs}>{inner}</h2>"

    body_html = re.sub(r"<h2([^>]*)>(.*?)</h2>", _h2, body_html, flags=re.S)
    chars = len(re.sub(r"\s", "", B.body_text(body_html)))
    mins = max(2, -(-chars // 450))
    if len(heads) < 2:
        return body_html, "", chars, mins

    chips = "".join(
        f'<a href="#{esc(hid)}"><i>{i}</i>{esc(label)}</a>'
        for i, (hid, label) in enumerate(heads, 1)
    )
    rows = "".join(
        f'<li><a href="#{esc(hid)}">{esc(label)}</a></li>' for hid, label in heads
    )
    toc = f"""<div class="gtoc">
  <div class="gtoc-top">
    <span class="gtoc-read"><svg class="ic" aria-hidden="true"><use href="#i-clock"/></svg> 본문 {chars:,}자 · 약 {mins}분</span>
    <button class="gtoc-btn" type="button" aria-expanded="false" aria-controls="gtoc-list"><span>전체 목차</span><b>{len(heads)}</b><span class="gtoc-cv" aria-hidden="true"></span></button>
  </div>
  <nav class="gtoc-chips" aria-label="목차 바로가기">{chips}</nav>
  <ol class="gtoc-list" id="gtoc-list" hidden>{rows}</ol>
</div>
<script>(function(){{var b=document.querySelector('.gtoc-btn');if(!b)return;var l=document.getElementById('gtoc-list');b.addEventListener('click',function(){{var open=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',open?'false':'true');if(l)l.hidden=open;}});}})();</script>"""
    return body_html, toc, chars, mins


# ----------------------------------------------------------------------
# 가이드 페이지
# ----------------------------------------------------------------------
def guide_bm(g: dict) -> str:
    """v43: 가이드 91편 공통 ★ 참고 글 저장 버튼(상단 메타 아래).

    저장은 브라우저(localStorage)에만 되고, 헤더 찜/견적 모달의 ‘저장한 참고 글’에서 다시 연다.
    """
    item = json.dumps({"t": g["navTitle"], "c": g["category"], "r": g["read"]},
                      ensure_ascii=False, separators=(",", ":"))
    return f"""      <div class="pg-bm">
        <button class="bm-btn" type="button" data-bm="/guides/{g['slug']}.html" data-bm-item="{esc(item)}" aria-pressed="false">
          <span class="bm-star" aria-hidden="true">★</span><span class="bm-t">참고 글 저장</span>
        </button>
        <span class="bm-note">이 브라우저에 저장 · 헤더 ♥ 안 ‘저장한 참고 글’에서 다시 열기</span>
      </div>"""


def guide_tool_hub(g: dict):
    """v45: 가이드가 다루는 도시(첫 투어의 city) → 도시 허브. 없으면 None."""
    order = {}
    for h in hub_list():
        for cid in (h.get("cityIds") or [h["slug"]]):
            order[cid] = h
    if g.get("toolHub") and g["toolHub"] in order:
        return order[g["toolHub"]]
    for tid in g.get("tours") or []:
        t = next((x for x in TOURS if x["id"] == tid), None)
        if t and t.get("city") in order:
            return order[t["city"]]
    return None


def guide_tools(g: dict) -> str:
    """v45: 가이드 상단 도구 바 — 환율·패스·SOS 를 이 글의 도시 프리셋으로.

    도시를 특정할 수 없는 글(준비물·비교)은 도구 페이지만 연결하고 도시 문구는 뺀다.
    """
    hub = guide_tool_hub(g)
    slug = hub["slug"] if hub else ""
    country = (hub.get("country") if hub else "") or ""
    links = tool_links(slug, country, up="../")
    if not hub:   # 도시를 특정할 수 없는 글은 국가 프리셋 없이 도구만 연결한다
        links["sos"] = "../sos.html"
    fx_text = fx_basis(links["cur"]) if links["cur"] else "12개 통화 · 일본 면세"
    where = esc(hub["name"]) if hub else "여행지"
    return f"""      <nav class="gtools" aria-label="{where} 바로 쓰는 도구">
        <span class="gtools-k"><b>{where}</b> 바로 쓰는 도구</span>
        <a class="gtool" href="{links['exchange']}"><span class="gtool-k">EXCHANGE</span><b>환율 계산</b><span class="gtool-n">{esc(fx_text)}</span></a>
        <a class="gtool" href="{links['passes']}"><span class="gtool-k">PASS</span><b>교통패스 본전</b><span class="gtool-n">하루 몇 회 타면 남는지</span></a>
        <a class="gtool" href="{links['sos']}"><span class="gtool-k">SOS</span><b>현지 긴급번호</b><span class="gtool-n">경찰·구급·공관·현지어</span></a>
      </nav>"""


def guide_page(out_root: Path, g: dict, base: str) -> Path:
    slug = g["slug"]
    body_html = read(GUIDES / f"{slug}.html")
    body_html, toc_html, _chars, read_min = auto_toc(body_html)
    g["read"] = read_min

    # v38: guides.json 의 faq 배열 한 곳에서 화면 FAQ 와 FAQPage JSON-LD 를 같이 만든다
    faq_json = ""
    if g.get("faq"):
        faq_html = "".join(
            f'<details class="fq"><summary><span class="fq-q"><b>Q.</b> {esc(q)}</span>'
            f'<span class="fq-ic" aria-hidden="true"></span></summary>'
            f'<div class="fq-a">{esc(a)}</div></details>'
            for q, a in g["faq"]
        )
        body_html = body_html.replace("<!-- @FAQ -->", faq_html)
        faq_json = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in g["faq"]
                ],
            },
            ensure_ascii=False,
        )
    body_html = inject_mid_ad(
        body_html,
        ad_slot(
            "guide-mid",
            "이 글의 계산, 내 일정으로 다시 해보기",
            "인원·지역을 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 계산합니다.",
            "../index.html#planner",
            "예산 계산기",
        ),
    )

    hero_img = ""
    if g.get("image"):
        # v49: 히어로도 WebP 변형을 먼저 제안 (모바일 480·720px), 없으면 원본 JPEG
        src_set = pic_sources(g["image"], "../", "(max-width:620px) 100vw, 800px")
        hero_img = f"""      <figure class="pg-hero-img">
        <picture>{src_set}
        <img src="../{esc(g['image'])}" alt="{esc(g['imageAlt'])}" width="1200" height="630" loading="eager" decoding="async" />
        </picture>
        <figcaption>{esc(g.get('imageCredit', '사진: Pexels'))}</figcaption>
      </figure>"""

    b0 = base.rstrip("/")
    pub = {
        "@type": "Organization",
        "@id": b0 + "/#organization",
        "name": SITE_NAME,
        "url": b0 + "/",
        "logo": {"@type": "ImageObject", "url": b0 + ORG_LOGO_PATH, "width": 512, "height": 512},
    }
    related_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": strip_tags(g["h1"]),
            "description": g["desc"],
            "datePublished": g["published"],
            "dateModified": g["updated"],
            "inLanguage": "ko",
            "author": pub,
            "publisher": pub,
            "articleSection": g.get("category", ""),
            "keywords": g.get("keywords", ""),
            "mainEntityOfPage": f"{b0}/guides/{slug}",
            "isPartOf": {"@id": b0 + "/#website"},
            "image": f"{b0}/{g['image']}" if g.get("image") else None,
        },
        ensure_ascii=False,
    )
    breadcrumb = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "트립픽", "item": f"{base.rstrip('/')}/"},
                {"@type": "ListItem", "position": 2, "name": "여행 가이드", "item": f"{base.rstrip('/')}/guides/"},
                {"@type": "ListItem", "position": 3, "name": g["navTitle"], "item": f"{base.rstrip('/')}/guides/{slug}"},
            ],
        },
        ensure_ascii=False,
    )
    body = f"""<div class="pg-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="../index.html">홈</a><i></i><a href="index.html">여행 가이드</a><i></i><b>{esc(g['navTitle'])}</b></nav>
    <span class="pg-kicker">{esc(g['category'])}</span>
    <div class="pg-head">
      <h1>{g['h1']}</h1>
      <p class="dek">{esc(g['dek'])}</p>
      <div class="pg-meta">
        <span><b>트립픽 편집</b></span><i></i>
        <span>최종 검증일 {g['updated'].replace('-', '.')}</span><i></i>
        <span>읽는 시간 약 {g['read']}분</span><i></i>
        <span>{esc(g.get('fxNote') or '가격 확인 2026.11.20')}</span>
      </div>
{guide_bm(g)}
{guide_tools(g)}
    </div>
{hero_img}
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
{share_row('guide')}
{cont_bar('가이드', g['navTitle'], '/guides/' + slug, g.get('image') or '')}
    <div class="pg-grid">
      <article class="doc">
{guide_summary(g)}
{toc_html}
{body_html}
      </article>
      <aside class="pg-side">
{product_cards(g)}
{related_guides(g)}
{side_common('../')}
      </aside>
    </div>
{guide_stays_box(g)}
{guide_next(g)}
{guide_actions(g)}
{share_row('guide')}
{cta_band('../', g.get('ctaTitle', '이 글의 계산, 내 일정으로 해보기'), g.get('ctaText', '인원과 지역을 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 총액을 계산합니다.'))}
  </div>
</div>"""

    body = body.replace(
        '<div class="pg-grid">',
        ad_slot(
            "guide-top",
            "숙소·항공은 도시별 최저가로",
            "트립닷컴 파트너스 링크로 도시 19곳 숙소·항공 12개 노선에 입장권·공항픽업·렌터카 16종, eSIM·유심 9개 도시와 유럽 전역 1종·공항철도 2개 노선을 더했습니다.",
            "../index.html#tripcom",
            "숙소·항공 보기",
        )
        + '\n    <div class="pg-grid">',
        1,
    )
    body = body.replace(
        '<div class="pg-cta">',
        ad_slot(
            "guide-bottom",
            "특가가 뜨면 가장 먼저 알려드릴게요",
            "원하는 여행지와 예산만 남기면 특가·땡처리 소식을 메일로 보내드립니다.",
            "../index.html#alert",
            "알림 신청",
        )
        + '\n<div class="pg-cta">',
        1,
    )

    return page(
        out_root,
        f"guides/{slug}.html",
        title=g["seoTitle"],
        desc=g["desc"],
        body=body,
        base=base,
        active="guides",
        og_type="article",
        keywords=g.get("keywords", ""),
        og_image=f"{base.rstrip('/')}/{g.get('ogImage') or g['image']}" if g.get("image") else "",
        og_image_alt=g.get("imageAlt", ""),
        jsonld=f'<script type="application/ld+json">{related_json}</script>\n<script type="application/ld+json">{breadcrumb}</script>'
        + (f'\n<script type="application/ld+json">{faq_json}</script>' if faq_json else ""),
    )


def guides_index(out_root: Path, base: str) -> Path:
    cats = []
    for g in GUIDES_LIST:
        if g["category"] not in cats:
            cats.append(g["category"])

    region_names = {r["code"]: r["name"] for r in EXTRA.get("regions", [])}
    # v31: 숙소 밴드의 지역 수는 stays.json에서 계산한다(하드코딩 금지)
    _stay_regions = STAYS.get("regions", [])
    _stay_kr_n = len([r for r in _stay_regions if r.get("scope") == "kr"])
    _stay_intl_n = len([r for r in _stay_regions if r.get("scope") != "kr"])

    sections = []
    for cat in cats:
        cards = []
        for g in [x for x in GUIDES_LIST if x["category"] == cat]:
            ex = guide_extra(g["slug"])
            thumb = (
                f'<div class="thumb"><picture>{pic_sources(g["image"], "../", "(max-width:620px) 92vw, 346px")}'
                f'<img src="../{esc(g["image"])}" alt="{esc(g["imageAlt"])}" loading="lazy" decoding="async" width="640" height="360" /></picture></div>'
                if g.get("image")
                else '<div class="thumb noimg">TRIPPICK GUIDE</div>'
            )
            tags = "".join(f'<span class="gc-tag">{esc(t)}</span>' for t in (ex.get("tags") or [])[:2])
            regions = " ".join(ex.get("regions") or [])
            cards.append(
                f"""        <a class="gcard" href="{g['slug']}.html" data-q="{esc(guide_search_blob(g))}" data-region="{esc(regions)}" data-tags="{esc(' '.join(ex.get('tags') or []))}">
          {thumb}
          <div class="gc-body">
            <span class="tag">{esc(g['category'])}</span>
            <h3>{esc(g['navTitle'])}</h3>
            <p>{esc(g['dek'])}</p>
            <div class="gc-foot"><b>{g['read']}분</b> · 최종 검증 {g['updated'].replace('-', '.')}</div>
            <div class="gc-tags">{tags}</div>
          </div>
        </a>"""
            )
        sections.append(
            f"""    <section class="gi-sec">
      <div class="gi-sec-head"><div><h2>{esc(cat)}</h2><p>{esc(CAT_NOTE.get(cat, ''))}</p></div></div>
      <div class="gi-grid">
{chr(10).join(cards)}
      </div>
    </section>"""
        )

    listing = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "트립픽 여행 가이드",
            "description": "예약 전에 실제로 계산해 본 비용·동선·교통패스 손익분기 가이드 모음",
            "url": f"{base.rstrip('/')}/guides/",
            "hasPart": [
                {
                    "@type": "Article",
                    "headline": g["navTitle"],
                    "url": f"{base.rstrip('/')}/guides/{g['slug']}.html",
                    "datePublished": g["published"],
                    "dateModified": g["updated"],
                }
                for g in GUIDES_LIST
            ],
        },
        ensure_ascii=False,
    )

    region_chips = "".join(
        f'<button class="gf-chip" type="button" data-region="{esc(r["code"])}">{esc(r["name"])}</button>'
        for r in EXTRA.get("regions", [])
    )
    tag_chips = "".join(
        f'<button class="gf-chip" type="button" data-tag="{esc(t)}">{esc(t)}</button>'
        for t in EXTRA.get("tags", [])
    )

    body = f"""<div class="pg-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="../index.html">홈</a><i></i><b>여행 가이드</b></nav>
    <span class="pg-kicker">TRIPPICK GUIDES · {len(GUIDES_LIST)}편</span>
    <div class="pg-head">
      <h1>예약 전에 <em>숫자로</em> 확인하는 여행 가이드</h1>
      <p class="dek">교통패스 본전, 현장 추가금, 우기·성수기 변수, 공항에서 시내까지 실제 요금. 상품 상세페이지를 하나씩 옮겨 적으면서 확인한 값으로 계산했습니다. 광고 문구 대신 손익분기와 실경비를 적었습니다.</p>
      <div class="pg-meta">
        <span><b>트립픽 편집</b></span><i></i>
        <span>전체 {len(GUIDES_LIST)}편</span><i></i>
        <span>최종 검증 {TODAY.strftime('%Y.%m.%d')}</span>
      </div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="gfind" role="search" aria-label="가이드 검색">
      <div class="gfind-row">
        <label class="gfind-in">
          <svg class="ic" aria-hidden="true"><use href="#i-search"/></svg>
          <input id="gq" type="search" placeholder="예: 오사카, eSIM, 우기, 리조트, 100엔" autocomplete="off" aria-label="가이드 검색어" />
          <button id="gqClear" class="gfind-x" type="button" hidden aria-label="검색 지우기">×</button>
        </label>
        <span class="gfind-count"><b id="gcount">{len(GUIDES_LIST)}</b>편</span>
      </div>
      <div class="gfind-chips" role="group" aria-label="여행지 필터">
        <button class="gf-chip on" type="button" data-region="all">전체 여행지</button>
        {region_chips}
      </div>
      <div class="gfind-chips gfind-chips--tag" role="group" aria-label="주제 필터">
        <button class="gf-chip on" type="button" data-tag="all">전체 주제</button>
        {tag_chips}
      </div>
    </div>
    <div class="gi-stays">
      <div><b>숙소부터 정하고 싶다면 — 테마별 찐숙소 {len(STAYS.get('hotels', []))}곳</b>
        <p>국내 {_stay_kr_n}개 지역과 해외 {_stay_intl_n}개 도시(유럽 파리·런던·로마·바르셀로나 포함) 숙소를 트립닷컴 평점·리뷰 수·1박 최저가로 비교했습니다. 호캉스·수영장, 오션뷰, 온천·스파, 역세권·도보, 가성비, 가족·풀빌라로 바로 좁힐 수 있습니다.</p></div>
      <div class="gi-stays-links">
        <a href="../stays.html">찐숙소 전체 보기</a>
        <a href="../stays.html?theme=ocean">오션뷰</a>
        <a href="../stays.html?theme=onsen">온천·스파</a>
        <a href="../stays.html?scope=kr">국내만 보기</a>
      </div>
    </div>
    <div class="gi-intro">
      <div><b>가격은 ‘실질 1인가’로</b><p>표시가에 현장 추가금(입장료·팁·가이드 경비)을 더한 금액으로 비교합니다. 싼 상품이 실제로 싼지 여기서 갈립니다.</p></div>
      <div><b>패스는 손익분기부터</b><p>주유패스·지하철패스는 “하루 몇 번 타면 본전”을 먼저 계산합니다. 일정이 3일이어도 매일 타지 않으면 손해입니다.</p></div>
      <div><b>기준 시점을 밝힙니다</b><p>모든 글에 확인 날짜와 환율을 적었습니다. 요금은 개정되므로 결제 직전에 공식 안내를 한 번 더 확인하세요.</p></div>
    </div>
{chr(10).join(sections)}
    <div class="gfind-empty" id="gempty" hidden>
      <b>조건에 맞는 글이 없습니다.</b>
      <p>검색어를 줄이거나 필터를 ‘전체’로 바꿔 보세요. 예: 오사카 · eSIM · 우기 · 리조트 · 패스</p>
      <button type="button" id="greset">필터 초기화</button>
    </div>
{ad_slot("guides-index-bottom", "이 글들의 계산, 내 날짜로 해보기", "지역·인원·스타일을 넣으면 항공+숙소+투어+eSIM을 한 번에 계산합니다.", "../index.html#planner", "예산 계산기")}
{cta_band('../', '읽고 끝내지 말고, 내 날짜로 계산하기', '지역·인원·스타일을 넣으면 항공+숙소+투어+eSIM을 한 번에 계산해 A/B/C안으로 보여줍니다.')}
  </div>
</div>
{guide_filter_script()}"""

    return page(
        out_root,
        "guides/index.html",
        title=f"여행 가이드 {len(GUIDES_LIST)}편 | 교통패스 본전·공항 이동·패키지 실지출 — 트립픽",
        desc=(
            f"공항에서 시내까지, 교통패스 본전 계산, 3박4일 실경비, 패키지 실지출, 우기·시즌, eSIM, "
            f"기내 반입 규정, 기념품 리스트까지 — 예약 전에 숫자로 확인하는 여행 가이드 {len(GUIDES_LIST)}편. 2026년 11월 기준."
        ),
        body=body,
        base=base,
        active="guides",
        keywords="여행 가이드, 나리타 공항 시내 이동, 교토 버스투어 비교, 오사카 주유패스 본전, 도쿄 지하철 패스, 오사카 교토 3박4일 경비, 방콕 패키지 실지출, 이탈리아 패키지 비교, 괌 리조트 비교, 다낭 우기, 제주 3박4일, 울릉도 배편, 강원 스키장 비교, 일본 eSIM, 베트남 eSIM, 일본 기념품 리스트, 다낭 기념품, 대만 펑리수, 태국 기념품",
        jsonld=f'<script type="application/ld+json">{listing}</script>'
        + graph_ld(org_ld(base), website_ld(base),
                   breadcrumb_ld(base, [("트립픽", "/"), ("여행 가이드", None)])),
    )


# ----------------------------------------------------------------------
# 필수 페이지 (소개·개인정보·약관·문의)
# ----------------------------------------------------------------------
def content_page(out_root: Path, spec: dict, base: str) -> Path:
    slug = spec["slug"]
    body_html = read(PAGES / f"{slug}.html")
    if slug == "about":
        # v36: 소개 페이지의 숫자는 데이터에서 계산한다(상품·도시·제휴 링크·가이드·노쇼핑·국가 수).
        # content/pages/about.html 의 {{TOKEN}} 을 매번 새 값으로 채운다.
        _tours = load_json("tours.json")
        _trips = _tours["tours"]
        _aff = sum(len(TRIPCOM.get(k) or []) for k in ("tickets", "transfers", "cars", "esims", "rails"))
        _nums = {
            "{{TOURS}}": len(_trips),
            "{{CITIES}}": len(_tours.get("cities") or []),
            "{{AFF_ITEMS}}": _aff,
            "{{GUIDES}}": len(GUIDES_LIST),
            "{{NOSHOP}}": sum(1 for t in _trips if "노쇼핑" in (t.get("tags") or [])),
            "{{COUNTRIES}}": len({t.get("country") for t in _trips}),
        }
        for _k, _v in _nums.items():
            body_html = body_html.replace(_k, f"{_v:,}")
    body = f"""<div class="pg-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><b>{esc(spec['navTitle'])}</b></nav>
    <span class="pg-kicker">{esc(spec['kicker'])}</span>
    <div class="pg-head">
      <h1>{spec['h1']}</h1>
      <p class="dek">{esc(spec['dek'])}</p>
      <div class="pg-meta"><span>시행일 {spec['effective']}</span><i></i><span>최종 개정 {spec['updated'].replace('-', '.')}</span><i></i><span>문의 <b>{CONTACT_MAIL}</b></span></div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="pg-grid">
      <article class="doc">
{body_html}
      </article>
      <aside class="pg-side">
        <div class="side-card">
          <h3>사이트 안내</h3>
          <ul class="side-list">
            <li><a href="about.html">서비스 소개<span>선별·비교 기준과 수익 구조</span></a></li>
            <li><a href="contact.html">문의하기<span>오류 신고·제휴 문의</span></a></li>
            <li><a href="privacy.html">개인정보처리방침<span>수집 항목·쿠키·광고</span></a></li>
            <li><a href="terms.html">이용약관<span>정보 이용 조건과 한계</span></a></li>
          </ul>
        </div>
{side_common('')}
      </aside>
    </div>
  </div>
</div>"""
    return page(
        out_root,
        f"{slug}.html",
        title=spec["seoTitle"],
        desc=spec["desc"],
        body=body,
        base=base,
        keywords=spec.get("keywords", ""),
        jsonld=graph_ld(
            {
                "@type": "WebPage",
                "@id": f"{base.rstrip('/')}/{slug}",
                "name": spec["navTitle"],
                "url": f"{base.rstrip('/')}/{slug}",
                "inLanguage": "ko",
                "dateModified": spec["updated"],
                "isPartOf": {"@id": f"{base.rstrip('/')}/#website"},
                "publisher": {"@id": f"{base.rstrip('/')}/#organization"},
            },
            org_ld(base),
            website_ld(base),
            breadcrumb_ld(base, [("트립픽", "/"), (spec["navTitle"], None)]),
        ),
    )


# ----------------------------------------------------------------------
# 도시별 허브 페이지 (/osaka · /tokyo …) + /cities/
# ----------------------------------------------------------------------
_hub_cache = None
_SEASON_CACHE = None
# v25: 13곳 — 해외 7곳 뒤에 국내 6곳(제주 + 신규 서울·부산·강릉·여수·경주)
HUB_ORDER = [
    "osaka", "tokyo", "fukuoka", "okinawa", "danang", "nhatrang", "bangkok", "taipei",
    "singapore", "hongkong", "macau", "guam", "saipan",
    "paris", "london", "rome", "barcelona",
    "jeju", "seoul", "busan", "gangneung", "yeosu", "gyeongju",
]


def hub_specs() -> dict:
    global _hub_cache
    if _hub_cache is None:
        _hub_cache = load_json("city_hubs.json")
    return _hub_cache


def hub_list() -> list:
    order = {s: i for i, s in enumerate(HUB_ORDER)}
    return sorted(hub_specs()["cities"], key=lambda h: order.get(h["slug"], 99))


def hub_tours(hub: dict) -> list:
    ids = set(hub.get("cityIds") or [hub["slug"]])
    return [t for t in TOURS if t["city"] in ids]


def hub_city_rest(hub: dict):
    rid = hub.get("restaurants")
    if not rid:
        return None
    return next((c for c in RESTAURANTS["cities"] if c["id"] == rid), None)


def hub_country(hub: dict):
    cid = hub.get("giftCountry")
    if not cid:
        return None
    return next((c for c in GIFTS["countries"] if c["id"] == cid), None)


def hub_guides(hub: dict) -> list:
    by = {g["slug"]: g for g in GUIDES_LIST}
    return [by[s] for s in hub.get("guides", []) if s in by]


def hub_cards(tours: list) -> str:
    """홈과 같은 .pcard 카드. 비교 바구니 버튼(홈 전용 JS)만 뺀다."""
    out = []
    for i, t in enumerate(tours):
        card = B.card_html(t, i)
        card = re.sub(r'\s*<button class="cmp-btn".*?</button>', "", card, flags=re.S)
        out.append(card)
    return "\n        ".join(out)


def hub_compare(tours_count: int, rows: str, name: str) -> str:
    return f"""<details class="cmp">
        <summary>
          <span class="lhs"><svg class="ic" aria-hidden="true"><use href="#i-ticket"/></svg><span>{esc(name)} {tours_count}개 상품, 가격·조건 한눈에 비교표</span></span>
          <span class="hint">표 펼치기</span>
        </summary>
        <div class="table-wrap">
          <table class="compare">
            <caption class="sr-only">{esc(name)} 네이버 여행 상품 {tours_count}개 비교표</caption>
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
        <p class="scroll-hint">표는 좌우로 넘길 수 있습니다. ‘상세페이지 확인 필요’는 판매 페이지에 값이 표기되지 않은 항목입니다.</p>
      </details>"""


def hub_food_card(it: dict, tour, guide, has_hotel: bool) -> str:
    links = [
        f'<a href="https://www.google.com/maps/place/?q=place_id:{esc(it["place"])}" target="_blank" rel="noopener nofollow">'
        f'<svg class="ic" aria-hidden="true"><use href="#i-pin"/></svg>지도</a>'
    ]
    if tour:
        links.append(f'<a href="{esc(tour["url"])}" target="_blank" rel="noopener sponsored">이 도시 투어</a>')
    if guide:
        links.append(f'<a href="guides/{esc(guide["slug"])}.html">맛집 동선</a>')
    if has_hotel:
        links.append('<a href="#stay">숙소</a>')
    return f"""<article class="food" id="food-{esc(it['id'])}">
            <div class="food-top"><span class="food-area">{esc(it['area'])}</span><span class="food-slot">{esc(it['slot'])}</span></div>
            <h3 class="food-name">{esc(it['name'])}<span>{esc(it['nameKo'])} · {esc(it['category'])}</span></h3>
            <div class="food-dish"><b>{esc(it['dish'])}</b><span>{esc(it['price'])}</span></div>
            <ul class="food-facts">
              <li><i>영업</i>{esc(it['hours'])}</li>
              <li><i>휴무</i>{esc(it['closed'])}</li>
              <li><i>대기</i>{esc(it['wait'])}</li>
            </ul>
            <p class="food-tip">{esc(it['tip'])}</p>
            <span class="food-cau">{esc(it['caution'])}</span>
            <div class="food-foot">{''.join(links)}<span class="food-rate">구글 {esc(it['rating'])} · {esc(it['reviews'])}</span></div>
          </article>"""


def hub_food_route(city: dict, tour, guide, hotel, hub_name: str) -> str:
    def short(s: str) -> str:
        segs = s.split(" · ")
        return " · ".join(segs[:2]) if len(segs) > 1 and segs[1].startswith("약") else segs[0]

    steps = []
    if tour:
        title = re.split(r"\s*[(（]", tour["title"])[0].strip()
        tour_k = "오전" if tour["id"].endswith("_g") else "패키지"
        steps.append(
            f'<li><span class="fr-k">{tour_k}</span><a href="{esc(tour["url"])}" target="_blank" rel="noopener sponsored">'
            f'{esc(title)}</a><span class="fr-m">{won(tour["sale"])}원~</span></li>'
        )
    for slot in ("점심", "저녁"):
        pick = next((i for i in city["items"] if i.get("slot") == slot), None)
        if not pick:
            continue
        steps.append(
            f'<li><span class="fr-k">{slot}</span><a class="js-food-jump" href="#food-{esc(pick["id"])}">'
            f'{esc(pick["nameKo"])}</a><span class="fr-m">{esc(short(pick["price"]))}</span></li>'
        )
        if slot == "점심":
            extra = (f'<li><span class="fr-k">오후</span><a href="#gifts">선물·기념품 {esc(hub_name)}</a>'
                     f'<span class="fr-m">{esc(guide["read"])}분 가이드</span></li>' if guide else "")
            steps.append(extra)
    if hotel:
        steps.append(
            f'<li><span class="fr-k">숙소</span><a href="#stay">{esc(hotel["city"])} 숙소 최저가</a>'
            f'<span class="fr-m">트립닷컴</span></li>'
        )
    return "".join(s for s in steps if s)


def hub_gift_cards(country: dict) -> str:
    cards = []
    for it in country["items"]:
        lvl = " warn" if it.get("level") == "warn" else ""
        cards.append(f"""<article class="gift">
            <div class="gift-name"><b>{esc(it['name'])}</b><span>{esc(it.get('local', ''))}</span></div>
            <div class="gift-price"><b>{esc(it['price'])}</b><span>{esc(it['krw'])}</span></div>
            <div class="gift-where"><svg class="ic" aria-hidden="true"><use href="#i-pin"/></svg>{esc(it['where'])}</div>
            <p class="gift-tip">{esc(it['tip'])}</p>
            <span class="gift-cau{lvl}">{esc(it['caution'])}</span>
          </article>""")
    return '<div class="gift-grid">' + "".join(cards) + "</div>"


def hub_gift_links(country: dict, hub: dict) -> str:
    rows = []
    ids = set(hub.get("cityIds") or [hub["slug"]])
    tours_by_id = {t["id"]: t for t in TOURS}
    links = []
    for ln in country.get("links", []):
        if ln.get("kind") == "hotel":
            continue  # 이 페이지 아래 숙소 섹션에서 바로 연결한다
        if ln.get("kind") == "tour" and tours_by_id.get(ln.get("id"), {}).get("city") not in ids:
            continue
        links.append(ln)
    for url, kind, title, meta in B._gift_links(
        links,
        {"tours": TOURS},
        {"products": ESSENTIALS},
        TRIPCOM,
        {"guides": GUIDES_LIST},
    ):
        ext = ' target="_blank" rel="noopener sponsored"' if url.startswith("http") else ""
        rows.append(
            f'<a class="gift-link" href="{esc(url)}"{ext}><i>{kind}</i><b>{esc(title)}</b><span>{esc(meta)}{" · 제휴" if ext else ""}</span></a>'
        )
    return '<div class="gift-links">' + "".join(rows) + "</div>" if rows else ""


def hub_ess_cards(pick: int = 4) -> str:
    rows = []
    for e in [x for x in ESSENTIALS if x["category"] == "여행용품"][:pick]:
        thumb = ""
        if e.get("image"):
            thumb = (f'<span class="ess-thumb"><img src="{esc(e["image"])}" alt="{esc(e["name"])}"'
                     f' width="400" height="400" loading="lazy" /></span>')
        rows.append(f"""<a class="ess" href="{esc(e.get('url') or e['naverMe'])}" target="_blank" rel="noopener sponsored">
              {thumb}
              <span class="ess-k">준비물 · {esc(e.get('categoryLabel') or e['category'])}</span>
              <b>{esc(e['name'])}</b>
              <span class="ess-store">{esc(e['store'])}</span>
              <span class="ess-foot"><span class="ess-price">{won(e['price'])}원<small>~</small></span>
                <span class="ess-go">{esc(B.ess_cta(e))} <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span></span>
            </a>""")
    return '<div class="ess-grid ess-grid-4">' + "".join(rows) + "</div>"


# v17: 도시 허브 안 eSIM 비교 블록(네이버 쇼핑 커넥트 실링크만)
ESIM_PICK = {
    "jp": {
        "title": "eSIM, 1일 300원권과 3일 무제한",
        "lead": "1일 300~590원권을 날짜별로 끊는 쪽과 3일 완전무제한 14,620원 두 갈래입니다. "
                "2인 여행이면 인원수만큼 사야 하고, 설치 QR은 출발 전에 받아 두세요.",
        "ids": ["jp-esim-usimsa-kddi-1d", "jp-esim-lingsim-1d", "jp-esim-usimsa-3d-tokyo", "jp-esim-trip-37658069"],
        "badges": {"jp-esim-trip-37658069": "1~30일 선택"},
    },
    "vn": {
        "title": "eSIM, 1일 200원부터",
        "lead": "베트남은 1일권이 200~800원이라 날짜별로 끊는 게 가장 쌉니다. 영상·지도 업무를 하거나 "
                "데이터를 아끼지 않으려면 3일 무제한(17,850원)을 섞는 편이 낫습니다.",
        "ids": ["vn-esim-usimsa-1d", "vn-esim-lingsim-1d", "vn-esim-usimsa-3d"],
    },
    "th": {
        "title": "eSIM, 1일 300원부터",
        "lead": "방콕 시내는 숙소·카페 와이파이가 많아 1일권을 날짜별로 끊어도 충분합니다. "
                "파타야·섬 일정처럼 이동이 많은 날이 있으면 3일 무제한을 섞으세요.",
        "ids": ["th-esim-usimsa-1d", "th-esim-usimsa-3d", "th-esim-trip-46275998"],
        "badges": {"th-esim-trip-46275998": "1~30일 선택"},
    },
    "tw": {
        "title": "eSIM, 1일 760원부터",
        "lead": "2박3일이면 3일 무제한 한 장이 계산이 쉽고, 4일 이상 머물면 1일권을 날짜별로 붙이는 쪽이 쌉니다. "
                "두 상품 모두 출발 전 설치형이라 공항에서 줄 서지 않습니다.",
        "ids": ["tw-esim-lingsim-1d", "tw-esim-usimsa-3d"],
    },
    # v55: 괌·사이판·싱가포르 — 트립닷컴 eSIM. 가격이 ‘1일 요금제부터’라 단위를 같이 적는다.
    "us": {
        "title": "eSIM, 1일 1,050원부터",
        "lead": "괌·사이판은 통신사 단기 로밍보다 eSIM이 쌉니다. 1일 요금제가 1,050원(정가 1,313원)부터이고 1~30일 중에 고르니, "
                "4박5일이면 5일권을 한 장 사는 쪽이 1일권 다섯 장보다 계산이 간단합니다. 2인이면 인원수만큼 설치합니다.",
        "ids": ["gu-esim-trip-101949204"],
        "badges": {"gu-esim-trip-101949204": "1~30일 선택"},
        "suffix": " /1일",
    },
    # v56: 홍콩·마카오·인도네시아(발리) — 트립닷컴 eSIM. 가격이 '1일 요금제부터'라 단위를 같이 적는다.
    "hk": {
        "title": "eSIM, 1일 112원부터",
        "lead": "홍콩 eSIM은 1일 500MB 상품이 112원부터이고 4.7점·리뷰 3,498건으로 후기가 가장 많습니다. "
                "3박4일이면 4일 총량형을 한 장 사고, 마카오를 같이 돌면 공용 상품(1일 106~109원)이 계산이 쉽습니다. "
                "홍콩 현지 유심은 실명등록이 필요하지만 QR 설치형 eSIM은 그 절차가 없습니다.",
        "ids": ["hk-esim-trip-93409303"],
        "badges": {"hk-esim-trip-93409303": "1~30일 선택"},
        "suffix": " /1일",
    },
    "mo": {
        "title": "eSIM, 1일 106원부터",
        "lead": "마카오 전용 상품은 1일 241원부터이고, 중국 대륙·홍콩·마카오 공용 상품이 1일 106~109원이라 2곳을 같이 돌면 공용 쪽이 쌉니다. "
                "1박만 묵고 홍콩으로 돌아오는 일정이면 하루치만 있어도 충분합니다.",
        "ids": ["mo-esim-trip-100451304"],
        "badges": {"mo-esim-trip-100451304": "1~30일 선택"},
        "suffix": " /1일",
    },
    "id": {
        "title": "eSIM, 1일 101원부터",
        "lead": "발리 eSIM은 1일 101원부터이고 4.6점·리뷰 6,471건입니다. 3박4일이면 4일 총량형 한 장으로 끝나고, "
                "우붓·스미냑 모두 시내 속도는 비슷합니다. 길리섬·누사페니다로 넘어가는 날은 해상에서 끊길 수 있습니다.",
        "ids": ["id-esim-trip-46278708"],
        "badges": {"id-esim-trip-46278708": "1~30일 선택"},
        "suffix": " /1일",
    },
    "sg": {
        "title": "eSIM, 1일 109원부터",
        "lead": "싱가포르 eSIM은 1일 500MB가 109원부터이고, 리뷰 5,512개·4.6점으로 후기가 가장 많은 쪽입니다. "
                "3박4일이면 4일 총량형을 한 장 사고, 영상통화를 많이 한다면 1일 2GB형을 섞으세요.",
        "ids": ["sg-esim-trip-46011732"],
        "badges": {"sg-esim-trip-46011732": "1~30일 선택"},
        "suffix": " /1일",
    },
}


def hub_esim_section(hub: dict) -> str:
    spec = ESIM_PICK.get(hub.get("country"))
    if not spec:
        return ""
    cards = []
    for eid in spec["ids"]:
        e = next((x for x in ESSENTIALS if x["id"] == eid), None)
        if not e:
            continue
        price = f'{won(e["price"])}원'
        if e.get("listPrice") and e["listPrice"] > e["price"]:
            price += f'<small>{won(e["listPrice"])}원</small>'
        price += esc(spec.get("suffix") or "")
        badge = (spec.get("badges") or {}).get(eid) or ("1일권" if "1d" in eid else "3일 무제한")
        cards.append(f"""<a class="esim-card" href="{esc(B.ess_url(e))}" target="_blank" rel="noopener sponsored">
        <span class="esim-top"><span class="esim-badge">{badge}</span><span class="esim-store">{esc(e['store'])}</span></span>
        <b class="esim-name">{esc(e['name'])}</b>
        <span class="esim-price">{price}</span>
        <span class="esim-note">{esc(e.get('usage') or '')}</span>
        <span class="esim-go">{esc(B.ess_cta(e))} <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span>
      </a>""")
    if not cards:
        return ""
    return f"""<section class="hub-sec" id="esim">
  <div class="hub-sec-head">
    <div><span class="hub-k">DATA &amp; SIM</span>
      <h2>{esc(hub['name'])} {spec['title']}</h2>
      <p>{esc(spec['lead'])}</p></div>
    <div class="hub-fx">2026.11.26 제휴 상품 확인</div>
  </div>
  <div class="esim-cmp">{''.join(cards)}</div>
  <p class="hub-aff">eSIM 카드는 <b>네이버 쇼핑 커넥트</b> 제휴 링크입니다. 이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 구매 발생 시 수수료를 제공받습니다. 결제 금액은 같습니다.</p>
</section>"""


def hub_hotel_cards(hotels: list) -> str:
    return "".join(
        f'<a class="tc-card" href="{esc(h["url"])}" target="_blank" rel="noopener sponsored">'
        f'<span class="tc-city">{esc(h["city"])}{B.flag_svg(h["flag"], 14, 9.8)}</span>'
        f'<span class="tc-sub">{esc(h["sub"])}</span>'
        f'<span class="tc-note">{esc(h["note"])}</span>'
        f'<span class="tc-go">숙소 최저가 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span>'
        f'</a>'
        for h in hotels
    )


def hub_guide_cards(guides: list) -> str:
    cards = []
    for g in guides:
        thumb = (
            f'<div class="thumb"><picture>{pic_sources(g["image"], "", "(max-width:620px) 92vw, 346px")}'
            f'<img src="{esc(g["image"])}" alt="{esc(g["imageAlt"])}" loading="lazy" decoding="async" width="640" height="360" /></picture></div>'
            if g.get("image")
            else '<div class="thumb noimg">TRIPPICK GUIDE</div>'
        )
        cards.append(
            f"""        <a class="gcard" href="guides/{g['slug']}.html">
          {thumb}
          <div class="gc-body">
            <span class="tag">{esc(g['category'])}</span>
            <h3>{esc(g['navTitle'])}</h3>
            <p>{esc(g['dek'])}</p>
            <div class="gc-foot"><b>{g['read']}분</b> · {g['updated'].replace('-', '.')} 업데이트</div>
          </div>
        </a>"""
        )
    return '<div class="gi-grid">' + "".join(cards) + "</div>"


def hub_faq_pairs(hub: dict, tours: list) -> list:
    """v55: 허브 JSON-LD FAQ — 저장소 데이터로 답할 수 있는 질문만 만든다(지어낸 수치 금지)."""
    global _SEASON_CACHE
    name = hub["name"]
    out = []
    hs = [h for h in STAYS.get("hotels", []) if h["region"] == hub["slug"]]
    reg = next((r for r in STAYS.get("regions", []) if r["id"] == hub["slug"]), None)
    if hs:
        lo, hi = min(h["price"] for h in hs), max(h["price"] for h in hs)
        top = f" 최고 평점은 {reg['top']}입니다." if reg and reg.get("top") else ""
        out.append((
            f"{name} 숙소 1박은 얼마인가요?",
            f"{name} 숙소 {len(hs)}곳을 평점·리뷰·위치로 골랐습니다. 1박·2인·세금 포함 최저가는 {lo:,}원~{hi:,}원입니다.{top}",
        ))
    if _SEASON_CACHE is None:
        _SEASON_CACHE = {c["id"]: c for c in load_json("season.json")["cities"]}
    season = _SEASON_CACHE.get(hub["slug"])
    if season and season.get("access"):
        a = season["access"]
        out.append((
            f"{name}까지 비행시간은 얼마나 걸리나요?",
            f"{a.get('route', '인천 출발')} · {a.get('mode', '')}. {season.get('fareNote', '')}".replace(" · .", "."),
        ))
    spec = ESIM_PICK.get(hub.get("country"))
    if spec:
        e = next((x for x in ESSENTIALS if x["id"] == spec["ids"][0]), None)
        if e:
            _lp = f"(정가 {won(e['listPrice'])}원)" if e.get("listPrice") and e["listPrice"] > e["price"] else ""
            out.append((
                f"{name} eSIM은 얼마인가요?",
                f"{e['name']} — 1일 {won(e['price'])}원{_lp}부터이고, 기간을 1~30일에서 고릅니다. {e.get('usage', '')}",
            ))
    if tours:
        out.append((
            f"{name} 투어·패키지는 몇 개 있나요?",
            f"지금 판매 중인 상품 {len(tours)}개를 1인 가격과 미팅·포함 사항까지 같은 기준으로 비교했습니다. 1인 최저 {won(min(t['sale'] for t in tours))}원입니다.",
        ))
    else:
        out.append((
            f"{name}는 어떤 방식으로 여행하나요?",
            hub.get("tourNote") or f"{name}은 단독 투어·패키지 상품 없이 숙소와 동선으로 짜는 여행입니다.",
        ))
    return out


def hub_jsonld(hub: dict, tours: list, guides: list, base: str) -> str:
    b = base.rstrip("/")
    url = f"{b}/{hub['slug']}"
    dest = {
        "@type": "TouristDestination",
        "@id": url + "#destination",
        "name": hub["name"],
        "description": hub["metaDesc"],
        "url": url,
        "image": f"{b}/{hub['image']}",
        "touristType": "여행",
    }
    page_ld = {
        "@type": "CollectionPage",
        "@id": url + "#page",
        "url": url,
        "name": hub["seoTitle"],
        "description": hub["metaDesc"],
        "inLanguage": "ko",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": b + "/"},
        "about": {"@id": url + "#destination"},
        "mainEntity": {"@id": url + "#tours"},
    }
    tour_ld = {
        "@type": "ItemList",
        "@id": url + "#tours",
        "name": f"{hub['name']} 투어·패키지 {len(tours)}개",
        "numberOfItems": len(tours),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "item": {
                    "@type": "TouristTrip",
                    "name": t["title"],
                    "description": f'{t["theme"]} · {t["type"]} · {t["duration"]}',
                    "url": t["url"],
                    "touristType": t["type"],
                    "provider": {"@type": "Organization", "name": t["seller"]},
                },
            }
            for i, t in enumerate(tours, start=1)
        ],
    }
    guide_ld = {
        "@type": "ItemList",
        "@id": url + "#guides",
        "name": f"{hub['name']} 관련 가이드 {len(guides)}편",
        "numberOfItems": len(guides),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "item": {"@type": "Article", "headline": g["navTitle"], "url": f"{b}/guides/{g['slug']}"},
            }
            for i, g in enumerate(guides, start=1)
        ],
    }
    crumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "트립픽", "item": b + "/"},
            {"@type": "ListItem", "position": 2, "name": "도시별 여행", "item": f"{b}/cities/"},
            {"@type": "ListItem", "position": 3, "name": hub["name"]},
        ],
    }
    graph = {"@context": "https://schema.org", "@graph": [page_ld, dest, tour_ld, guide_ld, crumb, org_ld(base), website_ld(base)]}
    faq = hub_faq_pairs(hub, tours)
    if faq:
        graph["@graph"].insert(4, {
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq
            ],
        })
    raw = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{raw}</script>'


def hub_packages(slug: str, name: str) -> str:
    """v20: 도시 허브에 그 도시의 네이버 여행 커넥트 고단가 패키지를 붙인다."""
    items = [p for p in (PACKAGES.get("packages") or []) if p.get("city") == slug]
    if not items:
        return ""
    cards = []
    for p in items:
        off = round((p["price"] - p["sale"]) / p["price"] * 100) if p["price"] > p["sale"] else 0
        price = f'<b>{won(p["sale"])}원</b>'
        if off:
            price += f'<small>{won(p["price"])}원</small><em>{off}% 할인</em>'
        cards.append(
            f'<article class="pkg-card">'
            f'<span class="pkg-top"><span class="pkg-tag">{esc(p.get("type") or "해외패키지")}</span>'
            f'<span class="pkg-dur">{esc(p.get("duration", ""))}</span></span>'
            f'<b class="pkg-t">{esc(p["title"])}</b>'
            f'<p class="pkg-p">{esc(p.get("pitch", ""))}</p>'
            f'<span class="pkg-price">{price}</span>'
            f'<a class="pkg-btn" href="{esc(p["url"])}" target="_blank" rel="noopener sponsored">'
            f'네이버에서 상품 보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
            f'<p class="pkg-note">{esc(p.get("displayNote") or p.get("note", ""))}</p>'
            f'</article>'
        )
    return (f'<div class="hub-pkg"><div class="ess-ghead"><h3>💎 {esc(name)} 고단가 패키지</h3>'
            f'<span class="n">{len(items)}</span><span class="line" aria-hidden="true"></span>'
            f'<span class="ess-gnote">항공·숙소·일정 포함 · 1인 기준</span></div>'
            f'<div class="pkg-grid">{"".join(cards)}</div>'
            f'<p class="ess-cp-note">{esc(PACKAGES.get("disclosure", ""))}</p></div>')


def hub_stay_cards(slug: str) -> str:
    """v25: 도시 허브 안에 바로 놓는 찐숙소 카드(stays.json → .scard 그대로)."""
    region = next((r for r in STAYS.get("regions", []) if r["id"] == slug), None)
    if not region:
        return ""
    hs = [h for h in STAYS.get("hotels", []) if h["region"] == slug]
    hs.sort(key=lambda h: (-h["score"], -h["reviews"]))
    return "\n      ".join(stays_card(h, region) for h in hs)


def hub_tips(hub: dict) -> str:
    """v55: 도시 허브 '현지 기본 정보' — 공항·교통·환급처럼 그 도시에서 바로 쓰는 숫자만 모은다."""
    tips = hub.get("tips") or []
    if not tips:
        return ""
    rows = "".join(
        f'<div class="hub-tip"><b>{esc(t["k"])}</b><span>{esc(t["v"])}</span></div>' for t in tips
    )
    return (f'<div class="hub-tips" aria-label="{esc(hub["name"])} 현지 기본 정보">'
            f'<span class="hub-tips-h">현지 기본 정보 · 2026.11 확인</span>{rows}</div>')


def hub_faq_section(hub: dict, tours: list) -> str:
    """v55: 허브 화면 FAQ — JSON-LD(FAQPage)와 같은 문답을 본문에도 보이게 둔다."""
    pairs = hub_faq_pairs(hub, tours)
    if not pairs:
        return ""
    items = "".join(
        f'<details class="fq"><summary>{esc(q)}</summary><div class="fq-a"><p>{esc(a)}</p></div></details>'
        for q, a in pairs
    )
    return f'<section class="tf-faq" id="faq">\n  <h2>{esc(hub["name"])} 여행 자주 묻는 질문</h2>\n  {items}\n</section>'


def hub_page(out_root: Path, hub: dict, base: str) -> Path:
    slug = hub["slug"]
    tours = hub_tours(hub)
    rest = hub_city_rest(hub)
    country = hub_country(hub)
    guides = hub_guides(hub)
    hotels = [h for h in TRIPCOM["hotels"] if h.get("cityId") in (hub.get("hotels") or [])]
    flight = next((f for f in TRIPCOM["flights"] if hub.get("flight") and hub["flight"] in f["route"]), None)
    hub_acts = [
        a for a in (TRIPCOM.get("tickets") or []) + (TRIPCOM.get("transfers") or []) + (TRIPCOM.get("cars") or [])
        + (TRIPCOM.get("esims") or []) + (TRIPCOM.get("rails") or [])
        if a.get("cityId") == slug
    ]
    hub_tickets = [a for a in hub_acts if a["category"] == "ticket"]
    hub_pickups = [a for a in hub_acts if a["category"] in ("transfer", "car")]
    hub_net = [a for a in hub_acts if a["category"] in ("esim", "rail")]
    # v19: 이 도시의 클룩 링크(오사카·도쿄·다낭만 발급됨)
    kl = next((k for k in (KLOOK.get("links") or []) if k.get("cityId") == slug), None)
    lowest = min((t["sale"] for t in tours), default=0)
    tour_first = tours[0] if tours else None
    hotel_first = hotels[0] if hotels else None
    food_guide = next((g for g in guides if g["slug"].endswith("food-route")), None)

    # v25: 찐숙소(stays.json) — 투어가 없는 도시는 이 카드가 본문 상단에서 먼저 안내한다
    _stays = {r['id']: r for r in STAYS.get('regions', [])}
    _pick = _stays.get(slug)
    stay_pick_link = (
        f'<a class="hub-stay-pick" href="stays.html#{_pick["id"]}">'
        f'<b>{esc(hub["name"])} 찐숙소 {_pick["count"]}곳</b>'
        f'<span>평점·리뷰 수·1박 가격으로 고른 숙소 — 최고 평점 {esc(_pick["top"])}</span>'
        f'<i>보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></i></a>'
        if _pick else ''
    )
    _region = _pick

    # 위쪽 빠른 이동
    jumps = [("#tours", "투어·패키지", len(tours))]
    if rest:
        jumps.append(("#food", "현지 맛집", len(rest["items"])))
    if country:
        jumps.append(("#gifts", "선물·기념품", len(country["items"])))
    jumps.append(("#stay", "숙소·항공·입장권", len(hotels) + (1 if flight else 0) + len(hub_acts) + (1 if kl else 0)))
    esim_spec = ESIM_PICK.get(hub.get("country"))
    if esim_spec:
        jumps.append(("#esim", "eSIM", len(esim_spec["ids"])))
    jumps.append(("#guides", "관련 가이드", len(guides)))
    jump_html = "".join(
        f'<a href="{h}">{esc(n)} <b>{c}</b></a>' for h, n, c in jumps if c
    )

    # v18: 도시 페이지에서 바로 쓰는 도구 — 패스 본전 계산기 + 월별 시즌 캘린더
    pass_href, pass_title, pass_sub = HUB_PASS_TOOL.get(
        slug, ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이·싱가포르")
    )
    _season = SEASON_IDS
    cal_href = f"calendar.html#{slug}" if slug in _season else "calendar.html"
    cal_note = "성수기·항공권 참고가" if slug in _season else "19개 도시 12개월 캘린더"
    # v45: 환율·패스·SOS 를 이 도시 프리셋으로 바로 연다 (/exchange?cur=JPY · /passes?city=tokyo · /sos?country=JP)
    _links = tool_links(slug, hub.get("country") or "kr")
    pass_href = _links["passes"]
    fx_basis_text = (fx_basis(_links["cur"]) if _links["cur"] else "") or "12개 통화 · 면세 환급 계산"
    _sos_note = (f"{hub['name']} 경찰·구급·공관" if (hub.get("country") or "kr") in SOS_OF_COUNTRY
                 else "경찰·구급 10개국 · 이 도시 공관 번호는 직접 확인")
    hub_tools_html = f"""<div class="hub-tools" aria-label="{esc(hub['name'])} 도구">
  <a class="hub-tool" href="{_links['exchange']}"><span class="hub-tool-k">EXCHANGE</span><b>환율 계산 · 면세 환급</b><span class="hub-tool-n">{esc(fx_basis_text)}</span></a>
  <a class="hub-tool" href="{pass_href}"><span class="hub-tool-k">PASS</span><b>{esc(pass_title)}</b><span class="hub-tool-n">{esc(pass_sub)}</span></a>
  <a class="hub-tool" href="{_links['sos']}"><span class="hub-tool-k">SOS</span><b>현지 긴급번호 · 현지어 카드</b><span class="hub-tool-n">{esc(_sos_note)}</span></a>
  <a class="hub-tool" href="{cal_href}"><span class="hub-tool-k">SEASON</span><b>{esc(hub['name'])} 12개월 날씨·가격</b><span class="hub-tool-n">{esc(cal_note)}</span></a>
</div>"""

    _upd = (hub.get("updated") or hub_specs().get("updated") or "2026-11-20").replace("-", ".")
    meta = [f'<span><b>트립픽 편집</b></span>', '<i></i>', f'<span>업데이트 {_upd}</span>', '<i></i>']
    if tours:
        meta.append(f'<span>투어·패키지 {len(tours)}개</span><i></i>')
        meta.append(f'<span>1인 {won(lowest)}원~</span>')
    if rest:
        meta.append(f'<i></i><span>맛집 {len(rest["items"])}곳</span>')
    if hub_acts:
        meta.append(f'<i></i><span>입장권·픽업 {len(hub_acts)}</span>')
    if _region:
        meta.append(f'<i></i><span>찐숙소 {_region["count"]}곳</span>')
    meta.append(f'<i></i><span>가이드 {len(guides)}편</span>')

    # 투어 섹션
    tour_rows = "\n            ".join(B.table_row(t) for t in tours)
    if tours:
        tours_html = f"""<section class="hub-sec" id="tours">
  <div class="hub-sec-head">
    <div><span class="hub-k">TOURS &amp; PACKAGES</span>
      <h2>{esc(hub['name'])} 투어·패키지 <em>{len(tours)}개</em></h2>
      <p>네이버 여행에서 지금 판매 중인 상품입니다. 표시 가격은 1인 기준 최저가이고, 미팅 장소·입장료 포함 여부·현장 추가금·취소 마감일을 카드에 그대로 적었습니다.</p></div>
  </div>
  <div class="pgrid hub-grid">
    {hub_cards(tours)}
  </div>
  {hub_compare(len(tours), tour_rows, hub['name']) if tours else ''}
  {hub_packages(slug, hub['name'])}
  <p class="hub-aff">투어·패키지 링크는 <b>네이버 여행 커넥트</b> 제휴 링크입니다. 예약이 이루어지면 판매자로부터 수수료를 받지만, 결제 금액은 같습니다.</p>
</section>"""
    else:
        tours_html = f"""<section class="hub-sec" id="tours">
  <div class="hub-sec-head">
    <div><span class="hub-k">TOURS &amp; PACKAGES</span>
      <h2>{esc(hub['name'])} 여행은 어떻게 준비할까</h2>
      <p>이 도시는 단독 투어 없이 숙소·맛집·동선으로 완성되는 일정이라, 아래 네 가지로 바로 이어집니다.</p></div>
  </div>
  <div class="hub-nopkg">
    <p>{esc(hub.get('tourNote') or '지금 판매 중인 단독 투어·패키지 상품은 없습니다.')}</p>
    <div class="hub-nopkg-links">
      {stay_pick_link}
      <a href="#stay"><b>{esc(hub['name'])} 숙소·항공권·입장권</b><span>이 페이지 아래 숙소 섹션으로 바로</span><i>보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></i></a>
      <a href="#guides"><b>관련 가이드 {len(guides)}편</b><span>식비·입장료·이동 시간을 숫자로 계산한 글</span><i>보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></i></a>
      <a href="index.html#regions"><b>다른 지역 상품 보기</b><span>같은 기준으로 비교한 투어·패키지 전체</span><i>보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></i></a>
    </div>
  </div>
</section>"""

    # 맛집 섹션
    if rest:
        cards = "\n          ".join(
            hub_food_card(it, tour_first, food_guide, bool(hotel_first)) for it in rest["items"]
        )
        route = hub_food_route(rest, tour_first, food_guide, hotel_first, hub["name"])
        food_html = f"""<section class="hub-sec" id="food">
  <div class="hub-sec-head">
    <div><span class="hub-k">LOCAL FOOD</span>
      <h2>{esc(rest['name'])} 현지 맛집 <em>{len(rest['items'])}곳</em></h2>
      <p>{rest['intro']}</p></div>
    <div class="hub-fx">2026.11.20 확인 · {esc(RESTAURANTS['fx'])}</div>
  </div>
  <ol class="food-route" aria-label="{esc(rest['name'])} 하루 동선">{route}</ol>
  <div class="food-grid hub-food-grid">
          {cards}
  </div>
  <p class="hub-note">{esc(RESTAURANTS['note'])}</p>
</section>"""
    else:
        guide_links = "".join(
            f'<li><a href="guides/{esc(g["slug"])}.html">{esc(g["navTitle"])}<span>{g["read"]}분</span></a></li>'
            for g in guides[:3]
        )
        food_html = f"""<section class="hub-sec" id="food">
  <div class="hub-sec-head">
    <div><span class="hub-k">LOCAL FOOD</span>
      <h2>{esc(hub['name'])} 현지 맛집</h2></div>
  </div>
  <div class="hub-pending">
    <b>맛집 목록은 아직 검증을 마치지 않았습니다.</b>
    <p>{esc(hub.get('foodFallback') or '영업 중인지(구글 지도 OPERATIONAL), 공식 메뉴판 가격이 맞는지 확인한 가게만 싣습니다. 이 도시는 확인 절차가 끝나는 대로 추가하고, 그전까지는 아래 가이드에서 식비와 동선을 볼 수 있습니다.')}</p>
    <ul class="side-list">{guide_links}</ul>
  </div>
</section>"""

    # 선물 섹션
    if country:
        gift_html = f"""<section class="hub-sec" id="gifts">
  <div class="hub-sec-head">
    <div><span class="hub-k">SOUVENIR &amp; GIFT</span>
      <h2>{esc(country['name'])} 선물·기념품 <em>{len(country['items'])}종</em></h2>
      <p>{country['intro']}</p></div>
    <div class="hub-fx">2026.11 현지 정가 · {esc(GIFTS['fx'])}</div>
  </div>
  <div class="gift-card hub-gift">
    {hub_gift_cards(country)}
    <div class="gift-duty"><b>{esc(country['name'])} 반입·면세 한 줄</b><span>{esc(country['duty'])}</span></div>
    {hub_gift_links(country, hub)}
  </div>
</section>"""
    else:
        gift_html = f"""<section class="hub-sec" id="gifts">
  <div class="hub-sec-head">
    <div><span class="hub-k">BEFORE YOU GO</span>
      <h2>{esc(hub['name'])} 출발 전 준비물</h2>
      <p>{esc(hub.get('giftFallback') or '국내 여행이라 면세 한도·반입 규정이 따로 없습니다. 대신 현지에서 사기 번거로운 준비물을 집에서 미리 주문하는 링크만 모았습니다.')}</p></div>
  </div>
  {hub_ess_cards(4)}
  <p class="hub-aff">준비물 링크는 <b>쿠팡 파트너스</b> 제휴 링크입니다. 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>
</section>"""

    # 숙소·항공
    flight_html = ""
    if flight:
        flight_html = f"""<div class="tc-flights hub-flight">
      <a class="tc-flight" href="{esc(flight['url'])}" target="_blank" rel="noopener sponsored">
        <span class="tc-fr">{esc(flight['route'])}</span>
        <span class="tc-fs">{esc(flight['sub'])}</span>
        <span class="tc-go">항공권 검색 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span>
      </a>
    </div>"""
    act_html = ""
    if hub_acts:
        ticket_block = ""
        if hub_tickets:
            ticket_block = f"""<div class="tc-group tc-group--act">
    <div class="ess-ghead"><h3>🎟️ {esc(hub['name'])} 입장권·액티비티</h3><span class="n">{len(hub_tickets)}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">한국어 페이지 · 방문일을 넣어야 가격이 확정됩니다</span></div>
    <div class="tc-acts tc-acts--hub">{''.join(B.tc_act_card(a) for a in hub_tickets)}</div>
  </div>"""
        pickup_block = ""
        if hub_pickups:
            pickup_label = f"{esc(hub['name'])} 공항픽업·렌터카" if any(a["category"] == "car" for a in hub_pickups) else f"{esc(hub['name'])} 공항픽업·샌딩"
            pickup_block = f"""<div class="tc-group tc-group--act">
    <div class="ess-ghead"><h3>🚗 {pickup_label}</h3><span class="n">{len(hub_pickups)}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">도착 공항·목적지를 넣어야 요금이 확정됩니다</span></div>
    <div class="tc-acts tc-acts--hub">{''.join(B.tc_act_card(a) for a in hub_pickups)}</div>
  </div>"""
        act_html = ticket_block + pickup_block
        if hub_net:
            net_label = f"{esc(hub['name'])} eSIM·공항철도"
            act_html += f"""<div class="tc-group tc-group--act">
    <div class="ess-ghead"><h3>📶 {net_label}</h3><span class="n">{len(hub_net)}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">도착 전에 설치·발권하는 것들</span></div>
    <div class="tc-acts tc-acts--hub">{''.join(B.tc_act_card(a, '유심·eSIM 보기' if a['category'] == 'esim' else '기차표 보기') for a in hub_net)}</div>
  </div>"""
    klook_html = ""
    if kl:
        klook_html = f"""<div class="tc-group tc-group--act" id="klook">
    <div class="ess-ghead"><h3>🌏 클룩에서 {esc(hub['name'])} 투어·입장권</h3><span class="n">1</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">{esc(kl.get('highlight', ''))}</span></div>
    <div class="tc-acts tc-acts--hub">{B.tc_act_card(kl, '클룩에서 보기')}</div>
    <p class="ess-cp-note">{esc(KLOOK['disclosure'])}</p>
  </div>"""
    # v25: 숙소 섹션 — 트립닷컴 도시 목록 + (신규 국내 허브는) 찐숙소 카드까지 이 페이지에서 바로
    tc_list = hub.get("tripcomCity") or slug
    _tc_row = next((h for h in TRIPCOM["hotels"] if h.get("cityId") == tc_list), None)
    _list_url = (_pick or {}).get("listUrl") or (_tc_row or {}).get("url")
    tc_list_html = ""
    if _list_url:
        tc_list_html = (
            f'<div class="tc-flights hub-flight">'
            f'<a class="tc-flight" href="{esc(_list_url)}" target="_blank" rel="noopener sponsored">'
            f'<span class="tc-fr">트립닷컴 {esc((_pick or {}).get("name") or hub["name"])} 숙소 전체</span>'
            f'<span class="tc-fs">{esc((_tc_row or {}).get("sub") or "체크인 날짜를 넣으면 그날 최저가로 정렬됩니다")}</span>'
            f'<span class="tc-go">숙소 목록 열기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span></a></div>'
        )
    hotel_group = ""
    if hotels:
        hotel_group += f"""<div class="tc-group">
    <div class="ess-ghead"><h3>🏨 {esc(hub['name'])} 숙소</h3><span class="n">{len(hotels)}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">체크인 날짜 기준 최저가</span></div>
    <div class="tc-grid hub-tc">{hub_hotel_cards(hotels)}</div>
    {stay_pick_link}
  </div>"""
    if _pick and hub.get("stayCards"):
        # v25: 신규 도시 허브는 찐숙소 카드(평점·리뷰·1박 가격·예약 딥링크)를 이 페이지에서 바로 보여준다.
        hotel_group += f"""<div class="tc-group">
    <div class="ess-ghead"><h3>🛏️ {esc(hub['name'])} 찐숙소 <em>{_pick['count']}곳</em></h3><span class="n">{_pick['count']}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">2026-11-20 트립닷컴 조회값 · 1박·2인·세금 포함</span></div>
    <div class="sgrid hub-sgrid">{hub_stay_cards(slug)}</div>
    {stay_pick_link}
  </div>"""
    elif _pick and not hotels:
        hotel_group += f"""<div class="tc-group">
    <div class="ess-ghead"><h3>🛏️ {esc(hub['name'])} 찐숙소 {_pick['count']}곳</h3><span class="n">{_pick['count']}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">2026-11-20 트립닷컴 조회값</span></div>
    {stay_pick_link}
  </div>"""
    extra_stay = ""
    _extra = next((h for h in TRIPCOM["hotels"] if h.get("cityId") == hub.get("tripcomCity")), None) if hub.get("tripcomCity") and hub.get("tripcomCity") != slug else None
    if _extra:
        extra_stay = f"""<div class="tc-group">
    <div class="ess-ghead"><h3>🏨 {esc(_extra['city'])} 숙소</h3><span class="n">1</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">{esc(_extra.get('sub', ''))}</span></div>
    <div class="tc-grid hub-tc">{hub_hotel_cards([_extra])}</div>
  </div>"""
    stay_html = f"""<section class="hub-sec" id="stay">  <div class="hub-sec-head">
    <div><span class="hub-k">STAY &amp; FLIGHT &amp; TICKET</span>
      <h2>{esc(hub['name'])} 숙소·항공권·입장권</h2>
      <p>트립닷컴에서 직접 예약하는 숙소·항공권과, 현지에서 쓸 입장권·공항픽업·eSIM·공항철도입니다. 체크인 날짜와 방문일을 넣으면 그날 요금으로 열리고, 예약·결제는 트립닷컴에서 그대로 이루어집니다.</p></div>
  </div>
  {tc_list_html}
  {hotel_group}
  {extra_stay}
  {flight_html}
  {act_html}
  {klook_html}
  <p class="hub-note">{esc(TRIPCOM['disclosure'])}</p>
</section>"""

    # 가이드
    guides_html = f"""<section class="hub-sec" id="guides">
  <div class="hub-sec-head">
    <div><span class="hub-k">READ NEXT</span>
      <h2>{esc(hub['name'])} 관련 가이드 <em>{len(guides)}편</em></h2>
      <p>같은 도시의 교통패스 본전, 공항에서 시내까지 실제 요금, 패키지 실지출을 숫자로 계산한 글입니다.</p></div>
    <a class="hub-more" href="guides/index.html">가이드 전체 보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>
  </div>
  {hub_guide_cards(guides)}
</section>"""

    others = "".join(
        f'<a class="hub-city-chip" href="{esc(o["slug"])}">{B.flag_svg(o["flag"], 15, 10.5)}<b>{esc(o["nav"])}</b></a>'
        for o in hub_list() if o["slug"] != slug
    )

    body = f"""<div class="pg-hero hub-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><a href="cities/index.html">도시별 여행</a><i></i><b>{esc(hub['name'])}</b></nav>
    <span class="pg-kicker">{esc(hub['kicker'])} · {esc(hub['name'])}</span>
    <div class="pg-head">
      <h1>{hub['h1']}</h1>
      <p class="dek">{hub['intro']}</p>
      <div class="pg-meta">{''.join(meta)}</div>
    </div>
    <figure class="pg-hero-img">
      <img src="{esc(hub['image'])}" alt="{esc(hub['imageAlt'])}" width="1600" height="1000" loading="eager" />
      <figcaption>{esc(hub.get('imageCredit') or '사진: Pexels')}</figcaption>
    </figure>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
{share_row('hub')}
{cont_bar('도시', hub['nav'] + ' 여행', '/' + slug, hub['image'])}
    <nav class="hub-jump" aria-label="이 페이지 목차">{jump_html}</nav>
{hub_tools_html}
{hub_tips(hub)}
{ad_slot(f"hub-{slug}-top", "이 도시 숙소·항공 최저가", "체크인 날짜만 넣으면 트립닷컴 최저가로 열립니다.", "#stay", "숙소 보기")}
{tours_html}
{ad_slot(f"hub-{slug}-mid", "이 도시 일정, 내 예산으로 계산", "인원·지역·스타일만 넣으면 항공·숙소·투어·eSIM 총액을 A/B/C안으로 보여줍니다.", "index.html#planner", "예산 계산기")}
{food_html}
{gift_html}
{stay_html}
{hub_esim_section(hub)}
{ad_slot(f"hub-{slug}-bottom", "특가가 뜨면 가장 먼저 알려드릴게요", "원하는 여행지와 예산만 남기면 특가·땡처리 소식을 메일로 보내드립니다.", "index.html#alert", "알림 신청")}
{hub_faq_section(hub, tours)}
{guides_html}

    <div class="hub-others">
      <b>다른 도시 여행 페이지</b>
      <div class="hub-city-row">{others}<a class="hub-city-chip" href="cities/index.html"><b>도시 전체 보기</b></a></div>
    </div>

{share_row('hub')}
{cta_band('', hub['name'] + ' 일정, 내 날짜로 계산하기', '인원과 스타일을 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 총액을 계산합니다.')}
  </div>
</div>"""

    return page(
        out_root,
        f"{slug}.html",
        title=hub["seoTitle"],
        desc=hub["metaDesc"],
        body=body,
        base=base,
        active="cities",
        keywords=hub.get("keywords", ""),
        og_image=f"{base.rstrip('/')}/{hub.get('ogImage') or hub['image']}",
        og_image_alt=hub.get("imageAlt", ""),
        jsonld=hub_jsonld(hub, tours, guides, base),
    )


def cities_index(out_root: Path, base: str) -> Path:
    b = base.rstrip("/")
    hubs = hub_list()
    cards = []
    for h in hubs:
        tours = hub_tours(h)
        rest = hub_city_rest(h)
        country = hub_country(h)
        guides = hub_guides(h)
        lowest = min((t["sale"] for t in tours), default=0)
        act_n = len([
            a for a in (TRIPCOM.get("tickets") or []) + (TRIPCOM.get("transfers") or []) + (TRIPCOM.get("cars") or [])
            if a.get("cityId") == h["slug"]
        ])
        bits = [f"투어 {len(tours)}"]
        if rest:
            bits.append(f"맛집 {len(rest['items'])}")
        if country:
            bits.append(f"선물 {len(country['items'])}")
        if act_n:
            bits.append(f"입장권·픽업 {act_n}")
        bits.append(f"가이드 {len(guides)}")
        cards.append(f"""        <a class="gcard hub-card" href="../{h['slug']}.html">
          <div class="thumb"><img src="../{esc(h['image'])}" alt="{esc(h['imageAlt'])}" loading="lazy" width="800" height="500" /></div>
          <div class="gc-body">
            <span class="tag">{esc(h['nav'])}</span>
            <h3>{esc(h['name'])} 여행 — 투어·맛집·선물·숙소</h3>
            <p>{esc(h['metaDesc'][:118])}…</p>
            <div class="gc-foot"><b>{won(lowest)}원~</b> · {' · '.join(bits)}</div>
          </div>
        </a>""")

    listing = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "도시별 여행 페이지",
            "description": hub_specs()["indexDesc"],
            "url": f"{b}/cities/",
            "inLanguage": "ko",
            "hasPart": [
                {"@type": "WebPage", "name": f"{h['name']} 여행", "url": f"{b}/{h['slug']}"}
                for h in hubs
            ],
        },
        ensure_ascii=False,
    )
    crumb = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "트립픽", "item": b + "/"},
                {"@type": "ListItem", "position": 2, "name": "도시별 여행", "item": f"{b}/cities/"},
            ],
        },
        ensure_ascii=False,
    )

    body = f"""<div class="pg-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="../index.html">홈</a><i></i><b>도시별 여행</b></nav>
    <span class="pg-kicker">CITY GUIDES · {len(hubs)}곳</span>
    <div class="pg-head">
      <h1>도시 이름으로 찾는 <em>여행 준비</em> 페이지</h1>
      <p class="dek">{hub_specs()['indexDesc']}</p>
      <div class="pg-meta"><span><b>트립픽 편집</b></span><i></i><span>도시 {len(hubs)}곳</span><i></i><span>업데이트 2026.11.20</span></div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="hub-intro"><p>{hub_specs()['indexIntro']}</p></div>
    <div class="gi-grid hub-grid-3">
{chr(10).join(cards)}
    </div>
    <div class="hub-others hub-others--resorts" id="resorts">
      <p>나트랑·푸꾸옥·싱가포르·홍콩·발리·세부·코타키나발루·치앙마이 8곳은 아직 도시 페이지가 없습니다. 그전까지는 이 카드에서 입장권·액티비티와 공항픽업을 바로 예약합니다. 방문일과 도착 공항을 넣어야 실제 요금이 나옵니다.</p>
{B.render_resorts(TRIPCOM)}
    </div>
    <div class="hub-others">
      <b>아직 도시 페이지가 없는 지역</b>
      <p>삿포로·나트랑·괌·이탈리아·미서부·장가계 등 나머지 지역 상품은 홈의 지역 섹션에서 같은 기준으로 비교할 수 있습니다.</p>
      <a class="hub-more" href="../index.html#regions">홈에서 전체 상품 보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </div>
{cta_band('../', '도시를 정했으면, 내 날짜로 총액 계산', '인원과 스타일을 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 계산합니다.')}
  </div>
</div>"""

    return page(
        out_root,
        "cities/index.html",
        title=hub_specs()["indexTitle"],
        desc=hub_specs()["indexDesc"],
        body=body,
        base=base,
        active="cities",
        keywords="도시별 여행, 오사카 여행, 도쿄 여행, 후쿠오카 여행, 다낭 여행, 방콕 여행, 타이베이 여행, 제주 여행, 도시별 맛집, 도시별 선물",
        jsonld=f'<script type="application/ld+json">{listing}</script>\n<script type="application/ld+json">{crumb}</script>\n'
        + graph_ld(org_ld(base), website_ld(base)),
    )


# ----------------------------------------------------------------------
# v16 도구 페이지 — 환율·일본 면세(/exchange) · 항공사 수하물(/baggage)
# ----------------------------------------------------------------------
def _n(n, d: int = 0) -> str:
    return f"{n:,.{d}f}"


def _page_jsonld(page_path: str, name: str, desc: str, base: str, faq: list, crumbs: list) -> str:
    graph = [
        {
            "@type": "WebApplication",
            "name": name,
            "description": desc,
            "url": f"{base.rstrip('/')}/{page_path}",
            "applicationCategory": "TravelApplication",
            "operatingSystem": "Web",
            "inLanguage": "ko",
            "isAccessibleForFree": True,
            "publisher": {"@type": "Organization", "name": SITE_NAME},
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq
            ],
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": t, **({"item": u} if u else {})}
                for i, (t, u) in enumerate(crumbs)
            ],
        },
    ]
    return '<script type="application/ld+json">' + json.dumps(
        {"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False
    ) + "</script>"


def exchange_page(out_root: Path, base: str) -> Path:
    fx = load_json("fx.json")
    curs = fx["currencies"]
    opts = "\n                ".join(
        f'<option value="{c["code"]}">{c["symbol"]} {c["name"]} ({c["code"]})</option>' for c in curs
    )
    rows = []
    for c in curs:
        r = c["krw"]
        hundred = r * 100
        per10k = 10000 / r
        rows.append(
            f'<tr><th scope="row">{c["symbol"]} {c["name"]} <em>{c["code"]}</em></th>'
            f'<td>{_n(r, 3 if r < 10 else 2)}원</td>'
            f'<td>{_n(hundred, 2 if hundred < 100 else 0)}원</td>'
            f'<td>{_n(per10k, 0 if per10k > 1000 else 1)}{c["label"]}</td></tr>'
        )
    chips = []
    for i, v in enumerate(fx["taxPresets"]):
        chips.append(
            f'<button type="button" class="fx-chip" data-amount="{v}">{v:,}' + (" <span>(세전 5,000엔)</span>" if i == 0 else "") + "</button>"
        )

    body = read(PAGES / "exchange.html")
    body = body.replace("<!-- @FX_OPTIONS -->", opts)
    body = body.replace("<!-- @RATE_ROWS -->", "\n                ".join(rows))
    body = body.replace("<!-- @TAX_PRESETS -->", "\n            ".join(chips))
    # 고시일·고정 환산 기준 표기는 fx.json/planner.json에서 채운다(하드코딩 금지)
    body = body.replace("{{FX_DATE}}", (fx.get("fallbackUpdatedKst") or "")[:10].replace("-", "."))
    body = body.replace("{{BASIS_DATE}}", (fx.get("staticBasis") or {}).get("date", ""))
    body = body.replace("{{BASIS_JPY}}", f'{load_json("planner.json")["fx"]["JPY100"]:,}')
    payload = json.dumps(fx, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = body.replace(
        "<!-- @FX_DATA -->",
        f'<script type="application/json" id="fxData">{payload}</script>',
    )

    faq = [
        ("면세 환급은 결제액의 10%인가요, 9.09%인가요?",
         "세금 포함 가격에서 돌려받는 소비세는 결제액 x 10 / 110으로 약 9.09%입니다. 8% 경감세율 품목은 약 7.41%입니다."),
        ("5,000엔은 세전인가요, 세후인가요?",
         "세전(세금 별도) 5,000엔 이상입니다. 같은 매장에서 같은 날 산 물품을 합산하며 일반 물품과 식료품·소모품을 함께 계산할 수 있습니다. 10% 품목만 사면 세금 포함 5,500엔부터 대상입니다."),
        ("환급을 못 받는 경우는 언제인가요?",
         "구매일부터 90일이 지나 출국하거나, 수하물을 부친 뒤에 세관 확인을 받으면 환급이 어렵습니다. 일본 안에서 먹거나 쓴 물품, 같은 구매 기록 중 확인되지 않은 물품이 하나라도 있으면 그 기록 전체가 대상에서 빠집니다."),
        ("현금과 카드 중 어느 쪽이 유리한가요?",
         "결제 통화가 엔화면 엔화 결제가 원화 결제보다 환전 수수료가 적습니다. 카드사 해외 이용 수수료(보통 1~2%)와 ATM 인출 수수료를 함께 보고, 소액은 현금·큰 금액은 카드처럼 나눠 쓰는 편이 안전합니다."),
    ]
    jsonld = _page_jsonld(
        "exchange.html",
        "트립픽 환율·일본 면세 계산기",
        "12개 통화 실시간 환율 계산기와 2026년 11월 1일 리펀드 방식으로 바뀐 일본 면세 환급 계산기.",
        base,
        faq,
        [("트립픽", ""), ("환율·면세 계산기", None)],
    )
    return page(
        out_root,
        "exchange.html",
        title="환율 계산기 · 일본 면세 환급 계산기 (2026.11.1 리펀드) | 트립픽",
        desc="엔·동·바트·달러를 원화로 바로 계산하고, 2026년 11월 1일부터 공항 환급으로 바뀐 일본 면세(10%·8%) 환급 예상액과 실부담 원화를 계산합니다. 세전 5,000엔 기준과 90일 규정까지 정리.",
        body=body,
        base=base,
        active="exchange",
        keywords="엔화 계산기, 환율 계산기, 일본 면세 계산기, 리펀드 방식, 일본 세금 환급, 소비세 10% 8%",
        jsonld=jsonld,
    )


GEAR_IDS = [
    "cp-carrier-sm0320",
    "cp-carrier-botn-cl23",
    "cp-powerbank-anker-maggo",
    "cp-actioncam-dji-pocket3",
    "cp-earbuds-airpods-pro3",
    "cp-sleepset-silverbay",
    "cp-carrier-natgeo-28",
    "cp-headphone-sony-xm5",
    "cp-earbuds-sony-wf5",
    "cp-adapter-philips-70w",
]
BAG_ESIM_IDS = ["jp-esim-usimsa-3d", "vn-esim-usimsa-3d", "th-esim-usimsa-3d", "tw-esim-usimsa-3d"]
# v19: 출발 전 필수템 — 65W 충전기·저울·보조가방·샤워필터·우양산·방수팩
ESSFILL_IDS = [
    "cp-gan65w-homeplanet",
    "cp-luggagescale-homeplanet",
    "cp-bostonbag-mongddang",
    "cp-showerfilter-duvel",
    "cp-umbrella-crocodile",
    "cp-waterproof-sinji",
]
BAG_ESIM_LABEL = {"jp-esim-usimsa-3d": "일본", "vn-esim-usimsa-3d": "베트남",
                  "th-esim-usimsa-3d": "태국", "tw-esim-usimsa-3d": "대만"}


def gear_cards(ids: list | None = None) -> list:
    """v17: /baggage '오래 쓰는 여행 장비 6종' 카드(쿠팡 실링크). v19: ids 로 다른 묶음도 같은 카드로."""
    out = []
    for gid in (ids if ids is not None else GEAR_IDS):
        e = next((x for x in ESSENTIALS if x["id"] == gid), None)
        if not e:
            continue
        specs = "".join(f"<li>{esc(x)}</li>" for x in (e.get("specs") or []))
        listp = (f'<small>{won(e["listPrice"])}원</small>'
                 if e.get("listPrice") and e["listPrice"] > e["price"] else "")
        out.append(f"""<a class="gear" href="{esc(e.get('url') or e['naverMe'])}" target="_blank" rel="noopener sponsored">
              <span class="gear-thumb"><img src="{esc(e['image'])}" alt="{esc(e['name'])}" width="400" height="400" loading="lazy" /></span>
              <span class="gear-body">
                <span class="gear-tag">{esc(e.get('categoryLabel') or '여행 장비')}{f'<span class="gear-badge">{esc(e["badge"])}</span>' if e.get('badge') else ''}</span>
                <b class="gear-name">{esc(e['name'])}</b>
                <ul class="gear-specs">{specs}</ul>
                <span class="gear-foot"><span class="gear-price">{won(e['price'])}원{listp}</span><span class="gear-go">쿠팡에서 보기 →</span></span>
              </span>
            </a>""")
    return out


def bag_esim_links() -> list:
    out = []
    for eid in BAG_ESIM_IDS:
        e = next((x for x in ESSENTIALS if x["id"] == eid), None)
        if not e:
            continue
        out.append(f'<a href="{esc(B.ess_url(e))}" target="_blank" rel="noopener sponsored">'
                   f'<span class="ec">{esc(BAG_ESIM_LABEL.get(eid, ""))}</span>'
                   f'<b>{esc(e["name"])}</b><span class="ep">{won(e["price"])}원</span></a>')
    return out


def baggage_page(out_root: Path, base: str) -> Path:
    data = load_json("baggage.json")
    rows = []
    for a in data["airlines"]:
        warn = f'<span class="bag-warn">{esc(a["warn"])}</span>' if a.get("warn") else ""
        rows.append(f"""<tr>
                  <th scope="row" class="bag-name"><b>{esc(a["name"])}</b><em>{esc(a["short"])} · {esc(a["type"])}</em>{warn}</th>
                  <td data-label="기내"><div class="bag-cell"><b>{esc(a["cabin"])}</b><small>{esc(a["cabinSize"])} · {esc(a["personal"])}</small></div></td>
                  <td data-label="위탁"><div class="bag-cell"><b>{esc(a["checked"])}</b><small>{esc(a["checkedNote"])}</small></div></td>
                  <td data-label="1개 한도"><div class="bag-cell"><b>{esc(a["limit"])}</b></div></td>
                  <td data-label="공식 안내"><a class="bag-link" href="{a["official"]}" target="_blank" rel="noopener">{esc(a["officialLabel"])} ↗</a></td>
                </tr>""")
    cards = []
    for c in data["coupang"]:
        cards.append(f"""<a class="cpd-item" href="{c["url"]}" target="_blank" rel="noopener sponsored">
              <span class="cpd-top"><img src="{c["img"]}" alt="{esc(c["name"])}" width="52" height="52" loading="lazy" />
                <span><span class="cpd-tag">{esc(c["tag"])}</span><span class="cpd-name">{esc(c["name"])}</span><span class="cpd-hint">{esc(c["hint"])}</span></span></span>
              <span class="cpd-foot"><span class="cpd-price">{c["price"]:,}원</span><span class="cpd-go">쿠팡에서 보기 →</span></span>
            </a>""")

    body = read(PAGES / "baggage.html")
    body = body.replace("<!-- @BAG_ROWS -->", "\n                ".join(rows))
    body = body.replace("<!-- @COUPANG -->", "\n            ".join(cards))
    body = body.replace("<!-- @GEAR -->", "\n            ".join(gear_cards()))
    body = body.replace("<!-- @ESSFILL -->", "\n            ".join(gear_cards(ESSFILL_IDS)))
    body = body.replace("<!-- @ESIM -->", "\n            ".join(bag_esim_links()))

    faq = [
        ("기내 10kg은 캐리어만 재는 건가요?",
         "대부분 항공사가 캐리어와 노트북 가방·핸드백을 합쳐 10kg으로 봅니다. 공항 면세점에서 산 물건도 무게와 개수에 포함됩니다."),
        ("20,000mAh 보조배터리는 기내에 되나요?",
         "3.7V 기준 74Wh라 100Wh 이하로 1인 2개까지 반입할 수 있고 위탁은 안 됩니다. 100Wh를 넘으면 항공사 승인이, 160Wh를 넘으면 반입이 금지됩니다."),
        ("피치항공·비엣젯항공은 왜 7kg인가요?",
         "일본·베트남 LCC는 기내를 개인 소지품 포함 2개 합계 7kg으로 봅니다. 넘으면 탑승구에서 유료 위탁으로 바뀝니다."),
        ("아시아나 항공권인데 대한항공 규정이 적용되나요?",
         "2026년 12월 17일부터 아시아나 항공편이 대한항공(KE) 편명으로 통합 운항됩니다. 탑승일이 그 이후면 실제 운항사 기준이 적용되므로 이티켓의 허용량을 확인하세요."),
    ]
    jsonld = _page_jsonld(
        "baggage.html",
        "트립픽 항공사별 수하물 규정표",
        "대한항공·아시아나·진에어·티웨이·제주항공·에어부산·피치·비엣젯의 기내·위탁 수하물과 보조배터리 규정 비교.",
        base,
        faq,
        [("트립픽", ""), ("항공사 수하물 규정", None)],
    )
    return page(
        out_root,
        "baggage.html",
        title="항공사별 수하물 규정 비교 — 기내 10kg·위탁 0~30kg·보조배터리 2개 | 트립픽",
        desc="대한항공·아시아나·진에어·티웨이(트리니티)·제주항공·에어부산·피치·비엣젯 8곳의 기내 무게·크기와 운임별 무료 위탁, 보조배터리 160Wh 규정을 2026.11.20 기준으로 비교합니다.",
        body=body,
        base=base,
        active="baggage",
        keywords="기내 수하물 10kg, 위탁 수하물 15kg, LCC 수하물, 보조배터리 기내 반입, 160Wh, 피치항공 7kg, 비엣젯 수하물",
        jsonld=jsonld,
    )


# ----------------------------------------------------------------------
# v18 도구 페이지 — 교통패스 본전 계산기(/passes) · 월별 시즌 캘린더(/calendar)
# ----------------------------------------------------------------------
def _tc(kind: str, **match) -> dict | None:
    for it in TRIPCOM.get(kind) or []:
        if all(it.get(k) == v for k, v in match.items()):
            return it
    return None


def _tc_flight(city: str) -> dict | None:
    for f in TRIPCOM.get("flights") or []:
        if city and city in f.get("route", ""):
            return f
    return None


def _ess(eid: str) -> dict | None:
    return next((e for e in ESSENTIALS if e["id"] == eid), None)


def pk_link_card(kicker: str, title: str, price: str, url: str, cta: str) -> str:
    return (
        f'<a class="pk-link" href="{esc(url)}" target="_blank" rel="noopener sponsored">'
        f'<span class="pk-link-k">{esc(kicker)}</span>'
        f'<b>{esc(title)}</b>'
        f'<span class="pk-link-p">{esc(price)}</span>'
        f'<span class="pk-link-go">{esc(cta)} →</span></a>'
    )


def pass_links(slug: str) -> str:
    """도시별 패스·입장권 실링크 카드(네이버 커넥트 · 트립닷컴 파트너스)."""
    out = []
    if slug == "osaka":
        e = _ess("osaka-amazing-pass")
        if e:
            out.append(pk_link_card("네이버 여행", e["name"], f'{won(e["price"])}원', B.ess_url(e), "E-티켓 보기"))
        e2 = _ess("osaka-nankai-rapit")
        if e2:
            out.append(pk_link_card("네이버 여행", "난카이 라피트 공항특급", f'{won(e2["price"])}원', B.ess_url(e2), "공항철도 보기"))
        t = _tc("tickets", id="ticket_osaka")
        if t:
            out.append(pk_link_card("트립닷컴", "오사카 입장권·액티비티", "USJ·리버크루즈·가이유칸", t["url"], "최저가 보기"))
        h = _tc("hotels", cityId="osaka")
        if h:
            out.append(pk_link_card("트립닷컴", "오사카 숙소", "난바·우메다", h["url"], "요금 보기"))
    elif slug == "tokyo":
        e = _ess("tokyo-metro-pass")
        if e:
            out.append(pk_link_card("네이버 여행", "도쿄 메트로 패스 24·48·72시간", f'{won(e["price"])}원~', B.ess_url(e), "패스 보기"))
        e2 = _ess("tokyo-skyliner")
        if e2:
            out.append(pk_link_card("네이버 여행", "나리타→우에노 스카이라이너", f'{won(e2["price"])}원~', B.ess_url(e2), "기차표 보기"))
        r = _tc("rails", id="rail_skyliner")
        if r:
            out.append(pk_link_card("트립닷컴", r["title"], r.get("highlight") or "41분·지정석", r["url"], "공식 티켓"))
        t = _tc("tickets", id="ticket_tokyo")
        if t:
            out.append(pk_link_card("트립닷컴", "도쿄 입장권·액티비티", "디즈니·시부야 스카이", t["url"], "최저가 보기"))
    elif slug == "bangkok":
        t = _tc("tickets", id="ticket_bangkok")
        if t:
            out.append(pk_link_card("트립닷컴", "방콕 입장권·액티비티", "짜오프라야 크루즈·사파리", t["url"], "최저가 보기"))
        f = _tc_flight("방콕")
        if f:
            out.append(pk_link_card("트립닷컴", "서울→방콕 항공권", "인천 출발·왕복", f["url"], "최저가 검색"))
        h = _tc("hotels", cityId="bangkok")
        if h:
            out.append(pk_link_card("트립닷컴", "방콕 숙소", "수쿰빗·시암", h["url"], "요금 보기"))
    elif slug == "hongkong":
        out.append(pk_link_card("트립닷컴", "홍콩 숙소", "침사추이·코즈웨이 베이", "https://kr.trip.com/hotels/list?city=58&display=%ED%99%8D%EC%BD%A9&optionId=58&optionType=City&optionName=%ED%99%8D%EC%BD%A9&Allianceid=11407530&SID=336341874&trip_sub1=passes_hongkong_hotel&trip_sub3=D21275837", "요금 보기"))
        out.append(pk_link_card("트립닷컴", "홍콩공항(HKG) → 시내", "짐 많을 때 단독차량", "https://kr.trip.com/airport-transfers/airport-hkg/?Allianceid=11407530&SID=336341874&trip_sub1=passes_hongkong_transfer&trip_sub3=D21285812", "요금 보기"))
        out.append(pk_link_card("트립닷컴", "마카오 숙소", "코타이 리조트·세나도 광장", "https://kr.trip.com/hotels/list?city=59&display=%EB%A7%88%EC%B9%B4%EC%98%A4&optionId=59&optionType=City&optionName=%EB%A7%88%EC%B9%B4%EC%98%A4&Allianceid=11407530&SID=336341874&trip_sub1=passes_macau_hotel&trip_sub3=D21275837", "요금 보기"))
    elif slug == "taipei":
        t = _tc("tickets", id="ticket_taipei")
        if t:
            out.append(pk_link_card("트립닷컴", "타이베이 입장권·액티비티", "101 전망대·고궁박물원", t["url"], "최저가 보기"))
        h = _tc("hotels", cityId="taipei")
        if h:
            out.append(pk_link_card("트립닷컴", "타이베이 숙소", "시먼·중산", h["url"], "요금 보기"))
        tr = _tc("transfers", id="transfer_tpe")
        if tr:
            out.append(pk_link_card("트립닷컴", "타오위안공항 픽업", "시내 호텔까지", tr["url"], "요금 보기"))
    elif slug == "singapore":
        e = _ess("sg-esim-trip-46011732")
        if e:
            out.append(pk_link_card("트립닷컴", "싱가포르 eSIM (1~30일)", f'{won(e["price"])}원~ · 도착 전 설치', B.ess_url(e), "eSIM 보기"))
        h = _tc("hotels", cityId="singapore")
        if h:
            out.append(pk_link_card("트립닷컴", "싱가포르 숙소", "시티홀·오차드·차이나타운", h["url"], "요금 보기"))
        es = _ess("sg-gardens-ticket")
        if es:
            out.append(pk_link_card("트립닷컴", "가든스 바이 더 베이 입장권", f'{won(es["price"])}원', B.ess_url(es), "입장권 보기"))
    return "\n            ".join(out)


def passes_page(out_root: Path, base: str) -> Path:
    data = load_json("passes.json")
    osaka = data["osaka"]
    chips = "\n              ".join(
        f'<button type="button" class="pk-btn{" on" if i == 0 else ""}" data-pass="{p["id"]}" aria-pressed="{"true" if i == 0 else "false"}">'
        f'<b>{esc(p["name"])}</b><span>{_n(p["price"])}엔</span><em>{esc(p["note"])}</em></button>'
        for i, p in enumerate(osaka["passes"])
    )
    default_fac = {"castle", "umeda", "tsutenkaku", "cruise"}
    facs = "\n              ".join(
        f'<label class="pk-fac-i"><input type="checkbox" data-fac="{f["id"]}"'
        f'{" checked" if f["id"] in default_fac else ""} />'
        f'<span class="pk-fac-n">{esc(f["name"])}</span>'
        f'<span class="pk-fac-p">{_n(f["price"])}엔</span>'
        f'<span class="pk-fac-t">{esc(f["note"])}</span></label>'
        for f in osaka["facilities"]
    )
    tok_chips = "\n              ".join(
        f'<button type="button" class="pk-btn{" on" if t["id"] == "72" else ""}" data-tokyo="{t["id"]}" aria-pressed="{"true" if t["id"] == "72" else "false"}">'
        f'<b>{esc(t["name"])}</b><span>{_n(t["price"])}엔</span><em>어린이 {_n(t["child"])}엔</em></button>'
        for t in data["tokyo"]["tickets"]
    )
    narita_rows = "\n                ".join(
        f'<tr><th scope="row"><b>{esc(n["name"])}</b><small>{esc(n["note"])}</small></th>'
        f'<td>{esc(n["to"])}</td><td>{n["minutes"]}분</td><td class="num">{_n(n["price"])}엔</td>'
        f'<td class="num" data-narita-total="{n["id"]}">–</td></tr>'
        for n in data["tokyo"]["narita"]
    )
    tpe_chips = "\n              ".join(
        f'<button type="button" class="pk-btn{" on" if t["days"] == 1 else ""}" data-tpe="{t["id"]}" aria-pressed="{"true" if t["days"] == 1 else "false"}">'
        f'<b>{t["days"]}일권</b><span>{_n(t["price"])}대만달러</span><em>하루 {_n(t["price"] / t["days"])}대만달러</em></button>'
        for t in data["taipei"]["funpass"]
    )

    body = read(PAGES / "passes.html")
    sg_chips = "\n              ".join(
        f'<button type="button" class="pk-btn{" on" if t["days"] == 3 else ""}" data-sg="{t["id"]}" aria-pressed="{"true" if t["days"] == 3 else "false"}">'
        f'<b>{t["days"]}일권</b><span>{_n(t["price"])}싱가포르달러</span><em>{"무제한" if t["days"] == 1 else "하루 " + _n(t["price"] / t["days"]) + "싱가포르달러"}</em></button>'
        for t in data["singapore"]["touristPass"]
    )
    body = body.replace("<!-- @OSAKA_PASSES -->", chips)
    body = body.replace("<!-- @OSAKA_FACILITIES -->", facs)
    body = body.replace("<!-- @TOKYO_TICKETS -->", tok_chips)
    body = body.replace("<!-- @NARITA_ROWS -->", narita_rows)
    body = body.replace("<!-- @TAIPEI_PASSES -->", tpe_chips)
    body = body.replace("<!-- @SG_PASSES -->", sg_chips)
    hk_chips = "\n              ".join(
        f'<button type="button" class="pk-btn{" on" if st["id"] == "kowloon" else ""}" data-hk="{st["id"]}" aria-pressed="{"true" if st["id"] == "kowloon" else "false"}">'
        f'<b>{esc(st["name"])}</b><span>{_n(st["octopus"])}홍콩달러</span><em>왕복권 {_n(st["round"])} · {st["minutes"]}분</em></button>'
        for st in data["hongkong"]["stations"]
    )
    body = body.replace("<!-- @HK_STATIONS -->", hk_chips)
    for slug in ("osaka", "tokyo", "bangkok", "taipei", "singapore", "hongkong"):
        body = body.replace(f"<!-- @LINKS_{slug.upper()} -->", pass_links(slug))
    payload = json.dumps({"fx": data["fx"], "osaka": data["osaka"], "tokyo": data["tokyo"],
                          "bangkok": data["bangkok"], "taipei": data["taipei"],
                          "singapore": data["singapore"], "hongkong": data["hongkong"]},
                         ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = body.replace("<!-- @PK_DATA -->", f'<script type="application/json" id="pkData">{payload}</script>')

    faq = [
        ("오사카 주유패스 1day와 2day 중 뭐가 낫나요?",
         "시내 관광일이 연속 이틀이면 2day(5,000엔)가 1day 두 장(7,000엔)보다 2,000엔 쌉니다. 중간에 USJ나 교토 일정이 끼면 1day가 맞습니다."),
        ("도쿄 지하철권으로 야마노테선을 탈 수 있나요?",
         "아니요. 도쿄 메트로·도에이 13개 노선만 포함이고 JR 야마노테선은 별도 요금입니다."),
        ("방콕 BTS 1일권은 24시간인가요?",
         "아니요. 산 날 자정까지입니다. BTS만 되고 MRT·공항철도는 포함되지 않습니다."),
        ("타이베이 펀패스와 첩운 1일권의 차이는 무엇인가요?",
         "첩운 1일권 150대만달러는 지하철만, 펀패스 교통권 210대만달러는 지하철+버스+관광 셔틀 6개 노선까지 무제한입니다."),
        ("홍콩 공항철도 왕복권과 2인 묶음표 중 뭐가 싸나요?",
         "구룡역 기준 왕복권은 1인 195홍콩달러(2인 390), 2인 묶음표는 편도 150홍콩달러라 왕복이면 두 장을 사 300홍콩달러입니다. 날짜가 갈리는 3박4일이면 묶음표가 90홍콩달러 싸고, 같은 날 왕복이면 옥토퍼스 편도가 돌아오는 편 무료라 210홍콩달러로 가장 쌉니다."),
        ("싱가포르는 컨택트리스 카드와 Tourist Pass 중 뭐가 낫나요?",
         "3박4일이면 해외 결제 가능한 컨택트리스 카드가 쌉니다. 외국 카드는 사용한 날마다 0.60싱가포르달러가 붙지만 3일이면 1.80싱가포르달러입니다. Tourist Pass 3일권 29싱가포르달러는 하루 6회 이상 타야 본전이고, 1·2·3일권만 있어 4일 이상 일정에는 맞지 않습니다. EZ-Link는 카드값 5가 환불되지 않아 8~9일 이상일 때 유리합니다."),
    ]
    jsonld = _page_jsonld(
        "passes.html",
        "트립픽 교통패스 본전 계산기",
        "오사카 주유패스·도쿄 지하철 패스·방콕 BTS·타이베이 펀패스·싱가포르 Tourist Pass·홍콩 공항철도가 내 일정에서 본전을 넘는지 계산하는 도구.",
        base,
        faq,
        [("트립픽", ""), ("교통패스 본전 계산기", None)],
    )
    return page(
        out_root,
        "passes.html",
        title="교통패스 본전 계산기 — 오사카 주유패스·도쿄 지하철·BTS·펀패스·싱가포르 | 트립픽",
        desc="오사카 주유패스 3,500엔, 도쿄 지하철 800/1,200/1,500엔, 방콕 BTS 150밧, 타이베이 펀패스 210대만달러가 내 일정에서 본전을 넘는지 계산합니다. 탑승 횟수와 시설 입장료를 넣으면 원화로 이득·손해가 나옵니다.",
        body=body,
        base=base,
        active="passes",
        keywords="오사카 주유패스 본전, 도쿄 지하철 패스, 나리타 스카이라이너, 방콕 BTS 1일권, 타이베이 펀패스, 싱가포르 Tourist Pass, 싱가포르 컨택트리스, EZ-Link, 교통패스 계산기",
        jsonld=jsonld,
    )


def _clip(text: str, limit: int = 30) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


SEASON_TOUR_CITY = {"seoul": "seoul", "busan": "busan", "gangneung": "gangwon",
                    "gyeongju": "gyeongju", "jeju": "jeju"}
# v35: 트립닷컴 도시 eSIM 목록이 없는 도시는 나라별 쇼핑 커넥트 eSIM(실제 링크)으로 잇는다.
SEASON_ESIM_FALLBACK = {"jp": "jp-esim-usimsa-3d", "vn": "vn-esim-usimsa-3d",
                        "th": "th-esim-usimsa-3d", "tw": "tw-esim-usimsa-3d"}


def _season_tour(city_id: str) -> dict | None:
    tour_city = SEASON_TOUR_CITY.get(city_id)
    if not tour_city:
        return None
    return next((t for t in TOURS if t.get("city") == tour_city), None)


def _stays_count(slug: str) -> int:
    return sum(1 for h in STAYS.get("hotels", []) if h.get("region") == slug)


def season_links(c: dict) -> dict:
    """캘린더 상세 카드의 예약 링크.

    v32: fare=null(항공권 없음)·허브 없음·숙소 없음인 도시가 있으므로
    실제 자산이 있는 링크만 만든다(빈 버튼을 만들지 않는다).
    v35: eSIM 도 같은 원칙으로 붙인다(트립닷컴 도시 목록 → 나라별 쇼핑 커넥트 상품 순).
    """
    out = {}
    aff = c.get("affiliate") or {}
    links = c.get("links") or {}
    name = c.get("name", "")
    cid = c.get("id", "")

    if aff.get("flight"):
        # "오사카·교토" · "후쿠오카·규슈"처럼 묶인 이름은 첫 도시로 항공 노선을 찾는다
        f = _tc_flight(name.split("·")[0])
        if f:
            out["flight"] = {"label": f"{f['route']} 항공권", "url": f["url"]}

    h = _tc("hotels", cityId=links.get("stays") or cid)
    if h:
        out["hotel"] = {"label": f"{h['city']} 숙소", "url": h["url"]}

    t = _tc("tickets", id=f"ticket_{cid}")
    if t:
        out["ticket"] = {"label": _clip(t.get("title") or "입장권·액티비티"), "url": t["url"]}
    else:
        resort = next((r for r in TRIPCOM.get("resorts") or [] if r.get("cityId") == cid), None)
        if resort and (resort.get("ticket") or {}).get("url"):
            tk = resort["ticket"]
            out["ticket"] = {"label": _clip(tk.get("title") or "입장권·액티비티"), "url": tk["url"]}
        else:
            tour = _season_tour(cid)
            if tour:
                out["ticket"] = {"label": _clip(tour.get("title", ""), 34), "url": tour["url"]}

    tr = _tc("transfers", cityId=cid)
    if tr:
        out["transfer"] = {"label": _clip(tr.get("title") or "공항픽업", 24), "url": tr["url"]}
    else:
        resort = next((r for r in TRIPCOM.get("resorts") or [] if r.get("cityId") == cid), None)
        if resort and (resort.get("transfer") or {}).get("url"):
            tp = resort["transfer"]
            out["transfer"] = {"label": _clip(tp.get("title") or "공항픽업", 24), "url": tp["url"]}

    slug = links.get("stays")
    if slug:
        n = _stays_count(slug)
        out["stays"] = {"label": f"찐숙소 {n}곳 비교" if n else "숙소 비교", "url": f"/stays#{slug}"}

    # v35: eSIM — 트립닷컴 도시 eSIM 목록이 있으면 그걸, 없으면 나라별 쇼핑 커넥트 eSIM 으로 잇는다.
    # affiliate.esim 이 true 인데 링크를 못 만들던 도시(오사카·도쿄·후쿠오카·다낭·방콕·타이베이)가
    # 캘린더 상세 카드에서 eSIM 버튼 없이 비어 있던 구멍을 이 자리에서 메운다.
    if aff.get("esim"):
        e = _tc("esims", cityId=cid)
        if e:
            out["esim"] = {"label": _clip(e.get("title") or "eSIM", 26), "url": e["url"],
                           "note": e.get("highlight") or "도착 전 설치"}
        else:
            eid = SEASON_ESIM_FALLBACK.get(c.get("flag"))
            ess = _ess(eid) if eid else None
            if ess:
                out["esim"] = {"label": ess["categoryLabel"],
                               "url": ess.get("url") or ess["naverMe"],
                               "note": f"{won(ess['price'])}원부터 · {ess['store']}"}

    if links.get("guide"):
        g = next((x for x in GUIDES_LIST if x["slug"] == links["guide"]), None)
        if g:
            out["guide"] = {"label": _clip(g.get("navTitle", "")), "url": f"guides/{g['slug']}.html"}

    if links.get("cityPage"):
        out["cityPage"] = {"label": f"{name} 도시 페이지", "url": f"/{links['cityPage']}"}
    return out


SEASON_MONTHS_LABEL = {"spring": "3~5월", "summer": "6~8월", "autumn": "9~11월", "winter": "12~2월"}
SEASON_CAUTION = {
    "spring": "황사·꽃샘추위 — 3월 중순 이전 강원·경북 산간은 아침 영하이고, 4월 첫 주 벚꽃 주말은 숙소가 30~50% 오릅니다. 황사가 심한 날은 실내 일정으로 바꾸세요.",
    "summer": "장마 6월 하순~7월 중순, 태풍 8~9월 — 같은 7월에도 나트랑 비 8.4일·강릉 16일로 두 배 차이납니다. 태풍 예보가 나오면 항공 취소 규정부터 확인하세요.",
    "autumn": "태풍 끝물·일교차 — 9월 초는 아직 태풍 철이고, 10~11월은 아침저녁 10도 안팎까지 떨어집니다. 단풍 절정 주말에는 교토·서울 숙소가 가장 비쌉니다.",
    "winter": "한파·설 연휴 — 1월 셋째 주가 가장 춥고, 설 연휴(2027년 2월 6일 전후)에는 국내·동남아 항공이 함께 오릅니다. 유럽은 12월 연말에 숙소가 두 배가 됩니다.",
}
SEASON_GUIDE_LINK = {
    "spring": ("spring-travel-destinations", "봄 여행지 8곳 — 벚꽃 개화 순서"),
    "summer": ("summer-travel-destinations", "여름 여행지 8곳 — 장마·우기 피하기"),
    "autumn": ("autumn-travel-destinations", "가을 여행지 8곳 — 10월이 비 적음"),
    "winter": ("winter-travel-destinations", "겨울 여행지 8곳 — 27도와 영하 2도"),
}


def calendar_page(out_root: Path, base: str) -> Path:
    data = load_json("season.json")
    cities = data["cities"]
    filt = data.get("filters") or {}
    ui = data.get("ui") or {}
    regions = filt.get("regions") or []
    themes = filt.get("themes") or []
    seasons = filt.get("seasons") or []
    months_f = {m["month"]: m for m in (filt.get("months") or [])}
    season_kr = {"peak": "성수기", "shoulder": "준성수기", "off": "비수기"}
    theme_name = {t["code"]: t["name"] for t in themes}
    region_name = {r["code"]: r["name"] for r in regions}
    by_id = {c["id"]: c for c in cities}
    guides_have = {g["slug"] for g in GUIDES_LIST}
    cm = TODAY.month
    default_city = by_id.get("osaka") or cities[0]

    def flag_of(c: dict) -> str:
        return c.get("flagIso") or c.get("flag") or ""

    def theme_names_at(c: dict, m: int) -> str:
        return "·".join(theme_name[t] for t in (c.get("themes") or [])[m - 1] if t in theme_name) or "—"

    def fare_text(c: dict, m: int) -> str:
        if not c.get("fare"):
            return "—"
        band = c["fare"][c["season"][m - 1]]
        return f"약 {band[0] / 10000:.0f}~{band[1] / 10000:.0f}만원"

    def pick_btn(cid: str, name: str, why: str, month: int, score=None) -> str:
        sc = f"<i>{score}</i>" if score else ""
        return (f'<button type="button" class="sc-pick" data-pick-city="{cid}" data-pick-month="{month}">'
                f'<b>{esc(name)}{sc}</b><span>{esc(why)}</span></button>')

    # 도시 버튼 — 지역 그룹(모바일 2줄)
    groups = ui.get("cityGroups") or [
        {"region": r["code"], "name": r["name"],
         "cities": [c["id"] for c in cities if c.get("region") == r["code"]]} for r in regions
    ]
    city_blocks = []
    for grp in groups:
        btns = []
        for cid in grp.get("cities") or []:
            c = by_id.get(cid)
            if not c:
                continue
            on = c["id"] == default_city["id"]
            btns.append(
                f'<button type="button" class="sc-city{" on" if on else ""}" data-city-btn="{c["id"]}" '
                f'data-region="{esc(c.get("region", ""))}" aria-pressed="{"true" if on else "false"}">'
                f'{B.flag_svg(flag_of(c), 18, 12.6)}<b>{esc(c["name"])}</b></button>'
            )
        if btns:
            city_blocks.append(
                f'<div class="sc-cgroup" data-cgroup="{grp["region"]}">'
                f'<span class="sc-cgroup-n">{esc(grp["name"])}</span>'
                f'<div class="sc-cgroup-b">{"".join(btns)}</div></div>'
            )

    month_btns = "\n            ".join(
        f'<button type="button" class="sc-month{" on" if m == cm else ""}" data-month-btn="{m}" aria-pressed="{"true" if m == cm else "false"}">'
        f'<b>{m}월</b><small data-month-temp="{m}">{default_city["temp"][m - 1]:.0f}°</small></button>'
        for m in range(1, 13)
    )

    anchors = "".join(f'<span id="{c["id"]}"></span>' for c in cities)

    # 필터 칩
    season_chips = ['<button type="button" class="sc-chip on" data-season-btn="" aria-pressed="true">전체</button>']
    for s in seasons:
        season_chips.append(
            f'<button type="button" class="sc-chip" data-season-btn="{s["code"]}" aria-pressed="false">'
            f'{esc(s["name"])}<small>{SEASON_MONTHS_LABEL.get(s["code"], "")}</small></button>'
        )
    theme_chips = ['<button type="button" class="sc-chip on" data-theme-btn="" aria-pressed="true">전체</button>']
    for t in themes:
        theme_chips.append(
            f'<button type="button" class="sc-chip" data-theme-btn="{t["code"]}" aria-pressed="false">{esc(t["name"])}</button>'
        )
    region_chips = ['<button type="button" class="sc-chip on" data-region-btn="" aria-pressed="true">전체</button>']
    for r in regions:
        region_chips.append(
            f'<button type="button" class="sc-chip" data-region-btn="{r["code"]}" aria-pressed="false">'
            f'{esc(r["name"])}<small>{r.get("count", "")}</small></button>'
        )
    sort_chips = []
    for s in (filt.get("sort") or [{"code": "score", "name": "쾌적도"}]):
        on = s["code"] == "score"
        sort_chips.append(
            f'<button type="button" class="sc-chip{" on" if on else ""}" data-sort-btn="{s["code"]}" '
            f'aria-pressed="{"true" if on else "false"}">{esc(s["name"])}</button>'
        )

    # 이 달 추천 TOP 6 (빌드 시점 이번 달)
    mf = months_f.get(cm) or {}
    month_picks = "".join(
        pick_btn(p["id"], p["name"], p.get("why", ""), cm, p.get("score")) for p in (mf.get("picks") or [])
    )
    spot_rows = []
    for code, sp in (mf.get("themePicks") or {}).items():
        spot_rows.append(
            f'<span class="sc-trow"><span class="sc-theme-chip">{esc(theme_name.get(code, code))}</span>'
            f'<button type="button" class="sc-tspot" data-pick-city="{sp["id"]}" data-pick-month="{sp.get("month", cm)}">'
            f'{esc(sp["name"])} <small>{sp.get("month", cm)}월 · {esc(sp.get("why", ""))}</small></button></span>'
        )

    # 계절 패널 4개
    season_panels = []
    for s in seasons:
        code = s["code"]
        months = s["months"]
        mlab = SEASON_MONTHS_LABEL.get(code, "")
        cards = []
        for p in s.get("picks") or []:
            c = by_id.get(p["id"])
            if not c:
                continue
            best = max(months, key=lambda m: c["score"][m - 1])
            cards.append(pick_btn(p["id"], p["name"], p.get("why", ""), best))
        trows = []
        for tcode, arr in (s.get("themePicks") or {}).items():
            spots = "".join(
                f'<button type="button" class="sc-tspot" data-pick-city="{p["id"]}" data-pick-month="{p["month"]}">'
                f'{esc(p["name"])} <small>{p["month"]}월 · {esc(p.get("why", ""))}</small></button>'
                for p in arr
            )
            trows.append(
                f'<span class="sc-trow"><span class="sc-theme-chip">{esc(theme_name.get(tcode, tcode))}</span>{spots}</span>'
            )
        gslug, glabel = SEASON_GUIDE_LINK.get(code, ("", ""))
        glink = (f'<a href="/guides/{gslug}">{esc(glabel)} <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>'
                 if gslug in guides_have else "")
        season_panels.append(f"""<section class="sc-spanel" data-season-panel="{code}" aria-labelledby="scPan{code}">
          <span class="sc-kicker">{code.upper()} · {mlab}</span>
          <h2 id="scPan{code}">{esc(s["name"])} 여행지, {mlab}에 어디가 나은가</h2>
          <p class="sc-mnote">{esc(s.get("desc", ""))}</p>
          <div class="sc-picks">{"".join(cards)}</div>
          <div class="sc-tpicks">{"".join(trows)}</div>
          <p class="sc-warn"><b>주의</b> · {esc(SEASON_CAUTION.get(code, ""))}</p>
          <div class="sc-glinks">{glink}</div>
        </section>""")

    # 같은 달 비교표(빌드 시점 = 이번 달, 쾌적도 순) — JS가 선택한 달·정렬로 다시 그린다
    cmp_rows = []
    for c in sorted(cities, key=lambda x: (-x["score"][cm - 1], x["rainDays"][cm - 1])):
        s = c["season"][cm - 1]
        cmp_rows.append(
            f'<tr data-city-row="{c["id"]}"><th scope="row"><b>{esc(c["name"])}</b></th>'
            f'<td>{c["temp"][cm - 1]:.1f}°C</td><td>{_n(c["rain"][cm - 1])}mm</td>'
            f'<td>{c["rainDays"][cm - 1]:.1f}일</td>'
            f'<td><span class="sc-season {s}">{season_kr[s]}</span></td>'
            f'<td>{esc(theme_names_at(c, cm))}</td>'
            f'<td class="num">{fare_text(c, cm)}</td></tr>'
        )

    year_rows = []
    for c in cities:
        cells = "".join(
            f'<td><button type="button" class="sc-cell {c["season"][i]}" data-year-cell="{c["id"]}-{i + 1}" '
            f'data-themes="{" ".join((c.get("themes") or [])[i])}" '
            f'aria-label="{esc(c["name"])} {i + 1}월 {c["temp"][i]:.1f}도 {season_kr[c["season"][i]]}">'
            f'<b>{c["temp"][i]:.0f}°</b><span>{c["rain"][i]:.0f}</span></button></td>'
            for i in range(12)
        )
        year_rows.append(f'<tr data-year-row="{c["id"]}" data-region="{esc(c.get("region", ""))}"><th scope="row">{esc(c["name"])}</th>{cells}</tr>')

    # 상세 카드 초기값(오사카, 이번 달) — JS 없이도 읽히게
    dc = default_city
    i0 = cm - 1
    s0 = dc["season"][i0]
    lead_tbl = (data.get("lead") or {}).get(dc.get("trip", "international")) or {}
    init_links = season_links(dc)
    link_html = ""
    for key, kicker, note in (
        ("flight", "항공권", "최저가 검색"), ("hotel", "숙소", "이 달 요금"),
        ("ticket", "입장권·투어", "현지 액티비티"), ("transfer", "공항픽업", "공항→숙소"),
        ("esim", "eSIM·유심", "도착 전 설치"),
        ("stays", "찐숙소", "평점·1박 최저가"), ("guide", "가이드", "읽기"),
        ("cityPage", "도시 페이지", "맛집·선물·숙소"),
    ):
        L = init_links.get(key)
        if not L:
            continue
        ext = ' target="_blank" rel="noopener sponsored"' if L["url"].startswith("http") else ""
        link_html += (f'<a class="sc-link" href="{esc(L["url"])}"{ext}><span class="sc-link-k">{kicker}</span>'
                      f'<b>{esc(L["label"])}</b><span class="sc-link-n">{esc(L.get("note") or note)}</span></a>')
    dc_acc = dc.get("access") or {}
    acc_bits = []
    if dc_acc.get("mode"):
        acc_bits.append(dc_acc["mode"])
    if dc_acc.get("route"):
        acc_bits.append(dc_acc["route"])
    acc0 = " · ".join(acc_bits)
    if dc_acc.get("time"):
        acc0 += f' ({dc_acc["time"]})'
    acc0 += " · 추천 " + "·".join(map(str, dc.get("bestMonths") or [])) + "월 · 한산 " + "·".join(map(str, dc.get("quietMonths") or [])) + "월"
    fare_hint0 = "왕복·세금 포함" if dc.get("fare") else (dc.get("fareNote", "").split("—")[-1] or "KTX·버스 기준").strip()
    fare_main0 = (f"약 {dc['fare'][s0][0] / 10000:.0f}~{dc['fare'][s0][1] / 10000:.0f}만원"
                  if dc.get("fare") else "항공권 없음")

    body = read(PAGES / "calendar.html")
    body = body.replace("<!-- @SC_ANCHORS -->", anchors)
    body = body.replace("<!-- @SC_CITIES -->", "\n            ".join(city_blocks))
    body = body.replace("<!-- @SC_MONTHS -->", month_btns)
    body = body.replace("<!-- @SC_SEASON_CHIPS -->", "".join(season_chips))
    body = body.replace("<!-- @SC_THEME_CHIPS -->", "".join(theme_chips))
    body = body.replace("<!-- @SC_REGION_CHIPS -->", "".join(region_chips))
    body = body.replace("<!-- @SC_SORT_CHIPS -->", "".join(sort_chips))
    body = body.replace("<!-- @SC_MONTH_PICKS -->", month_picks)
    body = body.replace("<!-- @SC_MONTH_SPOTS -->", "".join(spot_rows))
    body = body.replace("<!-- @SC_SEASON_PANELS -->", "\n\n        ".join(season_panels))
    body = body.replace("<!-- @SC_CMP_ROWS -->", "\n                ".join(cmp_rows))
    body = body.replace("<!-- @SC_YEAR_ROWS -->", "\n              ".join(year_rows))
    body = body.replace(
        '<h2 id="scMonthHead">11월, 어디가 가장 나은가</h2>',
        f'<h2 id="scMonthHead">{esc(mf.get("headline", f"{cm}월, 어디가 가장 나은가"))}</h2>',
    )
    body = body.replace(
        '<p class="sc-mnote" id="scMonthNote"></p>',
        f'<p class="sc-mnote" id="scMonthNote">{esc(mf.get("note", ""))}</p>',
    )
    body = body.replace(
        '<h2 id="scCmpTitle"><span id="scCmpMonth">11월</span>, 어디가 가장 나은가</h2>',
        f'<h2 id="scCmpTitle"><span id="scCmpMonth">{cm}월</span>, 어디가 가장 나은가</h2>',
    )
    # 상세 카드 초기값
    body = body.replace('<span class="sc-kicker" id="scKicker">OSAKA</span>', f'<span class="sc-kicker" id="scKicker">{esc(dc["kicker"])}</span>')
    body = body.replace('<h2 id="scTitle">오사카·교토 <em>11월</em></h2>', f'<h2 id="scTitle">{esc(dc["name"])} <em>{cm}월</em></h2>')
    body = body.replace('<span class="sc-season" id="scSeason">–</span>', f'<span class="sc-season {s0}" id="scSeason">{season_kr[s0]}</span>')
    body = body.replace('<span class="sc-score-chip" id="scScore">–</span>', f'<span class="sc-score-chip" id="scScore">쾌적도 {dc["score"][i0]}</span>')
    ev0 = (dc.get("events") or [""] * 12)[i0] if isinstance(dc.get("events"), list) else ""
    if ev0:
        body = body.replace('<span class="sc-event" id="scEvent" hidden></span>',
                            f'<span class="sc-event" id="scEvent">{esc(ev0)}</span>')
    body = body.replace('<b id="scTemp">–</b>', f'<b id="scTemp">{dc["temp"][i0]:.1f}°C</b>')
    body = body.replace('<b id="scRain">–</b>', f'<b id="scRain">{_n(dc["rain"][i0])}mm</b>')
    body = body.replace('<b id="scDays">–</b>', f'<b id="scDays">{dc["rainDays"][i0]:.1f}일</b>')
    body = body.replace('<b id="scFare">–</b>', f'<b id="scFare">{fare_main0}</b>')
    body = body.replace('<small id="scFareHint">왕복·세금 포함</small>', f'<small id="scFareHint">{esc(fare_hint0)}</small>')
    body = body.replace('<p class="sc-note" id="scNote"></p>', f'<p class="sc-note" id="scNote">{esc(dc["note"][i0])}</p>')
    body = body.replace(
        '<p class="sc-access" id="scAccess"></p>',
        f'<p class="sc-access" id="scAccess">{esc(acc0)}</p>',
    )
    body = body.replace('<b id="scLead">–</b>', f'<b id="scLead">{esc(lead_tbl.get(s0, "—"))}</b>')
    body = body.replace('<b id="scLevel">–</b>', f'<b id="scLevel">{season_kr[s0]} · {"가장 비쌈" if s0 == "peak" else "중간" if s0 == "shoulder" else "가장 쌈"}</b>')
    weather0 = "덥고 습함" if dc["temp"][i0] >= 28 else "따뜻함" if dc["temp"][i0] >= 20 else "선선함" if dc["temp"][i0] >= 10 else "쌀쌀함"
    body = body.replace('<b id="scWeather">–</b>', f'<b id="scWeather">{weather0}</b>')
    body = body.replace('<div class="sc-links" id="scLinks"></div>', f'<div class="sc-links" id="scLinks">{link_html}</div>')
    if not any(init_links.get(k) for k in ("flight", "hotel", "ticket", "transfer")):
        body = body.replace('<p class="sc-nolink" id="scNoLink" hidden></p>',
                            '<p class="sc-nolink" id="scNoLink">이 도시는 제휴 예약 링크 없이 날씨·경비 기준만 제공합니다. 위 계절 가이드와 아래 같은 달 비교표에서 연결된 대안 도시를 보세요.</p>')

    payload_cities = []
    for c in cities:
        cc = dict(c)
        cc["links"] = season_links(c)
        payload_cities.append(cc)
    payload = json.dumps(
        {"updated": data["updated"], "lead": data.get("lead"), "filters": filt, "ui": ui, "cities": payload_cities},
        ensure_ascii=False, separators=(",", ":"),
    ).replace("</", "<\\/")
    body = body.replace("<!-- @SC_DATA -->", f'<script type="application/json" id="scData">{payload}</script>')

    faq = [
        ("오사카·도쿄는 언제가 가장 싼가요?",
         "1월 중순~2월 초와 6월 장마철입니다. 벚꽃·골든위크·오봉·연말에는 같은 항공권이 1.5~2배가 됩니다."),
        ("12월에 따뜻한 곳은 어디인가요?",
         "12월 평년 평균기온은 방콕 27.3도, 싱가포르 26.8도, 나트랑 24.7도, 다낭·호이안 22.2도 순입니다. 같은 12월에 서울은 0.2도, 강릉 3.3도입니다."),
        ("유럽 4개 도시는 언제 가야 하나요?",
         "파리·런던은 7~8월(파리 20.9도·비 7.4일, 런던 19.0도·비 7.9일), 로마·바르셀로나는 9월(로마 21.9도, 바르셀로나 22.1도)이 균형이 좋습니다."),
        ("서울·강릉·경주는 항공권 가격이 왜 없나요?",
         "국내 구간이라 KTX·고속버스 기준으로 적었습니다. 서울 왕복 5만~12만 원, 서울→강릉 KTX 2만 6,000원, 서울→신경주 KTX 4만 2,000원입니다."),
        ("다낭 우기 9~12월은 피해야 하나요?",
         "10~11월은 한 달에 20일 비가 오고 450~630mm가 내립니다. 9월과 12월은 가격이 30% 이상 낮아 리조트 휴양이면 선택지가 됩니다."),
        ("쾌적도 점수는 어떻게 계산했나요?",
         "기온(20~26도 만점) 55% + 강수 45% - 혼잡 감점(성수기 -12, 준성수기 -4)의 0~100점입니다. 순위보다 평균기온·비 온 날을 먼저 보세요."),
    ]
    jsonld = _page_jsonld(
        "calendar.html",
        "트립픽 월별 시즌·최저가 캘린더",
        "서울·부산·제주·강릉·경주·여수·오사카·도쿄·후쿠오카·타이베이·홍콩·다낭·나트랑·방콕·싱가포르·파리·런던·로마·바르셀로나 19개 도시의 1~12월 기온·강수량·성수기와 항공권 참고 가격대를 비교하는 캘린더.",
        base,
        faq,
        [("트립픽", ""), ("월별 시즌 캘린더", None)],
    )
    return page(
        out_root,
        "calendar.html",
        title="월별 여행 시즌 캘린더 — 19개 도시 12개월 날씨·성수기·항공권 가격대 | 트립픽",
        desc="서울·부산·제주·오사카·도쿄·타이베이·다낭·방콕·파리·런던 등 19개 도시의 1~12월 평균기온·강수량·비 온 날·성수기와 항공권 가격대를 비교합니다. 그 달의 항공·숙소·투어로 이어집니다.",
        body=body,
        base=base,
        active="calendar",
        keywords="여행 성수기, 비수기, 서울 날씨, 부산 날씨, 홍콩 날씨, 싱가포르 우기, 파리 날씨, 런던 날씨, 유럽 여행 시기, 벚꽃 시기, 단풍 시기, 설경 여행지, 항공권 예약 시점",
        jsonld=jsonld,
    )


# ----------------------------------------------------------------------
# sitemap
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# /stays — v23: 국내·해외 테마별 찐숙소 + 가이드 연결
# ----------------------------------------------------------------------
def _stays_region_by_id() -> dict:
    return {r["id"]: r for r in STAYS.get("regions", [])}


STAY_TYPE_ORDER = ["hotel", "resort", "onsen", "value", "hostel"]
STAY_TYPE_CHIP = {"hotel": "호텔", "resort": "리조트·풀빌라", "onsen": "온천 료칸", "value": "가성비", "hostel": "호스텔"}
STAY_THEME_ORDER = ["pool", "ocean", "onsen", "station", "value", "villa"]
# v50: /stays 는 첫 화면에 STAY_CHUNK곳만 그리고 나머지는 「더 보기」·스크롤로 이어 붙인다
STAY_CHUNK = 24

# v26: /stays 권역별 보기 — 국내 숙소를 권역으로 묶어 한눈에 고른다
STAY_GROUPS = [
    ("metro", "수도권", "서울·인천·가평"),
    ("gangwon", "강원", "춘천·강릉·속초·양양"),
    ("gyeong", "경상", "부산·경주·통영·거제"),
    ("jeolla", "전라", "여수·전주"),
    ("jeju", "제주", "제주"),
]
STAY_REGION_GROUP = {
    "seoul": "metro", "incheon": "metro", "gapyeong": "metro",
    "chuncheon": "gangwon", "gangneung": "gangwon", "sokcho": "gangwon", "yangyang": "gangwon",
    "busan": "gyeong", "gyeongju": "gyeong", "tongyeong": "gyeong", "geoje": "gyeong",
    "yeosu": "jeolla", "jeonju": "jeolla",
    "jeju": "jeju",
}
STAY_GROUP_NAME = {g: n for g, n, _ in STAY_GROUPS}

# v31: /stays 카드의 국가 배지에 국기를 함께 표시한다(해외 지역만)
STAY_COUNTRY_ISO = {
    "osaka": "jp", "tokyo": "jp", "fukuoka": "jp",
    "danang": "vn", "nhatrang": "vn", "bangkok": "th", "taipei": "tw",
    "paris": "fr", "london": "gb", "rome": "it", "barcelona": "es",
    "sapporo": "jp", "singapore": "sg",
}


def stay_group_of(region: dict) -> str:
    if region.get("scope") != "kr":
        return "intl"
    return STAY_REGION_GROUP.get(region["id"], "intl")


def _stay_themes() -> list:
    return STAYS.get("themes") or [{"id": t, "name": STAY_TYPE_CHIP.get(t, t), "note": ""} for t in STAY_THEME_ORDER]


def _stay_theme_name() -> dict:
    return {t["id"]: t["name"] for t in _stay_themes()}


def _stay_score_class(score: float) -> str:
    if score >= 9.3:
        return " gold"
    if score >= 9.0:
        return " good"
    return ""


def _stay_subs(h: dict) -> str:
    sub = h.get("sub") or {}
    order = ["청결도", "위치", "서비스", "시설"]
    parts = [f'{name} <b>{sub[name]}</b>' for name in order if sub.get(name)]
    if not parts:
        return ""
    return f'<div class="sc-sub"><span>{h["reviews"]:,}개 리뷰</span>' + "".join(f"<span>{p}</span>" for p in parts) + "</div>"


def _stay_basis_short(h: dict) -> str:
    """카드용 짧은 조회 기준 — '11.20~21 조회'."""
    basis = h.get("priceBasis") or ""
    head = basis.split("·")[0].strip()
    if not head:
        return ""
    head = head.replace("2026-", "").replace("-", ".")
    return f"{head} 조회"


def _stay_tags(h: dict) -> str:
    names = _stay_theme_name()
    out = []
    for t in (h.get("themes") or [])[:2]:
        if t in names and t != "station":  # v41: 역·도보권은 결정 배지로 한 번만
            out.append(f'<span class="sc-theme t-{t}">{esc(names[t])}</span>')
    for p in (h.get("pointTags") or [])[:2]:
        out.append(f'<span class="sc-pt">{esc(p)}</span>')
    if not out:
        return ""
    return '<div class="sc-tags">' + "".join(out) + "</div>"


# ---------------------------------------------------------------- v41 결정 배지·찜·비교
def stay_badges(h: dict) -> list:
    """숙소 카드에 붙일 (문구, 클래스, 설명) — stays.json 에 있는 값만 쓴다."""
    out = []
    basis = h.get("priceBasis") or ""
    if "세금" in basis:
        out.append(("세금·봉사료 포함", "tax", basis))
    w = (h.get("sub") or {}).get("위치")
    try:
        if w and float(w) >= 9.2:
            out.append((f"위치 {w}", "ko", "트립닷컴 투숙객 위치 점수(10점 만점)"))
    except (TypeError, ValueError):
        pass
    if "station" in (h.get("themes") or []):
        out.append(("역·도보권", "now", "역·도보로 움직이기 편한 위치"))
    if "2인 총액" in basis:
        out.append(("2인 총액 기준", "warn", basis))
    return out[:3]


def stay_badges_html(h: dict) -> str:
    items = stay_badges(h)
    m = re.match(r"(\d{4}-\d{2}-\d{2})", h.get("priceBasis") or "")
    if m:
        d = B._date_badge(m.group(1))
        if d:
            items.append(d)
    if not items:
        return ""
    return '<div class="dbadges">' + "".join(
        f'<span class="db db--{c}" title="{esc(ti)}">{esc(x)}</span>' for x, c, ti in items
    ) + "</div>"


def stay_wish_item(h: dict, region: dict) -> str:
    basis = h.get("priceBasis") or ""
    label = "2인 총액" if "2인 총액" in basis else "1박"
    data = {
        "n": h["name"],
        "u": h["url"],
        "i": h["img"],
        "p": f'{label} {h["price"]:,}원~',
        "t": f'숙소 · {region.get("name", "")}',
        "pr": h["price"],
        "un": "1박",
        "ct": region.get("name", ""),
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def stays_compare_json() -> str:
    """v41 — /stays 「나란히 비교」 데이터(최대 3곳). 카드에 있는 값만 옮긴다."""
    names = {r["id"]: r for r in STAYS.get("regions", [])}
    theme_name = _stay_theme_name()
    items = {}
    for h in STAYS.get("hotels", []):
        r = names.get(h["region"], {})
        basis = h.get("priceBasis") or ""
        items["stay:" + str(h["id"])] = {
            "k": "stay",
            "n": h["name"],
            "im": h["img"],
            "u": h["url"],
            "sub": f'{r.get("name", "")} · {h.get("typeLabel", "")} · {h.get("star", "")}성',
            "p": h["price"],
            "pl": "1박·2인·세금 포함" if "2인 총액" not in basis else "2인 총액·세금 포함",
            "sc": h["score"],
            "rv": h["reviews"],
            "ss": h.get("sub") or {},
            "zone": h.get("zone") or "",
            "ac": h.get("access") or "",
            "th": [theme_name[x] for x in (h.get("themes") or []) if x in theme_name],
            "pt": (h.get("pointTags") or [])[:2],
            "basis": basis,
            "bd": [[x, c] for x, c, _ in stay_badges(h)],
            "cta": "트립닷컴에서 예약",
        }
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return ('<script type="application/json" id="tpCompare" data-kind="stay" data-max="3">'
            + payload + "</script>")


def compare_shell(title: str = "숙소 나란히 비교", hint: str = "1박 가격·평점·위치 기준") -> str:
    """홈과 같은 비교 바·모달 마크업(js: assets/tp-v41.js)."""
    return f"""<div class="cmp-bar" id="cmpBar" aria-label="비교 바구니">
  <div class="wrap">
    <div class="cb-list" id="cbList"></div>
    <div class="cb-act">
      <span class="cb-count" id="cbCount">0 / 3</span>
      <button class="cb-open" type="button" id="cbOpen" disabled>나란히 비교</button>
      <button class="cb-clear" type="button" id="cbClear">비우기</button>
    </div>
  </div>
</div>

<div class="cmp-modal" id="cmpModal" hidden>
  <div class="cmp-sheet" role="dialog" aria-modal="true" aria-labelledby="cmpTitle">
    <div class="cmp-head">
      <div><b id="cmpTitle">{title}</b> <span class="hint">{hint}</span></div>
      <span class="cmp-head-act">
        <button class="cmp-close" type="button" id="cmpClearAll">전체 비우기</button>
        <button class="cmp-close" type="button" id="cmpClose">닫기</button>
      </span>
    </div>
    <p class="cmp-scroll-hint">표는 좌우로 밀어서 볼 수 있어요 · 맨 왼쪽 열은 항목 이름입니다</p>
    <div class="cmp-scroll" id="cmpBody"></div>
  </div>
</div>"""


def build_search_index() -> dict:
    """v41 통합 퀵서치 색인 — 도시 30 · 가이드 85 · 숙소 102 · 투어 84 · 맛집 75.

    URL 은 Cloudflare Pages 가 200 으로 서빙하는 확장자 없는 주소다. 도시 허브가 없는
    도시는 홈의 그 도시 섹션(#id), 투어는 홈 카드(#t-id), 숙소는 지역 필터(/stays?region=),
    맛집은 홈 맛집 카드(#id — 그 도시 탭이 열린다)로 바로 간다.
    """
    tours_doc = load_json("tours.json")
    cities = tours_doc.get("cities", [])
    hubs = {h["slug"]: h for h in hub_list()}
    hub_of = {}
    for h in hub_list():
        for cid in (h.get("cityIds") or [h["slug"]]):
            hub_of[cid] = h["slug"]
    stay_regions = {r["id"]: r for r in STAYS.get("regions", [])}
    stay_count = {}
    for h in STAYS.get("hotels", []):
        stay_count[h["region"]] = stay_count.get(h["region"], 0) + 1

    def norm(s) -> str:
        return re.sub(r"\s+", " ", str(s or "")).strip().lower()

    items = []

    # v44 — 위기상황 SOS 도구 페이지. 응급 상황에서 '경찰' '병원' '대사관' 같은
    # 단어로도 닿게 색인 맨 앞에 둔다(검색 탭은 v43.js 의 KIND_ORDER 에 page 를 추가했다).
    items.append({
        "t": "여행 중 위기상황 SOS",
        "k": "page",
        "m": "10개국 경찰·구급·대사관 번호 · 현지어 카드",
        "u": "/sos",
        "q": norm("위기상황 응급 긴급 sos 경찰 구급 소방 대사관 영사콜센터 공관 여권 분실 지갑 휴대폰 병원 응급실 약국 통역 현지어 여행 중 아플 때 사고 신고"),
    })
    # 도시 30 — 허브가 있는 도시 먼저
    def city_n(c):
        return sum(1 for x in TOURS if x["city"] == c["id"])
    ordered = sorted(cities, key=lambda c: (0 if c["id"] in hub_of else 1, -city_n(c)))
    for c in ordered:
        slug = hub_of.get(c["id"])
        region = stay_regions.get(slug or c["id"])
        n_stay = stay_count.get(region["id"], 0) if region else 0
        cname = "국내" if c["country"] == "kr" else B.COUNTRY_NAME.get(c["country"], "")
        meta = f'{cname} · 투어 {city_n(c)}개' + (f" · 찐숙소 {n_stay}곳" if n_stay else "")
        items.append({
            "t": c["name"] + " 여행",
            "k": "city",
            "m": meta,
            "u": f"/{slug}" if slug else f'/#{c["id"]}',
            "q": norm(" ".join([c["name"], c["title"], c.get("tagline", ""), c.get("duration_note", ""),
                                hubs.get(slug, {}).get("keywords", "") if slug else ""])),
        })

    # 가이드 85
    extra = EXTRA.get("guides") or {}
    region_names = {r["code"]: r["name"] for r in (EXTRA.get("regions") or [])}
    for g in GUIDES_LIST:
        ex = extra.get(g["slug"]) or {}
        q = " ".join([
            g.get("navTitle", ""), strip_tags(g.get("h1", "")), g.get("dek", ""), g.get("keywords", ""),
            g.get("category", ""), " ".join(ex.get("tags") or []),
            " ".join(region_names.get(x, x) for x in (ex.get("regions") or [])), ex.get("takeaway") or "",
        ])
        items.append({
            "t": g["navTitle"],
            "k": "guide",
            "m": f'{g["category"]} · {g["read"]}분 · 최종 검증 {g["updated"].replace("-", ".")}',
            "u": f'/guides/{g["slug"]}',
            "q": norm(q)[:460],
        })

    # 숙소 102
    for r in STAYS.get("regions", []):
        for h in [x for x in STAYS.get("hotels", []) if x["region"] == r["id"]]:
            items.append({
                "t": h["name"],
                "k": "stay",
                "m": f'{r["name"]} · {h["score"]:.1f}점 · 리뷰 {h["reviews"]:,} · 1박 {h["price"]:,}원~',
                "u": f'/stays?region={r["id"]}',
                "q": norm(" ".join([h["name"], h.get("en", ""), r["name"], r.get("country", ""),
                                    h.get("zone", ""), h.get("access", ""), h.get("typeLabel", ""),
                                    h.get("reason", "")]))[:360],
            })

    # 투어 84
    for x in TOURS:
        unit = "1팀" if B.is_team_item(x) else "1인"
        items.append({
            "t": x["title"],
            "k": "tour",
            "m": f'{x.get("city_label", "")} · {unit} {x["sale"]:,}원~ · {x["type"]}',
            "u": f'/#t-{x["id"]}',
            "q": norm(" ".join([x["title"], x.get("city_label", ""), x.get("seller", ""), x["type"],
                                x.get("theme", ""), " ".join(x.get("tags") or [])]))[:320],
        })

    # 맛집 75
    for c in (RESTAURANTS.get("cities") or []):
        for it in c.get("items") or []:
            items.append({
                "t": f'{it["nameKo"]} ({it["name"]})',
                "k": "food",
                "m": f'{c["name"]} · {it["category"]} · {it["price"]}',
                "u": f'/#{it["id"]}',
                "q": norm(" ".join([it["name"], it["nameKo"], c["name"], it.get("area", ""),
                                    it.get("category", ""), it.get("dish", ""), it.get("tip", "")]))[:360],
            })

    return {"generated": "2026-11-22", "items": items}


def stays_card(h: dict, region: dict, group: str | None = None, hidden: bool = False) -> str:
    sub = _stay_subs(h)
    scope = region.get("scope", "intl")
    flag = "국내" if scope == "kr" else (region.get("country") or "해외")
    iso = STAY_COUNTRY_ISO.get(region.get("id", ""))
    flag_ic = f'<span class="sc-fl">{B.flag_svg(iso, 13, 9.1)}</span>' if (scope != "kr" and iso) else ""
    grp = group or stay_group_of(region)
    bud = "low" if h["price"] <= 100000 else ("mid" if h["price"] <= 200000 else "high")
    return f"""    <article class="scard"{' hidden' if hidden else ''}" data-region="{h['region']}" data-tp-city="{h['region']}" data-group="{grp}" data-scope="{scope}" data-type="{h['type']}" data-themes="{' '.join(h.get('themes') or [])}" data-score="{h['score']}" data-price="{h['price']}" data-budget="{bud}">
      <a class="sc-thumb" href="{esc(h['url'])}" target="_blank" rel="noopener sponsored" aria-label="{esc(h['name'])} 트립닷컴에서 보기">
        <img src="{esc(h['img'])}" alt="{esc(region['name'])} {esc(h['name'])} 숙소 사진" width="720" height="480" loading="lazy" />
        <span class="sc-score{_stay_score_class(h['score'])}">{h['score']:.1f}</span>
        <span class="sc-type">{esc(h['typeLabel'])}</span>
      </a>
      <div class="sc-body">
        <div class="sc-top"><span class="sc-region">{esc(region['name'])} <i class="sc-flag{' kr' if scope == 'kr' else ''}">{flag_ic}{esc(flag)}</i></span><i></i><span>{h['star']}성</span></div>
        <h3><a href="{esc(h['url'])}" target="_blank" rel="noopener sponsored">{esc(h['name'])}</a></h3>
        {stay_badges_html(h)}
        <p class="sc-loc"><svg aria-hidden="true"><use href="#i-pin"/></svg><span>{esc(h['access'])}</span></p>
        <p class="sc-reason">{esc(h['reason'])}</p>
        {_stay_tags(h)}
        {sub}
        <div class="sc-acts">
          <button class="cmp-btn" type="button" data-cmp-add="stay:{h['id']}" aria-pressed="false" title="이 숙소를 비교 바구니에 담기">비교</button>
          <button class="wish-btn" type="button" data-wish="stay:{h['id']}" data-wish-item="{esc(stay_wish_item(h, region))}" aria-pressed="false" aria-label="찜하기" title="찜하기">
            <svg aria-hidden="true"><use href="#i-heart"/></svg><span class="wish-t">찜</span>
          </button>
        </div>
        <div class="sc-foot">
          <span class="sc-price"><b>{h['price']:,}원</b>1박~ <em class="sc-basis">{_stay_basis_short(h)}</em></span>
          <a class="sc-cta" href="{esc(h['url'])}" target="_blank" rel="noopener sponsored">예약 <span class="sc-ext">트립닷컴</span> <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
        </div>
      </div>
    </article>"""


def stays_jsonld(base: str, groups: list) -> str:
    b = base.rstrip("/")
    items = []
    for i, (region, hotels) in enumerate(groups, 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "ItemList",
                "name": f"{region['name']} 숙소 추천",
                "numberOfItems": len(hotels),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": j,
                        "item": {
                            "@type": "Hotel",
                            "name": h["name"],
                            "address": {"@type": "PostalAddress", "addressLocality": region["name"]},
                            "starRating": {"@type": "Rating", "ratingValue": h["star"]},
                            "aggregateRating": {
                                "@type": "AggregateRating",
                                "ratingValue": h["score"],
                                "reviewCount": h["reviews"],
                                "bestRating": 10,
                                "worstRating": 1,
                            },
                            "url": h["url"],
                        },
                    }
                    for j, h in enumerate(hotels, 1)
                ],
            },
        })
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"국내·해외 테마별 찐숙소 추천 {sum(len(h) for _, h in groups)}곳 | 트립픽",
        "description": "국내 " + "·".join(r["name"] for r, _ in groups if r.get("scope") == "kr") + f" {sum(len(h) for r, h in groups if r.get('scope') == 'kr')}곳과 해외 {len([1 for r, _ in groups if r.get('scope') != 'kr'])}개 도시 {sum(len(h) for r, h in groups if r.get('scope') != 'kr')}곳, 숙소 {sum(len(h) for _, h in groups)}곳을 트립닷컴 평점·리뷰 수·1박 최저가로 비교하고, 권역(수도권·강원·경상·전라·제주)과 테마(호캉스·오션뷰·온천·역세권·가성비·가족)로 골라 도시 가이드로 이어집니다.",
        "url": f"{b}/stays",
        "isPartOf": {"@type": "WebSite", "name": "트립픽", "url": f"{b}/"},
        "mainEntity": {"@type": "ItemList", "numberOfItems": sum(len(h) for _, h in groups), "itemListElement": items},
    }
    return json.dumps(data, ensure_ascii=False)


def _stay_guide_links(region: dict) -> str:
    """지역 → 도시 허브·가이드·트립닷컴 목록으로 이어지는 링크 묶음."""
    links = []
    hub = region.get("hub")
    if hub:
        links.append(f'<a class="sg-go hub" href="{hub}.html">{esc(region["name"])} 도시 가이드 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>')
    for g in region.get("guides") or []:
        slug = g.get("slug") if isinstance(g, dict) else g
        label = (g.get("label") if isinstance(g, dict) else None) or slug
        if not slug:
            continue
        links.append(f'<a class="sg-go" href="guides/{esc(slug)}.html">{esc(label)} <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>')
    if not links:
        links.append('<a class="sg-go" href="guides/index.html">국내 여행 가이드 모아보기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>')
    if region.get("listUrl"):
        links.append(f'<a class="sg-go trip" href="{esc(region["listUrl"])}" target="_blank" rel="noopener sponsored">트립닷컴 {esc(region["name"])} 숙소 전체 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>')
    return "".join(links)


STAYS_GUIDE_REGION = [
    # v27: 국내 4개 지역 가이드 — slug에 지역명이 들어가는 순서대로 먼저 잡는다
    ("sokcho", "sokcho"), ("yangyang", "yangyang"), ("jeonju", "jeonju"),
    ("tongyeong", "tongyeong"), ("geoje", "geoje"), ("incheon", "incheon"),
    ("osaka", "osaka"), ("tokyo", "tokyo"), ("fukuoka", "fukuoka"), ("yufuin", "fukuoka"),
    ("danang", "danang"), ("hoian", "danang"), ("nhatrang", "nhatrang"), ("dalat", "nhatrang"),
    ("bangkok", "bangkok"), ("taipei", "taipei"), ("yehliu", "taipei"), ("jiufen", "taipei"),
    ("sapporo", "sapporo"), ("singapore", "singapore"), ("okinawa", "okinawa"),
    ("jeju", "jeju"), ("busan", "busan"), ("gangwon", "gangneung"), ("ulleung", "gangneung"),
    ("seoul", "seoul"), ("yeosu", "yeosu"), ("gyeongju", "gyeongju"),
]
STAYS_GUIDE_THEME = {"winter": "onsen", "esim": "station", "packing": "value", "powerbank": "value"}


def guide_stays_box(g: dict) -> str:
    """가이드 → /stays 지역·테마 연결 박스(v23). 지역을 알 수 없으면 테마로 잇는다."""
    regions = {r["id"]: r for r in STAYS.get("regions", [])}
    hotels = STAYS.get("hotels", [])
    slug = g.get("slug", "")
    ex = guide_extra(slug)
    # v27: 한 가이드가 두 지역(속초·양양)을 묶을 때는 stayRegions 로 지정한다
    target_ids = [rid for rid in (ex.get("stayRegions") or []) if rid in regions]
    if not target_ids:
        for key, rid in STAYS_GUIDE_REGION:
            if key in slug and rid in regions:
                target_ids = [rid]
                break
    target_ids = [rid for rid in target_ids if any(h["region"] == rid for h in hotels)]
    theme = None
    for key, tid in STAYS_GUIDE_THEME.items():
        if key in slug:
            theme = tid
            break
    if not target_ids and not theme:
        theme = "ocean"
    names = {t["id"]: t["name"] for t in (STAYS.get("themes") or [])}
    rows = []
    for rid in target_ids:
        r = regions[rid]
        n = sum(1 for h in hotels if h["region"] == rid)
        rows.append(
            f'<a class="gsb-go" href="../stays.html#{r["id"]}"><b>{esc(r["name"])} 찐숙소 {n}곳</b>'
            f'<span>평점·리뷰 수·1박 최저가로 고른 숙소 — 최고 평점 {esc(r["top"])}</span></a>'
        )
    if theme:
        cnt = sum(1 for h in hotels if theme in (h.get("themes") or []))
        rows.append(
            f'<a class="gsb-go" href="../stays.html?theme={theme}"><b>{esc(names.get(theme, theme))} 숙소 {cnt}곳</b>'
            f'<span>같은 테마로 국내·해외 숙소를 한 번에 비교</span></a>'
        )
    if not rows:
        return ""
    return ('<div class="gsb"><b class="gsb-t">이 글의 일정에 묵을 숙소</b>'
            '<div class="gsb-rows">' + "".join(rows) + "</div>"
            '<p class="gsb-note">숙소 사진·평점·가격은 트립닷컴 조회값이고, 예약은 트립닷컴 제휴 링크로 이어집니다.</p></div>')


def stays_page(out_root: Path, base: str) -> Path:
    regions = STAYS.get("regions", [])
    hotels = STAYS.get("hotels", [])
    groups = [(r, [h for h in hotels if h["region"] == r["id"]]) for r in regions if any(h["region"] == r["id"] for h in hotels)]
    total = sum(len(h) for _, h in groups)
    kr_groups = [(r, hs) for r, hs in groups if r.get("scope") == "kr"]
    intl_groups = [(r, hs) for r, hs in groups if r.get("scope") != "kr"]
    kr_total = sum(len(hs) for _, hs in kr_groups)
    intl_total = sum(len(hs) for _, hs in intl_groups)
    _std = [h for h in hotels if "2인 총액" not in (h.get("priceBasis") or "")]
    price_min = min(h["price"] for h in _std)
    price_max = max(h["price"] for h in _std)
    score_min = min(h["score"] for h in hotels)
    score_max = max(h["score"] for h in hotels)
    source = STAYS.get("source", {})
    themes = _stay_themes()
    theme_name = _stay_theme_name()
    theme_note = {t["id"]: t.get("note", "") for t in themes}

    region_chips = "".join(
        f'<button class="gf-chip" type="button" data-region="{r["id"]}">{esc(r["name"])} <span>{len(hs)}</span></button>'
        for r, hs in kr_groups + intl_groups
    )
    # v26: 권역별 보기 — 국내 숙소를 수도권·강원·경상·전라·제주로 묶는다
    group_rows = []
    for gid, gname, gsub in STAY_GROUPS:
        grs = [(r, hs) for r, hs in kr_groups if STAY_REGION_GROUP.get(r["id"]) == gid]
        if not grs:
            continue
        ghotels = [h for _, hs in grs for h in hs]
        gstd = [h for h in ghotels if "2인 총액" not in (h.get("priceBasis") or "")]
        group_rows.append({
            "id": gid, "name": gname, "sub": gsub, "n": len(ghotels),
            "regions": grs,
            "min": min(h["price"] for h in (gstd or ghotels)),
            "max": max(h["price"] for h in (gstd or ghotels)),
            "score": max(h["score"] for h in ghotels),
        })
    group_chips = "".join(
        f'<button class="gf-chip" type="button" data-group="{g["id"]}">{esc(g["name"])} <span>{g["n"]}</span></button>'
        for g in group_rows
    )
    intl_chip = (f'<button class="gf-chip" type="button" data-group="intl">해외 <span>{intl_total}</span></button>'
                 if intl_total else "")
    group_cards = "".join(
        f'<a class="sg-group" href="stays.html?group={g["id"]}">'
        f'<span class="sg-group-k">{esc(g["name"])}</span>'
        f'<b>{g["n"]}곳 <span>1박 {g["min"]:,}~{g["max"]:,}원</span></b>'
        f'<em>{"·".join(esc(r["name"]) + " " + str(len(hs)) for r, hs in g["regions"])} · 최고 평점 {g["score"]:.1f}</em></a>'
        for g in group_rows
    )
    theme_chips = "".join(
        f'<button class="gf-chip" type="button" data-theme="{t}">{esc(theme_name[t])} '
        f'<span>{sum(1 for h in hotels if t in (h.get("themes") or []))}</span></button>'
        for t in STAY_THEME_ORDER if t in theme_name
    )
    cards = []
    _seen = 0
    for r, hs in groups:
        for h in hs:
            cards.append(stays_card(h, r, STAY_REGION_GROUP.get(r["id"]) if r.get("scope") == "kr" else "intl",
                                     hidden=_seen >= STAY_CHUNK))
            _seen += 1

    region_anchors = "".join(f'<span id="{r["id"]}"></span>' for r, _ in groups)
    region_links = "".join(
        f'<a class="sr-gitem" href="#{r["id"]}" data-jump="{r["id"]}">'
        f'<b>{esc(r["name"])} <span>{len(hs)}곳</span>{" <i class=\'sr-kr\'>국내</i>" if r.get("scope") == "kr" else ""}</b>'
        f'<span class="sr-range">1박 {min(h["price"] for h in hs if "2인 총액" not in (h.get("priceBasis") or "")):,}~{max(h["price"] for h in hs if "2인 총액" not in (h.get("priceBasis") or "")):,}원 · 평점 {min(h["score"] for h in hs):.1f}~{max(h["score"] for h in hs):.1f}</span>'
        f'<em>{esc(r["note"])}</em></a>'
        for r, hs in groups
    )
    theme_cards = "".join(
        f'<a class="th-card" href="stays.html?theme={t}">'
        f'<b>{esc(theme_name[t])}</b>'
        f'<span>{sum(1 for h in hotels if t in (h.get("themes") or []))}곳</span>'
        f'<em>{esc(theme_note.get(t, ""))}</em></a>'
        for t in STAY_THEME_ORDER if t in theme_name
    )
    guide_cards = "".join(
        f'<div class="sg-card{" kr" if r.get("scope") == "kr" else ""}">'
        f'<div class="sg-head"><b>{esc(r["name"])}</b><span>{len(hs)}곳 · 최고 평점 {max(h["score"] for h in hs):.1f}</span></div>'
        f'<div class="sg-links">{_stay_guide_links(r)}</div></div>'
        for r, hs in groups
    )
    kr_names = " / ".join(r["name"] for r, _ in kr_groups)
    intl_names = " / ".join(r["name"] for r, _ in intl_groups)
    kr_region_n = len(kr_groups)
    intro = (
        '<div><b>평점은 리뷰 수와 같이</b><p>트립닷컴 투숙객 리뷰 10점 만점 점수입니다. 리뷰가 수백 개 쌓인 곳과 신규 오픈으로 수십 개인 곳을 구분해 리뷰 수를 카드에 같이 적었습니다.</p></div>'
        f'<div><b>국내 {kr_total}곳 · 해외 {intl_total}곳</b><p>국내는 {kr_names} {kr_total}곳(2026-11-20~22 조회), 해외는 {intl_names} {intl_total}곳(2026-11-19~21 조회)입니다.</p></div>'
        '<div><b>예약은 트립닷컴에서</b><p>카드의 예약 버튼은 그 숙소의 트립닷컴 페이지로 바로 갑니다. 결제·취소는 트립닷컴 약관을 따릅니다.</p></div>'
    )

    # v39: 예산대 필터 — 1박 가격(2인·세금 포함)으로 10만 이하 / 10~20만 / 20만 이상
    bud_n = {"low": sum(1 for h in hotels if h["price"] <= 100000),
             "mid": sum(1 for h in hotels if 100000 < h["price"] <= 200000),
             "high": sum(1 for h in hotels if h["price"] > 200000)}
    budget_chips = "".join(
        f'<button class="gf-chip{" on" if bid == "all" else ""}" type="button" data-budget="{bid}">{label} <span>{bud_n[bid] if bid != "all" else total}</span></button>'
        for bid, label in (("all", "전체"), ("low", "10만 원 이하"), ("mid", "10~20만 원"), ("high", "20만 원 이상"))
    )

    body = f"""<div class="pg-hero stays-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><b>찐숙소</b></nav>
    <span class="pg-kicker">TRIPPICK STAYS · 국내 {kr_region_n}개 지역 + 해외 {len(intl_groups)}개 도시 {total}곳</span>
    <div class="pg-head">
      <h1><em>찐숙소</em> {total}곳 — 권역으로 고르고, 예산·테마로 좁힙니다</h1>
      <p class="dek">국내 {kr_region_n}개 지역 {kr_total}곳({kr_names})과 해외 {len(intl_groups)}개 도시 {intl_total}곳, <b>국내·해외 {len(groups)}개 지역 {total}곳</b>을 한 화면에 올렸습니다.
      <b>수도권·강원·경상·전라·제주</b> 권역으로 먼저 묶어 보고, <b>1박 10만 원 이하·10~20만·20만 원 이상</b> 예산대로 걸러 본 뒤, 호캉스·수영장, 오션뷰, 온천·스파, 역세권·도보, 가성비, 가족·풀빌라 테마로 다시 좁힐 수 있습니다. 정렬은 <b>추천순·가격 낮은순·평점 높은순</b>입니다.
      평점 <b>{score_min:.1f}~{score_max:.1f}</b>, 1박 <b>{price_min:,}~{price_max:,}원</b> 구간이고, 평점·리뷰 수·가격은 트립닷컴 목록의 실제 값을 그대로 옮겼습니다.</p>
      <div class="pg-meta">
        <span><b>트립픽 숙소 편집</b></span><i></i>
        <span>{total}곳 · {len(groups)}개 지역</span><i></i>
        <span>가격 확인 {source.get('checked', '2026-11-20').replace('-', '.')}</span><i></i>
        <span>1박·2인·세금 포함</span>
      </div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
{share_row('stays')}
{cont_bar('숙소', '찐숙소 ' + str(total) + '곳 — 테마별 숙소 비교', '/stays', 'images/og/stays.jpg')}
    <div class="sf" id="sf">
      <div class="sf-row">
        <div class="sf-scope" role="group" aria-label="국내·해외">
          <button class="gf-chip on" type="button" data-scope="all">전체 <span>{total}</span></button>
          <button class="gf-chip" type="button" data-scope="kr">국내 <span>{kr_total}</span></button>
          <button class="gf-chip" type="button" data-scope="intl">해외 <span>{intl_total}</span></button>
        </div>
        <button class="sf-fold" type="button" id="sfFold" aria-expanded="false">지역 선택 <i>▾</i></button>
        <div class="sf-chips sf-regionchips" role="group" aria-label="지역 선택">
          <button class="gf-chip on" type="button" data-region="all">지역 전체</button>
          {region_chips}
        </div>
      </div>
      <div class="sf-row sf-row--groups">
        <div class="sf-chips" role="group" aria-label="권역">
          <span class="sf-label">권역</span>
          <button class="gf-chip on" type="button" data-group="all">권역 전체</button>
          {group_chips}
          {intl_chip}
        </div>
      </div>
      <div class="sf-row">
        <div class="sf-chips" role="group" aria-label="테마">
          <button class="gf-chip on" type="button" data-theme="all">테마 전체</button>
          {theme_chips}
        </div>
      </div>
      <div class="sf-row sf-row--budget">
        <div class="sf-chips" role="group" aria-label="예산대">
          <span class="sf-label">예산</span>
          {budget_chips}
        </div>
        <div class="sf-sort" role="group" aria-label="정렬">
          <button class="gf-chip on" type="button" data-sort="rec">추천순</button>
          <button class="gf-chip" type="button" data-sort="price">가격 낮은 순</button>
          <button class="gf-chip" type="button" data-sort="score">평점 높은 순</button>
        </div>
        <span class="sf-count"><b id="sfCount">{total}</b>곳</span>
      </div>
    </div>

    <div class="stays-intro">{intro}</div>
    <div class="sf-anchors" aria-hidden="true">{region_anchors}</div>

    <div class="sgrid" id="sgrid">
{chr(10).join(cards)}
    </div>

    <div class="sgrid-more" id="sfMoreWrap">
      <span class="sf-more-note" id="sfMoreNote">{total}곳 중 {min(STAY_CHUNK, total)}곳 표시</span>
      <button type="button" id="sfMore">숙소 {min(STAY_CHUNK, total)}곳 더 보기</button>
      <span class="sf-more-hint">아래로 스크롤하면 자동으로 이어집니다</span>
    </div>

    <div class="gfind-empty" id="sfEmpty" hidden>
      <b>조건에 맞는 숙소가 없습니다.</b>
      <p>국내/해외·지역·테마·예산을 ‘전체’로 바꿔 보세요. 예산대는 1박 10만 원 이하·10~20만 원·20만 원 이상, 테마는 호캉스·수영장, 오션뷰, 온천·스파, 역세권·도보, 가성비, 가족·풀빌라 여섯 가지입니다.</p>
      <button type="button" id="sfReset">필터 초기화</button>
    </div>

    <h2 class="sr-h2">테마로 바로 보기</h2>
    <div class="th-grid" aria-label="테마 바로가기">
      {theme_cards}
    </div>

    <h2 class="sr-h2">권역별로 이렇게 갈립니다</h2>
    <p class="sr-dek">국내 숙소를 수도권(서울·인천·가평) · 강원(춘천·강릉·속초·양양) · 경상(부산·경주·통영·거제) · 전라(여수·전주) · 제주로 묶었습니다. 권역을 누르면 그 안의 숙소만 남고, 지역 카드를 누르면 그 도시만 남습니다.</p>
    <div class="sg-groups" aria-label="권역 바로가기">
      {group_cards}
    </div>

    <h2 class="sr-h2">지역별로 이렇게 갈립니다</h2>
    <div class="sr-regions" aria-label="지역 바로가기">
      {region_links}
    </div>

    <h2 class="sr-h2">숙소를 골랐으면 — 그 도시 동선과 예약</h2>
    <p class="sr-dek">숙소 위치를 정한 뒤에는 그 도시의 코스·맛집·교통 가이드로 이어서 보세요. 국내는 서울·인천·영종도·가평·춘천·강릉·속초·양양·전주·부산·경주·통영·거제·여수·제주 모두 가이드로 이어지고, 숙소 카드에서 바로 그 도시 동선으로 넘어갈 수 있습니다.</p>
    <div class="sg-grid" aria-label="지역별 가이드 연결">
      {guide_cards}
    </div>

    <div class="sr-band">
      <div><b>이 도시 전체 숙소를 날짜 넣고 비교하려면</b>
        <p>트립닷컴 도시 숙소 목록에서 체크인 날짜·인원을 넣으면 그날 요금으로 정렬됩니다. 카드의 예약 버튼은 숙소 한 곳으로 바로 갑니다.</p></div>
      <a class="btn-line" href="cities/index.html">도시별 여행 페이지 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </div>

    <p class="snote"><b>숫자 읽는 법</b> — 평점은 트립닷컴 투숙객 리뷰 10점 만점 기준이고, 옆의 리뷰 수와 함께 봐야 합니다.
    가격은 카드에 적힌 조회 날짜의 <b>1박, 성인 2명, 세금·서비스비용 포함</b> 최저가입니다(국내 {kr_total}곳 2026-11-20~22, 해외 {intl_total}곳 2026-11-19~21). 권역 버튼은 국내 숙소만 묶습니다.
    같은 숙소도 날짜·객실·잔여 상황에 따라 달라지므로 결제 직전 트립닷컴 결제 화면의 금액을 최종으로 확인하세요. 숙소 사진은 트립닷컴 숙소 페이지 이미지입니다.</p>

    <p class="snote"><b>제휴 고지</b> — 이 페이지의 예약 버튼은 트립닷컴 파트너스 제휴 링크입니다.
    예약이 이루어지면 트립픽이 트립닷컴으로부터 수수료를 받을 수 있으며, 구매자가 지불하는 금액에는 영향이 없습니다.
    숙소 선정과 순서는 평점·리뷰 수·위치를 기준으로 편집했고, 수수료율에 따라 배열하지 않았습니다.</p>

{share_row('stays')}
  </div>
</div>
{stays_filter_script()}
{compare_shell()}
{stays_compare_json()}"""

    return page(
        out_root,
        "stays.html",
        title=f"찐숙소 {total}곳 — 10만 원 이하·10~20만 예산별 비교 (2026) | 트립픽",
        desc=(
            f"국내 {kr_total}곳·해외 {intl_total}곳 숙소 {total}곳을 트립닷컴 평점·리뷰 수·1박 최저가(세금 포함)로 비교했습니다. "
            f"평점 {score_min:.1f}~{score_max:.1f}, 1박 {price_min:,}~{price_max:,}원. 10만 원 이하·테마 필터, 2026-11-22 확인."
        ),
        keywords=(
            "국내 호텔 추천, 서울 호텔, 인천 호텔, 영종도 호텔, 가평 호텔, 춘천 호텔, 남이섬 호텔, 부산 호텔, 강릉 호텔, 속초 호텔, 양양 호텔, 전주 호텔, 통영 호텔, 거제 호텔, 거제 오션뷰 호텔, 여수 호텔, 경주 호텔, 오션뷰 호텔, 호캉스 호텔, 온천 호텔, "
            "가성비 호텔, 가족 호텔, 풀빌라, 10만원 이하 호텔, 부산 호텔 가격, 오사카 호텔 추천, 도쿄 호텔 추천, 다낭 리조트 추천, 제주 호텔 추천, 파리 호텔 추천, 런던 호텔 추천, 로마 호텔 추천, 바르셀로나 호텔 추천, 싱가포르 호텔 추천, 삿포로 호텔 추천, 유럽 호텔, 트립닷컴 숙소"
        ),
        body=body,
        base=base,
        active="stays",
        og_image=f"{base.rstrip('/')}/images/og/stays.jpg",
        og_image_alt=f"국내·해외 {len(groups)}개 지역 찐숙소 {total}곳 — 트립픽",
        og_image_size=(1200, 630),
        jsonld=f'<script type="application/ld+json">{stays_jsonld(base, groups)}</script>\n'
        + graph_ld(org_ld(base), website_ld(base),
                   breadcrumb_ld(base, [("트립픽", "/"), ("찐숙소", None)])),
        inline_css=True,
    )


def stays_filter_script() -> str:
    return """<script>
(function(){
  var grid = document.getElementById('sgrid');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.scard'));
  var countEl = document.getElementById('sfCount');
  var emptyEl = document.getElementById('sfEmpty');
  var scopeBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-scope [data-scope]'));
  var regionBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-chips [data-region]'));
  var groupBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-chips [data-group]'));
  var themeBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-chips [data-theme]'));
  var budgetBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-row--budget [data-budget]'));
  var sortBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-sort [data-sort]'));
  /* v39: 추천순은 편집 순서(원래 DOM 순서)를 그대로 쓴다. */
  cards.forEach(function(c, i){ c.setAttribute('data-rec', i); });
  var state = { scope: 'all', group: 'all', region: 'all', theme: 'all', budget: 'all', sort: 'rec' };

  var CHUNK = 24;
  var shownAll = [];
  var limit = CHUNK;
  var moreWrap = document.getElementById('sfMoreWrap');
  var loadIO = null;
  var moreBtn = document.getElementById('sfMore');
  var moreNote = document.getElementById('sfMoreNote');

  /* v50: 처음 CHUNK곳만 그린다(직접 108곳을 그리면 모바일 LCP가 늦어짐). 더 보기·스크롤로 이어 붙인다. */
  function draw(){
    var take = shownAll.slice(0, limit);
    cards.forEach(function(c){ c.hidden = true; });
    take.forEach(function(c){ c.hidden = false; grid.appendChild(c); });
    countEl.textContent = shownAll.length;
    emptyEl.hidden = shownAll.length > 0;
    if (moreWrap){
      var rest = shownAll.length - take.length;
      moreWrap.hidden = rest <= 0;
      if (moreBtn) moreBtn.textContent = '숙소 ' + Math.min(CHUNK, rest) + '곳 더 보기';
      if (moreNote) moreNote.textContent = shownAll.length + '곳 중 ' + take.length + '곳 표시';
    }
    /* v50: 「더 보기」 블록이 아니라 '마지막 카드'를 지켜본다.
       블록을 지켜보면 카드가 위에 붙으면서 버튼이 화면 밖으로 밀려 내려가 스크롤이 튄다. */
    if (loadIO) { loadIO.disconnect(); loadIO = null; }
    if ('IntersectionObserver' in window && shownAll.length > limit) {
      var last = take[take.length - 1];
      if (last) {
        loadIO = new IntersectionObserver(function(es){
          for (var i = 0; i < es.length; i++) if (es[i].isIntersecting) { loadIO.disconnect(); loadIO = null; more(false); return; }
        }, { rootMargin: '700px 0px' });
        loadIO.observe(last);
      }
    }
  }
  function more(manual){
    if (shownAll.length <= limit) return;
    var prev = limit;
    limit += CHUNK;
    draw();
    /* 버튼으로 눌렀을 때는 새로 붙은 첫 카드로 이동해 '아무 일도 안 일어난' 느낌을 없앤다 */
    if (manual && shownAll[prev] && shownAll[prev].scrollIntoView) {
      shownAll[prev].scrollIntoView({ block: 'start' });
    }
  }
  if (moreBtn) moreBtn.addEventListener('click', function(){ more(true); });

  function scoreOf(c){ return parseFloat(c.getAttribute('data-score')) || 0; }
  function priceOf(c){ return parseInt(c.getAttribute('data-price'), 10) || 0; }
  function recOf(c){ return parseInt(c.getAttribute('data-rec'), 10) || 0; }
  function themesOf(c){ return (c.getAttribute('data-themes') || '').split(' ').filter(Boolean); }
  function budgetOf(c){ return c.getAttribute('data-budget') || 'high'; }

  function render(sync, keepLimit){
    var shown = cards.filter(function(c){
      var okS = state.scope === 'all' || c.getAttribute('data-scope') === state.scope;
      var okG = state.group === 'all' || c.getAttribute('data-group') === state.group;
      var okR = state.region === 'all' || c.getAttribute('data-region') === state.region;
      var okT = state.theme === 'all' || themesOf(c).indexOf(state.theme) >= 0;
      var okB = state.budget === 'all' || budgetOf(c) === state.budget;
      return okS && okG && okR && okT && okB;
    });
    shown.sort(function(a, b){
      if (state.sort === 'price') return priceOf(a) - priceOf(b);
      if (state.sort === 'score') return scoreOf(b) - scoreOf(a) || priceOf(a) - priceOf(b);
      return recOf(a) - recOf(b);
    });
    shownAll = shown;
    if (!keepLimit) limit = CHUNK;
    draw();
    if (sync !== false && window.history && history.replaceState){
      var p = [];
      if (state.scope !== 'all') p.push('scope=' + state.scope);
      if (state.group !== 'all') p.push('group=' + state.group);
      if (state.region !== 'all') p.push('region=' + state.region);
      if (state.theme !== 'all') p.push('theme=' + state.theme);
      if (state.budget !== 'all') p.push('budget=' + state.budget);
      if (state.sort !== 'rec') p.push('sort=' + state.sort);
      var url = location.pathname + (p.length ? '?' + p.join('&') : '');
      history.replaceState(null, '', url);
    }
    if (typeof syncFold === 'function') syncFold();
  }

  function mark(btns, el){
    btns.forEach(function(b){ b.classList.toggle('on', b === el); });
  }
  function bind(btns, key, attr){
    btns.forEach(function(btn){
      btn.addEventListener('click', function(){
        mark(btns, btn);
        state[key] = btn.getAttribute(attr);
        syncAfter(key, btn);
      });
    });
  }
  bind(scopeBtns, 'scope', 'data-scope');
  bind(regionBtns, 'region', 'data-region');
  bind(groupBtns, 'group', 'data-group');
  bind(themeBtns, 'theme', 'data-theme');
  bind(budgetBtns, 'budget', 'data-budget');
  bind(sortBtns, 'sort', 'data-sort');

  /* v26: 권역·지역·국내/해외가 서로 어긋나 빈 화면이 되지 않게 맞춰 줍니다. */
  function groupOfRegion(id){
    var c = cards.filter(function(x){ return x.getAttribute('data-region') === id; })[0];
    return c ? c.getAttribute('data-group') : 'all';
  }
  function pickGroup(id){
    var b = groupBtns.filter(function(x){ return x.getAttribute('data-group') === id; })[0];
    if (!b) b = groupBtns[0];
    mark(groupBtns, b);
    state.group = b ? b.getAttribute('data-group') : 'all';
  }
  function syncAfter(kind, el){
    if (kind === 'group' && state.group !== 'all'){
      state.region = 'all'; mark(regionBtns, regionBtns[0]);
      state.scope = 'all'; mark(scopeBtns, scopeBtns[0]);
    } else if (kind === 'scope'){
      state.group = 'all'; mark(groupBtns, groupBtns[0]);
      state.region = 'all'; mark(regionBtns, regionBtns[0]);
    } else if (kind === 'region'){
      /* v36: 다른 권역·국내/해외가 걸린 채 지역을 바꾸면 0건이 되던 문제 — 권역·범위를 지역에 맞춘다. */
      state.scope = 'all'; mark(scopeBtns, scopeBtns[0]);
      pickGroup(state.region === 'all' ? 'all' : groupOfRegion(state.region));
    } else if (kind === 'theme' && state.group === 'all' && state.region !== 'all'){
      pickGroup(groupOfRegion(state.region));
    }
    render();
  }

  function setRegion(id){
    var target = regionBtns.filter(function(b){ return b.getAttribute('data-region') === id; })[0];
    if (!target) return;
    mark(regionBtns, target);
    state.region = id;
    state.scope = 'all';
    mark(scopeBtns, scopeBtns[0]);
    pickGroup(groupOfRegion(id));
    render();
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-jump]'), function(a){
    a.addEventListener('click', function(e){
      e.preventDefault();
      setRegion(a.getAttribute('data-jump'));
      var sf = document.getElementById('sf');
      if (sf && sf.scrollIntoView) sf.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  var qs = new URLSearchParams(location.search);
  var qTheme = qs.get('theme'), qRegion = qs.get('region'), qScope = qs.get('scope'), qSort = qs.get('sort'), qGroup = qs.get('group'), qBudget = qs.get('budget');
  var needJump = false;
  if (qGroup){ var gb = groupBtns.filter(function(b){ return b.getAttribute('data-group') === qGroup; })[0]; if (gb){ mark(groupBtns, gb); state.group = qGroup; } }
  if (qScope){ var sb = scopeBtns.filter(function(b){ return b.getAttribute('data-scope') === qScope; })[0]; if (sb){ mark(scopeBtns, sb); state.scope = qScope; } }
  if (qRegion){ setRegion(qRegion); needJump = true; }
  if (qTheme){ var tb = themeBtns.filter(function(b){ return b.getAttribute('data-theme') === qTheme; })[0]; if (tb){ mark(themeBtns, tb); state.theme = qTheme; } }
  if (qBudget){ var bb = budgetBtns.filter(function(b){ return b.getAttribute('data-budget') === qBudget; })[0]; if (bb){ mark(budgetBtns, bb); state.budget = qBudget; } }
  if (qSort){ var so = sortBtns.filter(function(b){ return b.getAttribute('data-sort') === qSort; })[0]; if (so){ mark(sortBtns, so); state.sort = qSort; } }
  if (location.hash && location.hash.length > 1) setRegion(location.hash.slice(1));
  window.addEventListener('hashchange', function(){
    if (location.hash && location.hash.length > 1) setRegion(location.hash.slice(1));
  });

  /* v46: 모바일에서 ?region=guam 으로 들어오면 접힌 「지역 선택」 버튼에 선택 지역 이름을 보여 준다 */
  function foldName(){
    if (state.region && state.region !== 'all'){
      var b = regionBtns.filter(function(x){ return x.getAttribute('data-region') === state.region; })[0];
      if (b) return '지역: ' + b.textContent.replace(/[0-9]/g, '').trim();
    }
    return '지역 선택';
  }
  function syncFold(){
    var f = document.getElementById('sfFold'), sf = document.getElementById('sf');
    if (!f || !sf) return;
    f.innerHTML = foldName() + ' <i>' + (sf.classList.contains('open-regions') ? '▴' : '▾') + '</i>';
  }

  var fold = document.getElementById('sfFold');
  if (fold) fold.addEventListener('click', function(){
    var sf = document.getElementById('sf');
    var open = sf.classList.toggle('open-regions');
    fold.setAttribute('aria-expanded', open ? 'true' : 'false');
    syncFold();
    revealChips();
  });

  var reset = document.getElementById('sfReset');
  if (reset) reset.addEventListener('click', function(){
    state.scope = 'all'; state.group = 'all'; state.region = 'all'; state.theme = 'all'; state.budget = 'all'; state.sort = 'rec';
    mark(scopeBtns, scopeBtns[0]); mark(groupBtns, groupBtns[0]); mark(regionBtns, regionBtns[0]); mark(themeBtns, themeBtns[0]); mark(budgetBtns, budgetBtns[0]);
    if (sortBtns.length) mark(sortBtns, sortBtns[0]);
    render();
  });
  /* v46: ?region=guam 처럼 줄 끝 지역으로 들어오면 선택된 칩이 가로 스크롤 밖에 있어 안 보이던 문제 */
  function revealChips(){
    Array.prototype.forEach.call(document.querySelectorAll('.sf-chips'), function(box){
      var on = box.querySelector('.gf-chip.on');
      if (!on || !box.clientWidth) return;
      var b = box.getBoundingClientRect(), c = on.getBoundingClientRect();
      if (c.left < b.left || c.right > b.right){
        box.scrollLeft += (c.left - b.left) - (b.width - c.width) / 2;
      }
    });
  }
  render(false);
  revealChips();
  syncFold();
  if (needJump){ var sf = document.getElementById('sf'); if (sf && sf.scrollIntoView) sf.scrollIntoView({ block: 'start' }); revealChips(); }
})();
</script>"""


def quiz_links(base: str) -> dict:
    """v25 취향 퀴즈 결과 카드가 쓸 링크 — 허브·찐숙소·최저가 투어·가이드·트립닷컴 목록."""
    out = {}
    stays = {r["id"]: r for r in STAYS.get("regions", [])}
    for hub in hub_list():
        slug = hub["slug"]
        tours = hub_tours(hub)
        rest = hub_city_rest(hub)
        guides = hub_guides(hub)
        region = stays.get(slug)
        tour = min(tours, key=lambda t: t["sale"]) if tours else None
        out[slug] = {
            "url": f"/{slug}",
            "name": hub["nav"],
            "tour": (
                {"title": strip_tags(tour["title"]), "sale": tour["sale"], "url": tour["url"],
                 "type": tour["type"], "dur": tour["duration"]}
                if tour else None
            ),
            "stays": f"/stays#{slug}" if region else "",
            "staysN": region["count"] if region else 0,
            "staysTop": region["top"] if region else "",
            "listUrl": (region or {}).get("listUrl", ""),
            "restN": len(rest["items"]) if rest else 0,
            "guide": (
                {"title": guides[0]["navTitle"], "url": f"/guides/{guides[0]['slug']}"}
                if guides else None
            ),
            "img": hub["image"],
            "imgAlt": hub.get("imageAlt", ""),
        }
    return out


def quiz_page(out_root: Path, base: str) -> Path:
    qz = load_json("quiz.json")
    b = base.rstrip("/")
    links = quiz_links(base)
    payload = {"questions": qz["questions"], "cities": qz["cities"], "links": links}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    city_cards = "".join(
        f'<a class="qz-city" href="/{c["slug"]}">'
        f'<img src="{esc(links[c["slug"]]["img"])}" alt="{esc(links[c["slug"]]["imgAlt"])}" width="640" height="400" loading="lazy" />'
        f'<span class="qz-city-b"><span class="qz-city-k">{esc(c["kind"])} · {esc(c["best"])}</span>'
        f'<b>{esc(c["name"])}</b></span></a>'
        for c in qz["cities"] if c["slug"] in links
    )
    steps = "".join(
        f'<span><b>{i}.</b> {esc(q["q"])}</span>' for i, q in enumerate(qz["questions"], 1)
    )

    faq = [
        ("이 퀴즈는 무엇으로 추천하나요?",
         "트립픽이 정리한 13개 도시의 실제 상품 가격(2026-11-20 확인), 현지 식비, 이동 시간을 예산·일정·동행·분위기·비행시간 다섯 가지에 점수로 환산해 가장 가까운 곳을 고릅니다."),
        ("결과가 마음에 안 들면요?",
         "2·3순위 도시도 함께 보여드립니다. 1~3점 차이로 순위가 바뀌는 경우가 많아, 조건을 하나씩 바꿔 다시 해보시면 다른 후보가 나옵니다."),
        ("선택한 답이 저장되나요?",
         "퀴즈 결과는 이 브라우저(localStorage)에만 저장되고 서버로 보내지 않습니다. 홈의 ‘내 여행 준비’에서 다시 열 수 있고, 다른 기기와는 공유되지 않습니다."),
    ]
    faq_html = "".join(
        f'<details class="fq"><summary><span class="fq-q"><b>Q.</b> {esc(q)}</span>'
        f'<span class="fq-ic" aria-hidden="true"></span></summary>'
        f'<div class="fq-a">{esc(a)}</div></details>'
        for q, a in faq
    )
    faq_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq
            ],
        },
        ensure_ascii=False,
    )
    app_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "트립픽 1분 여행지 취향 퀴즈",
            "applicationCategory": "TravelApplication",
            "operatingSystem": "모든 브라우저",
            "url": f"{b}/quiz",
            "inLanguage": "ko",
            "description": "예산·일정·동행·분위기·이동 거리 다섯 질문으로 13개 도시 중 내 여행지를 찾는 무료 퀴즈.",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"},
        },
        ensure_ascii=False,
    )

    body = f"""<div class="pg-hero qz-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><b>취향 퀴즈</b></nav>
    <span class="pg-kicker">TRAVEL TASTE QUIZ · 13개 도시</span>
    <div class="pg-head">
      <h1>1분이면, <em>내 여행지</em>가 나옵니다</h1>
      <p class="dek">{esc(qz["lede"])}</p>
      <div class="pg-meta"><span><b>트립픽 편집</b></span><i></i><span>질문 5개</span><i></i><span>도시 13곳</span><i></i><span>업데이트 2026.11.20</span></div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
{share_row('page')}
{cont_bar('퀴즈', '1분 여행지 취향 퀴즈', '/quiz', 'images/og/quiz.jpg')}
    <div class="qz" id="quiz">
      <div class="qz-top">
        <span class="qz-step" id="qzStep">1 / 5</span>
        <div class="qz-bar" aria-hidden="true"><i id="qzBar"></i></div>
        <button type="button" class="qz-restart" id="qzRestart" hidden>처음부터</button>
      </div>
      <div class="qz-body" id="qzBody" aria-live="polite"></div>
      <div class="qz-foot">
        <button type="button" class="qz-back" id="qzBack" hidden>이전 질문</button>
        <span class="qz-hint">답을 고르면 바로 다음 질문으로 넘어갑니다.</span>
      </div>
      <noscript><p class="qz-noscript">퀴즈는 자바스크립트로 동작합니다. 아래 13개 도시에서 직접 골라 보세요.</p></noscript>
    </div>

    <section class="qz-result" id="qzResult" hidden aria-live="polite"></section>

    <details class="qz-guide" id="qzGuide" open>
      <summary>이렇게 고릅니다 — 질문 5개</summary>
      <div class="qz-steps">{steps}</div>
      <p class="qz-guide-note">{esc(qz["resultNote"])}</p>
    </details>

    <h2 class="qz-h2">13개 도시 — 퀴즈 없이 바로 보기</h2>
    <div class="qz-cities">{city_cards}</div>

    <h2 class="qz-h2">퀴즈에 대해 자주 묻는 질문</h2>
    <div class="qz-faq">{faq_html}</div>

{cta_band('', '도시를 골랐으면, 내 날짜로 총액 계산', '인원과 스타일을 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 계산합니다.')}
  </div>
</div>
<script type="application/json" id="quizData">{raw}</script>
<script>
{QUIZ_JS}
</script>"""

    return page(
        out_root,
        "quiz.html",
        title=qz["title"],
        desc=(
            "예산·일정·동행·분위기·비행시간 다섯 질문으로 13개 도시(오사카·도쿄·후쿠오카·다낭·나트랑·방콕·타이베이·제주·서울·부산·강릉·여수·경주) 중 "
            "내 여행지를 찾습니다. 결과 카드에서 그 도시의 투어·맛집·찐숙소·가이드로 바로 이어지고, 결과는 브라우저에 저장됩니다."
        ),
        body=body,
        base=base,
        active="cities",
        keywords="여행지 추천, 여행지 퀴즈, 여행 취향 테스트, 국내 여행지 추천, 해외 여행지 추천, 1박2일 추천, 예산별 여행지, 13개 도시",
        og_image=f"{b}/images/og/quiz.jpg",
        og_image_alt="트립픽 1분 여행지 취향 퀴즈 — 13개 도시 중 내 여행지 찾기",
        og_image_size=(1200, 630),
        jsonld=(
            f'<script type="application/ld+json">{app_json}</script>\n'
            f'<script type="application/ld+json">{faq_json}</script>\n'
            + graph_ld(org_ld(base), website_ld(base),
                       breadcrumb_ld(base, [("트립픽", "/"), ("여행지 취향 퀴즈", None)]))
        ),
    )


QUIZ_JS = r"""
(function(){
  var el = document.getElementById('quizData');
  if (!el) return;
  var D;
  try { D = JSON.parse(el.textContent); } catch (e) { return; }
  var KEY = 'trippick.quiz.v1';
  var body = document.getElementById('qzBody');
  var stepEl = document.getElementById('qzStep');
  var barEl = document.getElementById('qzBar');
  var backBtn = document.getElementById('qzBack');
  var restartBtn = document.getElementById('qzRestart');
  var resultEl = document.getElementById('qzResult');
  var guideEl = document.getElementById('qzGuide');
  var ans = {};
  var idx = 0;
  var N = D.questions.length;

  function won(n){ return Math.round(n).toLocaleString('ko-KR'); }
  function esc(v){
    return String(v == null ? '' : v).replace(/[&<>"]/g, function(c){
      return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c];
    });
  }
  function bySlug(slug){
    for (var i = 0; i < D.cities.length; i++) if (D.cities[i].slug === slug) return D.cities[i];
    return null;
  }
  function rank(){
    return D.cities.map(function(c, i){
      var s = 0;
      Object.keys(ans).forEach(function(q){ s += (c.scores[q + ':' + ans[q]] || 0); });
      return { c: c, s: s, i: i };
    }).sort(function(a, b){ return b.s - a.s || a.i - b.i; });
  }
  function resultUrl(slug){
    return location.origin + location.pathname + '?r=' + slug + '#qzResult';
  }

  function renderQ(){
    var q = D.questions[idx];
    stepEl.textContent = (idx + 1) + ' / ' + N;
    barEl.style.width = Math.round((idx / N) * 100) + '%';
    backBtn.hidden = idx === 0;
    restartBtn.hidden = !Object.keys(ans).length;
    var html = '<div class="qz-qw"><h2 class="qz-q">' + esc(q.q) + '</h2>' +
      '<p class="qz-sub">' + esc(q.sub) + '</p><div class="qz-opts">';
    q.options.forEach(function(o){
      var on = ans[q.id] === o.v;
      html += '<button type="button" class="qz-opt' + (on ? ' on' : '') + '" data-v="' + esc(o.v) + '" aria-pressed="' + on + '">' + esc(o.label) + '</button>';
    });
    html += '</div></div>';
    body.innerHTML = html;
  }

  function shareRow(url, title){
    return '<div class="share-row share-row--result" data-share data-share-url="' + esc(url) + '" data-share-title="' + esc(title) + '">' +
      '<span class="share-k">이 결과 공유하기</span>' +
      '<button type="button" class="share-btn share-btn--main" data-share-act="native">카톡·인스타·스레드로 보내기</button>' +
      '<button type="button" class="share-btn" data-share-act="copy">링크 복사</button>' +
      '<span class="share-note">링크를 받은 사람은 같은 결과 카드를 바로 봅니다.</span></div>';
  }

  function showResult(ranked){
    var top = ranked[0];
    var c = top.c;
    var L = D.links[c.slug] || {};
    var url = resultUrl(c.slug);
    var title = '내 여행지는 ' + c.name + ' — 트립픽 1분 취향 퀴즈';
    var rows = '<li class="qzr-main"><a href="' + esc(L.url || ('/' + c.slug)) + '"><b>' + esc(c.name) + ' 도시 페이지</b>' +
      '<span>투어·맛집·숙소·가이드를 한 화면에</span></a></li>';
    if (L.tour) {
      rows += '<li><a href="' + esc(L.tour.url) + '" target="_blank" rel="noopener sponsored"><b>' +
        esc(L.tour.title) + '</b><span>' + esc(L.tour.type) + ' · ' + esc(L.tour.dur) + ' · 1인 ' + won(L.tour.sale) + '원~</span></a></li>';
    }
    if (L.stays) {
      rows += '<li><a href="' + esc(L.stays) + '"><b>찐숙소 ' + (L.staysN || 0) + '곳</b><span>' +
        esc(L.staysTop || '') + ' — 평점·리뷰·1박 가격 비교</span></a></li>';
    }
    if (L.listUrl) {
      rows += '<li><a href="' + esc(L.listUrl) + '" target="_blank" rel="noopener sponsored"><b>트립닷컴 ' + esc(c.name) + ' 숙소 전체</b><span>체크인 날짜를 넣으면 그날 최저가로 정렬</span></a></li>';
    }
    if (L.guide) {
      rows += '<li><a href="' + esc(L.guide.url) + '"><b>' + esc(L.guide.title) + '</b><span>같은 도시를 숫자로 계산한 가이드</span></a></li>';
    }
    var alt = ranked.slice(1, 3).map(function(r){
      var l = D.links[r.c.slug] || {};
      return '<a class="qz-alt" href="' + esc(l.url || ('/' + r.c.slug)) + '"><em>차점</em><b>' + esc(r.c.name) + '</b><span>' + esc(r.c.best) + '</span></a>';
    }).join('');

    resultEl.innerHTML = '<div class="qzres">' +
      '<div class="qzres-top"><span class="qzres-k">내 여행지는</span><h2>' + esc(c.name) + '</h2>' +
      '<p class="qzres-best">' + esc(c.best) + '</p><span class="qzres-score">답한 조건 일치도 ' + top.s + '점</span></div>' +
      '<div class="qzres-body">' +
        '<img class="qzres-img" src="' + esc(L.img || '') + '" alt="' + esc(L.imgAlt || c.name) + '" width="640" height="400" loading="lazy" />' +
        '<div class="qzres-copy"><p class="qzres-why">' + esc(c.why) + '</p>' +
        '<ul class="qzres-links">' + rows + '</ul></div>' +
      '</div>' +
      shareRow(url, title) +
      '<div class="qzres-altbox"><b>조건이 하나만 달라도 바뀝니다 — 2·3순위</b><div class="qz-altrow">' + alt + '</div></div>' +
      '<div class="qzres-foot"><button type="button" class="qz-again" id="qzAgain">답을 바꿔 다시 하기</button>' +
      '<span>결과는 이 브라우저에 저장되어 홈의 ‘내 여행 준비’에서 다시 열 수 있습니다.</span></div>' +
      '</div>';
    resultEl.hidden = false;
    document.getElementById('quiz').hidden = true;
    if (guideEl) guideEl.open = false;
    try {
      localStorage.setItem(KEY, JSON.stringify({ slug: c.slug, name: c.name, why: c.best, url: '/quiz?r=' + c.slug, t: Date.now() }));
    } catch (e) {}
    try { history.replaceState(null, '', '?r=' + c.slug + '#qzResult'); } catch (e) {}
    var again = document.getElementById('qzAgain');
    if (again) again.addEventListener('click', function(){ restart(); });
    if (resultEl.scrollIntoView) {
      setTimeout(function(){ resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60);
    }
  }

  function restart(){
    ans = {}; idx = 0;
    resultEl.hidden = true; resultEl.innerHTML = '';
    document.getElementById('quiz').hidden = false;
    if (guideEl) guideEl.open = true;
    try { history.replaceState(null, '', location.pathname); } catch (e) {}
    renderQ();
  }

  function answered(){
    if (idx < N - 1) { idx += 1; renderQ(); return; }
    barEl.style.width = '100%';
    showResult(rank());
  }

  document.addEventListener('click', function(e){
    var opt = e.target.closest('.qz-opt');
    if (opt && body.contains(opt)) {
      var q = D.questions[idx];
      ans[q.id] = opt.getAttribute('data-v');
      Array.prototype.forEach.call(body.querySelectorAll('.qz-opt'), function(b){ b.classList.remove('on'); b.setAttribute('aria-pressed', 'false'); });
      opt.classList.add('on'); opt.setAttribute('aria-pressed', 'true');
      setTimeout(answered, 180);
      return;
    }
    if (e.target.closest('#qzBack')) {
      if (idx > 0) { idx -= 1; renderQ(); }
      return;
    }
    if (e.target.closest('#qzRestart')) { restart(); }
  });

  // 진입 조건: ?r=도시 → 그 결과, ?mood=바다 등 → 해당 답을 미리 고른 채 시작
  var qs = new URLSearchParams(location.search);
  var rslug = qs.get('r');
  if (rslug && bySlug(rslug)) {
    showResult(rank());
    return;
  }
  var mood = qs.get('mood');
  if (mood) {
    var mq = null;
    D.questions.forEach(function(q){ if (q.id === 'mood') mq = q; });
    if (mq && mq.options.some(function(o){ return o.v === mood; })) {
      ans.mood = mood;
      idx = 1;
    }
  }
  renderQ();
})();
"""


def not_found_page(out_root: Path, base: str) -> Path:
    """없는 주소용 404.html — 홈으로 되돌리는 동선과 인기 페어지를 둔다(noindex)."""
    links = "".join(
        f'<a href="{u}">{esc(n)}</a>'
        for u, n in [
            ("/", "홈"),
            ("/guides/", f"여행 가이드 {len(GUIDES_LIST)}편"),
            ("/cities/", f"도시별 페이지 {len(hub_list())}곳"),
            ("/osaka", "오사카·교토"),
            ("/tokyo", "도쿄"),
            ("/danang", "다낭·호이안"),
            ("/jeju", "제주"),
            ("/#checklist", "출국 체크리스트"),
            ("/exchange", "환율·면세 계산기"),
            ("/baggage", "수하물 규정"),
            ("/passes", "교통패스 본전 계산기"),
            ("/calendar", "월별 시즌 캘린더"),
            ("/sos", "여행 중 위기상황 SOS"),
            ("/#planner", "예산 계산기"),
        ]
    )
    body = f"""<div class="pg-body">
  <div class="wrap">
    <div class="nf-box">
      <b class="nf-no">404</b>
      <h1>이 주소에는 글이 없습니다</h1>
      <p>링크가 바뀌었거나 주소를 잘못 입력했습니다. 아래에서 다시 찾으시면 바로 이어집니다.</p>
      <div class="nf-links">{links}</div>
      <p class="nf-hint">찾는 글이 있으면 가이드 검색창에 도시나 주제를 넣어 보세요. 예: <a href="/guides/?q=오사카">오사카</a> · <a href="/guides/?q=eSIM">eSIM</a> · <a href="/guides/?q=우기">우기</a></p>
    </div>
  </div>
</div>"""
    p = page(
        out_root,
        "404.html",
        title="페이지를 찾을 수 없습니다 (404) | 트립픽",
        desc=f"요청한 주소가 없습니다. 여행 가이드 {len(GUIDES_LIST)}편·도시별 페이지 {len(hub_list())}곳·출국 체크리스트로 연결합니다.",
        body=body,
        base=base,
    )
    t = p.read_text(encoding="utf-8")
    t = t.replace(
        '<meta name="robots" content="index, follow, max-image-preview:large" />',
        '<meta name="robots" content="noindex, follow" />',
        1,
    )

    # v36: 404.html 은 없는 주소 어디서든 서빙되므로 상대 경로가 위험하다.
    # /foo/bar 에서 assets/site.css·./#checklist 를 그대로 두면 /foo/assets/... 로 풀려
    # 스타일·스크립트가 404 이고 메뉴가 /foo/#... 로 이동한다. 모든 상대 URL 을 루트 절대 경로로 바꾼다.
    def _root_rel(m: "re.Match") -> str:
        attr, val = m.group(1), m.group(2)
        if re.match(r'^(?:[a-z][a-z0-9+.\-]*:|//|/|#)', val, re.I):
            return m.group(0)
        if val.startswith("./"):
            val = val[2:]
        return f'{attr}="/{val}"'

    t = re.sub(r'(href|src)="([^\"]*)"', _root_rel, t)
    p.write_text(t, encoding="utf-8")
    return p


# ----------------------------------------------------------------------
# /checklist — v26: 여행 갈 때 D-Day 순서(4단계 타임라인)
# ----------------------------------------------------------------------
def checklist_page(out_root: Path, base: str) -> Path:
    ess_by_id = {e["id"]: e for e in ESSENTIALS}
    check = load_json("checklist.json")
    tl = json.loads((DATA / "timeline.json").read_text(encoding="utf-8"))
    B.TIMELINE = tl
    steps = tl["steps"]
    _stay_hotels = STAYS.get("hotels", [])
    _stay_regions = [r for r in STAYS.get("regions", []) if any(h["region"] == r["id"] for h in _stay_hotels)]
    _stay_kr_regions = len([r for r in _stay_regions if r.get("scope") == "kr"])
    _stay_intl_regions = len([r for r in _stay_regions if r.get("scope") != "kr"])
    intl_total = B.dday_total("intl")
    dom_total = B.dday_total("dom")
    kr = next((c for c in check["countries"] if c["id"] == "kr"), None)

    tools = [
        ("stays.html", "D-30", "찐숙소 " + str(len(STAYS.get("hotels", []))) + "곳", f"국내 {_stay_kr_regions}개 지역 + 해외 {_stay_intl_regions}개 도시를 평점·리뷰·1박 최저가로 비교"),
        ("calendar.html", "D-30", "월별 시즌 캘린더", "19개 도시 12개월 성수기·비수기와 항공권 가격이 오르는 달을 먼저 봅니다"),
        ("index.html#travelins", "D-30", "여행자보험 3곳 비교", "보장 항목·자기부담금을 카드사·보험사 공식 조건으로 비교"),
        ("passes.html", "D-14", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이·싱가포르 패스가 하루 이동 횟수로 남는지 계산"),
        ("index.html#essentials", "D-14", "eSIM·필수템", "나라별 eSIM 1일 100원대(유럽·이탈리아 102~109원)부터, 어댑터·보조배터리 구매 링크"),
        ("index.html#regions", "D-14", "투어·입장권 비교", "같은 도시 상품을 가격·현장 추가금·취소 규정까지 같은 기준으로 비교"),
        ("baggage.html", "D-3", "항공사 수하물 8곳", "기내·위탁 무게와 보조배터리 규정을 항공사별로 확인"),
        ("guides/flight-cheap-booking-baggage", "D-30", "항공권·수하물 총액", "대한항공·LCC 7곳 기내·위탁 기준과 사전 구매 요금을 같은 표로 비교"),
        ("exchange.html", "D-3", "환율·일본 면세 계산기", "12개 통화 환율과 일본 면세 환급액을 같은 날 기준으로 계산"),
        ("guides/flight-delay-card-lost-emergency", "D-0", "지연·분실 대처 순서", "지연 확인서·PIR·카드 정지까지 공항에서 첫 30분에 할 일"),
        ("index.html#fxcards", "D-3", "환전 카드 3종", "트래블로그·트래블월렛·하나카드 수수료와 환율을 비교"),
        ("guides/fukuoka-yufuin-3n4d-course", "D-30", "후쿠오카·유후인 3박4일", "하카타 2박+유후인 1박, 산큐패스 3일 12,000엔이 본전인지부터"),
        ("guides/chiang-mai-3n4d-course", "D-14", "치앙마이 3박4일", "공항 정액택시 150밧·썽태우 1인 30밧·코끼리 보호구역 2,500밧"),
        ("guides/bali-ubud-seminyak-3n4d-course", "D-30", "발리 우붓·스미냑 3박4일", "e-VOA 500,000루피아·관광세 150,000·그랩 340,000루피아"),
        ("guides/hongkong-macau-3n4d-course", "D-14", "홍콩·마카오 3박4일", "에어포트익스프레스 왕복 215·대교 셔틀 65홍콩달러와 면세 800달러"),
        ("guides/shanghai-2n3d-3n4d-course", "D-30", "상하이 무비자 30일", "2026-12-31까지 무비자 · 전자입국신고서 72시간 전 · 푸둥 지하철 7위안"),
        ("guides/japan-rental-car-etc-guide", "D-14", "일본 렌터카·국제면허", "국제운전면허 9,000원·ETC 카드·KEP/HEP·오키나와 예외까지"),
    ]
    tool_cards = "".join(
        f'<a class="ddtool" href="{href}"><span class="ddtool-d">{d}</span>'
        f'<b>{esc(title)}</b><span>{esc(desc)}</span>'
        f'<i>열기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></i></a>'
        for href, d, title, desc in tools
    )

    country_rows = "".join(
        f'<tr><th scope="row">{esc(c["name"])}</th><td>{esc(c["badge"])}</td>'
        f'<td class="num">{esc(c["feeTotal"])}</td>'
        f'<td>{esc((c["docs"][0]["when"] if c["docs"] else "—"))}</td>'
        f'<td>{len(c["docs"])}개</td></tr>'
        for c in check["countries"]
    )
    kr_note = (f'국내({esc(kr["name"])})는 입국서류가 없고 {len(kr["docs"])}개 서류만 확인하면 됩니다.' if kr else "")

    faq = [
        ("D-30에 숙소와 항공을 먼저 잡는 이유가 있나요?",
         "가격이 가장 크게 움직이는 두 가지이기 때문입니다. 숙소는 무료 취소 조건으로 먼저 잡아 두면 더 싼 곳이 나왔을 때 갈아탈 수 있고, 항공은 좌석이 적은 날부터 값이 올라갑니다. 두 가지를 먼저 고정하면 남은 3주는 투어와 준비물에 쓸 수 있습니다."),
        ("국내여행으로 바꾸면 무엇이 빠지나요?",
         f'여권·비자·환전·eSIM·액체류·입국서류 QR·공항픽업·면세 인도장 8개 항목을 숨깁니다. 국내여행은 {dom_total}개 항목만 남고, 렌터카·리프트권처럼 국내에만 해당하는 항목이 대신 나옵니다. 해외여행은 {intl_total}개입니다.'),
        ("출국 준비 체크리스트(나라별)와 무엇이 다른가요?",
         "이 페이지는 '언제 무엇을 하는지' 순서를 정리한 타임라인이고, 홈의 나라별 체크리스트는 나라를 고르면 입국서류·수수료·기내반입 규정이 바뀌는 목록입니다. 순서를 잡은 뒤 나라별 서류를 확인하는 식으로 같이 씁니다."),
        ("체크한 내용이 다른 기기와 공유되나요?",
         "공유되지 않습니다. 체크 상태와 국내·해외 선택은 이 브라우저의 localStorage에만 저장되고 서버로 보내지 않습니다. 브라우저 기록을 지우면 함께 사라집니다."),
    ]
    faq_html = "".join(
        f'<details class="fq"><summary><span class="fq-q"><b>Q.</b> {esc(q)}</span>'
        f'<span class="fq-ic" aria-hidden="true"></span></summary>'
        f'<div class="fq-a">{esc(a)}</div></details>'
        for q, a in faq
    )
    faq_json = json.dumps(
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        ensure_ascii=False,
    )
    howto_json = json.dumps(
        {"@context": "https://schema.org", "@type": "HowTo",
         "name": "여행 갈 때 D-Day 순서 — D-30부터 출발 당일까지",
         "description": "숙소·항공(D-30) → 투어·eSIM(D-14) → 수하물·환전(D-3) → 체크인·공항(D-0) 순서로 준비하는 4단계 여행 준비 타임라인입니다.",
         "totalTime": "P30D",
         "step": [{"@type": "HowToStep", "name": s["d"] + " " + s["title"], "text": s["why"]} for s in steps]},
        ensure_ascii=False,
    )

    body = f"""<div class="pg-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><b>여행 준비 D-Day</b></nav>
    <span class="pg-kicker">TRIPPICK CHECKLIST · D-30 → D-14 → D-3 → 출발 당일</span>
    <div class="pg-head">
      <h1><em>여행 준비</em> D-Day 순서 — 4단계로 정리</h1>
      <p class="dek">무엇부터 해야 할지 모를 때 쓰는 순서입니다. <b>D-30에 숙소와 항공</b>, <b>D-14에 투어·eSIM</b>,
      <b>D-3에 수하물·환전</b>, <b>출발 당일에는 체크인과 공항 동선</b>을 끝내도록 묶었습니다.
      국내여행으로 바꾸면 여권·환전·eSIM 항목이 빠지고 {dom_total}개 항목만 남습니다. 체크는 이 브라우저에 저장됩니다.</p>
      <div class="pg-meta">
        <span><b>트립픽 준비 편집</b></span><i></i>
        <span>{len(steps)}단계 · 해외 {intl_total}개 / 국내 {dom_total}개</span><i></i>
        <span>기준 {tl.get('checked', '2026-11-20').replace('-', '.')}</span>
      </div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
{share_row('page')}
{cont_bar('준비', '여행 준비 D-Day 4단계 타임라인', '/checklist', 'images/og/stays.jpg')}
{B.trip_widget_html(hub_list(), GUIDES_LIST, ess_by_id)}
    <div class="ddwrap">
{B.dday_timeline_html(ess_by_id)}
    </div>

    <div class="tp-bundle tp-bundle--checklist" data-tp-bundle="checklist" data-tp-chips="osaka,tokyo,fukuoka,danang,bangkok,taipei,paris,london,rome,barcelona" hidden></div>

    <h2 class="sr-h2">단계별로 쓰는 트립픽 도구</h2>
    <p class="sr-dek">각 단계에서 바로 열어 확인할 수 있는 페이지입니다. 가격·규정은 2026년 11월 20일 확인 기준입니다.</p>
    <div class="ddtools">{tool_cards}</div>

    <h2 class="sr-h2">나라별 입국서류·수수료 (같이 보기)</h2>
    <p class="sr-dek">D-14에 확인할 서류와 비용입니다. 나라를 고르면 기내반입 규정과 준비물 목록까지 바뀌는 표는 홈의 출국 준비 섹션에 있습니다. {kr_note}</p>
    <div class="ddtable-wrap">
      <table class="ddtable">
        <thead><tr><th scope="col">나라</th><th scope="col">비자·입국</th><th scope="col" class="num">비용</th><th scope="col">첫 서류 시기</th><th scope="col">서류</th></tr></thead>
        <tbody>{country_rows}</tbody>
      </table>
    </div>
    <p class="snote">수수료는 2026-11-20 기준이며 정부 요금은 예고 없이 바뀝니다. 결제·출국 직전에 각 공식 사이트에서 다시 확인하세요. 자세한 서류 설명과 신청 링크는 <a href="index.html#checklist">홈 출국 준비 체크리스트</a>에 있습니다.</p>

    <h2 class="sr-h2">여행 준비 자주 묻는 질문</h2>
    <div class="fqlist">{faq_html}</div>
{share_row('page')}
  </div>
</div>"""

    return page(
        out_root,
        "checklist.html",
        title=f"여행 준비 D-Day — D-30 숙소·항공 → D-14 투어·eSIM → D-3 수하물 | 트립픽",
        desc=(
            "여행 준비를 D-30 숙소·항공, D-14 투어·eSIM, D-3 수하물·환전, 당일 체크인 4단계로 정리했습니다. "
            f"국내여행은 여권·환전 항목이 빠지고 {dom_total}개만 남으며, 체크 상태는 브라우저에 저장됩니다."
        ),
        keywords=(
            "여행 준비 순서, 여행 D-Day, 여행 준비물 체크리스트, 출국 준비, 국내여행 준비물, "
            "해외여행 준비물, eSIM 언제, 환전 언제, 공항 몇 시간 전, 트래블카드"
        ),
        body=body,
        base=base,
        active="checklist",
        jsonld=(f'<script type="application/ld+json">{howto_json}</script>\n<script type="application/ld+json">{faq_json}</script>\n'
                + graph_ld(
                    {
                        "@type": "WebApplication",
                        "name": "여행 준비 D-Day 체크리스트",
                        "url": f"{base.rstrip('/')}/checklist",
                        "applicationCategory": "TravelApplication",
                        "operatingSystem": "Web",
                        "inLanguage": "ko",
                        "isAccessibleForFree": True,
                        "publisher": {"@id": f"{base.rstrip('/')}/#organization"},
                    },
                    org_ld(base), website_ld(base),
                    breadcrumb_ld(base, [("트립픽", "/"), ("여행 준비 D-Day", None)]),
                )),
    )


def _sos_tel(n: dict) -> str:
    """tel: 링크용 값. 데이터의 tel 은 숫자와 + 만 담고 있다(#7119 → %237119)."""
    t = (n.get("tel") or re.sub(r"[^0-9+#]", "", n.get("number", ""))).strip()
    return "tel:" + t


SOS_LANG = {"KR": "ko", "JP": "ja", "TH": "th", "VN": "vi", "TW": "zh-Hant",
            "SG": "en", "FR": "fr", "IT": "it", "ES": "es", "GB": "en"}


def sos_page(out_root: Path, base: str) -> Path:
    """v44 /sos — 여행 중 위기상황 SOS(10개국 긴급번호 + 현지어 카드).

    데이터는 data/sos_data.json 한 곳. 국가 패널을 서버에서 모두 그려 두고
    (검색·JS 꺼짐 대비) tp-v44.js 가 탭 전환·큰 글씨 카드만 맡는다.
    """
    sos = load_json("sos_data.json")
    cons = sos["consular"]
    med = sos["medicalConsult"]
    countries = sos["countries"]

    def tel_link(n: dict, extra: str = "") -> str:
        tail = f' <em>{esc(extra)}</em>' if extra else ""
        return f'<a href="{_sos_tel(n)}">{esc(n["number"])}</a>{tail}'

    common = "\n      ".join([
        f"""<a class="sos-call" href="{_sos_tel(cons)}">
        <small>외교부 · {esc(cons["hours"])}</small>
        <b>{esc(cons["name"])}</b>
        <span>{esc(cons["languages"])}</span>
        <span class="num">{esc(cons["phone"])}</span>
        <span class="go">눌러서 전화 →</span>
      </a>""",
        f"""<a class="sos-call" href="{_sos_tel(med)}">
        <small>소방청 · {esc(med["hours"])}</small>
        <b>{esc(med["name"])}</b>
        <span>{esc(med["note"])}</span>
        <span class="num">{esc(med["phone"])}</span>
        <span class="go">눌러서 전화 →</span>
      </a>""",
    ])

    tabs = "\n      ".join(
        f'<button class="sos-tab" type="button" role="tab" id="sosTab-{c["code"]}" data-cc="{c["code"]}" '
        f'aria-controls="sos-{c["code"]}" aria-selected="{"true" if i == 0 else "false"}">'
        f'<b aria-hidden="true">{c["flag"]}</b>{esc(c["name"])}</button>'
        for i, c in enumerate(countries)
    )

    panels = []
    for i, c in enumerate(countries):
        lang = SOS_LANG.get(c["code"], "ko")
        cards = []
        for n in c["numbers"]:
            meta = " · ".join(x for x in (n.get("hours"), n.get("languages")) if x)
            note = n.get("note")
            meta_html = esc(meta) + (f"<br>{esc(note)}" if note else "")
            cls = "sos-num primary" if n.get("primary") else "sos-num"
            cards.append(
                f'<a class="{cls}" href="{_sos_tel(n)}">'
                f'<span class="k">{esc(n["label"])}</span>'
                f'<span class="v">{esc(n["number"])}</span>'
                f'<span class="m">{meta_html}</span>'
                f'<span class="go">눌러서 전화 →</span></a>'
            )
        phrases = []
        for p in c["phrases"]:
            phrases.append(
                f'<button class="sos-pc" type="button" aria-label="{esc(p["ko"])} 크게 보기"'
                f' data-ko="{esc(p["ko"])}" data-local="{esc(p["local"])}"'
                f' data-pron="{esc(p["pron"])}" data-en="{esc(p["en"])}">'
                f'<span class="ko">{esc(p["ko"])}</span>'
                f'<span class="loc" lang="{lang}">{esc(p["local"])}</span>'
                f'<span class="pron">{esc(p["pron"])}</span>'
                f'<span class="en" lang="en">{esc(p["en"])}</span></button>'
            )
        notes = "".join(f"<li>{esc(x)}</li>" for x in c.get("notes") or [])
        addr = (
            f'<p class="sos-addr"><b>공관 주소</b> · {esc(c["address"])}</p>'
            if c.get("address") else ""
        )
        hidden = "" if i == 0 else " hidden"
        panels.append(
            f"""<section class="sos-panel" id="sos-{c["code"]}" data-panel-cc="{c["code"]}" role="tabpanel" aria-labelledby="sosTab-{c["code"]}"{hidden}>
        <div class="sos-phh">
          <div>
            <h2>{c["flag"]} {esc(c["name"])} <span>{esc(c["nameEn"])}</span></h2>
            <p>{esc(c["lang"])} · 긴급번호 {len(c["numbers"])}개</p>
          </div>
          <span class="sos-badge">전화하려면 누르세요</span>
        </div>
        <div class="sos-nums">
          {"".join(cards)}
        </div>
        {addr}
        <h3 class="sos-sec">현지어 카드 <span>누르면 큰 글씨로 전체 화면</span></h3>
        <div class="sos-pcs">
          {"".join(phrases)}
        </div>
        <ul class="sos-notes">{notes}</ul>
      </section>"""
        )

    # 전체 표 — 카드가 안 열리는 환경(JS 꺼짐·인쇄)에서도 번호를 찾을 수 있게
    rows = []
    for c in countries:
        urgent = [
            f'<span class="sos-tb-n">{tel_link(n, n["label"])}</span>'
            for n in c["numbers"] if n["kind"] in ("police", "ambulance", "fire", "emergency")
        ]
        kmb = [
            f'<span class="sos-tb-n">{tel_link(n, n["label"])}</span>'
            for n in c["numbers"]
            if n["kind"] in ("embassy", "embassy_emergency", "consular", "medical_consult")
        ]
        rows.append(
            f'<tr><td>{c["flag"]} {esc(c["name"])}</td>'
            f'<td>{"".join(urgent) or "—"}</td>'
            f'<td>{"".join(kmb) or "—"}</td></tr>'
        )

    faq = [
        ("해외에서 응급상황인데 현지어를 못 하면 어떻게 하나요?",
         "먼저 현지 응급번호(일본 119·태국 1669·유럽 112)로 전화하세요. 통역이 필요하면 24시간 영사안전콜센터 +82-2-3210-0404로 걸면 한국어로 받고, 필요할 때 현지 경찰·병원과의 통역을 연결해 줍니다. "
         "이 페이지의 현지어 카드를 눌러 큰 글씨 화면을 상대방에게 보여주는 것이 가장 빠릅니다. '한국어 통역 부탁해요' 문장은 10개국 모두 들어 있습니다."),
        ("유심이 없거나 잠긴 휴대폰에서도 긴급번호가 걸리나요?",
         "대부분 국가에서 잠금 화면의 '긴급 전화'로 112·119·911 같은 번호를 걸 수 있고, 유럽 통합 112는 유심·잔액 없이도 연결되는 경우가 많습니다. "
         "반대로 1330·영사안전콜센터 같은 일반 번호는 유심이나 와이파이 통화 앱이 필요합니다. 그래서 이 페이지를 출국 전에 홈 화면에 추가해 두는 것이 좋습니다."),
        ("영사안전콜센터와 119 재외국민 응급의료상담은 무엇이 다른가요?",
         "영사안전콜센터(+82-2-3210-0404, 24시간)는 7개 언어 통역으로 현지 경찰·병원·공관과 연결하고 여권 분실 같은 영사 업무를 안내합니다. "
         "119 재외국민 응급의료상담(+82-44-320-0119, 24시간)은 응급의학 전문의가 증상·복약·현지 병원 이용을 상담합니다. 의료 판단이 필요하면 119, 통역·행정이 필요하면 영사안전콜센터입니다."),
        ("대사관이 문을 닫은 밤이나 주말에는 어디로 전화하나요?",
         "각 공관의 '긴급(근무시간 외)' 번호로 겁니다. 이 페이지의 대사관 긴급 번호가 그 번호이고, 영사안전콜센터 +82-2-3210-0404는 24시간 연중무휴입니다. "
         "주말·야간에는 영사안전콜센터가 먼저 받아 관할 공관·긴급 담당자와 연결해 주는 편이 빠릅니다."),
        ("이 번호가 바뀌었는지 어떻게 확인하나요?",
         "외교부 해외안전여행 앱·홈페이지, 각 공관 홈페이지, 각국 정부·관광청 공식 안내에서 확인합니다. 이 페이지는 2026-11-22 기준으로 확인했고, "
         "태국 관광경찰(1155)처럼 앱으로도 신고할 수 있는 곳은 앱 안내를 함께 적었습니다. 번호는 현지 사정으로 바뀔 수 있습니다."),
    ]
    faq_html = "".join(
        f'<details class="fq"><summary><span class="fq-q"><b>Q.</b> {esc(q)}</span>'
        f'<span class="fq-ic" aria-hidden="true"></span></summary>'
        f'<div class="fq-a">{esc(a)}</div></details>'
        for q, a in faq
    )
    jsonld = '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "name": "여행 중 위기상황 SOS — 10개국 긴급번호·현지어 카드",
                "description": "한국·일본·태국·베트남·대만·싱가포르·프랑스·이탈리아·스페인·영국의 경찰·구급·관광경찰·한국 공관 번호와 현지어 문장 6개를 한 번의 탭으로.",
                "url": f"{base.rstrip('/')}/sos.html",
                "inLanguage": "ko",
                "isAccessibleForFree": True,
                "dateModified": sos.get("verified") or TODAY.isoformat(),
                "publisher": {"@type": "Organization", "name": SITE_NAME},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faq
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "트립픽", "item": base.rstrip("/") + "/"},
                    {"@type": "ListItem", "position": 2, "name": "여행 중 위기상황 SOS"},
                ],
            },
        ],
    }, ensure_ascii=False) + "</script>"

    body = read(PAGES / "sos.html")
    body = body.replace("<!-- @SOS_COMMON -->", common)
    body = body.replace("<!-- @SOS_TABS -->", tabs)
    body = body.replace("<!-- @SOS_COUNTRIES -->", "\n".join(panels))
    body = body.replace("<!-- @SOS_TABLE -->", "\n            ".join(rows))
    body = body.replace("<!-- @SOS_FAQS -->", faq_html)
    body = body.replace("<!-- @SOS_SHARE -->", share_row("page"))

    return page(
        out_root,
        "sos.html",
        title="여행 중 위기상황 SOS — 10개국 경찰·구급·대사관 번호와 현지어 문장 | 트립픽",
        desc=(
            "한국·일본·태국·베트남·대만·싱가포르·프랑스·이탈리아·스페인·영국의 경찰·구급·관광경찰·한국 공관 번호를 한 번의 탭으로 겁니다. "
            "영사안전콜센터 +82-2-3210-0404, 현지어 6문장 큰 글씨 카드. 2026-11-22 공식 안내 확인."
        ),
        keywords=(
            "여행 중 위기상황, 해외 응급전화, 영사안전콜센터, 119 재외국민 응급의료상담, 해외 경찰 전화, "
            "일본 119, 태국 1669, 유럽 112, 대사관 긴급번호, 여행 현지어 카드, 해외 여권 분실"
        ),
        body=body,
        base=base,
        active="sos",
        jsonld=jsonld,
    )


def coupons_page(out_root: Path, base: str) -> Path:
    """v57: 여행 할인코드·쿠폰 — 2026-11-26 확인된 트립닷컴 공식 코드만 수록.

    코드·조건·유효기간은 kr.trip.com/blog/trip-promotions/(2026-11-26 조회)에서 그대로 옮겼고,
    코드 문자열이 페이지에 없는 쿠폰(호텔·공항픽업·비즈니스석)은 '앱/링크에서 발급'으로만 적는다.
    클룩은 코드를 확인하지 못해 공식 쿠폰 페이지 링크만 둔다(가짜 코드 금지).
    """
    B = "https://kr.trip.com"
    AID = "Allianceid=11407530&SID=336341874"

    TRIP = [
        {
            "id": "flight-new",
            "badge": "신규회원",
            "title": "항공권 최대 22,000원 할인",
            "body": "트립닷컴에서 항공권을 처음 예약할 때 쓸 수 있습니다. 22만 원 이상 결제하면 5,000원, 55만 원 이상이면 22,000원이 빠집니다.",
            "code": "TRIPFLIGHT26KR",
            "cond": ["22만 원 이상 5,000원 · 55만 원 이상 22,000원", "신규회원 항공권 첫 예약", "결제 직전 입력"],
            "expiry": "2026.09.01 ~ 12.31",
            "cta": f"https://kr.trip.com/flights/?{AID}&trip_sub1=coupons_flight&trip_sub3=D21275837",
            "ctaLabel": "항공권 검색하며 적용",
        },
        {
            "id": "hotel-new",
            "badge": "앱 발급",
            "title": "호텔 신규 최대 10% (최대 13,000원) 할인",
            "body": "트립닷컴 앱을 내려받아 신규 가입하면 첫 호텔 예약에 쓸 수 있는 코드가 발급됩니다. 코드 문자열은 앱에서만 받을 수 있습니다.",
            "code": "",
            "cond": ["최대 10% · 최대 13,000원", "앱 가입 후 첫 호텔 예약", "앱에서 코드 발급"],
            "expiry": "앱 쿠폰함 표기 확인",
            "cta": f"https://kr.trip.com/hotels/?{AID}&trip_sub1=coupons_hotel&trip_sub3=D21372570",
            "ctaLabel": "호텔 최저가 보기",
        },
        {
            "id": "car-new",
            "badge": "신규회원",
            "title": "렌터카 최대 8% 할인",
            "body": "렌터카를 처음 예약하는 계정에 적용됩니다. 예약 화면에서 차량을 고른 뒤 결제 전에 코드를 넣습니다.",
            "code": "TRIPCAR8",
            "cond": ["최대 8%", "렌터카 첫 예약", "결제 전 코드 입력"],
            "expiry": "페이지 표기 확인",
            "cta": f"https://kr.trip.com/carhire/?{AID}&trip_sub1=coupons_car&trip_sub3=D21303312",
            "ctaLabel": "렌터카 검색하며 적용",
        },
        {
            "id": "transfer-new",
            "badge": "앱 전용",
            "title": "공항픽업 최대 10% 할인 (항공권 예약자는 12%)",
            "body": "앱 홈에서 공항픽업을 열면 10% 쿠폰이 바로 발급됩니다. 이미 트립닷컴에서 항공권을 예약했다면 12%까지 적용됩니다.",
            "code": "",
            "cond": ["앱에서만 쿠폰 발급", "픽업 첫 이용 10% · 항공권 예약자 12%", "항공편 지연 시 추가 요금 없음"],
            "expiry": "앱 쿠폰함 표기 확인",
            "cta": f"https://kr.trip.com/airport-transfers/?{AID}&trip_sub1=coupons_transfer&trip_sub3=D21303312",
            "ctaLabel": "공항픽업 보기",
        },
        {
            "id": "tour-ticket",
            "badge": "코드",
            "title": "투어·티켓 최대 6% 할인",
            "body": "입장권·투어·액티비티 결제에 쓰는 코드입니다. 도시별 상품 상세의 '쿠폰' 칸에 넣으면 적용 금액이 표시됩니다.",
            "code": "TRIPNAVER",
            "cond": ["투어·티켓 최대 6%", "상품별 적용 여부 다름", "결제 화면에서 최종 확인"],
            "expiry": "페이지 표기 확인",
            "cta": f"https://kr.trip.com/things-to-do/?{AID}&trip_sub1=coupons_tour&trip_sub3=D21303312",
            "ctaLabel": "투어·티켓 보기",
        },
        {
            "id": "biz-first",
            "badge": "링크 발급",
            "title": "비즈니스석·일등석 최대 60,000원 할인",
            "body": "비즈니스·일등석 예약에 적용되는 코드입니다. 코드는 트립닷컴 프로모션 페이지의 '비즈니스 항공권 할인 예약하기' 버튼에서 확인합니다.",
            "code": "",
            "cond": ["최대 60,000원", "비즈니스석·일등석", "프로모션 페이지에서 코드 확인"],
            "expiry": "페이지 표기 확인",
            "cta": "https://kr.trip.com/blog/trip-promotions/",
            "ctaLabel": "프로모션 페이지에서 코드 확인",
            "nofollow": True,
        },
    ]

    ALWAYS = [
        ("트래블카드", "해외 결제 수수료 0%", "트래블월렛·트래블로그·토스뱅크는 해외 가맹점 결제 수수료가 0%입니다. 3만 엔을 ATM에서 인출할 때 일반 카드와 6,568원 차이가 납니다.",
         "guides/travel-card-fees-comparison.html", "카드 3종 수수료 비교"),
        ("환전", "공항 37,520원 vs 앱 1,460원", "10만 엔을 바꿀 때 인천공항 환전 37,520원, 시내 14,590원, 앱 환전 우대 1,460원입니다. 같은 날 고시 기준입니다.",
         "guides/travel-card-packing-guide.html", "환전 수수료·짐싸기"),
        ("라운지", "PP·더라운지 카드 확인", "공항 라운지는 카드에 붙은 PP와 더라운지 중 어느 쪽인지에 따라 쓸 수 있는 라운지가 달라집니다.",
         "guides/airport-lounge-card-guide.html", "라운지 카드 비교"),
    ]

    cards = []
    for c in TRIP:
        code_html = (
            f'<div class="cpn-code"><code>{esc(c["code"])}</code>'
            f'<button type="button" class="cpn-copy" data-copy="{esc(c["code"])}" aria-label="{esc(c["code"])} 복사">복사</button></div>'
            if c["code"] else
            '<div class="cpn-code cpn-code--none"><span>코드 문자열 없이 앱·링크에서 발급됩니다</span></div>'
        )
        rel = "noopener" if c.get("nofollow") else "noopener sponsored"
        cards.append(f"""<article class="cpn" id="cpn-{c['id']}">
  <div class="cpn-top"><span class="cpn-p">트립닷컴</span><span class="cpn-b">{esc(c['badge'])}</span></div>
  <b class="cpn-t">{esc(c['title'])}</b>
  <p class="cpn-d">{esc(c['body'])}</p>
  {code_html}
  <ul class="cpn-cond">{''.join(f'<li>{esc(x)}</li>' for x in c['cond'])}</ul>
  <div class="cpn-foot"><span class="cpn-exp">유효 {esc(c['expiry'])}</span>
    <a class="cpn-go" href="{esc(c['cta'])}" target="_blank" rel="{rel}">{esc(c['ctaLabel'])} →</a></div>
</article>""")

    always_cards = "".join(
        f'<a class="cpn cpn--always" href="{href}">'
        f'<div class="cpn-top"><span class="cpn-p">{esc(kind)}</span><span class="cpn-b">쿠폰 없이</span></div>'
        f'<b class="cpn-t">{esc(title)}</b><p class="cpn-d">{esc(body)}</p>'
        f'<span class="cpn-go">{esc(label)} →</span></a>'
        for kind, title, body, href, label in ALWAYS
    )

    faq = [
        ("트립닷컴 할인코드는 어디에 입력하나요?",
         "결제 화면의 쿠폰·프로모션 코드 입력 칸에 넣습니다. 항공권은 승객 정보를 넣고 결제 직전 화면, 호텔은 결제 수단을 고르는 화면에 칸이 있습니다. 적용 금액이 표시되지 않으면 조건(최소 결제액·신규회원·상품)이 맞지 않는 경우입니다."),
        ("신규회원 할인은 계정마다 한 번인가요?",
         "트립닷컴 신규회원 쿠폰은 계정 기준으로 한 번 발급됩니다. 같은 사람이 계정을 여러 개 만들어 쓰는 것은 약관상 제한될 수 있고, 예약 후 취소·재예약 시 쿠폰이 돌아오지 않는 경우가 있습니다."),
        ("클룩 할인코드는 왜 코드가 없나요?",
         "이 페이지는 2026년 11월 26일 기준으로 코드 문자열과 조건이 공개된 것만 싣습니다. 클룩은 쿠폰이 앱·계정·결제 수단별로 발급되어 공개 문자열을 확인하지 못했으므로, 공식 쿠폰 페이지로만 연결합니다. 확인되는 대로 코드를 추가합니다."),
        ("쿠폰과 카드 할인을 같이 쓸 수 있나요?",
         "보통 쿠폰 1개와 카드 할인은 함께 적용되지만, 상품·결제 수단에 따라 하나만 적용됩니다. 결제 화면의 할인 내역에 두 줄이 모두 표시되는지 확인하고, 표시되지 않으면 결제를 진행하지 마세요."),
        ("유효기간이 지난 코드를 넣으면 어떻게 되나요?",
         "결제 화면에 '사용할 수 없는 코드'로 표시되고 금액은 그대로입니다. 이 페이지는 유효기간이 확인된 코드만 적고, 기간이 끝나면 다음 업데이트에서 지웁니다. 결제 전에 트립닷컴 프로모션 페이지에서 한 번 더 확인하세요."),
    ]
    faq_html = "".join(
        f'<details class="fq"><summary><span class="fq-q"><b>Q.</b> {esc(q)}</span>'
        f'<span class="fq-ic" aria-hidden="true"></span></summary><div class="fq-a">{esc(a)}</div></details>'
        for q, a in faq
    )

    body = f"""<div class="pg-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><b>할인쿠폰</b></nav>
    <span class="pg-kicker">COUPON</span>
    <div class="pg-head">
      <h1>여행 할인코드, <em>확인된 것만</em> 모았습니다</h1>
      <p class="dek">트립닷컴 공식 프로모션 페이지에서 2026년 11월 26일 확인한 코드와 조건입니다. 코드 문자열이 공개되지 않은 쿠폰은 '앱·링크 발급'으로만 적고, 클룩은 공식 쿠폰 페이지로 연결합니다.</p>
      <div class="pg-meta">
        <span><b>트립픽 편집</b></span><i></i><span>최종 검증일 2026.11.26</span><i></i>
        <span>코드 {sum(1 for c in TRIP if c['code'])}개 · 앱 발급 {sum(1 for c in TRIP if not c['code'])}개</span>
      </div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="pg-grid">
      <article class="doc">
        <div class="cpn-note">쿠폰 조건·유효기간은 판매처가 바꿀 수 있습니다. 결제 화면에 표시된 최종 금액이 기준이고, 이 페이지는 <b>2026-11-26 확인값</b>만 싣습니다.</div>
        <div class="tb">
          <div class="tb-h"><b>한눈에 보는 트립닷컴 코드</b><span>kr.trip.com 프로모션 페이지 2026-11-26</span></div>
          <div class="tb-scroll">
            <table>
              <thead><tr><th>대상</th><th>혜택</th><th>코드</th><th>조건</th></tr></thead>
              <tbody>
                <tr><td>항공권(신규)</td><td>최대 22,000원</td><td><b>TRIPFLIGHT26KR</b></td><td>22만↑ 5,000 · 55만↑ 22,000</td></tr>
                <tr><td>렌터카(신규)</td><td>최대 8%</td><td><b>TRIPCAR8</b></td><td>첫 예약</td></tr>
                <tr><td>투어·티켓</td><td>최대 6%</td><td><b>TRIPNAVER</b></td><td>상품별 적용 여부 다름</td></tr>
                <tr><td>호텔(신규)</td><td>최대 10%·13,000원</td><td>앱 발급</td><td>앱 가입 후 첫 예약</td></tr>
                <tr><td>공항픽업</td><td>10% (항공 예약자 12%)</td><td>앱 발급</td><td>앱 전용</td></tr>
                <tr><td>비즈니스·일등석</td><td>최대 60,000원</td><td>링크 발급</td><td>프로모션 페이지에서 확인</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <h2 id="trip">트립닷컴 할인코드 6개</h2>
        <div class="cpn-grid">{''.join(cards)}</div>

        <h2 id="klook">클룩(Klook) 쿠폰</h2>
        <div class="cpn-grid">
          <a class="cpn cpn--always" href="https://www.klook.com/ko/coupons/?aid=144067" target="_blank" rel="noopener sponsored">
            <div class="cpn-top"><span class="cpn-p">클룩</span><span class="cpn-b">공식 페이지</span></div>
            <b class="cpn-t">진행 중인 쿠폰·프로모션 목록</b>
            <p class="cpn-d">클룩은 쿠폰을 앱·계정·결제 수단별로 발급해서 공개된 코드 문자열을 확인하지 못했습니다. 공식 쿠폰 페이지에서 내 계정에 발급된 쿠폰과 적용 조건을 확인하세요.</p>
            <span class="cpn-go">클룩 쿠폰 페이지 열기 →</span>
          </a>
        </div>

        <h2 id="always">코드 없이 상시 적용되는 혜택</h2>
        <div class="cpn-grid">{always_cards}</div>

        <h2 id="rules">쓰기 전에 확인할 것</h2>
        <ul>
          <li><b>결제 화면 금액이 기준</b> — 코드를 넣고 할인 줄이 생겼는지, 최종 결제액이 줄었는지 확인한 뒤 결제하세요.</li>
          <li><b>신규회원 조건</b> — 계정당 1회이고, 취소 후 재예약 때 쿠폰이 돌아오지 않는 경우가 있습니다.</li>
          <li><b>앱 전용</b> — 호텔·공항픽업 쿠폰은 앱에서만 발급됩니다. 웹에서는 코드 칸이 보여도 적용되지 않습니다.</li>
          <li><b>중복</b> — 쿠폰 1개와 카드 할인은 함께 적용되는 경우가 많지만, 상품에 따라 하나만 적용됩니다.</li>
          <li><b>유효기간</b> — 기간이 지나면 자동으로 만료됩니다. 이 페이지는 확인된 기간만 적고, 끝나면 지웁니다.</li>
        </ul>

        <h2 id="faq">자주 묻는 질문</h2>
        {faq_html}
      </article>
      <aside class="pg-side">
        <div class="side-card">
          <b>쿠폰과 함께 쓰는 도구</b>
          <a href="stays.html">찐숙소 126곳 — 1박 최저가</a>
          <a href="passes.html">교통패스 본전 계산기</a>
          <a href="exchange.html">환율·면세 계산기</a>
          <a href="checklist.html">여행 준비 D-Day</a>
        </div>
      </aside>
    </div>
  </div>
</div>
<style>
.cpn-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:12px 0 6px}}
@media(max-width:700px){{.cpn-grid{{grid-template-columns:1fr}}}}
.cpn{{display:flex;flex-direction:column;gap:7px;border:1px solid var(--line);border-radius:16px;background:#fff;padding:15px 16px}}
.cpn:hover{{border-color:var(--blue);box-shadow:0 3px 14px rgba(16,32,46,.07);text-decoration:none}}
.cpn-top{{display:flex;align-items:center;gap:6px}}
.cpn-p{{font-size:11.5px;font-weight:800;color:var(--blue-600);letter-spacing:.02em}}
.cpn-b{{font-size:10.5px;font-weight:800;color:var(--ink-2);background:var(--soft);border-radius:999px;padding:2px 8px}}
.cpn-t{{font-size:15.5px;font-weight:800;color:var(--navy);line-height:1.35}}
.cpn-d{{margin:0;font-size:12.8px;color:var(--ink-3);line-height:1.62}}
.cpn-code{{display:flex;align-items:center;gap:8px;border:1px dashed var(--blue);border-radius:11px;background:var(--blue-soft);padding:9px 11px}}
.cpn-code code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:14px;font-weight:800;color:var(--navy);letter-spacing:.04em}}
.cpn-copy{{margin-left:auto;border:1px solid var(--blue);background:#fff;color:var(--blue-600);font-size:11.5px;font-weight:800;border-radius:8px;padding:5px 10px;cursor:pointer}}
.cpn-copy.on{{background:var(--blue);color:#fff}}
.cpn-code--none{{border-style:solid;border-color:var(--line);background:var(--soft);font-size:11.8px;color:var(--ink-3)}}
.cpn-cond{{margin:2px 0 0;padding-left:17px;font-size:12.2px;color:var(--ink-3);line-height:1.6}}
.cpn-foot{{margin-top:auto;display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding-top:4px}}
.cpn-exp{{font-size:11.5px;font-weight:700;color:var(--ink-3)}}
.cpn-go{{margin-left:auto;font-size:12.2px;font-weight:800;color:var(--blue-600)}}
.cpn-note{{border:1px solid var(--line);border-left:3px solid var(--blue);border-radius:10px;background:#fff;padding:11px 13px;font-size:12.6px;color:var(--ink-2);line-height:1.6}}
</style>"""

    cpn_ld = {
        "@type": "CollectionPage",
        "name": "여행 할인코드·쿠폰 — 트립닷컴·클룩 (2026년 11월)",
        "description": "트립닷컴 공식 할인코드 6개와 클룩 쿠폰 페이지, 코드 없이 적용되는 여행 혜택을 2026년 11월 26일 기준으로 정리했습니다.",
        "url": f"{base.rstrip('/')}/coupons.html",
        "inLanguage": "ko-KR",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(TRIP),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": {
                        "@type": "Offer",
                        "name": c["title"],
                        "description": " · ".join(c["cond"]),
                        "url": f"{base.rstrip('/')}/coupons.html#cpn-{c['id']}",
                        "availability": "https://schema.org/InStock",
                        "seller": {"@type": "Organization", "name": "Trip.com"},
                    },
                }
                for i, c in enumerate(TRIP)
            ],
        },
    }
    jsonld = graph_ld(
        cpn_ld,
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq
            ],
        },
        breadcrumb_ld(base, [("트립픽", ""), ("할인쿠폰", None)]),
    )

    script = """<script>
(function () {
  var btns = document.querySelectorAll('[data-copy]');
  Array.prototype.forEach.call(btns, function (btn) {
    btn.addEventListener('click', function () {
      var v = btn.getAttribute('data-copy') || '';
      var done = function () {
        var old = btn.getAttribute('data-old') || btn.textContent;
        btn.setAttribute('data-old', old);
        btn.textContent = '복사됨 ✓';
        btn.classList.add('on');
        setTimeout(function () { btn.textContent = old; btn.classList.remove('on'); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(v).then(done, function () { done(); });
      } else {
        var ta = document.createElement('textarea');
        ta.value = v;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (err) {}
        document.body.removeChild(ta);
        done();
      }
    });
  });
})();
</script>"""

    return page(
        out_root,
        "coupons.html",
        title="여행 할인코드·쿠폰 — 트립닷컴·클룩 (2026년 11월) | 트립픽",
        desc="2026-11-26 확인된 트립닷컴 할인코드 TRIPFLIGHT26KR(항공 최대 22,000원)·TRIPCAR8(렌터카 8%)·TRIPNAVER(투어 6%), 앱 발급 호텔·공항픽업 쿠폰과 클룩 쿠폰 페이지, 카드·환전·라운지 상시 혜택을 한 페이지에 정리했습니다.",
        body=body,
        base=base,
        active="coupons",
        keywords="트립닷컴 할인코드, 트립닷컴 쿠폰, 클룩 할인코드, 여행 할인쿠폰, TRIPFLIGHT26KR, TRIPCAR8, TRIPNAVER, 호텔 할인코드, 항공권 할인, 공항픽업 쿠폰",
        jsonld=jsonld,
        scripts=script,
    )



def write_sitemap(out_root: Path, base: str):
    b = base.rstrip("/")
    urls = [(f"{b}/", "1.0", "weekly")]
    urls += [
        (f"{b}/cities/", "0.9", "weekly"),
    ]
    urls += [(f"{b}/{h['slug']}.html", "0.9", "weekly") for h in hub_list()]
    urls += [
        (f"{b}/guides/", "0.9", "weekly"),
    ]
    urls += [(f"{b}/guides/{g['slug']}.html", "0.8", "monthly") for g in GUIDES_LIST]
    urls += [
        (f"{b}/exchange.html", "0.8", "monthly"),
        (f"{b}/quiz.html", "0.9", "monthly"),
        (f"{b}/baggage.html", "0.8", "monthly"),
        (f"{b}/checklist.html", "0.9", "monthly"),
        (f"{b}/sos.html", "0.9", "monthly"),
        (f"{b}/stays.html", "0.9", "weekly"),
        (f"{b}/passes.html", "0.9", "monthly"),
        (f"{b}/calendar.html", "0.9", "monthly"),
        (f"{b}/coupons.html", "0.9", "weekly"),
        (f"{b}/about.html", "0.6", "monthly"),
        (f"{b}/contact.html", "0.6", "monthly"),
        (f"{b}/privacy.html", "0.4", "yearly"),
        (f"{b}/terms.html", "0.4", "yearly"),
    ]
    items = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{TODAY.isoformat()}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>"
        for u, p, c in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n</urlset>\n"
    )
    (out_root / "sitemap.xml").write_text(clean_site_urls(xml, b), encoding="utf-8")


def write_indexnow_key(out_root: Path):
    """v48: IndexNow 키 파일 — data/indexnow.json 의 key 를 `<key>.txt` 로 사이트 루트에 둡니다.

    IndexNow(빙·네이버·얀덱스 등 참여 검색엔진)는 이 파일로 소유 확인을 하므로,
    https://trippick.pages.dev/<key>.txt 가 200 으로 열려야 URL 제출이 유효합니다.
    """
    path = DATA / "indexnow.json"
    if not path.exists():
        return
    try:
        key = str(json.loads(path.read_text(encoding="utf-8")).get("key") or "").strip()
    except (OSError, ValueError):
        return
    if not re.fullmatch(r"[a-f0-9]{16,64}", key):
        return
    (out_root / f"{key}.txt").write_text(key + "\n", encoding="utf-8")


def write_assets(style: str, out_root: Path):
    extra = read(CONTENT / "pages.css")
    css = (
        "/* 트립픽 — template.html 의 <style> + content/pages.css (자동 생성, 직접 수정 금지) */\n"
        + style
        + "\n\n"
        + extra
    )
    (out_root / "assets").mkdir(parents=True, exist_ok=True)
    (out_root / "assets" / "site.css").write_text(css, encoding="utf-8")
    # v25: 이어보기·공유 스크립트도 배포 폴더로 복사(홈 index.html 과 서브페이지가 같이 씁니다)
    js_src = CONTENT / "v25.js"
    if js_src.exists():
        shutil.copy2(js_src, out_root / "assets" / "trip-save.js")
    # v35: 제휴 클릭 추적(tp_clicks_v1) + 「한 번에 예약·준비 묶음」 스크립트
    js35 = CONTENT / "v35.js"
    if js35.exists():
        shutil.copy2(js35, out_root / "assets" / "tp-v35.js")
        stale = out_root / "assets" / "tp-v34.js"
        if stale.exists():
            stale.unlink()
    # v42: 통합 퀵서치 · 어디든지 파인더 · 찜 견적서 · 비교 스크립트(홈·서브페이지 공통)
    # v43: 통합 퀵서치·찜 견적서(v42) + 내 여행 D-Day·★ 참고 글 저장
    js43 = CONTENT / "v43.js"
    if js43.exists():
        shutil.copy2(js43, out_root / "assets" / "tp-v43.js")
        for name in ("tp-v42.js", "tp-v41.js"):
            stale = out_root / "assets" / name
            if stale.exists():
                stale.unlink()
    # v44: /sos 국가 전환 · 현지어 큰 글씨 카드(이 페이지에서만 로드)
    js44 = CONTENT / "v44.js"
    if js44.exists():
        shutil.copy2(js44, out_root / "assets" / "tp-v44.js")
    # v22: Cloudflare Pages 캐시 헤더(_headers)도 배포 폴더로 복사
    hdr = ROOT / "_headers"
    if hdr.exists() and hdr.resolve() != (out_root / "_headers").resolve():
        shutil.copy2(hdr, out_root / "_headers")
    # v47: 자체 호스팅 Pretendard(assets/fonts/*.woff2 + pretendard.css) 동기화
    font_src = ROOT / "assets" / "fonts"
    if font_src.is_dir():
        font_dst = out_root / "assets" / "fonts"
        font_dst.mkdir(parents=True, exist_ok=True)
        for f in font_src.iterdir():
            if f.is_file() and (not (font_dst / f.name).exists()
                                or f.stat().st_mtime > (font_dst / f.name).stat().st_mtime):
                shutil.copy2(f, font_dst / f.name)
    # v20: 상품 이미지·에셋도 배포 폴더로 동기화(없거나 더 새로운 파일만 복사)
    for src_dir, dst_rel in ((ROOT / "assets" / "ess", "assets/ess"), (ROOT / "images", "images")):
        if not src_dir.is_dir():
            continue
        dst_dir = out_root / dst_rel
        for src in src_dir.rglob("*"):
            if not src.is_file():
                continue
            dst = dst_dir / src.relative_to(src_dir)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if (not dst.exists()) or src.stat().st_mtime > dst.stat().st_mtime:
                shutil.copy2(src, dst)


# ----------------------------------------------------------------------
# 내부 링크 검사
# ----------------------------------------------------------------------
def check_links(out_root: Path) -> int:
    import urllib.parse

    files = sorted(out_root.rglob("*.html"))
    ids = {}
    for f in files:
        t = read(f)
        ids[f.resolve()] = set(re.findall(r'id="([^"]+)"', t))
    bad = []
    anchor_only = []
    total = 0
    for f in files:
        t = read(f)
        hrefs = re.findall(r'<(?:a|link)\b[^>]*?\bhref="([^"]+)"', t)
        srcs = re.findall(r'<img\b[^>]*?\bsrc="([^"]+)"', t)
        for href in hrefs + srcs:
            if href.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
                continue
            if "' +" in href or "+'" in href or " esc(" in href:
                continue  # index.html 의 JS 문자열 템플릿
            total += 1
            path, _, frag = href.partition("#")
            path = urllib.parse.unquote(path).split("?")[0]
            if not path:
                if frag and f.resolve() not in ids:
                    anchor_only.append((f, href))
                elif frag and frag not in ids[f.resolve()]:
                    bad.append((f, href, "페이지 내 앵커 없음"))
                continue
            if path.startswith("/"):
                target = (out_root / path.lstrip("/")).resolve()
            else:
                target = (f.parent / path).resolve()
            if not target.exists() and not path.endswith("/"):
                # Cloudflare Pages 의 확장자 없는 주소 → 같은 이름의 .html 파일
                alt = Path(str(target) + ".html")
                if alt.exists():
                    target = alt
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                bad.append((f, href, "파일 없음"))
                continue
            if frag:
                tids = ids.get(target)
                if tids is None:
                    bad.append((f, href, "HTML 아님"))
                elif frag not in tids:
                    bad.append((f, href, "앵커 없음"))
    print(f"[link-check] HTML {len(files)}개 · 내부 링크 {total}개 검사")
    if anchor_only:
        print(f"[link-check] 페이지 내 '#' 링크 {len(anchor_only)}개(무시)")
    if bad:
        for f, href, why in bad[:40]:
            print(f"  ✗ {f.relative_to(out_root)} → {href} ({why})")
        print(f"[link-check] 실패 {len(bad)}건")
        return 1
    print("[link-check] 실패 0건")
    return 0


# ----------------------------------------------------------------------
def main():
    global SPRITE, TOTAL, TOURS, ESSENTIALS, GUIDES_LIST, CAT_NOTE
    global RESTAURANTS, GIFTS, TRIPCOM, EXTRA, KLOOK, PACKAGES, STAYS, SEASON_IDS

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT), help="출력 디렉터리 (기본: tour_hub)")
    ap.add_argument("--base", default="https://trippick.pages.dev", help="정본 URL")
    ap.add_argument("--check-links", action="store_true")
    ap.add_argument("--only", default="", help="'pages'·'guides'·'hubs' 중 하나만 생성")
    args = ap.parse_args()

    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    style, SPRITE = template_parts()
    tours = load_json("tours.json")
    TOTAL = len(tours["tours"])
    TOURS = tours["tours"]
    city_label = {c["id"]: c["name"] for c in tours.get("cities", [])}
    for t in TOURS:
        t["city_label"] = city_label.get(t["city"], "")
    ESSENTIALS = load_json("essentials.json")["products"]
    RESTAURANTS = load_json("restaurants.json")
    GIFTS = load_json("gifts.json")
    TRIPCOM = load_json("tripcom.json")
    KLOOK = load_json("klook.json")
    PACKAGES = load_json("packages.json")
    STAYS = load_json("stays.json")
    SEASON_IDS = {c["id"] for c in load_json("season.json")["cities"]}

    gspec = load_json("guides.json")
    GUIDES_LIST = gspec["guides"]
    # v38: 목록 카드·허브의 읽기 시간도 본문 글자수 기준으로 통일
    for _g in GUIDES_LIST:
        _p = GUIDES / f"{_g['slug']}.html"
        if _p.exists():
            _g["read"] = B.read_minutes(read(_p))
    CAT_NOTE = gspec.get("categoryNotes", {})
    EXTRA = load_json("guide_extra.json")

    write_assets(style, out_root)
    global GLOBAL_CSS
    GLOBAL_CSS = (out_root / "assets" / "site.css").read_text(encoding="utf-8")

    # v20: 홈(index.html)은 build.py가 만든 것을 그대로 배포 폴더로 복사한다.
    home = ROOT / "index.html"
    if home.exists() and home.resolve() != (out_root / "index.html").resolve():
        shutil.copy2(home, out_root / "index.html")
    # v50: 홈이 fetch 하는 정적 JSON(tp-data·tp-plans·tp-search·tp-compare)
    for _f in ("tp-data.json", "tp-plans.json", "tp-search.json", "tp-compare.json"):
        _src = ROOT / "data" / _f
        _dst = out_root / "data" / _f
        if _src.exists() and _src.resolve() != _dst.resolve():
            _dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(_src, _dst)

    made = []
    if args.only in ("", "pages"):
        for spec in gspec["pages"]:
            made.append(content_page(out_root, spec, args.base))
    if args.only in ("", "guides"):
        made.append(guides_index(out_root, args.base))
        for g in GUIDES_LIST:
            made.append(guide_page(out_root, g, args.base))
    if args.only in ("", "hubs"):
        made.append(cities_index(out_root, args.base))
        for hub in hub_list():
            made.append(hub_page(out_root, hub, args.base))

    if args.only in ("", "pages"):
        made.append(exchange_page(out_root, args.base))
        made.append(baggage_page(out_root, args.base))
        made.append(passes_page(out_root, args.base))
        made.append(calendar_page(out_root, args.base))
        made.append(sos_page(out_root, args.base))
        made.append(quiz_page(out_root, args.base))
        made.append(checklist_page(out_root, args.base))
        made.append(stays_page(out_root, args.base))
        made.append(coupons_page(out_root, args.base))

    if args.only == "":
        idx = build_search_index()
        payload = json.dumps(idx, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        (out_root / "search_index.json").write_text(payload, encoding="utf-8")
        if (ROOT / "search_index.json").resolve() != (out_root / "search_index.json").resolve():
            (ROOT / "search_index.json").write_text(payload, encoding="utf-8")

    write_sitemap(out_root, args.base)
    write_indexnow_key(out_root)
    not_found_page(out_root, args.base)
    print(f"[build_pages] {len(made)}개 페이지 + sitemap.xml + assets/site.css → {out_root}")
    for p in made:
        print("  ·", p.relative_to(out_root))

    if args.check_links:
        sys.exit(check_links(out_root))


if __name__ == "__main__":
    main()
