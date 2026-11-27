#!/usr/bin/env python3
"""v66 검증 — 신규 가이드 12편 + 사이트맵 219 URL + 허브·지역 연결.

    python3 tools/verify_v66.py

1. 가이드 171편 · 도시 허브 32곳 · 찐숙소 171곳 · 지역 코드 12개(말레이시아 추가)
2. 신규 12편: 본문 3,000자(공백 제외)·표 5개·h2 5개·FAQ 5문항·제휴 5건·이미지·OG·확인값
3. 사이트맵 219 URL · sitemap-index 3분할 합계 일치 · sitemap-guides 172 · 중복 0
4. 허브 연결: /london /fukuoka /okinawa /sydney 에 신규 편 링크, /guides/ 171편 표기
5. 역링크: 기존 가이드에서 신규 편으로 가는 본문 링크
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT.parent / "deploy_site"
DATA = ROOT / "data"
G = ROOT / "content" / "guides"
SITE = "https://trippick.pages.dev"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

fails: list[str] = []


def check(ok: bool, msg: str):
    if ok:
        print("  ✓", msg)
    else:
        fails.append(msg)
        print("  ✗", msg)


def load(n):
    return json.loads((DATA / n).read_text(encoding="utf-8"))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


guides = load("guides.json")["guides"]
by_slug = {g["slug"]: g for g in guides}
hubs = load("city_hubs.json")["cities"]
extra = load("guide_extra.json")

print("[1] 데이터 규모")
check(len(guides) == 171, f"가이드 {len(guides)}편 (기대 171)")
check(len(hubs) == 32, f"도시 허브 {len(hubs)}곳 (기대 32)")
check("my" in {r["code"] for r in extra["regions"]}, "지역 코드에 말레이시아(my)")

print("[2] 신규 12편")
NEW = {
    "la-las-vegas-grand-canyon-course": ["$100", "$35", "$99.95", "1.75", "51.02"],
    "london-4n5d-course-budget": ["£37.70", "£8.90", "£5.90", "£21", "20:30"],
    "dubai-stopover-3n4d-guide": ["AED 189", "AED 25", "7.50", "90일", "AED 99"],
    "melbourne-sydney-6n7d-guide": ["$25.90", "$34", "$19.30", "$18.61", "$104"],
    "japan-small-cities-comparison": ["1,300엔", "1,000엔", "1,400엔", "1,500엔", "1,200엔"],
    "okinawa-rental-car-bus-guide": ["6,600엔", "1,040엔", "1,610엔", "290엔", "1,000엔"],
    "europe-night-train-ryanair-guide": ["£21.49", "£39", "€39", "€37.90", "£6.99"],
    "travel-adapter-voltage-world-guide": ["220V", "100V", "120V", "G형", "100–240V"],
    "bali-driver-nusa-penida-guide": ["550,000", "170,000", "25,000", "15,000", "60,000"],
    "fukuoka-hakata-tenjin-shopping-guide": ["1,000엔", "280엔", "5,000엔", "10:00~21:00", "24시간"],
    "malaysia-kuala-lumpur-2n3d-guide": ["RM55", "RM2.60", "RM127", "RM10", "28분"],
    "hawaii-island-hopping-guide": ["$49", "$42", "$30", "$1", "$55"],
}
for slug, tokens in NEW.items():
    g = by_slug.get(slug)
    check(g is not None, f"{slug}: guides.json 항목")
    if not g:
        continue
    check(len(g.get("seoTitle") or "") <= 60, f"{slug}: seoTitle {len(g.get('seoTitle') or '')}자")
    html = read(G / f"{slug}.html")
    text = re.sub(r"<[^>]+>", " ", html)
    chars = len(re.sub(r"\s", "", text))
    check(chars >= 3000, f"{slug}: 본문 {chars}자 (기대 3,000+)")
    check(html.count("<table") >= 5, f"{slug}: 표 {html.count('<table')}개 (기대 5+)")
    check(len(re.findall(r"<h2\b", html)) >= 5, f"{slug}: h2 {len(re.findall(r'<h2', html))}개")
    check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항")
    check(html.count('class="gact-link"') >= 5, f"{slug}: 제휴 링크 {html.count('gact-link')}건")
    for t in tokens:
        check(t in text or t in html, f"{slug}: 확인값 {t}")
    check((ROOT / g["image"]).exists(), f"{slug}: 히어로 이미지 파일")
    check((ROOT / g["ogImage"]).exists(), f"{slug}: OG 이미지 파일")
    webp = (ROOT / g["image"]).with_name((ROOT / g["image"]).stem + "-720.webp")
    check(webp.exists(), f"{slug}: WebP 720 변형")
    page = read(OUT / "guides" / f"{slug}.html")
    check(bool(page), f"{slug}: 페이지 생성")
    if page:
        check("<!-- @FAQ -->" not in page, f"{slug}: FAQ 토큰 미치환")
        check("FAQPage" in page, f"{slug}: FAQ 구조화 데이터")
        check(any(x in page for x in ("../exchange", "../passes", "../checklist", "../sos")),
              f"{slug}: 도구 링크")

print("[3] 허브·역링크")
HUB = {"london": "london-4n5d-course-budget", "fukuoka": "fukuoka-hakata-tenjin-shopping-guide",
       "okinawa": "okinawa-rental-car-bus-guide", "sydney": "melbourne-sydney-6n7d-guide"}
for hub, slug in HUB.items():
    page = read(OUT / f"{hub}.html")
    check(f"/guides/{slug}" in page or f"{slug}.html" in page, f"/{hub} 에 {slug} 링크")
BACK = {
    "sydney-4n5d-course": "melbourne-sydney-6n7d-guide",
    "okinawa-3n4d-course": "okinawa-rental-car-bus-guide",
    "fukuoka-yufuin-3n4d-course": "fukuoka-hakata-tenjin-shopping-guide",
    "london-transport-heathrow-guide": "london-4n5d-course-budget",
    "bali-ubud-seminyak-3n4d-course": "bali-driver-nusa-penida-guide",
    "hawaii-oahu-5n7d-course": "hawaii-island-hopping-guide",
    "us-west-4canyons": "la-las-vegas-grand-canyon-course",
    "singapore-3n4d-course-budget": "malaysia-kuala-lumpur-2n3d-guide",
    "travel-card-packing-guide": "travel-adapter-voltage-world-guide",
    "europe-train-eurail-vs-point": "europe-night-train-ryanair-guide",
}
for src, dst in BACK.items():
    check(f"{dst}.html" in read(G / f"{src}.html"), f"역링크 {src} → {dst}")

print("[4] 사이트맵 219 URL")
sm = read(OUT / "sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
check(len(locs) == 219, f"sitemap.xml {len(locs)} URL (기대 219)")
check(len(set(locs)) == len(locs), "sitemap 중복 0")
for slug in NEW:
    check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug}")
idx = ET.fromstring(read(OUT / "sitemap-index.xml"))
parts = [e.text for e in idx.findall("sm:sitemap/sm:loc", NS)]
check(len(parts) == 3, f"sitemap-index 분할 {len(parts)}개")
tot = 0
for p in parts:
    name = p.rsplit("/", 1)[-1]
    n = len(re.findall(r"<loc>", read(OUT / name)))
    tot += n
    print(f"    · {name}: {n}")
check(tot == len(locs), f"sitemap-index 합계 {tot} = sitemap {len(locs)}")
check(len(re.findall(r"<loc>", read(OUT / "sitemap-hubs.xml"))) == 32, "sitemap-hubs 32")
check(len(re.findall(r"<loc>", read(OUT / "sitemap-guides.xml"))) == 172, "sitemap-guides 172")

print("[5] 표기 숫자")
gi = re.sub(r"\s+", " ", read(OUT / "guides" / "index.html"))
check("가이드 171편" in gi, "/guides/ 171편 표기")
st = read(OUT / "stays.html")
check("171" in st, "/stays 171곳 표기")

print()
if fails:
    print(f"[verify_v66] 실패 {len(fails)}건")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("[verify_v66] PASS — 가이드 171 · 신규 12 · 사이트맵 219 · 허브 32 · 숙소 171")
