#!/usr/bin/env python3
"""v64 검증 — 신규 가이드 8편 + 사이트맵 225 URL + 허브 연결.

    python3 tools/verify_v64.py

1. 가이드 177편 · 신규 8편(미국 ESTA·영국 ETA·간사이공항·뉴욕 4박5일·나고야 3박4일·
   일본 식당 예약·마카오 1박2일·파리 교통권) 메타·본문·이미지
2. 본문 3,000자 이상 · 표 5개 이상 · h2 6개 이상 · FAQ 5문항 · 제휴 링크 5건 이상
3. sitemap.xml 225 URL + /sitemap-index.xml 3분할 합계 일치 · 중복 0
4. 허브·기존 가이드 상호 연결 · 도구 링크 2종 이상
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

print("[1] 가이드 177편")
check(len(guides) == 177, f"가이드 {len(guides)}편 (기대 177)")

NEW = {
    "us-esta-application-guide": ["$40.62", "2년", "90일", "72시간", "10.62"],
    "uk-eta-application-guide": ["£20", "6개월", "2년", "3영업일", "2025"],
    "kansai-airport-osaka-kyoto-transfer": ["970엔", "1,210엔", "2,700엔", "1,410엔", "23:55"],
    "new-york-4n5d-course-budget": ["$8.75", "$3.00", "$35", "$26", "$46"],
    "nagoya-3n4d-course-budget": ["1,430엔", "3,300엔", "3,600", "1,000엔", "110엔"],
    "japan-restaurant-reservation-guide": ["440엔", "390엔", "100%", "4,000엔", "お通し"],
    "macau-1n2d-ferry-bus-guide": ["194", "65", "MOP6", "MOP12", "MOP13"],
    "paris-metro-navigo-guide": ["€2.55", "€14", "€32.40", "€2", "€57.70"],
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
    check(all("Allianceid=11407530" in u or "link.coupang.com" in u for u in links),
          "제휴 링크 ID 유지")
    img = ROOT / g["image"]
    check(img.exists() and img.stat().st_size > 40_000, f"히어로 {g['image']}")
    for w in (480, 720, 960):
        wp = img.with_name(f"{slug}-{w}.webp")
        check(wp.exists(), f"WebP {w}")
    og = ROOT / g["ogImage"]
    check(og.exists() and og.stat().st_size > 50_000, f"OG {g['ogImage']}")
    page = OUT / "guides" / f"{slug}.html"
    html = page.read_text(encoding="utf-8")
    check('"@type": "Article"' in html or '"@type":"Article"' in html, "Article JSON-LD")
    check("FAQPage" in html, "FAQPage JSON-LD")
    check(f"/guides/{slug}\"" in html or f"/guides/{slug}<" in html, "canonical 확장자 없음")
    check(all(m in body for m in must), f"확인값 표기 {must}")
    check("<!-- @FAQ -->" not in html, "@FAQ 마커 치환")

print("[2] 내부 도구 링크")
for slug in NEW:
    body = (G / f"{slug}.html").read_text(encoding="utf-8")
    tools = {t for t in ("../checklist.html", "../exchange.html", "../sos.html",
                         "../coupons.html", "../stays.html", "../passes.html") if t in body}
    check(len(tools) >= 2, f"{slug} 도구 링크 {len(tools)}종 {sorted(tools)}")

print("[3] 사이트맵")
sm = ET.parse(OUT / "sitemap.xml").getroot()
locs = [e.text for e in sm.findall("sm:url/sm:loc", NS)]
check(len(locs) == 225, f"sitemap.xml {len(locs)} URL (기대 225)")
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

print("[4] 허브·기존 가이드 연결")
gi = (OUT / "guides" / "index.html").read_text(encoding="utf-8")
check("177편" in gi, "/guides/ 171편 표기")
for hub, slug in (("macau", "macau-1n2d-ferry-bus-guide"),
                  ("paris", "paris-metro-navigo-guide"),
                  ("osaka", "kansai-airport-osaka-kyoto-transfer")):
    hub_html = (OUT / f"{hub}.html").read_text(encoding="utf-8")
    check(slug in hub_html, f"/{hub} 허브에 {slug} 연결")
for src, dst in (("entry-immigration-guide", "us-esta-application-guide"),
                 ("entry-immigration-guide", "uk-eta-application-guide"),
                 ("hongkong-macau-3n4d-course", "macau-1n2d-ferry-bus-guide"),
                 ("paris-london-5n7d", "paris-metro-navigo-guide"),
                 ("osaka-usj-transfer", "kansai-airport-osaka-kyoto-transfer"),
                 ("tokyo-food-route", "japan-restaurant-reservation-guide")):
    row = by_slug.get(src) or {}
    check(dst in row.get("related", []), f"역링크 {src} → {dst}")

print()
if fails:
    print(f"실패 {len(fails)}건:")
    for m in fails:
        print(" -", m)
    raise SystemExit(1)
print("모든 검사 통과")
