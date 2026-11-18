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
TODAY = date(2026, 11, 18)

# index.html 에 실제로 있는 앵커만 쓴다(build.py --check-links 로 검증)
NAV = [
    ("index.html#courses", "추천 코스", "courses"),
    ("index.html#planner", "예산 계산기", "planner"),
    ("index.html#checklist", "출국 준비", "checklist"),
    ("index.html#regions", "지역·투어", "regions"),
    ("guides/index.html", "여행 가이드", "guides"),
    ("index.html#essentials", "여행 필수품", "essentials"),
    ("index.html#alert", "특가 알림", "alert"),
    ("index.html#howto", "예약 전 체크", "howto"),
]

VERIFY_META = """<meta name="google-site-verification" content="LcZmYDzmsn2pIDvvwDXtLezOnQi8dEOjQ67-xBWdfCw" />
<meta name="google-site-verification" content="Y3lrh6zGKCcwxVcFKL8ujJ1QK1Xi4HjHaL2KhZLku78" />
<meta name="naver-site-verification" content="de9b4241355a3ab6e83e5c102d1f6f1e6f244302" />
<meta name="naver-site-verification" content="ab10e600052c8a46301698e6f7c1dd39c3c2aa95" />"""

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
        links.append(f'      <a href="{up}{href}"{f" class=\"on\"" if on else ""}>{label}</a>')
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
<link rel="stylesheet" href="{up}assets/site.css" />
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
      <p class="side-note">가격은 2026-11-17 확인 기준 최저가입니다. 예약·구매 시점에 상세페이지에서 최종 확인하세요.</p>
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


ADSENSE_CLIENT = "ca-pub-0000000000000000"


def ad_slot(slot: str, title: str, text: str, href: str, cta: str, kicker: str = "트립픽 추천") -> str:
    """가이드·목록 페이지용 광고 슬롯.
    승인 전에는 내부 추천 배너만 보이고(빈 <ins> 없음) 레이아웃이 깨지지 않습니다.
    승인 후에는 주석을 풀고 {client}·data-ad-slot 두 값만 바꾸면 바로 켜집니다."""
    return f'''<aside class="adslot adslot--flat" data-ad-slot="{slot}" aria-label="광고·추천 영역">
  <!-- 주석을 풀고 ca-pub-… / data-ad-slot 값만 넣으면 애드센스가 표시됩니다(승인 후).
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
    return f"""    <div class="side-card">
      <h3>바로가기</h3>
      <p>코스·상품·필수품을 한 화면에서 같은 기준으로 비교합니다.</p>
      <a class="go" href="{up}index.html#planner">내 예산으로 총액 계산 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#essentials">여행 필수품 보기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#gifts">나라별 선물·기념품 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#checklist">출국 준비 체크리스트 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#tripcom">도시별 숙소·항공권 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}index.html#regions">지역별 투어 보기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      <a class="go" href="{up}guides/index.html">가이드 전체 보기 <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </div>"""


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
        <span>업데이트 {g['updated'].replace('-', '.')}</span><i></i>
        <span>읽는 시간 약 {g['read']}분</span><i></i>
        <span>{esc(g.get('fxNote') or '가격 확인 2026.11.17')}</span>
      </div>
    </div>
{hero_img}
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="pg-grid">
      <article class="doc">
{body_html}
      </article>
      <aside class="pg-side">
{product_cards(g)}
{related_guides(g)}
{side_common('../')}
      </aside>
    </div>
{cta_band('../', g.get('ctaTitle', '이 글의 계산, 내 일정으로 해보기'), g.get('ctaText', '인원과 지역을 넣으면 항공·숙소·투어·eSIM까지 같은 기준으로 총액을 계산합니다.'))}
  </div>
</div>"""

    body = body.replace(
        '<div class="pg-grid">',
        ad_slot(
            "guide-top",
            "숙소·항공은 도시별 최저가로",
            "트립닷컴 파트너스 링크로 도시 15곳 숙소와 항공 6개 노선을 모았습니다.",
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

    sections = []
    for cat in cats:
        cards = []
        for g in [x for x in GUIDES_LIST if x["category"] == cat]:
            thumb = (
                f'<div class="thumb"><img src="../{esc(g["image"])}" alt="{esc(g["imageAlt"])}" loading="lazy" width="640" height="360" /></div>'
                if g.get("image")
                else '<div class="thumb noimg">TRIPPICK GUIDE</div>'
            )
            cards.append(
                f"""        <a class="gcard" href="{g['slug']}.html">
          {thumb}
          <div class="gc-body">
            <span class="tag">{esc(g['category'])}</span>
            <h3>{esc(g['navTitle'])}</h3>
            <p>{esc(g['dek'])}</p>
            <div class="gc-foot"><b>{g['read']}분</b> · {g['updated'].replace('-', '.')} 업데이트</div>
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
        <span>최근 업데이트 {TODAY.strftime('%Y.%m.%d')}</span>
      </div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="gi-intro">
      <div><b>가격은 ‘실질 1인가’로</b><p>표시가에 현장 추가금(입장료·팁·가이드 경비)을 더한 금액으로 비교합니다. 싼 상품이 실제로 싼지 여기서 갈립니다.</p></div>
      <div><b>패스는 손익분기부터</b><p>주유패스·지하철패스는 “하루 몇 번 타면 본전”을 먼저 계산합니다. 일정이 3일이어도 매일 타지 않으면 손해입니다.</p></div>
      <div><b>기준 시점을 밝힙니다</b><p>모든 글에 확인 날짜와 환율을 적었습니다. 요금은 개정되므로 결제 직전에 공식 안내를 한 번 더 확인하세요.</p></div>
    </div>
{chr(10).join(sections)}
{ad_slot("guides-index-bottom", "이 글들의 계산, 내 날짜로 해보기", "지역·인원·스타일을 넣으면 항공+숙소+투어+eSIM을 한 번에 계산합니다.", "../index.html#planner", "예산 계산기")}
{cta_band('../', '읽고 끝내지 말고, 내 날짜로 계산하기', '지역·인원·스타일을 넣으면 항공+숙소+투어+eSIM을 한 번에 계산해 A/B/C안으로 보여줍니다.')}
  </div>
</div>"""

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
# sitemap
# ----------------------------------------------------------------------
def write_sitemap(out_root: Path, base: str):
    b = base.rstrip("/")
    urls = [(f"{b}/", "1.0", "weekly")]
    urls += [
        (f"{b}/guides/", "0.9", "weekly"),
    ]
    urls += [(f"{b}/guides/{g['slug']}.html", "0.8", "monthly") for g in GUIDES_LIST]
    urls += [
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
            path = urllib.parse.unquote(path)
            if not path:
                if frag and f.resolve() not in ids:
                    anchor_only.append((f, href))
                elif frag and frag not in ids[f.resolve()]:
                    bad.append((f, href, "페이지 내 앵커 없음"))
                continue
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

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT), help="출력 디렉터리 (기본: tour_hub)")
    ap.add_argument("--base", default="https://trippick.pages.dev", help="정본 URL")
    ap.add_argument("--check-links", action="store_true")
    ap.add_argument("--only", default="", help="'pages' 또는 'guides' 만 생성")
    args = ap.parse_args()

    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    style, SPRITE = template_parts()
    tours = load_json("tours.json")
    TOTAL = len(tours["tours"])
    TOURS = tours["tours"]
    ESSENTIALS = load_json("essentials.json")["products"]

    gspec = load_json("guides.json")
    GUIDES_LIST = gspec["guides"]
    CAT_NOTE = gspec.get("categoryNotes", {})

    write_assets(style, out_root)

    made = []
    if args.only in ("", "pages"):
        for spec in gspec["pages"]:
            made.append(content_page(out_root, spec, args.base))
    if args.only in ("", "guides"):
        made.append(guides_index(out_root, args.base))
        for g in GUIDES_LIST:
            made.append(guide_page(out_root, g, args.base))

    write_sitemap(out_root, args.base)
    print(f"[build_pages] {len(made)}개 페이지 + sitemap.xml + assets/site.css → {out_root}")
    for p in made:
        print("  ·", p.relative_to(out_root))

    if args.check_links:
        sys.exit(check_links(out_root))


if __name__ == "__main__":
    main()
