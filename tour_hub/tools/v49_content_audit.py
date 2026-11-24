#!/usr/bin/env python3
"""v49 감사 — 가이드 본문 분량·제휴 비율·중복 키워드 + 전 페이지 내부 링크 in-degree."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse, unquote

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


def page_url(rel: str) -> str:
    p = rel.as_posix()
    p = re.sub(r"index\.html$", "", p)
    return SITE + "/" + p


def norm_href(href: str, base_url: str) -> str | None:
    from urllib.parse import urljoin
    u = urljoin(base_url, href)
    if not u.startswith(SITE):
        return None
    path = urlparse(u).path
    if path.endswith("index.html"):
        path = path[: -len("index.html")]
    if path == "":
        path = "/"
    # 확장자 없는 pretty URL 을 실제 파일 키로
    if path.endswith("/"):
        path += "index.html"
    elif not re.search(r"\.[a-z0-9]{2,5}$", path):
        path += ".html"
    return path


def main():
    pages = {}
    for f in OUT.rglob("*.html"):
        rel = f.relative_to(OUT)
        if rel.name in ("googleece2734ba5b7b23a.html", "naver1a2e72ce656ca4889c08fec3050b4703.html"):
            continue
        if "assets" in rel.parts:
            continue
        pages[rel.as_posix()] = f

    # ---- in-degree ----
    indeg = Counter()
    edges = defaultdict(set)
    for rel, f in pages.items():
        s = f.read_text(encoding="utf-8", errors="ignore")
        base = page_url(Path(rel))
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

    print(f"[pages] {len(pages)}")
    print("\n=== in-degree 하위 25 ===")
    for rel, n in sorted(indeg.items(), key=lambda x: (x[1], x[0]))[:25]:
        print(f"{n:4d}  {rel}   ← from {sorted(edges[rel])[:4]}")

    # ---- guides ----
    gdir = OUT / "guides"
    rows = []
    for f in sorted(gdir.glob("*.html")):
        if f.name == "index.html":
            continue
        s = f.read_text(encoding="utf-8", errors="ignore")
        art = re.search(r'<article class="doc">(.*?)</article>', s, re.S)
        body = art.group(1) if art else s
        # 요약·목차 박스 제외한 순수 본문
        core = re.sub(r'<div class="g-sum">.*?</div>\s*</div>', " ", body, flags=re.S)
        core = re.sub(r'<div class="gtoc">.*?</div>\s*</div>', " ", core, flags=re.S)
        text_all = strip(body)
        text_core = strip(core)
        aff = sum(1 for h in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', body) if any(a in h for a in AFF))
        internal = sum(1 for h in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', body)
                       if not h.startswith(("#", "mailto:", "tel:", "javascript:")) and not h.startswith("http"))
        ext = sum(1 for h in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', body) if h.startswith("http"))
        title = re.search(r"<title>(.*?)</title>", s, re.S)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", body, re.S)
        rows.append({
            "file": f.name,
            "title": strip(title.group(1)) if title else "",
            "h1": strip(h1.group(1)) if h1 else "",
            "chars": len(re.sub(r"\s", "", text_all)),
            "core_chars": len(re.sub(r"\s", "", text_core)),
            "aff": aff, "internal": internal, "ext": ext,
            "h2": len(h2),
            "indeg": indeg.get("guides/" + f.name, 0),
        })

    print(f"\n=== 가이드 {len(rows)}편 ===")
    print("본문(요약·목차 제외) 공백제외 글자수 분포:")
    cs = sorted(r["core_chars"] for r in rows)
    for q in (0, 5, 10, 25, 50, 75, 90, 100):
        i = min(len(cs) - 1, int(q / 100 * (len(cs) - 1)))
        print(f"  p{q:3d} = {cs[i]}")

    short = sorted(rows, key=lambda r: r["core_chars"])[:20]
    print("\n짧은 가이드 20편 (core 글자수, 제휴/내부링크):")
    for r in short:
        print(f"  {r['core_chars']:5d}  aff={r['aff']:2d} int={r['internal']:2d} h2={r['h2']:2d}  {r['file']}")

    thin = [r for r in rows if r["core_chars"] < 1500]
    print(f"\n1,500자 미만: {len(thin)}편")

    heavy = sorted(rows, key=lambda r: -r["aff"])[:15]
    print("\n제휴 링크 많은 가이드 15편:")
    for r in heavy:
        print(f"  aff={r['aff']:2d} int={r['internal']:2d} chars={r['core_chars']:5d}  {r['file']}")

    # 카니발라이제이션: 제목 토큰 자카드
    def toks(t):
        return set(re.findall(r"[가-힣]{2,}|[A-Za-z]{3,}", t))
    pairs = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = toks(rows[i]["title"]), toks(rows[j]["title"])
            if not a or not b:
                continue
            jac = len(a & b) / len(a | b)
            pairs.append((jac, rows[i]["file"], rows[j]["file"], rows[i]["title"], rows[j]["title"]))
    pairs.sort(reverse=True)
    print("\n제목 유사도 상위 12쌍 (자카드):")
    for jac, fa, fb, ta, tb in pairs[:12]:
        print(f"  {jac:.2f}  {fa} | {fb}")
        print(f"        {ta[:60]}  /  {tb[:60]}")

    Path("/workspace/trippick_repo/v49_guides_audit.json").write_text(
        json.dumps({"guides": rows, "indeg": dict(indeg), "pairs": [
            {"jac": j, "a": a, "b": b} for j, a, b, _, _ in pairs[:30]]}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    # 총계
    print("\n총 제휴 링크(가이드 본문):", sum(r["aff"] for r in rows))


if __name__ == "__main__":
    main()
