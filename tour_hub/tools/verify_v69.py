#!/usr/bin/env python3
"""v69 검증 — 신규 가이드 3편(미국 렌터카·바르셀로나·튀르키예) + 사이트맵 225 URL.

    python3 tools/verify_v69.py

1. 가이드 177편 · 허브 32곳 · 찐숙소 182곳(지역 42곳)
2. 신규 3편: 본문 3,000자(공백 제외)·표 8개 이상·h2 6개 이상·FAQ 5문항·제휴 6건·이미지·OG·확인값
3. 사이트맵 225 URL · sitemap-index 3분할 합계 일치 · sitemap-guides 178 · 중복 0
4. 역링크 6편 → 신규 3편 · /guides/ 177편 표기
5. 클룩 코드(KLKUSCAR10%·KLKEUTOUR20%) 쿠폰 페이지 수록 · 서치콘솔 action.md 225개
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
stays = load("stays.json")

print("[1] 데이터 규모")
check(len(guides) == 177, f"가이드 {len(guides)}편 (기대 177)")
check(len(hubs) == 32, f"도시 허브 {len(hubs)}곳 (기대 32)")
check(len(stays["hotels"]) == 182, f"찐숙소 {len(stays['hotels'])}곳 (기대 182)")
check(len(stays["regions"]) == 42, f"숙소 지역 {len(stays['regions'])}곳 (기대 42)")

print("[2] 신규 3편")
NEW = {
    "usa-rental-car-insurance-guide": ["9,000원", "26.99", "42.38", "3.5476", "10.25", "9.99", "33.99", "4.95"],
    "barcelona-gaudi-montserrat-3n4d-guide": ["26", "36", "40", "18", "13.00", "2.90", "7.75", "13.30", "50"],
    "turkey-istanbul-cappadocia-guide": ["46.20", "165", "470", "2,750", "105", "260", "160", "1,950"],
}
from PIL import Image  # noqa: E402

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
    check(html.count("<table") >= 8, f"{slug}: 표 {html.count('<table')}개 (기대 8+)")
    check(len(re.findall(r"<h2\b", html)) >= 6, f"{slug}: h2 {len(re.findall(r'<h2', html))}개")
    check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항")
    check(html.count('class="gact-link"') >= 6, f"{slug}: 제휴 링크 {html.count('gact-link')}건")
    for t in tokens:
        check(t in text or t in html, f"{slug}: 확인값 {t}")
    check((ROOT / g["image"]).exists(), f"{slug}: 히어로 이미지 파일")
    check((ROOT / g["ogImage"]).exists(), f"{slug}: OG 이미지 파일")
    if (ROOT / g["image"]).exists():
        check(Image.open(ROOT / g["image"]).size == (1200, 800), f"{slug}: 히어로 1200×800")
    if (ROOT / g["ogImage"]).exists():
        check(Image.open(ROOT / g["ogImage"]).size == (1200, 630), f"{slug}: OG 1200×630")
    webp = (ROOT / g["image"]).with_name((ROOT / g["image"]).stem + "-720.webp")
    check(webp.exists(), f"{slug}: WebP 720 변형")
    page = read(OUT / "guides" / f"{slug}.html")
    check(bool(page), f"{slug}: 페이지 생성")
    if page:
        check("<!-- @FAQ -->" not in page, f"{slug}: FAQ 토큰 미치환")
        check(page.count('"@type": "Question"') == 5, f"{slug}: FAQPage JSON-LD 5문항")
        check('rel="noopener sponsored"' in page, f"{slug}: 제휴 rel 표기")
        check(any(x in page for x in ("../exchange", "../passes", "../checklist", "../sos")),
              f"{slug}: 도구 링크")

print("[3] 사이트맵 225 URL")
sm = read(OUT / "sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
check(len(locs) == 225, f"sitemap.xml {len(locs)} URL (기대 225)")
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
check(len(re.findall(r"<loc>", read(OUT / "sitemap-guides.xml"))) == 178, "sitemap-guides 178")

print("[4] 역링크·표기")
BACK = {
    "japan-rental-car-etc-guide": "usa-rental-car-insurance-guide",
    "southeast-asia-rental-car-license-guide": "usa-rental-car-insurance-guide",
    "us-esta-application-guide": "usa-rental-car-insurance-guide",
    "travel-insurance-guide": "usa-rental-car-insurance-guide",
    "spain-barcelona-madrid": "barcelona-gaudi-montserrat-3n4d-guide",
    "visa-free-stay-duration-guide": "turkey-istanbul-cappadocia-guide",
}
for src, dst in BACK.items():
    check(f"{dst}.html" in read(G / f"{src}.html"), f"역링크 {src} → {dst}")
gi = re.sub(r"\s+", " ", read(OUT / "guides" / "index.html"))
check("가이드 177편" in gi, "/guides/ 177편 표기")
for slug in NEW:
    check(f'href="{slug}"' in gi, f"/guides/ 목록에 {slug}")
home = read(OUT / "index.html")
check("가이드 177" in home or "177편" in home, "홈 가이드 수 표기")

print("[5] 쿠폰 코드·서치콘솔")
cp = read(OUT / "coupons.html")
check("KLKUSCAR10%" in cp, "쿠폰 페이지에 KLKUSCAR10%")
check("KLKEUTOUR20%" in cp, "쿠폰 페이지에 KLKEUTOUR20%")
act = read(Path("/workspace/scheduled-actions/🔍-구글-서치콘솔-색인-요청-재시도/action.md"))
check("225개" in act, "서치콘솔 action.md 225개 반영")
check("usa-rental-car-insurance-guide" in act, "서치콘솔 action.md 신규 3편 반영")

print()
if fails:
    print(f"[verify_v69] 실패 {len(fails)}건")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("[verify_v69] PASS — 가이드 177 · 신규 3 · 사이트맵 225 · 허브 32 · 숙소 182")
