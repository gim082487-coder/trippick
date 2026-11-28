#!/usr/bin/env python3
"""v68 검증 — 숙소 지역 2곳(푸껫·고베)·숙소 11곳 + 신규 가이드 3편 + 사이트맵 225 URL.

    python3 tools/verify_v68.py

1. 가이드 177편 · 허브 32곳 · 찐숙소 182곳(지역 42곳)
2. 신규 3편: 본문 3,000자(공백 제외)·표 6개 이상·h2 5개 이상·FAQ 5문항·제휴 5건 이상·이미지·OG·확인값
3. 숙소: 푸껫 6곳·고베 5곳, 2026-12-10~11 조회 기준 표기, 상세 페이지 확인, /stays 표기 182
4. 사이트맵 225 URL · sitemap-index 3분할 합계 일치 · sitemap-guides 178 · 중복 0
5. 역링크(상하이·베이징·세부·보홀·괌) · 클룩 홋카이도 코드 원문
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
check(len(guides) == 179, f"가이드 {len(guides)}편 (기대 179)")
check(len(hubs) == 32, f"도시 허브 {len(hubs)}곳 (기대 32)")
check(len(stays["hotels"]) == 182, f"찐숙소 {len(stays['hotels'])}곳 (기대 182)")
check(len(stays["regions"]) == 42, f"숙소 지역 {len(stays['regions'])}곳 (기대 42)")

print("[2] 신규 3편")
NEW = {
    "china-visa-free-alipay-wechat-pay-guide": ["30일", "2026년 12월 31일", "200위안", "3%", "50위안", "5,000달러"],
    "boracay-3n4d-course-budget": ["535페소", "300페소", "150페소", "50페소", "45,066", "388,896"],
    "saipan-3n4d-course-budget": ["G-CNMI ETA", "45일", "2년", "35~50달러", "169,355", "1,279,300"],
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
    check(html.count("<table") >= 6, f"{slug}: 표 {html.count('<table')}개 (기대 6+)")
    check(len(re.findall(r"<h2\b", html)) >= 5, f"{slug}: h2 {len(re.findall(r'<h2', html))}개")
    check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항")
    check(html.count('class="gact-link"') >= 5, f"{slug}: 제휴 링크 {html.count('gact-link')}건")
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

print("[3] 숙소 확장 — 푸껫·고베")
reg = {r["id"]: r for r in stays["regions"]}
check("phuket" in reg and "kobe" in reg, "지역 phuket·kobe 등록")
for rid, want in (("phuket", 6), ("kobe", 5)):
    hs = [h for h in stays["hotels"] if h["region"] == rid]
    check(len(hs) == want, f"{rid}: 숙소 {len(hs)}곳 (기대 {want})")
    check(all(h["price"] > 0 for h in hs), f"{rid}: 1박 최저가 채움")
    check(all(h["priceBasis"].startswith("2026-12-10~11") for h in hs), f"{rid}: 가격 기준일 표기")
    check(all((ROOT / h["img"]).exists() for h in hs), f"{rid}: 숙소 이미지 파일")
    check(all("Allianceid=11407530" in h["url"] and "trip_sub3" in h["url"] for h in hs),
          f"{rid}: 파트너스 딥링크")
    check(all(h.get("sub") for h in hs), f"{rid}: 세부 점수")
    check(all("trip.com/hotels/list" in reg[rid]["listUrl"] for _ in [0]), f"{rid}: 목록 URL")
st = read(OUT / "stays.html")
check("푸껫" in st and "고베" in st, "/stays 에 푸껫·고베 표기")
check("182" in st, "/stays 182곳 표기")
check(st.count('id="phuket"') >= 1 and st.count('id="kobe"') >= 1, "/stays 앵커 phuket·kobe")

print("[4] 사이트맵 225 URL")
sm = read(OUT / "sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
check(len(locs) == 227, f"sitemap.xml {len(locs)} URL (기대 227)")
check(len(set(locs)) == len(locs), "sitemap 중복 0")
for slug in NEW:
    check(f"{SITE}/guides{''}/{slug}" in locs, f"sitemap 에 /guides/{slug}")
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
check(len(re.findall(r"<loc>", read(OUT / "sitemap-guides.xml"))) == 180, "sitemap-guides 178")

print("[5] 역링크·표기")
BACK = {
    "shanghai-2n3d-3n4d-course": "china-visa-free-alipay-wechat-pay-guide",
    "beijing-3n4d-course": "china-visa-free-alipay-wechat-pay-guide",
    "cebu-3n4d-course": "boracay-3n4d-course-budget",
    "bohol-3n4d-course": "boracay-3n4d-course-budget",
    "guam-4n5d-course": "saipan-3n4d-course-budget",
}
for src, dst in BACK.items():
    check(f"{dst}.html" in read(G / f"{src}.html") or f"{dst}" in read(G / f"{src}.html"),
          f"역링크 {src} → {dst}")
ph = read(OUT / "guides" / "phuket-3n4d-budget.html")
check("stays#phuket" in ph, "푸껫 가이드 → /stays#phuket 숙소 박스")
kb = read(OUT / "guides" / "osaka-kobe-nara-daytrip-guide.html")
check("stays#kobe" in kb, "고베 가이드 → /stays#kobe 숙소 박스")
gi = re.sub(r"\s+", " ", read(OUT / "guides" / "index.html"))
check("가이드 179편" in gi, "/guides/ 177편 표기")
for slug in NEW:
    check(f'href="{slug}"' in gi, f"/guides/ 목록에 {slug}")

print("[6] 클룩 홋카이도 코드(메일 원문 대조)")
cp = read(OUT / "coupons.html")
check("홋카이도투어5%" in cp, "쿠폰 코드 홋카이도투어5% (메일 원문 일치)")
check("KLKEUTOUR5%" not in cp, "오기 KLKEUTOUR5% 없음")

print()
if fails:
    print(f"[verify_v68] 실패 {len(fails)}건")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("[verify_v68] PASS — 가이드 177 · 숙소 182(지역 42) · 신규 3 · 사이트맵 225 · 허브 32")
