#!/usr/bin/env python3
"""v51 회귀 검증 — 신규 고검색 가이드 4편 + 내부 링크·사이트맵 정합.

    python3 tools/verify_v51.py

1. 가이드 110편 · sitemap 138 URL · 모든 lastmod 2026-11-25(KST)
2. v51 신규 4편 — 본문 2,200자 이상, Article·BreadcrumbList·FAQPage·Organization,
   히어로 1200×800·OG 1200×630, FAQ 4문항, 도구 바(EXCHANGE·PASS·SOS), 제휴 카드
3. 신규 가이드 ↔ 기존 허브/가이드 양방향 related, 도쿄·오사카 허브 guides 반영
4. build.py 산출(tour_hub/sitemap.xml)과 build_pages 산출(deploy_site/sitemap.xml) 동일
5. IndexNow 키 파일 배포본
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT.parent / "deploy_site"
SITE = "https://trippick.pages.dev"
LASTMOD = "2026-11-25"

NEW = ["japan-winter-clothing", "tokyo-disney-parks", "japan-ic-card", "usj-express-pass"]
BACKLINKS = {
    "sapporo-winter": "japan-winter-clothing",
    "tokyo-package-4d-vs-3d": "tokyo-disney-parks",
    "tokyo-subway-ticket": "japan-ic-card",
    "osaka-usj-transfer": "usj-express-pass",
}
fails: list[str] = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def ld_types(html: str) -> list[dict]:
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            out.append(json.loads(raw))
        except ValueError as e:
            fails.append(f"JSON-LD 파싱 실패: {e}")
    return out


def flat_types(objs: list[dict]) -> Counter:
    c: Counter = Counter()
    stack = list(objs)
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            t = o.get("@type")
            if isinstance(t, str):
                c[t] += 1
            elif isinstance(t, list):
                c.update(t)
            stack += list(o.values())
        elif isinstance(o, list):
            stack += o
    return c


def body_chars(html: str) -> int:
    """본문 글자수 — 목차(nav.toc)·스크립트·스타일 제외, 공백 제외."""
    h = re.sub(r"<nav class=\"toc\".*?</nav>", " ", html, count=1, flags=re.S)
    h = re.sub(r"<script\b.*?</script>", " ", h, flags=re.S)
    h = re.sub(r"<style\b.*?</style>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = re.sub(r"&[a-z]+;", " ", h)
    return len(re.sub(r"\s", "", h))


def main():
    gspec = load("guides.json")
    guides = gspec["guides"]
    by = {g["slug"]: g for g in guides}
    check(len(guides) == 113, f"가이드 {len(guides)}편 (기대 113)")

    # 1·2 신규 4편
    for slug in NEW:
        g = by.get(slug)
        check(g is not None, f"{slug}: guides.json 에 없음")
        if not g:
            continue
        src = ROOT / "content" / "guides" / f"{slug}.html"
        check(src.exists(), f"{slug}: 본문 파일 없음")
        if src.exists():
            chars = body_chars(read(src))
            check(chars >= 2200, f"{slug}: 본문 {chars}자 (2,200자 미만)")
        page = OUT / "guides" / f"{slug}.html"
        check(page.exists(), f"{slug}: 배포본 없음")
        if not page.exists():
            continue
        html = read(page)
        t = flat_types(ld_types(html))
        for want in ("Article", "BreadcrumbList", "FAQPage", "Organization"):
            check(t.get(want, 0) >= 1, f"{slug}: {want} 스키마 없음")
        check(len(g.get("faq") or []) >= 4, f"{slug}: FAQ 문항 {len(g.get('faq') or [])}개 (기대 4+)")
        for img, size in ((g["image"], (1200, 800)), (g["ogImage"], (1200, 630))):
            p = ROOT / img
            check(p.exists(), f"{slug}: 이미지 없음 {img}")
            if p.exists():
                with Image.open(p) as im:
                    check(im.size == size, f"{slug}: {img} 크기 {im.size} (기대 {size})")
        for tool in ("EXCHANGE", "PASS", "SOS"):
            check(tool in html, f"{slug}: 도구 바 {tool} 없음")
        check("gact-k" in html, f"{slug}: 제휴 카드 없음")
        check(html.count('class="tb"') >= 1, f"{slug}: 표 없음")
        # related 역방향
        for target in (g.get("related") or []):
            tgt = by.get(target)
            check(tgt is not None, f"{slug}: related {target} 없음")
            if tgt is not None:
                check(slug in (tgt.get("related") or []),
                      f"{slug} → {target} 단방향(역링크 없음)")

    for old, new in BACKLINKS.items():
        check(new in (by[old].get("related") or []), f"{old}: {new} 역링크 없음")

    hubs = {h["slug"]: h for h in load("city_hubs.json")["cities"]}
    check("tokyo-disney-parks" in hubs["tokyo"]["guides"], "도쿄 허브에 tokyo-disney-parks 없음")
    check("japan-ic-card" in hubs["tokyo"]["guides"], "도쿄 허브에 japan-ic-card 없음")
    check("usj-express-pass" in hubs["osaka"]["guides"], "오사카 허브에 usj-express-pass 없음")
    check("관련 가이드 13편" in hubs["tokyo"]["metaDesc"], "도쿄 허브 metaDesc 가이드 수 미갱신")
    check("관련 가이드 15편" in hubs["osaka"]["metaDesc"], "오사카 허브 metaDesc 가이드 수 미갱신")

    # 3 사이트맵
    sm_out = read(OUT / "sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm_out)
    lastmods = set(re.findall(r"<lastmod>([^<]+)</lastmod>", sm_out))
    check(len(locs) == 141, f"sitemap {len(locs)} URL (기대 141)")
    check(locs and lastmods == {LASTMOD}, f"lastmod {sorted(lastmods)} (기대 {LASTMOD})")
    for slug in NEW:
        check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug} 없음")
    src_sm = read(ROOT / "sitemap.xml")
    check(src_sm == sm_out, "build.py 산출과 build_pages 산출 sitemap 불일치")

    # 4 IndexNow
    key = str(load("indexnow.json").get("key") or "")
    kp = OUT / f"{key}.txt"
    check(kp.exists() and read(kp).strip() == key, "IndexNow 키 파일 배포본 없음/불일치")

    print(f"가이드 {len(guides)}편 · sitemap {len(locs)} URL · lastmod {sorted(lastmods)} · 신규 {len(NEW)}편")
    if fails:
        print("\n실패:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("[verify_v51] PASS")


if __name__ == "__main__":
    main()
