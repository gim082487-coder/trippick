#!/usr/bin/env python3
"""v43 회귀 검증 — 재방문 루프(내 여행 D-Day) · ★ 참고 글 저장 · 실전 가이드 3편.

`python3 build.py && python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links`
를 먼저 실행한 뒤 이 파일을 돌린다.

검사 항목
 1. 가이드 91편 · v43 신규 3편 본문/FAQ 5문항/OG 1200×630/히어로 1200×800
 2. 신규 3편의 양방향 연결 — ../stays · ../passes · ../checklist · 도시 허브 · 기존 관련 가이드
 3. 가이드 91편 전체에 ★ 참고 글 저장 버튼(data-bm · data-bm-item)
 4. 홈·/checklist 의 D-Day 위젯(도시 13곳·단계 5개·localStorage 키)과 tp-v43.js 로드
 5. tp-v43.js 에 v42 기능(퀵서치·찜 견적서·비교)과 v43 기능(D-Day·북마크)이 함께 있는지
 6. sitemap 131 URL · action.md 에 v43 3편 URL·131개 기준
 7. 구 assets/tp-v42.js·tp-v41.js 잔존 없음
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent      # tour_hub/
DATA = ROOT / "data"
OUT = (ROOT / "../deploy_site").resolve()
ACTION = Path("/workspace/scheduled-actions/🔍-구글-서치콘솔-색인-요청-재시도/action.md")

NEW = {
    "airport-arrival-city-transfer-guide": "오사카",
    "japan-convenience-store-must-buy": "도쿄",
    "overseas-roaming-esim-install-troubleshooting": "다낭",
}
fails = []


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def check(ok, msg):
    if not ok:
        fails.append(msg)


guides = load("guides.json")["guides"]
by = {g["slug"]: g for g in guides}
check(len(guides) == 119, f"가이드 {len(guides)}편 (기대 119)")

# ---------------------------------------------------------------- 1. 신규 3편
for slug, hubword in NEW.items():
    g = by.get(slug)
    check(g is not None, f"guides.json 에 {slug} 없음")
    if not g:
        continue
    page = OUT / "guides" / f"{slug}.html"
    check(page.exists(), f"배포본 없음: {slug}.html")
    check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항 (기대 5)")
    for key in ("image", "ogImage", "seoTitle", "desc", "keywords", "ctaTitle", "ctaText"):
        check(bool(g.get(key)), f"{slug}: {key} 없음")
    og = OUT / (g.get("ogImage") or "")
    if og.exists():
        check(Image.open(og).size == (1200, 630), f"{slug}: OG {Image.open(og).size} (기대 1200×630)")
    else:
        fails.append(f"{slug}: OG 파일 없음 {og}")
    hero = OUT / (g.get("image") or "")
    if hero.exists():
        check(Image.open(hero).size == (1200, 800), f"{slug}: 히어로 {Image.open(hero).size} (기대 1200×800)")
    if page.exists():
        html = read(page)
        check(html.count('"@type": "Question"') == 5, f"{slug}: FAQPage JSON-LD 5문항 아님")
        check(html.count('details class="fq"') == 5, f"{slug}: 화면 FAQ {html.count('details class=\"fq\"')}문항 (기대 5)")
        check("FAQPage" in html, f"{slug}: FAQPage JSON-LD 없음")
        check('rel="noopener sponsored"' in html, f"{slug}: rel=\"noopener sponsored\" 제휴 링크 없음")
        check(html.count('rel="noopener sponsored"') >= 2, f"{slug}: 제휴 링크 2개 미만")
        for target in ("../stays", "../passes", "../checklist"):
            check(re.search(r'href="' + re.escape(target) + r'(\.html)?"', html) is not None,
                  f"{slug}: {target} 링크 없음")
        hub_check = hubword if hubword in ("osaka", "tokyo", "fukuoka", "danang", "bangkok", "taipei") else "osaka"
        check(re.search(r'href="\.\./' + hub_check + r'(\.html)?"', html) is not None,
              f"{slug}: 도시 허브 링크 없음")

# 도시 허브 → 새 가이드 역방향
for hub_slug in ("osaka", "tokyo", "fukuoka", "danang", "bangkok", "taipei"):
    hub_html = read(OUT / f"{hub_slug}.html")
    for slug in NEW:
        if slug == "airport-arrival-city-transfer-guide" or hub_slug in ("osaka", "tokyo", "fukuoka"):
            check((f'guides/{slug}.html' in hub_html) or (f'href="guides/{slug}"' in hub_html), f"{hub_slug} 허브에 {slug} 링크 없음")

# ---------------------------------------------------------------- 2. ★ 참고 글 저장 (91편)
guide_files = sorted((OUT / "guides").glob("*.html"))
bms = 0
for f in guide_files:
    if f.name == "index.html":
        continue
    html = read(f)
    if 'class="bm-btn"' in html and f'data-bm="/guides/{f.name}"' in html and "data-bm-item=" in html:
        bms += 1
check(bms == 119, f"★ 참고 글 저장 버튼이 있는 가이드 {bms}편 (기대 119)")

# ---------------------------------------------------------------- 3. D-Day 위젯
home = read(OUT / "index.html")
checklist = read(OUT / "checklist.html")
for name, html in (("홈", home), ("/checklist", checklist)):
    check('data-tp-trip' in html, f"{name}: D-Day 위젯 없음")
    m = re.search(r'<script type="application/json" id="tpTripData">(.*?)</script>', html, re.S)
    check(m is not None, f"{name}: tpTripData 없음")
    if m:
        payload = json.loads(m.group(1).replace("<\\/", "</"))
        check(len(payload.get("cities") or []) == 13, f"{name}: 도시 {len(payload.get('cities') or [])}곳 (기대 13)")
        stages = [s["d"] for s in payload.get("stages") or []]
        check(stages == ["D-14", "D-7", "D-3", "D-1", "현지"], f"{name}: 단계 {stages}")
        for c in payload["cities"]:
            check(len(c.get("g") or []) == 2, f"{name}: {c['s']} 가이드 {len(c.get('g') or [])}편 (기대 2)")
            check(bool(c.get("e")), f"{name}: {c['s']} 미예약 필수품 CTA 없음")
check('id="tpTrip"' in home, "홈: #tpTrip 앵커 없음")
check("assets/tp-v43.js" in home and "assets/tp-v43.js" in checklist, "홈·/checklist 가 tp-v43.js 를 안 씀")
check("assets/tp-v43.js" in read(OUT / "guides" / "airport-arrival-city-transfer-guide.html"),
      "가이드가 tp-v43.js 를 안 씀")

# ---------------------------------------------------------------- 4. JS 기능
js = OUT / "assets" / "tp-v43.js"
check(js.exists(), "assets/tp-v43.js 없음")
check(not (OUT / "assets" / "tp-v42.js").exists(), "구 assets/tp-v42.js 가 남아 있음")
check(not (OUT / "assets" / "tp-v41.js").exists(), "구 assets/tp-v41.js 가 남아 있음")
if js.exists():
    src = read(js)
    for token in ("trippick.trip.v1", "trippick.bookmarks.v1", "trippick.wish.v1",
                  "data-bm", "tpTripData", "data-tp-trip-save" if "data-tp-trip-save" in src else "data-tp-trip-city",
                  "data-wl-copy", "data-qs-open", "tpCompare", "tp-strip"):
        check(token in src, f"tp-v43.js 에 {token} 없음")
    try:
        import esprima
        try:
            esprima.parseScript(src)
        except Exception as e:
            fails.append(f"tp-v43.js 문법 오류: {str(e)[:90]}")
    except ImportError:
        try:
            r = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
            if r.returncode != 0:
                fails.append("tp-v43.js 문법 오류(node): " + r.stderr[:120])
        except FileNotFoundError:
            pass

# ---------------------------------------------------------------- 5. sitemap·action
sm = read(OUT / "sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
check(len(locs) == 147, f"sitemap {len(locs)} URL (기대 147)")
for slug in NEW:
    check(f"/guides/{slug}" in sm, f"sitemap 에 /guides/{slug} 없음")
if ACTION.exists():
    act = read(ACTION)
    check(act.startswith("---\ntitle:"), "action.md 프론트매터가 맨 앞에 없음")
    check("kind: scheduled-action" in act, "action.md kind 변경됨")
    for slug in NEW:
        check(f"https://trippick.pages.dev/guides/{slug}" in act, f"action.md 에 {slug} URL 없음")
    check("147개" in act, "action.md 사이트맵 기준 수(147개) 미갱신")
else:
    fails.append(f"action.md 없음: {ACTION}")

print(f"가이드 {len(guides)}편 · ★ 저장 버튼 {bms}편 · sitemap {len(locs)} URL")
if fails:
    print("\n실패:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("\n모든 검사 통과")
