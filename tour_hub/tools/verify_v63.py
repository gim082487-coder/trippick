#!/usr/bin/env python3
"""v63 검증 — 신규 가이드 3편 + sitemap-index 분리 + 레거시 정리.

    python3 tools/verify_v63.py

1. 가이드 138편 · 신규 3편(도쿄 3박4일·무비자 체류기간·동남아 렌터카) 메타·본문·이미지
2. sitemap.xml 180 URL 그대로 + /sitemap-index.xml 3분할(core·hubs·guides) 합 180 · 중복 0
3. robots.txt 두 줄(Sitemap + Sitemap index) · 레거시 tour_hub/exchange.html 제거
4. 제휴 링크 파라미터(Allianceid=11407530·SID=336341874·rel=sponsored) 유지
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

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
fails: list[str] = []


def check(ok: bool, msg: str):
    if ok:
        print("  ✓", msg)
    else:
        fails.append(msg)
        print("  ✗", msg)


guides = json.loads((DATA / "guides.json").read_text(encoding="utf-8"))["guides"]
by_slug = {g["slug"]: g for g in guides}

print("[1] 가이드 166편")
check(len(guides) == 166, f"가이드 {len(guides)}편 (기대 166)")

NEW = {
    "tokyo-3n4d-course-budget": ["1,060엔", "1,500엔", "1,800엔", "2,700엔", "72시간"],
    "visa-free-stay-duration-guide": ["90일", "45일", "30일", "500,000루피아", "2028"],
    "southeast-asia-rental-car-license-guide": ["9,000원", "2023", "90일", "발리", "무면허"],
}

for slug, must in NEW.items():
    print(f"[신규] {slug}")
    g = by_slug.get(slug)
    check(bool(g), "guides.json 등록")
    if not g:
        continue
    body = (G / f"{slug}.html").read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", "", body)
    text = re.sub(r"\s+", "", text)
    check(len(text) >= 3000, f"본문 {len(text)}자 (3,000자 이상)")
    check(len(re.findall(r"<table", body)) >= 5, f"표 {len(re.findall(r'<table', body))}개")
    check(len(re.findall(r"<h2", body)) >= 6, f"h2 {len(re.findall(r'<h2', body))}개")
    check(len(g.get("faq", [])) == 5, f"FAQ {len(g.get('faq', []))}문항")
    links = re.findall(r'href="(https://[^"]+)"[^>]*rel="[^"]*sponsored', body)
    check(len(links) >= 5, f"제휴 링크 {len(links)}개")
    check(all("Allianceid=11407530" in u or "link.coupang.com" in u or "naver.me" in u for u in links),
          "제휴 링크 ID 유지")
    img = ROOT / g["image"]
    check(img.exists() and img.stat().st_size > 40_000, f"히어로 {g['image']}")
    for w in (480, 720, 960):
        wp = img.with_name(f"{slug}-{w}.webp")
        check(wp.exists(), f"WebP {w}")
    og = ROOT / g["ogImage"]
    check(og.exists() and og.stat().st_size > 50_000, f"OG {g['ogImage']}")
    for token in ("/checklist", "/exchange", "/sos", "/coupons", "/stays"):
        pass
    page = OUT / "guides" / f"{slug}.html"
    html = page.read_text(encoding="utf-8")
    check('"@type": "Article"' in html or '"@type":"Article"' in html, "Article JSON-LD")
    check("FAQPage" in html, "FAQPage JSON-LD")
    check(f"/guides/{slug}\"" in html or f"/guides/{slug}<" in html, "canonical 확장자 없음")
    check(all(m in body for m in must), f"확인값 표기 {must}")
    check("<!-- @FAQ -->" not in html, "@FAQ 마커 치환")

print("[2] 내부 도구 링크")
tool_link_counts = {}
for slug in NEW:
    body = (G / f"{slug}.html").read_text(encoding="utf-8")
    tools = {t for t in ("../checklist.html", "../exchange.html", "../sos.html", "../coupons.html", "../stays.html") if t in body}
    tool_link_counts[slug] = tools
    check(len(tools) >= 2, f"{slug} 도구 링크 {len(tools)}종 {sorted(tools)}")

print("[3] 사이트맵")
sm = ET.parse(OUT / "sitemap.xml").getroot()
locs = [e.text for e in sm.findall("sm:url/sm:loc", NS)]
check(len(locs) == 214, f"sitemap.xml {len(locs)} URL (기대 214)")
check(len(set(locs)) == len(locs), "sitemap.xml 중복 0")
for slug in NEW:
    check(f"https://trippick.pages.dev/guides/{slug}" in locs, f"sitemap 포함 {slug}")

idx = ET.parse(OUT / "sitemap-index.xml").getroot()
children = [e.text for e in idx.findall("sm:sitemap/sm:loc", NS)]
check(len(children) == 3, f"sitemap-index 자식 {len(children)}개")
all_child: list[str] = []
for url in children:
    name = url.rsplit("/", 1)[-1]
    f = OUT / name
    check(f.exists(), f"{name} 존재")
    if not f.exists():
        continue
    root = ET.parse(f).getroot()
    clocs = [e.text for e in root.findall("sm:url/sm:loc", NS)]
    check(len(clocs) > 0, f"{name} {len(clocs)} URL")
    check(len(set(clocs)) == len(clocs), f"{name} 중복 0")
    all_child += clocs
check(len(all_child) == len(locs), f"분할 합계 {len(all_child)} = sitemap {len(locs)}")
check(set(all_child) == set(locs), "분할·단일 사이트맵 URL 집합 동일")

robots = (OUT / "robots.txt").read_text(encoding="utf-8")
check("Sitemap: https://trippick.pages.dev/sitemap.xml" in robots, "robots.txt sitemap.xml")
check("Sitemap: https://trippick.pages.dev/sitemap-index.xml" in robots, "robots.txt sitemap-index.xml")

print("[4] 레거시 정리·색인")
check(not (ROOT / "exchange.html").exists(), "레거시 tour_hub/exchange.html 제거")
check((ROOT / "content" / "pages" / "exchange.html").exists(), "정본 content/pages/exchange.html 유지")
gi = (OUT / "guides" / "index.html").read_text(encoding="utf-8")
check("166편" in gi, "/guides/ 166편 표기")
tokyo = (OUT / "tokyo.html").read_text(encoding="utf-8")
check("tokyo-3n4d-course-budget" in tokyo, "/tokyo 허브에 신규 가이드 연결")
check((OUT / "exchange.html").exists(), "/exchange 빌드 정상")

print()
if fails:
    print(f"실패 {len(fails)}건:")
    for m in fails:
        print(" -", m)
    raise SystemExit(1)
print("모든 검사 통과")
