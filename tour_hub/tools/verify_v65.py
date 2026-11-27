#!/usr/bin/env python3
"""v65 검증 — 신규 허브 6곳·찐숙소 30곳·가이드 8편·상품 10건·사이트맵 219 URL.

    python3 tools/verify_v65.py

1. city_hubs 32곳 · stays 171곳(지역 40) · guides 171편 · tripcom 입장권 23·픽업 33·eSIM 28
2. 신규 허브 6곳: 페이지 존재, 찐숙소 수, 가이드 수, 현지 기본 정보, 이미지 파일
3. 신규 가이드 8편: 본문 3,000자(공백 제외)·표 5개·h2 5개·FAQ 5문항·제휴 5건·이미지·OG
4. 사이트맵 219 URL · sitemap-index 3분할 합계 일치 · 중복 0
5. 신규 상품의 파트너스 코드(Allianceid·SID·trip_sub1·trip_sub3)와 상태
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
tc = load("tripcom.json")

print("[1] 데이터 규모")
check(len(guides) == 171, f"가이드 {len(guides)}편 (기대 171)")
check(len(hubs) == 32, f"도시 허브 {len(hubs)}곳 (기대 32)")
check(len(stays["hotels"]) == 171, f"찐숙소 {len(stays['hotels'])}곳 (기대 171)")
check(len(stays["regions"]) == 40, f"숙소 지역 {len(stays['regions'])}곳 (기대 40)")
check(len(tc["tickets"]) == 23, f"입장권 {len(tc['tickets'])}건 (기대 23)")
check(len(tc["transfers"]) == 33, f"공항픽업 {len(tc['transfers'])}건 (기대 33)")
check(len(tc["esims"]) == 28, f"eSIM {len(tc['esims'])}건 (기대 28)")

print("[2] 신규 허브 6곳")
HUBS = {"sapporo": 9, "nagoya": 5, "phuquoc": 5, "cebu": 5, "newyork": 5, "sydney": 5}
hub_by_slug = {h["slug"]: h for h in hubs}
for slug, n in HUBS.items():
    h = hub_by_slug.get(slug)
    check(h is not None, f"{slug}: city_hubs 항목")
    if not h:
        continue
    check(h.get("stayCards") is True, f"{slug}: 찐숙소 카드 사용")
    check(bool(h.get("tips")) and len(h["tips"]) >= 4, f"{slug}: 현지 기본 정보 {len(h.get('tips') or [])}개")
    check(bool(h.get("image")) and (ROOT / h["image"]).exists(), f"{slug}: 대표 이미지 파일")
    check(bool(h.get("ogImage")) and (ROOT / h["ogImage"]).exists(), f"{slug}: OG 이미지 파일")
    hs = [x for x in stays["hotels"] if x["region"] == slug]
    check(len(hs) == n, f"{slug}: 찐숙소 {len(hs)}곳 (기대 {n})")
    page = read(OUT / f"{slug}.html")
    check(bool(page), f"{slug}: 페이지 생성")
    if page:
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page))
        check(f"찐숙소 {n}곳" in txt, f"{slug}: 페이지에 찐숙소 {n}곳 표기")
        check(f"관련 가이드 {len(h.get('guides') or [])}편" in txt, f"{slug}: 가이드 {len(h.get('guides') or [])}편 표기")
        check("현지 기본 정보" in txt, f"{slug}: 현지 기본 정보 블록")
        card_imgs = re.findall(r'<img[^>]+src="([^"]+)"', page)
        missing = [s for s in card_imgs if not s.startswith("http") and not (ROOT / s).exists()]
        check(not missing, f"{slug}: 이미지 파일 누락 {len(missing)}")

print("[3] 신규 가이드 8편")
NEW = {
    "london-transport-heathrow-guide": ["£5.90", "£15.50", "£26", "£8.90", "£10.50"],
    "rome-vatican-colosseum-booking-guide": ["€18", "€20", "€25", "€62.90", "€14"],
    "taiwan-transport-thsr-guide": ["NT$160", "NT$100", "NT$2,200", "NT$2,500", "NT$380"],
    "cebu-bohol-ferry-transfer-guide": ["960페소", "1,440", "25페소", "10kg", "50페소"],
    "kyoto-2n3d-course-budget": ["1,100엔", "800엔", "230엔", "500엔", "2,700엔"],
    "hongkong-octopus-ael-guide": ["HK$120", "HK$170", "HK$150", "HK$34.6", "HK$105"],
    "vietnam-4cities-comparison-guide": ["650", "545", "50,000동", "55,113원", "850,000동"],
    "thailand-cities-comparison-guide": ["336", "350", "45밧", "150밧", "144밧"],
}
for slug, tokens in NEW.items():
    g = by_slug.get(slug)
    check(g is not None, f"{slug}: guides.json 항목")
    if not g:
        continue
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
    page = read(OUT / "guides" / f"{slug}.html")
    check("<!-- @FAQ -->" not in page, f"{slug}: FAQ 토큰 미치환")
    page = read(OUT / "guides" / f"{slug}.html")
    check(bool(page), f"{slug}: 페이지 생성")
    if page:
        check("FAQPage" in page, f"{slug}: FAQ 구조화 데이터")
        check(any(x in page for x in ("../exchange", "../passes", "../checklist", "../sos")),
              f"{slug}: 도구 링크")

print("[4] 신규 상품 파트너스 코드")
for kind in ("tickets", "transfers", "esims"):
    for a in tc[kind]:
        if a.get("checked") != "2026-11-27":
            continue
        u = a["url"]
        ok = ("Allianceid=11407530" in u and "SID=336341874" in u
              and "trip_sub1=" in u and "trip_sub3=" in u)
        check(ok and a.get("status") == "verified_200_ko", f"{a['id']}: 코드·상태")

print("[5] 사이트맵 219 URL")
sm = read(OUT / "sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
check(len(locs) == 219, f"sitemap.xml {len(locs)} URL (기대 219)")
check(len(set(locs)) == len(locs), "sitemap 중복 0")
for slug in HUBS:
    check(f"{SITE}/{slug}" in locs, f"sitemap 에 /{slug}")
for slug in NEW:
    check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug}")
check(f"{SITE}/stays" in locs and f"{SITE}/cities/" in locs, "sitemap 에 /stays·/cities/")
idx = ET.fromstring(read(OUT / "sitemap-index.xml"))
parts = [e.text for e in idx.findall("sm:sitemap/sm:loc", NS)]
check(len(parts) == 3, f"sitemap-index 분할 {len(parts)}개")
tot = 0
for p in parts:
    name = p.rsplit("/", 1)[-1]
    sub = read(OUT / name)
    n = len(re.findall(r"<loc>", sub))
    tot += n
    print(f"    · {name}: {n}")
check(tot == len(locs), f"sitemap-index 합계 {tot} = sitemap {len(locs)}")
check(len(re.findall(r"<loc>", read(OUT / "sitemap-hubs.xml"))) == 32, "sitemap-hubs 32")
check(len(re.findall(r"<loc>", read(OUT / "sitemap-guides.xml"))) == 172, "sitemap-guides 172")

print("[6] 표기 숫자")
cities = read(OUT / "cities" / "index.html")
check("CITY GUIDES · 32곳" in re.sub(r"\s+", " ", cities) or "도시 32곳" in cities, "/cities/ 32곳")
st = read(OUT / "stays.html")
check("171" in st, "/stays 171곳 표기")
gi = read(OUT / "guides" / "index.html")
check("가이드 171편" in re.sub(r"\s+", " ", gi), "/guides/ 171편 표기")

print()
if fails:
    print(f"[verify_v65] 실패 {len(fails)}건")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("[verify_v65] PASS — 허브 32 · 숙소 171 · 가이드 171 · 상품 84+ · 사이트맵 219")
