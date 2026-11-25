#!/usr/bin/env python3
"""v41 회귀 검증 — 통합 퀵서치 · 찜 · 나란히 비교 · 결정 배지.

`python3 build.py && python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links`
뒤에 실행한다.

검사 항목
 1. search_index.json — 도시 30·가이드(데이터 기준)·숙소 116·투어 84·맛집 75, URL 이 전부 실제로 열리는 곳인지
    (가이드 파일 존재 / 홈 앵커 존재 / /stays 지역 존재 / 도시 허브 파일 존재)
 2. 카드의 찜·비교 버튼 키가 비교 데이터(tpCompare)와 1:1 인지, 찜 데이터 JSON 이 파싱되는지
 3. 결정 배지가 데이터에 있는 속성만 말하는지 — 즉시확정·모바일 바우처는 안내문에 그 표현이 있을 때만,
    무료 취소는 cancelShort 에 무료/전액이 있을 때만. (없는 속성 지어내기 금지)
 4. 결정 배지에 쓰는 클래스가 정해진 목록 안인지
 5. 새로 넣은 id(t-·) 가 페이지 안에서 중복되지 않는지
 6. assets/tp-v43.js 존재·문법(esprima 또는 node --check)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = (ROOT / "../deploy_site").resolve()
fails = []


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def check(ok, msg):
    if not ok:
        fails.append(msg)


def read(p):
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------- 1. 검색 색인
idx_path = OUT / "search_index.json"
check(idx_path.exists(), "search_index.json 없음")
idx = json.loads(read(idx_path)) if idx_path.exists() else {"items": []}
items = idx.get("items") or []
counts = {}
for it in items:
    counts[it["k"]] = counts.get(it["k"], 0) + 1
expect = {"city": 30, "guide": len(json.loads((DATA / "guides.json").read_text(encoding="utf-8"))["guides"]),
          "stay": 116, "tour": 84, "food": 75}
for k, n in expect.items():
    check(counts.get(k) == n, f"search_index.json {k} {counts.get(k)}건 (기대 {n})")

home = read(OUT / "index.html")
stays = read(OUT / "stays.html")
stays_regions = set(re.findall(r'class="gf-chip[^"]*" type="button" data-region="([^"]+)"', stays))
hub_slugs = {r["id"] for r in load("stays.json")["regions"]}
bad_urls = []
for it in items:
    u = it.get("u") or ""
    if u.startswith("/guides/"):
        if not (OUT / "guides" / (u.split("/guides/")[1].split("?")[0] + ".html")).exists():
            bad_urls.append(u)
    elif u.startswith("/stays?region="):
        rid = u.split("region=")[1].split("&")[0]
        if rid not in stays_regions:
            bad_urls.append(u)
    elif u.startswith("/#"):
        if f'id="{u[2:]}"' not in home:
            bad_urls.append(u)
    elif u.startswith("/"):
        slug = u.strip("/")
        if not (OUT / slug / "index.html").exists() and not (OUT / (slug + ".html")).exists():
            bad_urls.append(u)
    else:
        bad_urls.append(u)
check(not bad_urls, f"search_index.json 열리지 않는 URL {len(bad_urls)}건: {bad_urls[:6]}")

# ---------------------------------------------------------------- 2. 찜·비교 키
tour_ids = [t["id"] for t in load("tours.json")["tours"]]
hotel_ids = [str(h["id"]) for h in load("stays.json")["hotels"]]
tour_doc = load("tours.json")


def compare_payload(html):
    m = re.search(r'<script type="application/json" id="tpCompare"([^>]*)>(.*?)</script>', html, re.S)
    if not m:
        return None, {}
    attrs = m.group(1)
    kind_m = re.search(r'data-kind="([a-z]+)"', attrs)
    kind = kind_m.group(1) if kind_m else None
    body = (m.group(2) or "").strip()
    if not body:
        src = re.search(r'data-src="([^"]+)"', attrs)
        p = OUT / src.group(1) if src else None
        if p and p.exists():
            body = p.read_text(encoding="utf-8")
    if not body:
        return kind, {}
    return kind, json.loads(body)


kind, cmp_map = compare_payload(home)
check(kind == "tour", f"홈 tpCompare kind={kind}")
check(len(cmp_map) == 84, f"홈 비교 데이터 {len(cmp_map)}건 (기대 84)")
adds = set(re.findall(r'data-cmp-add="(tour:[^"]+)"', home))
check(adds == set(cmp_map), f"홈 비교 버튼 {len(adds)}개 ↔ 데이터 {len(cmp_map)}개 불일치")
wishes = re.findall(r'data-wish="(tour:[^"]+)" data-wish-item="([^"]*)"', home)
check(len(wishes) == 84, f"홈 찜 버튼 {len(wishes)}개 (기대 84)")
for key, raw in wishes:
    try:
        d = json.loads(raw.replace("&quot;", '"').replace("&amp;", "&"))
        check(bool(d.get("n")) and d.get("u", "").startswith("https://"), f"홈 찜 데이터 이상 {key}")
    except Exception as e:
        fails.append(f"홈 찜 데이터 JSON 오류 {key}: {e}")

kind2, cmp2 = compare_payload(stays)
check(kind2 == "stay", f"/stays tpCompare kind={kind2}")
check(len(cmp2) == 116, f"/stays 비교 데이터 {len(cmp2)}건 (기대 119)")
adds2 = set(re.findall(r'data-cmp-add="(stay:[^"]+)"', stays))
check(adds2 == set(cmp2), f"/stays 비교 버튼 {len(adds2)}개 ↔ 데이터 {len(cmp2)}개 불일치")
for key, h in cmp2.items():
    check(h.get("p", 0) > 0, f"/stays 비교 가격 없음 {key}")
    check(h.get("sc", 0) > 0, f"/stays 비교 평점 없음 {key}")
    check("trip_sub3=" in h.get("u", ""), f"/stays 비교 링크 제휴 파라미터 없음 {key}")
    check(bool(h.get("bd")) is True, f"/stays 배지 없음 {key}")

# ---------------------------------------------------------------- 3·4. 결정 배지 정직성
ALLOWED = {"ko", "now", "free", "warn", "tax", "plain", "date"}
cards = re.findall(r'<article class="pcard[^"]*" id="t-([^"]+)".*?</article>', home, re.S)
badge_bad = []
for cid in cards:
    m = re.search(r'<article class="pcard[^"]*" id="t-%s".*?</article>' % re.escape(cid), home, re.S)
    if not m:
        continue
    block = m.group(0)
    t = next((x for x in tour_doc["tours"] if x["id"] == cid), None)
    if not t:
        continue
    txt = " ".join(str(t.get(k) or "") for k in ("perks", "meeting"))
    for cls, title, label in re.findall(r'<span class="db db--([a-z]+)" title="([^"]*)">([^<]+)</span>', block):
        if cls not in ALLOWED:
            badge_bad.append(f"{cid}: 알 수 없는 배지 클래스 {cls}")
        if label == "즉시확정" and not re.search(r"즉시\s*확정", txt):
            badge_bad.append(f"{cid}: 즉시확정 근거 없음")
        if label in ("모바일 바우처", "모바일 티켓") and "모바일" not in txt:
            badge_bad.append(f"{cid}: 모바일 근거 없음")
        if label == "무료 취소" and not ("무료" in (t.get("cancelShort") or "") or "전액 환불" in (t.get("cancelShort") or "")):
            badge_bad.append(f"{cid}: 무료 취소 근거 없음")
        if label == "한국어 가이드" and "한국어" not in (t.get("guide") or ""):
            badge_bad.append(f"{cid}: 한국어 가이드 근거 없음")
check(not badge_bad, f"결정 배지 근거 불일치 {len(badge_bad)}건: {badge_bad[:5]}")

stay_badges = re.findall(r'<span class="db db--([a-z]+)" title="([^"]*)">([^<]+)</span>', stays)
for cls, title, label in stay_badges:
    if cls not in ALLOWED:
        fails.append(f"/stays 알 수 없는 배지 클래스 {cls}")
    if label == "세금·봉사료 포함" and "세금" not in title:
        fails.append("/stays 세금 표기 근거 없음")
check(any(lbl == "세금·봉사료 포함" for _, _, lbl in stay_badges), "/stays 세금·봉사료 포함 배지 없음")

# ---------------------------------------------------------------- 5. id 중복
for name, html in (("index.html", home), ("stays.html", stays)):
    ids = re.findall(r'(?<![-\w])id="([^"]+)"', html)
    dup = sorted({x for x in ids if ids.count(x) > 1 and (x.startswith("t-") or x in ("cmpBar", "cmpModal", "tpCompare"))})
    check(not dup, f"{name}: 새 id 중복 {dup[:5]}")

# ---------------------------------------------------------------- 6. JS
# v43: v41 의 퀵서치·찜·비교는 tp-v43.js 로 이어지고, D-Day·참고 글 저장이 더해졌다.
js = OUT / "assets" / "tp-v43.js"
check(js.exists(), "assets/tp-v43.js 없음")
check(not (OUT / "assets" / "tp-v41.js").exists(), "구 assets/tp-v41.js 가 남아 있음")
check(not (OUT / "assets" / "tp-v42.js").exists(), "구 assets/tp-v42.js 가 남아 있음")
if js.exists():
    src = read(js)
    check("data-qs-open" in src and "tpCompare" in src and "trippick.wish.v1" in src, "tp-v43.js 핵심 기능 누락")
    check("trippick.trip.v1" in src and "trippick.bookmarks.v1" in src, "tp-v43.js D-Day·북마크 기능 누락")
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
            print("(esprima·node 없음 — JS 문법 검사 생략)")

print(f"검색 색인 {len(items)}건 " + " · ".join(f"{k} {counts.get(k)}" for k in expect))
print(f"비교 데이터 홈 {len(cmp_map)} · /stays {len(cmp2)} · 찜 버튼 홈 {len(wishes)} · /stays {len(adds2)}")
print(f"결정 배지 {len(re.findall(r'<span class=\"db db--', home + stays))}개 문구·근거 검사")
if fails:
    print("\n실패:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("\n모든 검사 통과")
