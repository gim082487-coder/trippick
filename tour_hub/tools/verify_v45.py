#!/usr/bin/env python3
"""v45 회귀 검증 — 도시 연동 도구 프리셋 · 신규 가이드 3편 · /sos 인쇄 저장.

`python3 build.py && python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links`
뒤에 실행한다.

검사 항목
 1. 가이드 100편 · v45 신규 3편(다낭 3박5일·타이베이 3박4일·환전 수수료) 본문/이미지/FAQ
 2. 신규 가이드 og:image 가 1200×630 이고 100KB 이상인지
 3. 도시 허브 13곳의 도구 4개 — 환율(?cur=)·패스(?city=)·SOS(?country=) 프리셋이 국가에 맞는지
 4. 가이드 상단 도구 바(.gtools) — 100편 전부에 있고, 도시가 특정되는 글은 그 도시 통화·국가로 연결되는지
 5. /exchange ?cur= · /passes ?city= · /sos ?country= 를 처리하는 스크립트가 산출물에 있는지
 6. /sos 인쇄·PDF 저장 버튼(#sosPrint)과 인쇄 CSS(패널 펼침) 존재
 7. 신규 가이드의 제휴 링크가 rel="sponsored" + trip_sub3 를 갖는지
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = (ROOT / "../deploy_site").resolve()
NEW = ["danang-hoian-3n5d", "taipei-3n4d-course-budget", "currency-payment-fees"]
CUR = {"jp": "JPY", "vn": "VND", "th": "THB", "tw": "TWD"}
SOS = {"jp": "JP", "vn": "VN", "th": "TH", "tw": "TW", "kr": "KR"}
fails = []


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def check(ok, msg):
    if not ok:
        fails.append(msg)


def main():
    guides = load("guides.json")["guides"]
    by_slug = {g["slug"]: g for g in guides}
    check(len(guides) == 110, f"가이드 {len(guides)}편 (기대 110)")

    # 1·2·7 신규 가이드
    for slug in NEW:
        g = by_slug.get(slug)
        check(g is not None, f"{slug}: guides.json 에 없음")
        if not g:
            continue
        page = OUT / "guides" / f"{slug}.html"
        check(page.exists(), f"{slug}: 산출물 없음")
        if not page.exists():
            continue
        html = read(page)
        check("@FAQ" not in html, f"{slug}: @FAQ 토큰 미치환")
        check(html.count('<details class="fq">') == 5, f"{slug}: 화면 FAQ 5문항 아님({html.count('<details class=\"fq\">')})")
        check('"@type": "FAQPage"' in html, f"{slug}: FAQPage JSON-LD 없음")
        check("gtoc" in html, f"{slug}: 목차(auto_toc) 없음")
        check("읽는 시간" in html, f"{slug}: 읽기 시간 표기 없음")
        img = ROOT / g["image"]
        check(img.exists(), f"{slug}: 이미지 파일 없음 {g['image']}")
        if img.exists():
            w, h = Image.open(img).size
            check((w, h) == (1200, 630), f"{slug}: og:image {w}×{h} (기대 1200×630)")
            check(img.stat().st_size > 60_000, f"{slug}: 이미지가 너무 작음({img.stat().st_size}B)")
        spon = re.findall(r'<a class="gact" href="([^"]+)"[^>]*rel="[^"]*sponsored', html)
        check(len(spon) >= 1, f"{slug}: 제휴(gact·sponsored) 링크 없음")
        for u in spon:
            check("trip_sub3=" in u, f"{slug}: trip_sub3 없는 제휴 링크 {u[:70]}")
        for q, a in g.get("faq") or []:
            check(len(q) > 8 and len(a) > 40, f"{slug}: FAQ 문항/답이 너무 짧음 — {q[:20]}")

    # 3 도시 허브 프리셋
    hubs = load("city_hubs.json")["cities"]
    check(len(hubs) == 13, f"도시 허브 {len(hubs)}곳 (기대 13)")
    for h in hubs:
        slug, cc = h["slug"], h.get("country") or "kr"
        page = OUT / f"{slug}.html"
        if not page.exists():
            fails.append(f"허브 {slug}: 산출물 없음")
            continue
        html = read(page)
        want_cur = CUR.get(cc)
        if want_cur:
            check(f"exchange?cur={want_cur}&amp;city={slug}" in html,
                  f"허브 {slug}: 환율 프리셋(exchange?cur={want_cur}) 없음")
        else:
            check('href="exchange"' in html, f"허브 {slug}: 환율 도구 링크 없음")
        check(f"sos?country={SOS[cc]}" in html, f"허브 {slug}: SOS 프리셋(sos?country={SOS[cc]}) 없음")
        if slug in ("osaka", "tokyo", "bangkok", "taipei"):
            check(f"passes?city={slug}" in html, f"허브 {slug}: 패스 프리셋(passes?city=) 없음")
        else:
            check('href="passes"' in html, f"허브 {slug}: 패스 도구 링크 없음")
        check('class="hub-tools"' in html and html.count('class="hub-tool"') == 4,
              f"허브 {slug}: 도구 4개 아님")

    # 4 가이드 도구 바
    for g in guides:
        page = OUT / "guides" / f"{g['slug']}.html"
        if not page.exists():
            continue
        html = read(page)
        check('class="gtools"' in html, f"가이드 {g['slug']}: 도구 바 없음")
    for slug, cur in (("danang-hoian-3n5d", "VND"), ("taipei-3n4d-course-budget", "TWD")):
        html = read(OUT / "guides" / f"{slug}.html")
        check(f"exchange?cur={cur}&amp;city=" in html, f"{slug}: 가이드 도구 바 통화 프리셋({cur}) 없음")

    # 5 도구 페이지 파라미터 처리
    ex = read(OUT / "exchange.html")
    check("QS.get('cur')" in ex and "fxPreset" in ex, "/exchange: ?cur= 프리셋 코드 없음")
    check('class="fx-presets"' in ex, "/exchange: 통화 바로가기 칩 없음")
    pk = read(OUT / "passes.html")
    check("QS.get('city')" in pk, "/passes: ?city= 프리셋 코드 없음")
    sos = read(OUT / "sos.html")
    check("get('country')" in read(OUT / "assets" / "tp-v44.js"), "/sos: ?country= 프리셋 코드 없음")

    # 6 /sos 인쇄·저장
    check('id="sosPrint"' in sos, "/sos: 인쇄·PDF 저장 버튼 없음")
    check("window.print()" in read(OUT / "assets" / "tp-v44.js"), "/sos: 인쇄 호출 스크립트 없음")
    css = read(OUT / "assets" / "site.css")
    check(".sos-panel[hidden]" in css, "인쇄 CSS: 숨은 국가 패널 펼침 규칙 없음")
    check(".sos-save" in css, "CSS: .sos-save 규칙 없음")
    check(".gtools" in css, "CSS: .gtools 규칙 없음")

    # 7 sitemap 에 신규 3편
    sm = read(OUT / "sitemap.xml")
    for slug in NEW:
        check(f"/guides/{slug}" in sm, f"sitemap: {slug} 없음")

    print(f"가이드 {len(guides)}편 · 허브 {len(hubs)}곳 · 신규 3편 · /sos 인쇄·프리셋")
    if fails:
        print("\n실패:")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("[verify_v45] PASS")


if __name__ == "__main__":
    main()
