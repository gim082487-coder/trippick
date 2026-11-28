#!/usr/bin/env python3
"""v67 검증 — 릴스 착지 경비 가이드 2편 + 신규 가이드 3편 + 클룩 쿠폰 8건 + 사이트맵 225 URL.

    python3 tools/verify_v67.py

1. 가이드 177편 · 허브 32곳 · 찐숙소 182곳
2. 신규 5편: 본문 3,000자(공백 제외)·표 7개·h2 6개·FAQ 5문항·제휴 5건·이미지·OG·확인값
3. /coupons: 6개 카테고리 37건 · 클룩 코드 4종 · 클룩 링크 aid=144067 유지 · 검증일 2026-11-27
4. 사이트맵 225 URL · sitemap-index 3분할 합계 일치 · sitemap-guides 178 · 중복 0
5. 허브 연결(파리·방콕·오사카·로마)·역링크·다낭 3박5일 페이지
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

print("[2] 신규 5편")
NEW = {
    "paris-4n5d-budget": ["790,612", "€2.55", "€70", "€32", "662,400"],
    "bangkok-3n4d-budget": ["1,311,369", "1,000밧", "28,900", "45밧", "144밧"],
    "phuket-3n4d-budget": ["100밧", "1,450밧", "400밧", "147,774", "301,935"],
    "rome-south-italy-daytrip-guide": ["€3.30", "€20", "€25", "€14.80", "€2.50"],
    "osaka-kobe-nara-daytrip-guide": ["330엔", "420엔", "680엔", "800엔", "1,300엔"],
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
    check(html.count("<table") >= 7, f"{slug}: 표 {html.count('<table')}개 (기대 7+)")
    check(len(re.findall(r"<h2\b", html)) >= 6, f"{slug}: h2 {len(re.findall(r'<h2', html))}개")
    check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항")
    check(html.count('class="gact-link"') >= 5, f"{slug}: 제휴 링크 {html.count('gact-link')}건")
    for t in tokens:
        check(t in text or t in html, f"{slug}: 확인값 {t}")
    check((ROOT / g["image"]).exists(), f"{slug}: 히어로 이미지 파일")
    check((ROOT / g["ogImage"]).exists(), f"{slug}: OG 이미지 파일")
    from PIL import Image
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

print("[3] /coupons — 클룩 블프·투어 쿠폰")
cp = read(OUT / "coupons.html")
check(cp.count('class="cpn"') == 37, f"쿠폰 카드 {cp.count('class=\"cpn\"')}건 (기대 37)")
check(cp.count('data-filter=') == 7, f"탭 {cp.count('data-filter=')}개 (전체+6카테고리)")
check("클룩 블프·투어 쿠폰" in cp, "카테고리 '클룩 블프·투어 쿠폰'")
for code in ("홋카이도투어5%", "KLKEUTOUR20%", "KLKJPCAR20000", "KLKUSCAR10%"):
    check(code in cp, f"쿠폰 코드 {code}")
for token in ("2026.11.30", "2026.12.31", "11.24 ~ 12.15", "11.26 ~ 11.30", "최대 96%"):
    check(token in cp, f"쿠폰 기간·혜택 {token}")
check("검증일 2026-11-27" in cp, "쿠폰 검증일 2026.11.27")
kl = re.findall(r'href="(https://www\.klook\.com[^"]*)"', cp)
check(len(kl) >= 8, f"클룩 링크 {len(kl)}건 (기대 8+)")
check(all("aid=144067" in u for u in kl), "클룩 링크 전부 aid=144067 유지")
check("37건" in cp, "본문 37건 표기")

print("[4] 사이트맵 225 URL")
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

print("[5] 허브·역링크")
HUB = {"paris": "paris-4n5d-budget", "bangkok": "bangkok-3n4d-budget", "osaka": "osaka-kobe-nara-daytrip-guide",
       "rome": "rome-south-italy-daytrip-guide"}
for hub, slug in HUB.items():
    page = read(OUT / f"{hub}.html")
    check(f"/guides/{slug}" in page or f"{slug}.html" in page, f"/{hub} 에 {slug} 링크")
check("phuket-3n4d-budget" in read(OUT / "bangkok.html"), "/bangkok 에 푸껫 가이드 링크")
BACK = {
    "paris-metro-navigo-guide": "paris-4n5d-budget",
    "paris-london-5n7d": "paris-4n5d-budget",
    "bangkok-3n4d-course": "bangkok-3n4d-budget",
    "bangkok-pattaya-3n5d-course-budget": "bangkok-3n4d-budget",
    "thailand-cities-comparison-guide": "phuket-3n4d-budget",
    "italy-rome-florence-venice": "rome-south-italy-daytrip-guide",
    "rome-vatican-colosseum-booking-guide": "rome-south-italy-daytrip-guide",
    "osaka-kyoto-3n4d": "osaka-kobe-nara-daytrip-guide",
    "danang-hoian-rainy": "danang-hoian-3n5d",
}
for src, dst in BACK.items():
    check(f"{dst}.html" in read(G / f"{src}.html"), f"역링크 {src} → {dst}")

print("[6] 다낭 3박5일 페이지")
dn = OUT / "guides" / "danang-hoian-3n5d.html"
check(dn.exists(), "/guides/danang-hoian-3n5d 페이지 생성")
check("/guides/danang-hoian-3n5d" in read(OUT / "danang.html"), "/danang 허브에서 3박5일 가이드 링크")

print("[7] 표기 숫자")
gi = re.sub(r"\s+", " ", read(OUT / "guides" / "index.html"))
check("가이드 177편" in gi, "/guides/ 171편 표기")
check("182" in read(OUT / "stays.html"), "/stays 182곳 표기")

print()
if fails:
    print(f"[verify_v67] 실패 {len(fails)}건")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("[verify_v67] PASS — 가이드 177 · 신규 5 · 쿠폰 37 · 사이트맵 225 · 허브 32 · 숙소 182")
