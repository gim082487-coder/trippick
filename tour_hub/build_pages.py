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
from datetime import date
from pathlib import Path

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
TODAY = date(2026, 11, 20)
CSS_V = "23"   # assets/site.css 캐시 버전 — CSS·디자인을 바꿀 때 함께 올린다

# index.html 에 실제로 있는 앵커만 쓴다(build.py --check-links 로 검증)
# v18: 메뉴 9개 + '도구' 드롭다운 1개. 1280px에서 한 줄에 들어오도록 계산기·표 페이지는 드롭다운으로 묶는다.
NAV = [
    ("index.html#courses", "추천 코스", "courses"),
    ("index.html#planner", "예산 계산기", "planner"),
    ("index.html#checklist", "출국 준비", "checklist"),
    ("index.html#regions", "지역·투어", "regions"),
    ("cities/index.html", "도시별", "cities"),
    ("stays.html", "찐숙소", "stays"),
    ("guides/index.html", "여행 가이드", "guides"),
    ("index.html#foods", "맛집", "foods"),
    ("index.html#essentials", "여행 필수품", "essentials"),
    ("index.html#alert", "특가 알림", "alert"),
]

# 드롭다운에 들어가는 계산기·표 페이지 (v18에 /passes · /calendar 추가)
TOOLS = [
    ("exchange.html", "환율·일본 면세 계산기", "exchange", "12개 통화 · 면세 환급"),
    ("baggage.html", "항공사 수하물 규정", "baggage", "기내·위탁·배터리"),
    ("passes.html", "교통패스 본전 계산기", "passes", "오사카·도쿄·방콕·타이베이"),
    ("calendar.html", "월별 시즌 캘린더", "calendar", "7개 도시 12개월"),
]
TOOL_KEYS = {k for _, _, k, _ in TOOLS}

# 1080px 이하에서 숨길 보조 메뉴(핵심 메뉴와 드롭다운만 남긴다)
HIDE_SM = {"checklist", "foods", "alert"}
STAYS: dict = {}   # data/stays.json — v21 /stays
KLOOK: dict = {}   # data/klook.json (main 에서 채운다)
PACKAGES: dict = {}  # data/packages.json — v20 고단가 패키지

# 도시 허브 → /passes 탭 (없는 도시는 전체 페이지로)
HUB_PASS_TOOL = {
    "osaka": ("passes.html#osaka", "오사카 주유패스, 사면 남는가", "시설 체크로 본전 계산"),
    "tokyo": ("passes.html#tokyo", "도쿄 지하철 패스·나리타 비교", "24·48·72시간 본전"),
    "bangkok": ("passes.html#bangkok", "방콕 BTS 1일권 본전", "150밧 vs 개별권"),
    "taipei": ("passes.html#taipei", "타이베이 펑패스 vs 이지카드", "1·2·3·5일 비교"),
    "fukuoka": ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이"),
    "danang": ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이"),
    "jeju": ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이"),
}

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
          <a href="{up}index.html#checklist">출국 준비 체크</a>
          <a href="{up}exchange.html">환율·일본 면세 계산기</a>
          <a href="{up}baggage.html">항공사 수하물 규정</a>
          <a href="{up}passes.html">교통패스 본전 계산기</a>
          <a href="{up}calendar.html">월별 시즌·최저가 캘린더</a>
          <a href="{up}cities/index.html">도시별 여행 페이지</a>
          <a href="{up}stays.html">찐숙소 — 국내·해외 {len(STAYS.get("hotels", [])) or 30}곳</a>
          <a href="{up}guides/index.html">여행 가이드</a>
          <a href="{up}index.html#alert">특가 알림</a>
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
) -> Path:
    up = "../" * rel_path.count("/")
    canonical = f"{base.rstrip('/')}/{rel_path}"
    if rel_path.endswith("index.html"):
        canonical = f"{base.rstrip('/')}/{rel_path[: -len('index.html')]}"
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
<meta property="og:image" content="{og_image or (base.rstrip('/') + '/images/courses/hero_kyoto_street.jpg')}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<meta name="twitter:image" content="{og_image or (base.rstrip('/') + '/images/courses/hero_kyoto_street.jpg')}" />
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css" />
<link rel="stylesheet" href="{up}assets/site.css?v={CSS_V}" />
<link rel="icon" href="{FAVICON}" />
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
</body>
</html>
"""
    target = out_root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(clean_site_urls(head, base), encoding="utf-8")
    return target


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
      <a class="go" href="{up}index.html#checklist">출국 준비 체크리스트 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
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
# 가이드 페이지
# ----------------------------------------------------------------------
def guide_page(out_root: Path, g: dict, base: str) -> Path:
    slug = g["slug"]
    body_html = read(GUIDES / f"{slug}.html")
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
        hero_img = f"""      <figure class="pg-hero-img">
        <img src="../{esc(g['image'])}" alt="{esc(g['imageAlt'])}" width="1200" height="630" loading="eager" />
        <figcaption>{esc(g.get('imageCredit', '사진: Pexels'))}</figcaption>
      </figure>"""

    related_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": strip_tags(g["h1"]),
            "description": g["desc"],
            "datePublished": g["published"],
            "dateModified": g["updated"],
            "inLanguage": "ko",
            "author": {"@type": "Organization", "name": SITE_NAME},
            "publisher": {"@type": "Organization", "name": SITE_NAME},
            "mainEntityOfPage": f"{base.rstrip('/')}/guides/{slug}.html",
            "image": f"{base.rstrip('/')}/{g['image']}" if g.get("image") else None,
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
                {"@type": "ListItem", "position": 3, "name": g["navTitle"]},
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
    </div>
{hero_img}
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="pg-grid">
      <article class="doc">
{guide_summary(g)}
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
{cta_band('../', g.get('ctaTitle', '이 글의 계산, 내 일정으로 해보기'), g.get('ctaText', '인원과 지역을 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 총액을 계산합니다.'))}
  </div>
</div>"""

    body = body.replace(
        '<div class="pg-grid">',
        ad_slot(
            "guide-top",
            "숙소·항공은 도시별 최저가로",
            "트립닷컴 파트너스 링크로 도시 15곳 숙소·항공 6개 노선에 입장권·공항픽업·렌터카 16종, eSIM 5개 도시·공항철도 2개 노선을 더했습니다.",
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
        og_image=f"{base.rstrip('/')}/{g['image']}" if g.get("image") else "",
        jsonld=f'<script type="application/ld+json">{related_json}</script>\n<script type="application/ld+json">{breadcrumb}</script>',
    )


def guides_index(out_root: Path, base: str) -> Path:
    cats = []
    for g in GUIDES_LIST:
        if g["category"] not in cats:
            cats.append(g["category"])

    region_names = {r["code"]: r["name"] for r in EXTRA.get("regions", [])}

    sections = []
    for cat in cats:
        cards = []
        for g in [x for x in GUIDES_LIST if x["category"] == cat]:
            ex = guide_extra(g["slug"])
            thumb = (
                f'<div class="thumb"><img src="../{esc(g["image"])}" alt="{esc(g["imageAlt"])}" loading="lazy" width="640" height="360" /></div>'
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
        <p>국내 서울·부산·강릉·여수·경주와 해외 8개 도시 숙소를 트립닷컴 평점·리뷰 수·1박 최저가로 비교했습니다. 호캉스·수영장, 오션뷰, 온천·스파, 역세권·도보, 가성비, 가족·풀빌라로 바로 좁힐 수 있습니다.</p></div>
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
            f"나리타·하네다 공항에서 시내까지, 교토 버스투어 vs 자유일정, 오사카 주유패스·도쿄 지하철패스 본전, "
            f"오사카·교토 3박4일 실경비, 방콕·이탈리아 패키지 실지출, 괌 리조트 조식 비교, 다낭 우기, 제주·울릉·강원, "
            f"일본·베트남 eSIM, 미서부·미동부·스페인·포르투갈·호주·뉴질랜드 장거리 실지출, 다낭 54홀 vs 푸꾸옥 36홀 골프, "
            f"장가계 특별약관, 보조배터리·액체류 기내 규정, 일본·베트남·대만·태국 기념품 리스트까지. 예약 전에 숫자로 확인하는 여행 가이드 {len(GUIDES_LIST)}편."
        ),
        body=body,
        base=base,
        active="guides",
        keywords="여행 가이드, 나리타 공항 시내 이동, 교토 버스투어 비교, 오사카 주유패스 본전, 도쿄 지하철 패스, 오사카 교토 3박4일 경비, 방콕 패키지 실지출, 이탈리아 패키지 비교, 괌 리조트 비교, 다낭 우기, 제주 3박4일, 울릉도 배편, 강원 스키장 비교, 일본 eSIM, 베트남 eSIM, 일본 기념품 리스트, 다낭 기념품, 대만 펑리수, 태국 기념품",
        jsonld=f'<script type="application/ld+json">{listing}</script>',
    )


# ----------------------------------------------------------------------
# 필수 페이지 (소개·개인정보·약관·문의)
# ----------------------------------------------------------------------
def content_page(out_root: Path, spec: dict, base: str) -> Path:
    slug = spec["slug"]
    body_html = read(PAGES / f"{slug}.html")
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
        jsonld=f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": spec["navTitle"], "url": f"{base.rstrip('/')}/{slug}.html", "inLanguage": "ko", "dateModified": spec["updated"]}, ensure_ascii=False)}</script>',
    )


# ----------------------------------------------------------------------
# 도시별 허브 페이지 (/osaka · /tokyo …) + /cities/
# ----------------------------------------------------------------------
_hub_cache = None
HUB_ORDER = ["osaka", "tokyo", "fukuoka", "danang", "bangkok", "taipei", "jeju"]


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
        "ids": ["jp-esim-usimsa-kddi-1d", "jp-esim-lingsim-1d", "jp-esim-usimsa-3d-tokyo"],
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
        "ids": ["th-esim-usimsa-1d", "th-esim-usimsa-3d"],
    },
    "tw": {
        "title": "eSIM, 1일 760원부터",
        "lead": "2박3일이면 3일 무제한 한 장이 계산이 쉽고, 4일 이상 머물면 1일권을 날짜별로 붙이는 쪽이 쌉니다. "
                "두 상품 모두 출발 전 설치형이라 공항에서 줄 서지 않습니다.",
        "ids": ["tw-esim-lingsim-1d", "tw-esim-usimsa-3d"],
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
        badge = "1일권" if "1d" in eid else "3일 무제한"
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
    <div class="hub-fx">2026.11.20 네이버 쇼핑 커넥트 확인</div>
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
            f'<div class="thumb"><img src="{esc(g["image"])}" alt="{esc(g["imageAlt"])}" loading="lazy" width="640" height="360" /></div>'
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
    graph = {"@context": "https://schema.org", "@graph": [page_ld, dest, tour_ld, guide_ld, crumb]}
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
        slug, ("passes.html", "교통패스 본전 계산기", "오사카·도쿄·방콕·타이베이")
    )
    hub_tools_html = f"""<div class="hub-tools" aria-label="{esc(hub['name'])} 도구">
  <a class="hub-tool" href="{pass_href}"><span class="hub-tool-k">PASS</span><b>{esc(pass_title)}</b><span class="hub-tool-n">{esc(pass_sub)}</span></a>
  <a class="hub-tool" href="calendar.html#{slug}"><span class="hub-tool-k">SEASON</span><b>{esc(hub['name'])} 12개월 날씨·가격</b><span class="hub-tool-n">성수기·항공권 참고가</span></a>
</div>"""

    meta = [f'<span><b>트립픽 편집</b></span>', '<i></i>', '<span>업데이트 2026.11.20</span>', '<i></i>']
    meta.append(f'<span>투어·패키지 {len(tours)}개</span><i></i>')
    meta.append(f'<span>1인 {won(lowest)}원~</span>')
    if rest:
        meta.append(f'<i></i><span>맛집 {len(rest["items"])}곳</span>')
    if hub_acts:
        meta.append(f'<i></i><span>입장권·픽업 {len(hub_acts)}</span>')
    meta.append(f'<i></i><span>가이드 {len(guides)}편</span>')

    # 투어 섹션
    tour_rows = "\n            ".join(B.table_row(t) for t in tours)
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
    <b>맛집 5곳은 아직 검증을 마치지 않았습니다.</b>
    <p>영업 중인지(구글 지도 OPERATIONAL), 공식 메뉴판 가격이 맞는지 확인한 가게만 싣기 때문에 국내 도시는 다음 업데이트에 넣습니다. 그전까지는 아래 가이드에서 식비와 동선을 볼 수 있습니다.</p>
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
      <p>국내 여행이라 면세 한도·반입 규정이 따로 없습니다. 대신 현지에서 사기 번거로운 준비물을 집에서 미리 주문하는 링크만 모았습니다.</p></div>
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
    _stays = {r['id']: r for r in STAYS.get('regions', [])}
    _pick = _stays.get(slug)
    stay_pick_link = (
        f'<a class="hub-stay-pick" href="stays.html#{_pick["id"]}">'
        f'<b>{esc(hub["name"])} 찐숙소 {_pick["count"]}곳</b>'
        f'<span>평점·리뷰 수·1박 가격으로 고른 숙소 — 최고 평점 {esc(_pick["top"])}</span>'
        f'<i>보기 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></i></a>'
        if _pick else ''
    )
    stay_html = f"""<section class="hub-sec" id="stay">  <div class="hub-sec-head">
    <div><span class="hub-k">STAY &amp; FLIGHT &amp; TICKET</span>
      <h2>{esc(hub['name'])} 숙소·항공권·입장권</h2>
      <p>트립닷컴에서 직접 예약하는 숙소·항공권과, 현지에서 쓸 입장권·공항픽업·eSIM·공항철도입니다. 체크인 날짜와 방문일을 넣으면 그날 요금으로 열리고, 예약·결제는 트립닷컴에서 그대로 이루어집니다.</p></div>
  </div>
  <div class="tc-group">
    <div class="ess-ghead"><h3>🏨 {esc(hub['name'])} 숙소</h3><span class="n">{len(hotels)}</span><span class="line" aria-hidden="true"></span><span class="ess-gnote">체크인 날짜 기준 최저가</span></div>
    <div class="tc-grid hub-tc">{hub_hotel_cards(hotels)}</div>
    {stay_pick_link}
  </div>
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
    <nav class="hub-jump" aria-label="이 페이지 목차">{jump_html}</nav>
{hub_tools_html}
{ad_slot(f"hub-{slug}-top", "이 도시 숙소·항공 최저가", "체크인 날짜만 넣으면 트립닷컴 최저가로 열립니다.", "#stay", "숙소 보기")}
{tours_html}
{ad_slot(f"hub-{slug}-mid", "이 도시 일정, 내 예산으로 계산", "인원·지역·스타일만 넣으면 항공·숙소·투어·eSIM 총액을 A/B/C안으로 보여줍니다.", "index.html#planner", "예산 계산기")}
{food_html}
{gift_html}
{stay_html}
{hub_esim_section(hub)}
{ad_slot(f"hub-{slug}-bottom", "특가가 뜨면 가장 먼저 알려드릴게요", "원하는 여행지와 예산만 남기면 특가·땡처리 소식을 메일로 보내드립니다.", "index.html#alert", "알림 신청")}
{guides_html}

    <div class="hub-others">
      <b>다른 도시 여행 페이지</b>
      <div class="hub-city-row">{others}<a class="hub-city-chip" href="cities/index.html"><b>도시 전체 보기</b></a></div>
    </div>

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
        og_image=f"{base.rstrip('/')}/{hub['image']}",
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
        jsonld=f'<script type="application/ld+json">{listing}</script>\n<script type="application/ld+json">{crumb}</script>',
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
              <span class="cpd-top"><img src="{c["img"]}" alt="" width="52" height="52" loading="lazy" />
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
    body = body.replace("<!-- @OSAKA_PASSES -->", chips)
    body = body.replace("<!-- @OSAKA_FACILITIES -->", facs)
    body = body.replace("<!-- @TOKYO_TICKETS -->", tok_chips)
    body = body.replace("<!-- @NARITA_ROWS -->", narita_rows)
    body = body.replace("<!-- @TAIPEI_PASSES -->", tpe_chips)
    for slug in ("osaka", "tokyo", "bangkok", "taipei"):
        body = body.replace(f"<!-- @LINKS_{slug.upper()} -->", pass_links(slug))
    payload = json.dumps({"fx": data["fx"], "osaka": data["osaka"], "tokyo": data["tokyo"],
                          "bangkok": data["bangkok"], "taipei": data["taipei"]},
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
    ]
    jsonld = _page_jsonld(
        "passes.html",
        "트립픽 교통패스 본전 계산기",
        "오사카 주유패스·도쿄 지하철 패스·방콕 BTS·타이베이 펀패스가 내 일정에서 본전을 넘는지 계산하는 도구.",
        base,
        faq,
        [("트립픽", ""), ("교통패스 본전 계산기", None)],
    )
    return page(
        out_root,
        "passes.html",
        title="교통패스 본전 계산기 — 오사카 주유패스·도쿄 지하철·BTS·펀패스 | 트립픽",
        desc="오사카 주유패스 3,500엔, 도쿄 지하철 800/1,200/1,500엔, 방콕 BTS 150밧, 타이베이 펀패스 210대만달러가 내 일정에서 본전을 넘는지 계산합니다. 시설 입장료와 지하철 횟수를 넣으면 엔·바트·대만달러와 원화로 이득·손해가 나옵니다.",
        body=body,
        base=base,
        active="passes",
        keywords="오사카 주유패스 본전, 도쿄 지하철 패스, 나리타 스카이라이너, 방콕 BTS 1일권, 타이베이 펀패스, 교통패스 계산기",
        jsonld=jsonld,
    )


def season_links(c: dict) -> dict:
    out = {}
    f = _tc_flight(c.get("flightRoute") or "")
    if f:
        out["flight"] = {"label": f"{f['route']} 항공권", "url": f["url"]}
    h = _tc("hotels", cityId=c.get("hotelCity"))
    if h:
        out["hotel"] = {"label": f"{h['city']} 숙소", "url": h["url"]}
    t = _tc("tickets", id=f"ticket_{c['id']}")
    if t:
        out["ticket"] = {"label": t["title"], "url": t["url"]}
    if c.get("guide"):
        g = next((x for x in GUIDES_LIST if x["slug"] == c["guide"]), None)
        if g:
            out["guide"] = {"label": g["navTitle"], "url": f"guides/{g['slug']}.html"}
    out["cityPage"] = f"/{c['cityPage']}"
    return out


def calendar_page(out_root: Path, base: str) -> Path:
    data = load_json("season.json")
    cities = data["cities"]
    flags = {c["id"]: c.get("flag", "") for c in cities}
    city_btns = "\n            ".join(
        f'<button type="button" class="sc-city{" on" if i == 0 else ""}" data-city-btn="{c["id"]}" aria-pressed="{"true" if i == 0 else "false"}">'
        f'{B.flag_svg(flags.get(c["id"], ""), 18, 12.6)}<b>{esc(c["name"])}</b></button>'
        for i, c in enumerate(cities)
    )
    month_btns = "\n            ".join(
        f'<button type="button" class="sc-month{" on" if m == 11 else ""}" data-month-btn="{m}" aria-pressed="{"true" if m == 11 else "false"}">'
        f'<b>{m}월</b><small data-month-temp="{m}">–</small></button>'
        for m in range(1, 13)
    )

    season_kr = {"peak": "성수기", "shoulder": "준성수기", "off": "비수기"}
    # 비교표(빌드 시점 이번 달 = 11월) — JS가 선택한 달로 다시 그린다.
    cm = 11
    cmp_rows = []
    for c in cities:
        band = c["fare"][c["season"][cm - 1]]
        cmp_rows.append(
            f'<tr data-city-row="{c["id"]}"><th scope="row"><b>{esc(c["name"])}</b></th>'
            f'<td>{c["temp"][cm - 1]:.1f}°C</td><td>{_n(c["rain"][cm - 1])}mm</td>'
            f'<td>{c["rainDays"][cm - 1]:.1f}일</td>'
            f'<td><span class="sc-season {c["season"][cm - 1]}">{season_kr[c["season"][cm - 1]]}</span></td>'
            f'<td class="num">약 {band[0] / 10000:.0f}~{band[1] / 10000:.0f}만원</td></tr>'
        )
    year_rows = []
    for c in cities:
        cells = "".join(
            f'<td><button type="button" class="sc-cell {c["season"][i]}" data-year-cell="{c["id"]}-{i + 1}" '
            f'aria-label="{esc(c["name"])} {i + 1}월 {c["temp"][i]:.1f}도 {season_kr[c["season"][i]]}">'
            f'<b>{c["temp"][i]:.0f}°</b><span>{c["rain"][i]:.0f}</span></button></td>'
            for i in range(12)
        )
        year_rows.append(f'<tr><th scope="row">{esc(c["name"])}</th>{cells}</tr>')

    body = read(PAGES / "calendar.html")
    body = body.replace("<!-- @SC_CITIES -->", city_btns)
    body = body.replace("<!-- @SC_MONTHS -->", month_btns)
    body = body.replace("<!-- @SC_CMP_ROWS -->", "\n                ".join(cmp_rows))
    body = body.replace("<!-- @SC_YEAR_ROWS -->", "\n              ".join(year_rows))

    payload_cities = []
    for c in cities:
        cc = dict(c)
        cc["links"] = season_links(c)
        payload_cities.append(cc)
    payload = json.dumps({"updated": data["updated"], "lead": data["lead"], "cities": payload_cities},
                         ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = body.replace("<!-- @SC_DATA -->", f'<script type="application/json" id="scData">{payload}</script>')

    faq = [
        ("오사카·도쿄는 언제가 가장 싼가요?",
         "1월 중순~2월 초와 6월 장마철입니다. 벚꽃·골든위크·오봉·연말에는 같은 항공권이 1.5~2배가 됩니다."),
        ("다낭 우기 9~12월은 피해야 하나요?",
         "10~11월은 한 달에 20일 비가 오고 450~630mm가 내립니다. 9월과 12월은 가격이 30% 이상 낮아 리조트 휴양이면 선택지가 됩니다."),
        ("항공권은 언제 예약해야 싼가요?",
         "국제선 성수기는 출발 10~16주 전, 비수기는 3~6주 전이 가장 쌉니다. 제주 등 국내선은 성수기 4~8주, 비수기 2~4주 전입니다."),
        ("성수기 구분은 무엇을 기준으로 했나요?",
         "각국 공휴일과 학교 방학, 골든위크·오봉·송크란·춘절 같은 현지 축제 일정, 최근 판매 흐름을 기준으로 정리했습니다."),
    ]
    jsonld = _page_jsonld(
        "calendar.html",
        "트립픽 월별 시즌·최저가 캘린더",
        "오사카·도쿄·후쿠오카·다낭·방콕·타이베이·제주의 1~12월 기온·강수량·성수기와 항공권 참고 가격대, 예약 시점을 비교하는 캘린더.",
        base,
        faq,
        [("트립픽", ""), ("월별 시즌 캘린더", None)],
    )
    return page(
        out_root,
        "calendar.html",
        title="월별 여행 시즌 캘린더 — 7개 도시 12개월 날씨·성수기·항공권 가격대 | 트립픽",
        desc="오사카·도쿄·후쿠오카·다낭·방콕·타이베이·제주의 1~12월 평균기온·강수량·비 온 날·성수기와 항공권 참고 가격대, 예약 시점을 한 화면에서 비교합니다. 달을 고르면 그 달의 항공·숙소·투어 링크로 바로 이어집니다.",
        body=body,
        base=base,
        active="calendar",
        keywords="여행 성수기, 비수기, 오사카 날씨, 도쿄 날씨, 다낭 우기, 방콕 우기, 타이베이 장마, 제주 성수기, 항공권 예약 시점",
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


def _stay_tags(h: dict) -> str:
    names = _stay_theme_name()
    out = []
    for t in (h.get("themes") or [])[:2]:
        if t in names:
            out.append(f'<span class="sc-theme t-{t}">{esc(names[t])}</span>')
    for p in (h.get("pointTags") or [])[:2]:
        out.append(f'<span class="sc-pt">{esc(p)}</span>')
    if not out:
        return ""
    return '<div class="sc-tags">' + "".join(out) + "</div>"


def stays_card(h: dict, region: dict) -> str:
    sub = _stay_subs(h)
    scope = region.get("scope", "intl")
    flag = "국내" if scope == "kr" else (region.get("country") or "해외")
    return f"""    <article class="scard" data-region="{h['region']}" data-scope="{scope}" data-type="{h['type']}" data-themes="{' '.join(h.get('themes') or [])}" data-score="{h['score']}" data-price="{h['price']}">
      <a class="sc-thumb" href="{esc(h['url'])}" target="_blank" rel="noopener sponsored" aria-label="{esc(h['name'])} 트립닷컴에서 보기">
        <img src="{esc(h['img'])}" alt="{esc(region['name'])} {esc(h['name'])} 숙소 사진" width="720" height="480" loading="lazy" />
        <span class="sc-score{_stay_score_class(h['score'])}">{h['score']:.1f}</span>
        <span class="sc-type">{esc(h['typeLabel'])}</span>
      </a>
      <div class="sc-body">
        <div class="sc-top"><span class="sc-region">{esc(region['name'])} <i class="sc-flag{' kr' if scope == 'kr' else ''}">{esc(flag)}</i></span><i></i><span>{h['star']}성</span></div>
        <h3><a href="{esc(h['url'])}" target="_blank" rel="noopener sponsored">{esc(h['name'])}</a></h3>
        <p class="sc-loc"><svg aria-hidden="true"><use href="#i-pin"/></svg><span>{esc(h['access'])}</span></p>
        <p class="sc-reason">{esc(h['reason'])}</p>
        {_stay_tags(h)}
        {sub}
        <div class="sc-foot">
          <span class="sc-price"><b>{h['price']:,}원</b>1박~</span>
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
        "description": "국내 5개 도시와 해외 8개 도시 숙소를 트립닷컴 평점·리뷰 수·1박 최저가로 비교하고, 테마(호캉스·오션뷰·온천·역세권·가성비·가족)로 골라 도시 가이드로 이어집니다.",
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
    ("osaka", "osaka"), ("tokyo", "tokyo"), ("fukuoka", "fukuoka"), ("yufuin", "fukuoka"),
    ("danang", "danang"), ("hoian", "danang"), ("nhatrang", "nhatrang"), ("dalat", "nhatrang"),
    ("bangkok", "bangkok"), ("taipei", "taipei"), ("yehliu", "taipei"), ("jiufen", "taipei"),
    ("jeju", "jeju"), ("busan", "busan"), ("gangwon", "gangneung"), ("ulleung", "gangneung"),
    ("seoul", "seoul"), ("yeosu", "yeosu"), ("gyeongju", "gyeongju"),
]
STAYS_GUIDE_THEME = {"winter": "onsen", "esim": "station", "packing": "value", "powerbank": "value"}


def guide_stays_box(g: dict) -> str:
    """가이드 → /stays 지역·테마 연결 박스(v23). 지역을 알 수 없으면 테마로 잇는다."""
    regions = {r["id"]: r for r in STAYS.get("regions", [])}
    hotels = STAYS.get("hotels", [])
    slug = g.get("slug", "")
    target = None
    for key, rid in STAYS_GUIDE_REGION:
        if key in slug and rid in regions:
            target = regions[rid]
            break
    if target:
        n = sum(1 for h in hotels if h["region"] == target["id"])
        if not n:
            target = None
    theme = None
    for key, tid in STAYS_GUIDE_THEME.items():
        if key in slug:
            theme = tid
            break
    if not target and not theme:
        theme = "ocean"
    names = {t["id"]: t["name"] for t in (STAYS.get("themes") or [])}
    rows = []
    if target:
        rows.append(
            f'<a class="gsb-go" href="../stays.html#{target["id"]}"><b>{esc(target["name"])} 찐숙소 {n}곳</b>'
            f'<span>평점·리뷰 수·1박 최저가로 고른 숙소 — 최고 평점 {esc(target["top"])}</span></a>'
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
    price_min = min(h["price"] for h in hotels)
    price_max = max(h["price"] for h in hotels)
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
    theme_chips = "".join(
        f'<button class="gf-chip" type="button" data-theme="{t}">{esc(theme_name[t])} '
        f'<span>{sum(1 for h in hotels if t in (h.get("themes") or []))}</span></button>'
        for t in STAY_THEME_ORDER if t in theme_name
    )
    cards = []
    for r, hs in groups:
        for h in hs:
            cards.append(stays_card(h, r))

    region_anchors = "".join(f'<span id="{r["id"]}"></span>' for r, _ in groups)
    region_links = "".join(
        f'<a class="sr-gitem" href="#{r["id"]}" data-jump="{r["id"]}">'
        f'<b>{esc(r["name"])} <span>{len(hs)}곳</span>{" <i class=\'sr-kr\'>국내</i>" if r.get("scope") == "kr" else ""}</b>'
        f'<span class="sr-range">1박 {min(h["price"] for h in hs):,}~{max(h["price"] for h in hs):,}원 · 평점 {min(h["score"] for h in hs):.1f}~{max(h["score"] for h in hs):.1f}</span>'
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
    intro = (
        '<div><b>평점은 리뷰 수와 같이</b><p>트립닷컴 투숙객 리뷰 10점 만점 점수입니다. 리뷰가 수백 개 쌓인 곳과 신규 오픈으로 수십 개인 곳을 구분해 리뷰 수를 카드에 같이 적었습니다.</p></div>'
        f'<div><b>국내 {kr_total}곳 · 해외 {intl_total}곳</b><p>국내는 서울·부산·강릉·여수·경주 {kr_total}곳(2026-11-20~21 조회), 해외는 오사카·도쿄·후쿠오카·다낭·나트랑·방콕·타이베이·제주 {intl_total}곳(2026-11-19~20 조회)입니다.</p></div>'
        '<div><b>예약은 트립닷컴에서</b><p>카드의 예약 버튼은 그 숙소의 트립닷컴 페이지로 바로 갑니다. 결제·취소는 트립닷컴 약관을 따릅니다.</p></div>'
    )

    body = f"""<div class="pg-hero stays-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><b>찐숙소</b></nav>
    <span class="pg-kicker">TRIPPICK STAYS · 국내 {len(kr_groups)}개 도시 + 해외 {len(intl_groups)}개 도시 {total}곳</span>
    <div class="pg-head">
      <h1><em>찐숙소</em> {total}곳 — 테마로 고르고, 가이드로 이어집니다</h1>
      <p class="dek">서울·부산·강릉·여수·경주 국내 {kr_total}곳을 새로 넣어 <b>국내·해외 13개 도시 {total}곳</b>을 한 화면에 올렸습니다.
      평점 <b>{score_min:.1f}~{score_max:.1f}</b>, 1박 <b>{price_min:,}~{price_max:,}원</b> 구간이고, 호캉스·수영장, 오션뷰, 온천·스파, 역세권·도보, 가성비, 가족·풀빌라 테마로 바로 좁힐 수 있습니다.
      평점·리뷰 수·가격은 트립닷컴 목록의 실제 값을 그대로 옮겼고, 예약 버튼은 파트너스 딥링크로 연결됩니다.</p>
      <div class="pg-meta">
        <span><b>트립픽 숙소 편집</b></span><i></i>
        <span>{total}곳 · {len(groups)}개 도시</span><i></i>
        <span>가격 확인 {source.get('checked', '2026-11-20').replace('-', '.')}</span><i></i>
        <span>1박·2인·세금 포함</span>
      </div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
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
      <div class="sf-row">
        <div class="sf-chips" role="group" aria-label="테마">
          <button class="gf-chip on" type="button" data-theme="all">테마 전체</button>
          {theme_chips}
        </div>
        <div class="sf-sort" role="group" aria-label="정렬">
          <button class="gf-chip on" type="button" data-sort="score">평점 높은 순</button>
          <button class="gf-chip" type="button" data-sort="price">가격 낮은 순</button>
        </div>
        <span class="sf-count"><b id="sfCount">{total}</b>곳</span>
      </div>
    </div>

    <div class="stays-intro">{intro}</div>
    <div class="sf-anchors" aria-hidden="true">{region_anchors}</div>

    <div class="sgrid" id="sgrid">
{chr(10).join(cards)}
    </div>

    <div class="gfind-empty" id="sfEmpty" hidden>
      <b>조건에 맞는 숙소가 없습니다.</b>
      <p>국내/해외·지역·테마를 ‘전체’로 바꿔 보세요. 테마는 호캉스·수영장, 오션뷰, 온천·스파, 역세권·도보, 가성비, 가족·풀빌라 여섯 가지입니다.</p>
      <button type="button" id="sfReset">필터 초기화</button>
    </div>

    <h2 class="sr-h2">테마로 바로 보기</h2>
    <div class="th-grid" aria-label="테마 바로가기">
      {theme_cards}
    </div>

    <h2 class="sr-h2">지역별로 이렇게 갈립니다</h2>
    <div class="sr-regions" aria-label="지역 바로가기">
      {region_links}
    </div>

    <h2 class="sr-h2">숙소를 골랐으면 — 그 도시 동선과 예약</h2>
    <p class="sr-dek">숙소 위치를 정한 뒤에는 그 도시의 코스·맛집·교통 가이드로 이어서 보세요. 국내는 부산 요트·강원 스키·제주 3박4일 가이드를 연결하고, 서울·여수·경주는 국내 가이드 모아보기와 트립닷컴 숙소 목록으로 이어집니다.</p>
    <div class="sg-grid" aria-label="지역별 가이드 연결">
      {guide_cards}
    </div>

    <div class="sr-band">
      <div><b>이 도시 전체 숙소를 날짜 넣고 비교하려면</b>
        <p>트립닷컴 도시 숙소 목록에서 체크인 날짜·인원을 넣으면 그날 요금으로 정렬됩니다. 카드의 예약 버튼은 숙소 한 곳으로 바로 갑니다.</p></div>
      <a class="btn-line" href="cities/index.html">도시별 여행 페이지 <svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </div>

    <p class="snote"><b>숫자 읽는 법</b> — 평점은 트립닷컴 투숙객 리뷰 10점 만점 기준이고, 옆의 리뷰 수와 함께 봐야 합니다.
    가격은 카드에 적힌 조회 날짜의 <b>1박, 성인 2명, 세금·서비스비용 포함</b> 최저가입니다(국내 19곳 2026-11-20~21, 해외 30곳 2026-11-19~20).
    같은 숙소도 날짜·객실·잔여 상황에 따라 달라지므로 결제 직전 트립닷컴 결제 화면의 금액을 최종으로 확인하세요. 숙소 사진은 트립닷컴 숙소 페이지 이미지입니다.</p>

    <p class="snote"><b>제휴 고지</b> — 이 페이지의 예약 버튼은 트립닷컴 파트너스 제휴 링크입니다.
    예약이 이루어지면 트립픽이 트립닷컴으로부터 수수료를 받을 수 있으며, 구매자가 지불하는 금액에는 영향이 없습니다.
    숙소 선정과 순서는 평점·리뷰 수·위치를 기준으로 편집했고, 수수료율에 따라 배열하지 않았습니다.</p>
  </div>
</div>
{stays_filter_script()}"""

    return page(
        out_root,
        "stays.html",
        title=f"국내·해외 테마별 찐숙소 {total}곳 — 서울·부산·강릉·여수·경주 + 해외 8개 도시 평점·가격 비교 (2026) | 트립픽",
        desc=(
            f"국내 서울·부산·강릉·여수·경주와 해외 오사카·도쿄·후쿠오카·다낭·나트랑·방콕·타이베이·제주 숙소 {total}곳을 "
            f"트립닷컴 평점·리뷰 수·1박 최저가(세금 포함)로 비교했습니다. 평점 {score_min:.1f}~{score_max:.1f}, 1박 {price_min:,}~{price_max:,}원. "
            "호캉스·수영장, 오션뷰, 온천·스파, 역세권·도보, 가성비, 가족·풀빌라 테마 필터와 국내/해외 구분, 도시 가이드 연결, 예약은 트립닷컴 제휴 딥링크. 2026-11-20 확인."
        ),
        keywords=(
            "국내 호텔 추천, 서울 호텔, 부산 호텔, 강릉 호텔, 여수 호텔, 경주 호텔, 오션뷰 호텔, 호캉스 호텔, 온천 호텔, "
            "가성비 호텔, 가족 호텔, 풀빌라, 오사카 호텔 추천, 도쿄 호텔 추천, 다낭 리조트 추천, 제주 호텔 추천, 트립닷컴 숙소"
        ),
        body=body,
        base=base,
        active="stays",
        jsonld=f'<script type="application/ld+json">{stays_jsonld(base, groups)}</script>',
    )


def stays_filter_script() -> str:
    return """<script>
(function(){
  var grid = document.getElementById('sgrid');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.scard'));
  var countEl = document.getElementById('sfCount');
  var emptyEl = document.getElementById('sfEmpty');
  var scopeBtns = Array.prototype.slice.call(document.querySelectorAll('[data-scope]'));
  var regionBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-chips [data-region]'));
  var themeBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-chips [data-theme]'));
  var sortBtns = Array.prototype.slice.call(document.querySelectorAll('.sf-sort [data-sort]'));
  var state = { scope: 'all', region: 'all', theme: 'all', sort: 'score' };

  function scoreOf(c){ return parseFloat(c.getAttribute('data-score')) || 0; }
  function priceOf(c){ return parseInt(c.getAttribute('data-price'), 10) || 0; }
  function themesOf(c){ return (c.getAttribute('data-themes') || '').split(' ').filter(Boolean); }

  function render(sync){
    var shown = cards.filter(function(c){
      var okS = state.scope === 'all' || c.getAttribute('data-scope') === state.scope;
      var okR = state.region === 'all' || c.getAttribute('data-region') === state.region;
      var okT = state.theme === 'all' || themesOf(c).indexOf(state.theme) >= 0;
      return okS && okR && okT;
    });
    shown.sort(function(a, b){
      return state.sort === 'price' ? priceOf(a) - priceOf(b) : scoreOf(b) - scoreOf(a);
    });
    cards.forEach(function(c){ c.hidden = true; });
    shown.forEach(function(c){ c.hidden = false; grid.appendChild(c); });
    countEl.textContent = shown.length;
    emptyEl.hidden = shown.length > 0;
    if (sync !== false && window.history && history.replaceState){
      var p = [];
      if (state.scope !== 'all') p.push('scope=' + state.scope);
      if (state.region !== 'all') p.push('region=' + state.region);
      if (state.theme !== 'all') p.push('theme=' + state.theme);
      if (state.sort !== 'score') p.push('sort=' + state.sort);
      var url = location.pathname + (p.length ? '?' + p.join('&') : '');
      history.replaceState(null, '', url);
    }
  }

  function mark(btns, el){
    btns.forEach(function(b){ b.classList.toggle('on', b === el); });
  }
  function bind(btns, key, attr){
    btns.forEach(function(btn){
      btn.addEventListener('click', function(){
        mark(btns, btn);
        state[key] = btn.getAttribute(attr);
        if (key === 'scope' && state.region !== 'all'){
          var r = regionBtns.filter(function(b){ return b.getAttribute('data-region') === state.region; })[0];
          if (r && r.getAttribute('data-scope') && r.getAttribute('data-scope') !== state.scope){ state.region = 'all'; mark(regionBtns, regionBtns[0]); }
        }
        render();
      });
    });
  }
  bind(scopeBtns, 'scope', 'data-scope');
  bind(regionBtns, 'region', 'data-region');
  bind(themeBtns, 'theme', 'data-theme');
  bind(sortBtns, 'sort', 'data-sort');

  function setRegion(id){
    var target = regionBtns.filter(function(b){ return b.getAttribute('data-region') === id; })[0];
    if (!target) return;
    mark(regionBtns, target);
    state.region = id;
    var sc = target.getAttribute('data-scope');
    if (sc){ mark(scopeBtns, scopeBtns[0]); }
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
  var qTheme = qs.get('theme'), qRegion = qs.get('region'), qScope = qs.get('scope'), qSort = qs.get('sort');
  var needJump = false;
  if (qScope){ var sb = scopeBtns.filter(function(b){ return b.getAttribute('data-scope') === qScope; })[0]; if (sb){ mark(scopeBtns, sb); state.scope = qScope; } }
  if (qRegion){ setRegion(qRegion); needJump = true; }
  if (qTheme){ var tb = themeBtns.filter(function(b){ return b.getAttribute('data-theme') === qTheme; })[0]; if (tb){ mark(themeBtns, tb); state.theme = qTheme; } }
  if (qSort){ var so = sortBtns.filter(function(b){ return b.getAttribute('data-sort') === qSort; })[0]; if (so){ mark(sortBtns, so); state.sort = qSort; } }
  if (location.hash && location.hash.length > 1) setRegion(location.hash.slice(1));
  window.addEventListener('hashchange', function(){
    if (location.hash && location.hash.length > 1) setRegion(location.hash.slice(1));
  });

  var fold = document.getElementById('sfFold');
  if (fold) fold.addEventListener('click', function(){
    var sf = document.getElementById('sf');
    var open = sf.classList.toggle('open-regions');
    fold.setAttribute('aria-expanded', open ? 'true' : 'false');
    fold.innerHTML = open ? '지역 선택 <i>▴</i>' : '지역 선택 <i>▾</i>';
  });

  var reset = document.getElementById('sfReset');
  if (reset) reset.addEventListener('click', function(){
    state.scope = 'all'; state.region = 'all'; state.theme = 'all';
    mark(scopeBtns, scopeBtns[0]); mark(regionBtns, regionBtns[0]); mark(themeBtns, themeBtns[0]);
    render();
  });
  render(false);
  if (needJump){ var sf = document.getElementById('sf'); if (sf && sf.scrollIntoView) sf.scrollIntoView({ block: 'start' }); }
})();
</script>"""



def not_found_page(out_root: Path, base: str) -> Path:
    """없는 주소용 404.html — 홈으로 되돌리는 동선과 인기 페어지를 둔다(noindex)."""
    links = "".join(
        f'<a href="{u}">{esc(n)}</a>'
        for u, n in [
            ("/", "홈"),
            ("/guides/", f"여행 가이드 {len(GUIDES_LIST)}편"),
            ("/cities/", "도시별 페이지 7곳"),
            ("/osaka", "오사카·교토"),
            ("/tokyo", "도쿄"),
            ("/danang", "다낭·호이안"),
            ("/jeju", "제주"),
            ("/#checklist", "출국 체크리스트"),
            ("/exchange", "환율·면세 계산기"),
            ("/baggage", "수하물 규정"),
            ("/passes", "교통패스 본전 계산기"),
            ("/calendar", "월별 시즌 캘린더"),
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
        desc="요청한 주소가 없습니다. 여행 가이드 44편·도시별 페이지 7곳·출국 체크리스트로 연결합니다.",
        body=body,
        base=base,
    )
    t = p.read_text(encoding="utf-8")
    t = t.replace(
        '<meta name="robots" content="index, follow, max-image-preview:large" />',
        '<meta name="robots" content="noindex, follow" />',
        1,
    )
    p.write_text(t, encoding="utf-8")
    return p


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
        (f"{b}/baggage.html", "0.8", "monthly"),
        (f"{b}/stays.html", "0.9", "weekly"),
        (f"{b}/passes.html", "0.9", "monthly"),
        (f"{b}/calendar.html", "0.9", "monthly"),
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
    # v22: Cloudflare Pages 캐시 헤더(_headers)도 배포 폴더로 복사
    hdr = ROOT / "_headers"
    if hdr.exists():
        shutil.copy2(hdr, out_root / "_headers")
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
    global RESTAURANTS, GIFTS, TRIPCOM, EXTRA, KLOOK, PACKAGES, STAYS

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

    gspec = load_json("guides.json")
    GUIDES_LIST = gspec["guides"]
    CAT_NOTE = gspec.get("categoryNotes", {})
    EXTRA = load_json("guide_extra.json")

    write_assets(style, out_root)

    # v20: 홈(index.html)은 build.py가 만든 것을 그대로 배포 폴더로 복사한다.
    home = ROOT / "index.html"
    if home.exists() and home.resolve() != (out_root / "index.html").resolve():
        shutil.copy2(home, out_root / "index.html")

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
        made.append(stays_page(out_root, args.base))

    write_sitemap(out_root, args.base)
    not_found_page(out_root, args.base)
    print(f"[build_pages] {len(made)}개 페이지 + sitemap.xml + assets/site.css → {out_root}")
    for p in made:
        print("  ·", p.relative_to(out_root))

    if args.check_links:
        sys.exit(check_links(out_root))


if __name__ == "__main__":
    main()
