#!/usr/bin/env python3
"""v50 콘텐츠 감사 — 가이드 본문 분량·제휴 링크 밀도·제목 유사도·내부 링크 고립.

v49_content_audit.py 의 두 가지 결함을 고친 판입니다.
  1) 요약박스(g-sum)·목차(gtoc)를 지울 때 `.*?</div>\s*</div>` 정규식을 써서
     일부 글에서 본문 대부분을 함께 지웠습니다(예: travel-hacks 는 6,124자 → 1,446자).
     → div 깊이를 세는 균형 파서로 바꿉니다.
  2) 제목 유사도만 보고 검색 의도를 구분하지 못했습니다.
     → 제목·H1·메타 description 을 함께 출력합니다.

    python3 tools/v50_content_audit.py [--full]
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

OUT = Path(__file__).resolve().parent.parent.parent / "deploy_site"
SITE = "https://trippick.pages.dev"
AFF = ("naver.me", "link.coupang.com", "trip.com", "klook.com", "agoda", "booking.com",
       "yanolja", "yeogi", "smartstore", "brandconnect", "coupang")


def strip(s: str) -> str:
    s = re.sub(r"<script\b.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style\b.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<svg\b.*?</svg>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&[a-z]+;|&#\d+;", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def cut_block(html: str, cls: str) -> str:
    """<div class="{cls}..."> … 짝이 맞는 </div> 까지를 통째로 지운다."""
    i = html.find(f'<div class="{cls}')
    if i < 0:
        return html
    depth = 0
    for m in re.finditer(r"<div\b|</div>", html[i:]):
        if m.group(0) == "</div>":
            depth -= 1
            if depth == 0:
                return html[:i] + html[i + m.end():]
        else:
            depth += 1
    return html[:i]


def page_url(rel: str) -> str:
    p = re.sub(r"index\.html$", "", rel)
    return SITE + "/" + p


def norm_href(href: str, base_url: str) -> str | None:
    u = urljoin(base_url, href)
    if not u.startswith(SITE):
        return None
    path = urlparse(u).path
    if path.endswith("index.html"):
        path = path[: -len("index.html")]
    if path == "":
        path = "/"
    if path.endswith("/"):
        path += "index.html"
    elif not re.search(r"\.[a-z0-9]{2,5}$", path):
        path += ".html"
    return path


def main():
    pages = {}
    for f in OUT.rglob("*.html"):
        rel = f.relative_to(OUT).as_posix()
        if "assets" in rel.split("/"):
            continue
        pages[rel] = f

    indeg = Counter()
    edges = defaultdict(set)
    for rel, f in pages.items():
        s = f.read_text(encoding="utf-8", errors="ignore")
        base = page_url(Path(rel).as_posix())
        for href in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', s):
            if href.startswith(("#", "mailto:", "javascript:", "tel:")):
                continue
            tgt = norm_href(href, base)
            if tgt is None:
                continue
            trel = tgt.lstrip("/")
            if trel not in pages or trel == rel:
                continue
            edges[trel].add(rel)
            indeg[trel] += 1

    gdir = OUT / "guides"
    rows = []
    for f in sorted(gdir.glob("*.html")):
        if f.name == "index.html":
            continue
        s = f.read_text(encoding="utf-8", errors="ignore")
        art = re.search(r'<article class="doc">(.*?)</article>', s, re.S)
        body = art.group(1) if art else s
        core = cut_block(cut_block(body, "g-sum"), "gtoc")
        text_core = strip(core)
        aff = sum(1 for h in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', body) if any(a in h for a in AFF))
        title = re.search(r"<title>(.*?)</title>", s, re.S)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        desc = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
        rows.append({
            "file": f.name,
            "slug": f.stem,
            "title": strip(title.group(1)) if title else "",
            "h1": strip(h1.group(1)) if h1 else "",
            "desc": strip(desc.group(1)) if desc else "",
            "chars": len(re.sub(r"\s", "", text_core)),
            "aff": aff,
            "per": round(len(re.sub(r"\s", "", text_core)) / max(aff, 1)),
            "h2": len(re.findall(r"<h2[^>]*>", body)),
            "indeg": indeg.get("guides/" + f.name, 0),
        })

    cs = sorted(r["chars"] for r in rows)
    print(f"[가이드 {len(rows)}편] 본문(요약·목차 제외) 공백제외 글자수")
    for q in (0, 5, 10, 25, 50, 75, 90, 100):
        i = min(len(cs) - 1, int(q / 100 * (len(cs) - 1)))
        print(f"  p{q:3d} = {cs[i]}")
    thin = [r for r in rows if r["chars"] < 1800]
    print(f"  1,800자 미만: {len(thin)}편 {[r['slug'] for r in thin]}")

    print("\n짧은 가이드 10편")
    for r in sorted(rows, key=lambda r: r["chars"])[:10]:
        print(f"  {r['chars']:5d}자  제휴 {r['aff']:2d}개({r['per']}자당 1개)  h2 {r['h2']:2d}  {r['slug']}")

    print("\n제휴 링크 많은 가이드 8편 (밀도순)")
    for r in sorted(rows, key=lambda r: r["per"])[:8]:
        print(f"  {r['chars']:5d}자  제휴 {r['aff']:2d}개  {r['per']:4d}자당 1개  {r['slug']}")

    def toks(t):
        return set(re.findall(r"[가-힣]{2,}|[A-Za-z]{3,}", t))

    pairs = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = toks(rows[i]["title"]), toks(rows[j]["title"])
            if not a or not b:
                continue
            pairs.append((len(a & b) / len(a | b), rows[i], rows[j]))
    pairs.sort(reverse=True, key=lambda x: x[0])
    print("\n제목 유사도 상위 8쌍")
    for jac, a, b in pairs[:8]:
        print(f"  {jac:.2f}  {a['slug']} | {b['slug']}")
        print(f"         A: {a['title']}")
        print(f"         B: {b['title']}")

    low = sorted(rows, key=lambda r: r["indeg"])[:8]
    print("\n내부 링크 in-degree 하위 8편")
    for r in low:
        print(f"  {r['indeg']:3d}  {r['slug']}")

    if "--full" in __import__("sys").argv:
        print("\n전체 목록")
        for r in sorted(rows, key=lambda r: r["chars"]):
            print(f"  {r['chars']:5d}  aff={r['aff']:2d} indeg={r['indeg']:2d}  {r['slug']}")

    (Path(__file__).resolve().parent.parent.parent / "v50_guides_audit.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
